# Rasterise the falcon exactly as murmuration.html fills it, and score it against the model.
#
#   uvx --with pillow --with numpy python falcon/outline/rasterise_outline.py \
#       [--html murmuration.html] [--sil falcon/renders/silhouettes] [--out DIR]
#
# The page's own FALCON table, pushFalcon, birdFrame and wp are cut out of the HTML and run under
# node with a plan-view projection (heading +y, no dihedral, scale 2 so one unit is one half-span).
# Every Path2D that pushFalcon fills is recorded and rasterised here with the canvas non-zero
# winding rule, one fill per path as the page's draw call does, right and left sides included.
# The frame matches falcon_render.py's top camera: 1200 px, 1.25 m across, centred on world
# (0, -0.05), head up, so the result overlays renders/silhouettes/<pose>__top.png pixel for pixel.
#
# Prints, for each key pose, IoU against the model's silhouette (and what even-odd or a single
# shared path would have given), then the areas of a sweep of blends.  With --out it writes
# overlays: black both, red model only, blue page only.
import argparse, json, os, re, subprocess, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RES, VIEW_M, CENTRE_Y = 1200, 1.25, -0.05

JS = r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
function cut(re) {                                   // a declaration, from its start to its matching close
  const m = re.exec(src); if (!m) throw new Error('not found: ' + re);
  let i = src.indexOf(m[1] || '{', m.index), d = 0;
  for (; i < src.length; i++) { const c = src[i]; if (c === '{') d++; else if (c === '}' && --d === 0) break; }
  return src.slice(m.index, i + 1) + ';\n';
}
const code = 'let _x = 0, _y = 0, _z = 0; function P(x, y, z) { _x = x; _y = y; _z = z; }\n'
  + /^let bX,.*$/m.exec(src)[0] + '\n' + cut(/function wp\(/) + cut(/function birdFrame\(/)
  + cut(/const FALCON = /) + /^const FALCON_SPAN = [^;]*;/m.exec(src)[0] + '\n' + cut(/function pushFalcon\(/)
  + `class Rec { constructor() { this.subs = []; } moveTo(x, y) { this.subs.push([[x, y]]); }
       lineTo(x, y) { this.subs[this.subs.length - 1].push([x, y]); } closePath() {} }
     const jobs = JSON.parse(process.argv[2]), out = [];
     for (const [tuck, fan, fx = 0, fy = 1, fz = 0, th = 0] of jobs) {
       const paths = [new Rec(), new Rec(), new Rec()];      // right wing, left wing, body and tail
       pushFalcon(paths, 0, 0, 0, fx, fy, fz, th, 2, tuck, fan);
       out.push(paths.map(p => p.subs));
     }
     console.log(JSON.stringify({ falcon: FALCON, span: FALCON_SPAN, shapes: out }));`;
new Function('process', code)(process);
"""


def page_shapes(html, jobs):
    r = subprocess.run(['node', '-e', JS, html, json.dumps(jobs)], capture_output=True, text=True)
    if r.returncode: sys.exit(r.stderr)
    return json.loads(r.stdout)


def winding(subpaths, to_px):
    """Winding number at every pixel centre for a set of closed subpaths (canvas fills close them)."""
    d = np.zeros((RES, RES + 1), np.int32)
    for sp in subpaths:
        p = to_px(np.asarray(sp, float))
        q = np.roll(p, -1, axis=0)
        for (x0, y0), (x1, y1) in zip(p, q):
            if y0 == y1: continue
            lo, hi = (y0, y1) if y0 < y1 else (y1, y0)
            r0, r1 = max(int(np.ceil(lo - .5)), 0), min(int(np.ceil(hi - .5)), RES)   # rows whose centre is in [lo, hi)
            if r1 <= r0: continue
            rows = np.arange(r0, r1)
            xs = x0 + (rows + .5 - y0) * (x1 - x0) / (y1 - y0)
            cols = np.clip(np.ceil(xs - .5).astype(int), 0, RES)
            np.add.at(d, (rows, cols), 1 if y1 > y0 else -1)
    return np.cumsum(d, axis=1)[:, :RES]


def rasterise(shape, half_span, origin, rule='nonzero', one_path=False, to_px=None):
    def plan(p):                                     # page units (x right, y forward, half-spans) -> pixels
        return np.stack([RES / 2 + p[:, 0] * half_span / VIEW_M * RES,
                         RES / 2 - (p[:, 1] * half_span + origin - CENTRE_Y) / VIEW_M * RES], 1)
    to_px = to_px or plan
    paths = [[sp for path in shape for sp in path]] if one_path else shape
    out = np.zeros((RES, RES), bool)
    for path in paths:
        w = winding(path, to_px)
        out |= (w != 0) if rule == 'nonzero' else (w % 2 != 0)
    return out


def iou(a, b): return (a & b).sum() / max((a | b).sum(), 1)
def area(m): return m.sum() * (VIEW_M / RES) ** 2


def overlay(model, page):
    im = np.full(model.shape + (3,), 255, np.uint8)
    im[model & page] = (20, 20, 20); im[model & ~page] = (230, 40, 40); im[~model & page] = (40, 80, 230)
    return Image.fromarray(im)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--html', default=os.path.join(ROOT, 'murmuration.html'))
    ap.add_argument('--sil', default=os.path.join(ROOT, 'falcon', 'renders', 'silhouettes'))
    ap.add_argument('--poses', default=os.path.join(ROOT, 'falcon', 'blender', 'poses_falcon.json'))
    ap.add_argument('--out')
    a = ap.parse_args()
    poses = json.load(open(a.poses))
    first = page_shapes(a.html, [[0, 0]])
    F = first['falcon']
    hs, origin, keys, knots = F['halfSpanM'], F['aOriginM'], F['keys'], F['knots']
    blends = [0, .17, .33, .5, .67, .83, 1]
    jobs = [[k, poses[n].get('tail_fan', 0)] for n, k in zip(keys, knots)] + [[t, 0] for t in blends]
    shapes = page_shapes(a.html, jobs)['shapes']
    if a.out: os.makedirs(a.out, exist_ok=True)
    print(f'page table: wing {len(F["wing"][0]) // 2} points x {len(keys)} keys, body {len(F["body"]) // 2}, '
          f'tail {len(F["tail"]) // 2}; FALCON_SPAN {first["span"]}; {len(shapes[0])} separately filled path(s)')
    print('\nkey pose        tuck   IoU     area page  model (m2)   model-only px  page-only px | IoU even-odd  IoU one shared path')
    for n, k, shape in zip(keys, knots, shapes):
        page = rasterise(shape, hs, origin)
        model = np.asarray(Image.open(os.path.join(a.sil, f'{n}__top.png')).convert('L')) < 128
        eo = rasterise(shape, hs, origin, rule='evenodd')
        one = rasterise(shape, hs, origin, one_path=True)
        print(f'{n:14s} {k:5.3f}  {iou(page, model):.4f}  {area(page):.4f}    {area(model):.4f}       '
              f'{(model & ~page).sum():6d}        {(page & ~model).sum():6d}      |   {iou(eo, model):.4f}        {iou(one, model):.4f}')
        if a.out: overlay(model, page).save(os.path.join(a.out, f'overlay_{n}.png'))
    print('\nblend   tuck   area m2   width m   centroid y m (model frame)')
    strip = []
    for t, shape in zip(blends, shapes[len(keys):]):
        m = rasterise(shape, hs, origin)
        ys, xs = np.nonzero(m)
        cy = CENTRE_Y + (RES / 2 - (ys.mean() + .5)) * VIEW_M / RES
        print(f'        {t:4.2f}   {area(m):.4f}    {(xs.max() - xs.min() + 1) * VIEW_M / RES:.3f}     {cy:+.4f}')
        strip.append(Image.fromarray(np.where(m, 20, 255).astype(np.uint8)))
        if a.out: strip[-1].save(os.path.join(a.out, f'blend_{t:.2f}.png'))
    # Seen level from the rear quarter with the wings raised 0.5 rad, the near wing shows its underside
    # and the far wing its upper side: opposite windings on screen.  One shared path cancels the lap.
    side = page_shapes(a.html, [[0, 0, .8, 0, .6, .5]])['shapes'][0]
    px = lambda p: np.stack([RES / 2 + p[:, 0] * 500, RES * .7 - p[:, 1] * 500], 1)
    sep, one = rasterise(side, hs, origin, to_px=px), rasterise(side, hs, origin, one_path=True, to_px=px)
    print(f'\nrear-quarter view, wings raised: filled px with one fill per part {sep.sum()}, with one shared path {one.sum()} '
          f'({(sep & ~one).sum()} px cancelled)')
    if a.out:
        overlay(sep, one).save(os.path.join(a.out, 'overlay_rear_quarter.png'))
        sheet = Image.new('L', (RES * len(strip) // 2, RES // 2), 255)
        for i, im in enumerate(strip): sheet.paste(im.resize((RES // 2, RES // 2)), (i * RES // 2, 0))
        sheet.save(os.path.join(a.out, 'blend_strip.png'))


if __name__ == '__main__':
    main()
