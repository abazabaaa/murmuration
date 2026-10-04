"""Score a falcon outline table (or a silhouette render) against normalised flight-photo masks.

usage: score_outline.py OUTLINE.json POSE --photos NORM.png [NORM.png ...]
       score_outline.py OUTLINE.json POSE --photo-dir DIR --set glide|soar|all
       score_outline.py RENDER.png   LABEL ...            (an image skips the rasterising step)
       options: [--tail-fan 0..1] [--out scores.json] [--overlay path.png] [--px 1000]

OUTLINE.json is either the table the page uses today (blender/falcon-outline.json: wingGlide,
wingStoop, body, tail, tailFan) or the newer shape { wing: { <pose>: [...] }, body, tail, tailFan }.
POSE picks the wing: `glide` reads wingGlide or wing.glide, and so on.

What it does
1. Rasterises the outline the way pushFalcon() in murmuration.html fills it: right wing, left wing
   (mirrored, traversed in reverse so it winds the same way), and one body+tail polygon (down the
   right edge, back up the left), all subpaths of ONE path filled with the nonzero rule.  The
   winding number is summed over the three subpaths per pixel, as canvas does, so a region where
   they cancel would come out as a hole here too.  Flat pose (flap angle th = 0), head up; the
   page's 1 px stroke of the same path is not drawn.
2. Feeds that raster to silhouette.py's own main() (segment, symmetry axis, half-span, 400x400
   head-up raster), so the outline is normalised by the same code as the photos and renders.
   The half-span is measured, not assumed.  The head-direction heuristic is checked against the
   known orientation and silhouette.py is rerun with --flip if it got it wrong.
3. Scores whole-bird IoU against each photo mask after the best vertical shift within +-40 px
   (compare.py's best_iou, copied verbatim because compare.py has no import guard).

The photo masks are derived from third-party photographs and are not in the repository.  An
--overlay image contains them: keep it out of git (falcon/analysis/validation/ is ignored).
"""
import argparse, contextlib, glob, io, json, pathlib, sys, tempfile
import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
SETS = {  # file-name prefixes of the reference masks, HANDOVER section 7
    'glide': ['03_', '04_', '06_', 'flight_ventral_B_'],
    'soar': ['02_', 'flight_ventral_A_', '05_'],
}
SETS['all'] = SETS['glide'] + SETS['soar']
PONITZ_TUCK = (0.26, 0.36)       # Ponitz et al. 2014, tucked stoop: width / length


# ---------- outline table -> subpaths, exactly as pushFalcon() emits them ----------

def pairs(flat):
    a = np.asarray(flat, float)
    if a.ndim != 1 or len(a) % 2:
        raise SystemExit('outline lists must be flat [a, w, a, w, ...]')
    return a.reshape(-1, 2)


def load_outline(path, pose):
    d = json.loads(pathlib.Path(path).read_text())
    if isinstance(d.get('wing'), dict):                       # new format
        if pose not in d['wing']:
            raise SystemExit(f'pose {pose!r} not in wing: {sorted(d["wing"])}')
        wing = d['wing'][pose]
    else:                                                     # old format: wingGlide, wingStoop
        key = 'wing' + pose[:1].upper() + pose[1:]
        if key not in d:
            have = sorted(k[4:].lower() for k in d if k.startswith('wing'))
            raise SystemExit(f'pose {pose!r} not found ({key}); have {have}')
        wing = d[key]
    tail = pairs(d['tail'])
    fan = pairs(d['tailFan']) if 'tailFan' in d else tail
    return pairs(wing), pairs(d['body']), tail, fan


def subpaths(wing, body, tail, fan, tail_fan=0.0):
    """Three closed polygons of (a, w) points in the order pushFalcon() draws them."""
    t = tail + (fan - tail) * tail_fan
    bt = np.concatenate([body, t])
    mir = np.array([1.0, -1.0])
    return [wing,                       # side = +1
            wing[::-1] * mir,           # side = -1: j = len - 2 - i
            np.concatenate([bt, bt[::-1] * mir])]


