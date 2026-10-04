"""Segment a bird-against-sky photo (or a render) and measure its planform.

usage: silhouette.py IMAGE [--out DIR] [--invert] [--thresh T]

Steps: Otsu threshold (bird darker than sky unless --invert), keep the largest component,
fill holes, then find the bilateral symmetry axis by maximising reflection IoU over angle
and offset.  In the symmetry frame (u across = span, v along = body, +v toward the head)
it reports span, length, tail and per-station leading/trailing edges, all normalised by
the half-span so photos at any scale compare directly.
"""
import argparse, json, pathlib, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import filters, measure, morphology, transform


def segment_skydist(img, hyst=None):
    """Bird = far (in RGB) from a smooth sky model.  Works for blue, grey and white skies and for
    both pale bellies and black wingtips, which a single luma or blueness threshold cannot."""
    rgb = np.asarray(img.convert('RGB'), dtype=float) / 255
    H, W, _ = rgb.shape
    yy, xx = np.mgrid[0:H, 0:W] / max(H, W)
    A = np.stack([np.ones_like(xx), xx, yy, xx * xx, xx * yy, yy * yy], -1).reshape(-1, 6)
    flat = rgb.reshape(-1, 3)
    # first guess at sky: the image border
    b = np.zeros((H, W), bool); b[:H // 20] = b[-H // 20:] = True; b[:, :W // 20] = b[:, -W // 20:] = True
    sky = b.ravel()
    for _ in range(3):
        idx = np.flatnonzero(sky)[:: max(1, sky.sum() // 150000)]
        coef, *_ = np.linalg.lstsq(A[idx], flat[idx], rcond=None)
        bg = A @ coef
        d = np.linalg.norm(flat - bg, axis=1)
        t = filters.threshold_otsu(d)
        sky = d <= t * .6
    m = (d > t).reshape(H, W)
    m = ndi.binary_opening(m, structure=morphology.disk(1))
    lab = measure.label(m)
    big = np.argmax(np.bincount(lab.ravel())[1:]) + 1
    if hyst:
        # pale, backlit flight feathers (starling underwing) sit below the Otsu cut: keep weaker
        # pixels when they connect to the bird, then bridge the gaps between feather shafts with a
        # closing scaled to the bird (about 0.5 % of its bounding-box diagonal)
        weak = (d > t * hyst).reshape(H, W)
        weak = ndi.binary_opening(weak, structure=morphology.disk(1))
        lab_w = measure.label(weak)
        keep = np.unique(lab_w[lab == big]); keep = keep[keep > 0]
        m = np.isin(lab_w, keep)
        ys, xs = np.nonzero(m)
        r = max(2, int(round(.005 * np.hypot(np.ptp(xs), np.ptp(ys)))))
        m = ndi.binary_closing(np.pad(m, r + 1), structure=morphology.disk(r))[r + 1:-r - 1, r + 1:-r - 1]
        return ndi.binary_fill_holes(m)
    m = ndi.binary_closing(lab == big, structure=morphology.disk(2))
    return ndi.binary_fill_holes(m)


def segment(img, invert=False, thresh=None, bluesky=False, skydist=False, hyst=None):
    if skydist:
        return segment_skydist(img, hyst)
    if bluesky:                                  # bird = not blue: pale buff bellies match the sky in luma
        rgb = np.asarray(img.convert('RGB'), dtype=float) / 255
        g = 1 - np.clip(rgb[..., 2] - (rgb[..., 0] + rgb[..., 1]) / 2 + .5, 0, 1)
        invert = True
    else:
        g = np.asarray(img.convert('L'), dtype=float) / 255
    # sky gradients defeat a global threshold: fit a smooth quadratic sky to the pixels a first
    # pass calls sky, subtract it, threshold again (twice).  A filter-based background fails
    # when the bird fills much of the frame.
    H, W = g.shape
    yy, xx = np.mgrid[0:H, 0:W] / max(H, W)
    A = np.stack([np.ones_like(xx), xx, yy, xx * xx, xx * yy, yy * yy], -1).reshape(-1, 6)
    d = -g if not invert else g
    for _ in range(3):
        t = filters.threshold_otsu(d)
        sky = (d <= t).ravel()
        idx = np.flatnonzero(sky)[:: max(1, sky.sum() // 200000)]
        coef, *_ = np.linalg.lstsq(A[idx], g.ravel()[idx], rcond=None)
        bg = (A @ coef).reshape(H, W)
        d = (g - bg) if invert else (bg - g)
    t = thresh if thresh is not None else filters.threshold_otsu(d)
    m = d > t
    m = ndi.binary_opening(m, structure=morphology.disk(1))
    lab = measure.label(m)
    if lab.max() == 0:
        raise SystemExit('nothing segmented')
    big = np.argmax(np.bincount(lab.ravel())[1:]) + 1
    m = ndi.binary_fill_holes(lab == big)
    return m


def reflect_iou(pts, mask_set, theta, c, shape):
    # reflect points across the line through c with direction (cos θ, sin θ)
    d = np.array([np.cos(theta), np.sin(theta)])
    p = pts - c
    proj = p @ d
    r = 2 * np.outer(proj, d) - p + c
    ri = np.round(r).astype(int)
    ok = (ri[:, 0] >= 0) & (ri[:, 0] < shape[1]) & (ri[:, 1] >= 0) & (ri[:, 1] < shape[0])
    hit = np.zeros(len(pts), bool)
    hit[ok] = mask_set[ri[ok, 1], ri[ok, 0]]
    inter = hit.sum()
    return inter / (2 * len(pts) - inter)


def symmetry_axis(m):
    ys, xs = np.nonzero(m)
    pts = np.c_[xs, ys].astype(float)
    if len(pts) > 40000:
        pts = pts[np.random.default_rng(0).choice(len(pts), 40000, replace=False)]
    c0 = pts.mean(0)
    # span axis ≈ major principal axis; body (symmetry) axis ≈ perpendicular
    ev, evec = np.linalg.eigh(np.cov((pts - c0).T))
    best = (-1, 0.0, c0)
    for k in (0, 1):                                   # either principal axis may be the symmetry axis
        th0 = np.arctan2(evec[1, k], evec[0, k])
        across = np.array([-np.sin(th0), np.cos(th0)])
        for dth in np.radians(np.arange(-25, 25.1, 1)):
            for off in np.linspace(-.15, .15, 31) * np.ptp(pts @ across):
                c = c0 + off * across
                s = reflect_iou(pts, m, th0 + dth, c, m.shape)
                if s > best[0]:
                    best = (s, th0 + dth, c)
    s, th, c = best
    for dth in np.radians(np.linspace(-1, 1, 11)):     # refine
        for off in np.linspace(-3, 3, 13):
            cc = c + off * np.array([-np.sin(th), np.cos(th)])
            v = reflect_iou(pts, m, th + dth, cc, m.shape)
            if v > best[0]:
                best = (v, th + dth, cc)
    return best


def measure_planform(m, theta, c, head_hint=None):
    ys, xs = np.nonzero(m)
    p = np.c_[xs, ys].astype(float) - c
    v_dir = np.array([np.cos(theta), np.sin(theta)])   # along body
    u_dir = np.array([-v_dir[1], v_dir[0]])            # across (span)
    u, v = p @ u_dir, p @ v_dir
    half = (u.max() - u.min()) / 2
    uc = (u.max() + u.min()) / 2
    u = u - uc
    # orient +v toward the head: the head is the narrow short protrusion, the tail is longer.
    # heuristic: wings' leading edges lie on the head side, so the wing mass centroid
    # (|u| > 0.4 half) sits on the head side of the body centre-of-extent.
    core = np.abs(u) < .06 * half
    vmid = (v[core].max() + v[core].min()) / 2
    wing = np.abs(u) > .4 * half
    vsign = 1
    if v[wing].mean() < vmid:
        v = -v; vsign = -vsign
    if head_hint == 'flip':
        v = -v; vsign = -vsign
    core = np.abs(u) < .06 * half
    nose, tail = v[core].max(), v[core].min()
    length = nose - tail
    # per-station edges, both sides averaged
    stations = np.linspace(0, 1, 41)
    le, te = [], []
    for s in stations:
        band = np.abs(np.abs(u) / half - s) < .0125
        if band.sum() < 3:
            le.append(np.nan); te.append(np.nan); continue
        le.append(np.percentile(v[band], 99.5) / half)
        te.append(np.percentile(v[band], 0.5) / half)
    le, te = np.array(le), np.array(te)
    # tail: below the wing trailing edge at the root region (|u| < 0.12 half) the silhouette is tail only
    area = m.sum() / half ** 2
    # body/tail half-width along the axis: the contiguous run of pixels through u = 0 in each
    # v bin (under the wings this run is the whole wing, so it is reported but flagged)
    vb = np.linspace(tail, nose, 61)
    bw = []
    for k in range(len(vb) - 1):
        sel = (v >= vb[k]) & (v < vb[k + 1])
        uu = np.sort(np.round(u[sel]).astype(int))          # pixels
        if len(uu) == 0:
            bw.append(np.nan); continue
        uu = np.unique(uu)
        if not (uu.min() <= 0 <= uu.max()):
            bw.append(0.0); continue
        i0 = np.searchsorted(uu, 0)
        lo = hi = min(i0, len(uu) - 1)
        while hi + 1 < len(uu) and uu[hi + 1] - uu[hi] <= 2: hi += 1
        while lo - 1 >= 0 and uu[lo] - uu[lo - 1] <= 2: lo -= 1
        bw.append(float((uu[hi] - uu[lo] + 1) / 2 / half))
    return dict(
        body_v=((vb[:-1] + vb[1:]) / 2 / half).tolist(), body_halfwidth=bw,
        half_span_px=float(half), span_over_length=float(2 * half / length),
        length_over_halfspan=float(length / half), nose=float(nose / half), tail_tip=float(tail / half),
        area_over_halfspan2=float(area), aspect_ratio=float((2 * half) ** 2 / m.sum()),
        stations=stations.tolist(), le=le.tolist(), te=te.tolist(),
        chord=(le - te).tolist(),
    ), (u / half, v / half), dict(c=c, u_dir=u_dir, v_dir=v_dir, uc=uc, vsign=vsign, half=half)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('image'); ap.add_argument('--out', default='.')
    ap.add_argument('--invert', action='store_true'); ap.add_argument('--thresh', type=float)
    ap.add_argument('--bluesky', action='store_true'); ap.add_argument('--skydist', action='store_true')
    ap.add_argument('--hyst', type=float, help='with --skydist: keep pixels above HYST x the Otsu cut when connected to the bird (e.g. 0.4)')
    ap.add_argument('--flip', action='store_true', help='head direction heuristic got it wrong')
    a = ap.parse_args()
    img = Image.open(a.image)
    m = segment(img, a.invert, a.thresh, a.bluesky, a.skydist, a.hyst)
    iou, th, c = symmetry_axis(m)
    res, (u, v), fr = measure_planform(m, th, c, 'flip' if a.flip else None)
    res.update(image=a.image, symmetry_iou=float(iou), axis_deg=float(np.degrees(th)))
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    stem = pathlib.Path(a.image).stem
    # normalised planform raster (head up), for overlaying photos against renders
    R = 400
    # inverse mapping: every canvas pixel samples the mask, so small sources cannot leave gaps
    jj, ii = np.meshgrid(np.arange(R) + .5, np.arange(R) + .5)
    un = (jj / R * 2.2 - 1.1) * fr['half'] + fr['uc']
    vn = (1.1 - ii / R * 2.2) * fr['half'] * fr['vsign']
    src = fr['c'][None, None, :] + un[..., None] * fr['u_dir'] + vn[..., None] * fr['v_dir']
    canvas = ndi.map_coordinates(m.astype(float), [src[..., 1] - .5, src[..., 0] - .5], order=1, cval=0) > .5
    canvas = canvas.astype(np.uint8) * 255
    Image.fromarray(canvas).save(out / f'{stem}__norm.png')
    over = np.asarray(img.convert('RGB')).copy()
    over[m] = (over[m] * .4 + np.array([255, 0, 0]) * .6).astype(np.uint8)
    Image.fromarray(over).save(out / f'{stem}__mask.jpg', quality=85)
    (out / f'{stem}.json').write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ('symmetry_iou', 'span_over_length', 'aspect_ratio', 'nose', 'tail_tip')}, indent=1))


if __name__ == '__main__':
    main()