def winding_raster(polys, px):
    """Summed winding number per pixel centre.  Returns (filled mask, geometry dict).
    Image x = w (across), image y = -a (head up)."""
    allp = np.concatenate(polys)
    pad = 0.15
    w_ext = np.abs(allp[:, 1]).max() + pad
    a_hi, a_lo = allp[:, 0].max() + pad, allp[:, 0].min() - pad
    W, H = int(round(2 * w_ext * px)), int(round((a_hi - a_lo) * px))
    xs = np.arange(W) + .5
    wind = np.zeros((H, W), np.int16)
    for p in polys:
        X = (p[:, 1] + w_ext) * px
        Y = (a_hi - p[:, 0]) * px
        for k in range(len(p)):
            x0, y0, x1, y1 = X[k], Y[k], X[(k + 1) % len(p)], Y[(k + 1) % len(p)]
            if y0 == y1:
                continue
            lo, hi = (y0, y1) if y0 < y1 else (y1, y0)
            r0, r1 = max(0, int(np.ceil(lo - .5))), min(H, int(np.ceil(hi - .5)))   # rows with lo <= y < hi
            if r1 <= r0:
                continue
            yc = np.arange(r0, r1) + .5
            xc = x0 + (yc - y0) * (x1 - x0) / (y1 - y0)       # edge x at each row
            wind[r0:r1] += (1 if y1 > y0 else -1) * (xs[None, :] < xc[:, None])
    return wind != 0, dict(px=px, w_ext=w_ext, a_hi=a_hi, a_lo=a_lo, winding_values=sorted(int(v) for v in np.unique(wind)))


def raster_extents(mask, px):
    ys, xs = np.nonzero(mask)
    width, length = (xs.max() - xs.min() + 1) / px, (ys.max() - ys.min() + 1) / px
    return dict(width_halfspans=round(float(width), 4), length_halfspans=round(float(length), 4),
                width_over_length=round(float(width / length), 4))


def direct_norm(mask, geo, R=400):
    """The 400x400 raster built straight from the table (origin a = 0, half-span = widest filled
    pixel).  Only used to check silhouette.py's orientation and normalisation, never for scores."""
    ys, xs = np.nonzero(mask)
    half = (xs.max() - xs.min() + 1) / 2 / geo['px']
    jj, ii = np.meshgrid(np.arange(R) + .5, np.arange(R) + .5)
    w = (jj / R * 2.2 - 1.1) * half
    a = (1.1 - ii / R * 2.2) * half
    x = np.floor((w + geo['w_ext']) * geo['px']).astype(int)
    y = np.floor((geo['a_hi'] - a) * geo['px']).astype(int)
    ok = (x >= 0) & (x < mask.shape[1]) & (y >= 0) & (y < mask.shape[0])
    out = np.zeros((R, R), bool)
    out[ok] = mask[y[ok], x[ok]]
    return out, half


# ---------- normalise through silhouette.py, score like compare.py ----------

def run_silhouette(image, outdir, flip=False):
    """Call silhouette.main() itself; returns (norm mask, its json)."""
    sys.path.insert(0, str(HERE))
    import silhouette
    argv = sys.argv
    sys.argv = ['silhouette.py', str(image), '--out', str(outdir)] + (['--flip'] if flip else [])
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            silhouette.main()
    finally:
        sys.argv = argv
    stem = pathlib.Path(image).stem
    return load(pathlib.Path(outdir) / f'{stem}__norm.png'), json.loads((pathlib.Path(outdir) / f'{stem}.json').read_text())


def load(p):
    return np.asarray(Image.open(p).convert('L')) > 127


def best_iou(a, b, max_shift=40):                # verbatim from compare.py
    best = (0, 0)
    for dy in range(-max_shift, max_shift + 1, 1):
        bb = np.roll(b, dy, axis=0)
        i = (a & bb).sum(); u = (a | bb).sum()
        if i / u > best[0]: best = (i / u, dy)
    return best


def photo_list(photos, photo_dir, which):
    out = [pathlib.Path(p) for p in photos or []]
    if photo_dir:
        for pre in SETS[which]:
            hit = sorted(glob.glob(str(pathlib.Path(photo_dir) / f'{pre}*__norm.png')))
            if len(hit) != 1:
                raise SystemExit(f'expected one {pre}*__norm.png in {photo_dir}, found {len(hit)}')
            out.append(pathlib.Path(hit[0]))
    return out


def score(source, pose, photos, tail_fan=0.0, px=1000, overlay=None, keep=None):
    """source: outline json or silhouette image.  Returns the result dict."""
    source = pathlib.Path(source)
    res = dict(source=source.name, pose=pose)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(keep or tmp); tmp.mkdir(parents=True, exist_ok=True)
        if source.suffix.lower() == '.json':
            mask, geo = winding_raster(subpaths(*load_outline(source, pose), tail_fan), px)
            img = tmp / f'{source.stem}__{pose}.png'
            Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).save(img)   # dark bird, white sky
            direct, half = direct_norm(mask, geo)
            norm, sj = run_silhouette(img, tmp)
            flipped = best_iou(norm, direct[::-1])[0] > best_iou(norm, direct)[0]   # origins differ, so allow the shift
            if flipped:
                norm, sj = run_silhouette(img, tmp, flip=True)
            res.update(tail_fan=tail_fan, raster_px_per_unit=px, raster_size=[mask.shape[1], mask.shape[0]],
                       winding_values=geo['winding_values'],
                       raster=dict(raster_extents(mask, px), half_span_units=round(float(half), 4)),
                       silhouette=dict(half_span_units=round(sj['half_span_px'] / px, 4),
                                       span_over_length=round(sj['span_over_length'], 4),
                                       symmetry_iou=round(sj['symmetry_iou'], 4), axis_deg=round(sj['axis_deg'], 2),
                                       needed_flip=bool(flipped),
                                       iou_vs_direct_normalisation=round(best_iou(norm, direct)[0], 4)))
        else:
            norm, sj = run_silhouette(source, tmp)
            res.update(silhouette=dict(span_over_length=round(sj['span_over_length'], 4),
                                       symmetry_iou=round(sj['symmetry_iou'], 4), axis_deg=round(sj['axis_deg'], 2)))
    per, tiles = [], []
    for p in photos:
        ref = load(p)
        v, dy = best_iou(norm, ref)
        per.append(dict(photo=p.name.replace('__norm.png', ''), iou=round(float(v), 4), shift=int(dy)))
        if overlay:
            ref = np.roll(ref, dy, axis=0)
            rgb = np.full(norm.shape + (3,), 255, np.uint8)
            rgb[ref & ~norm] = (220, 60, 60)     # photo only: red
            rgb[norm & ~ref] = (60, 90, 220)     # outline only: blue
            rgb[norm & ref] = (40, 40, 40)       # both: dark
            tiles.append(rgb)
    if per:
        res.update(photos=per, mean_iou=round(float(np.mean([x['iou'] for x in per])), 4))
    if overlay and tiles:
        pathlib.Path(overlay).parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(np.concatenate(tiles, axis=1)).save(overlay)
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('outline', help='outline table (.json) or a silhouette image')
    ap.add_argument('pose', help='glide, stoop, ... (a label only when the first argument is an image)')
    ap.add_argument('--photos', nargs='*', help='normalised photo masks (*__norm.png from silhouette.py)')
    ap.add_argument('--photo-dir', help='directory of *__norm.png; use with --set')
    ap.add_argument('--set', choices=sorted(SETS), default='glide', help='reference set taken from --photo-dir')
    ap.add_argument('--tail-fan', type=float, default=0.0, help='0 closed tail .. 1 tailFan')
    ap.add_argument('--px', type=int, default=1000, help='raster pixels per outline unit')
    ap.add_argument('--out', help='write the result as json')
    ap.add_argument('--overlay', help='red photo only, blue outline only, dark both. Contains photo masks: do not commit')
    ap.add_argument('--keep', help='directory to keep the raster and silhouette.py outputs in')
    a = ap.parse_args()
    res = score(a.outline, a.pose, photo_list(a.photos, a.photo_dir, a.set), a.tail_fan, a.px, a.overlay, a.keep)
    txt = json.dumps(res, indent=1)
    if a.out:
        pathlib.Path(a.out).write_text(txt + '\n')
    print(txt)


if __name__ == '__main__':
    main()
