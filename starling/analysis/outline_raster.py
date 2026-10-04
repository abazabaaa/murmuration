"""Rasterise an outline JSON (bird_outline.py format) to a top-view mask, and score it against a
silhouette render.  Shared by the export check and the low-point reduction.

usage: outline_raster.py OUTLINE.json POSE --check RENDER.png --ortho M --cy M
"""
import argparse, json
import numpy as np
from PIL import Image, ImageDraw


def pairs(flat): return np.asarray(flat, float).reshape(-1, 2)          # (a, w)


def bird_polys(O, pose):
    """Closed polygons in (a, w) half-span units: right+left wing chains, body, tail."""
    t = O['tailFanOfPose'].get(pose, 0)
    tail = (1 - t) * pairs(O['tail']) + t * pairs(O['tailFan'])
    polys = []
    for side in (1, -1):
        wg = pairs(O['wing'][pose]) * [1, side]
        polys.append(wg)
    body = pairs(O['body']); polys.append(np.r_[body, (body * [1, -1])[::-1]])
    polys.append(np.r_[tail, (tail * [1, -1])[::-1]])
    return polys


def raster(polys, hs, ortho, cy, res=1200):
    """Same framing as the ortho top camera: width `ortho` m, centred on world (0, cy); head up."""
    im = Image.new('L', (res, res), 0); d = ImageDraw.Draw(im)
    s = res / ortho
    for p in polys:
        x = p[:, 1] * hs; y = p[:, 0] * hs
        d.polygon([(res / 2 + xi * s, res / 2 - (yi - cy) * s) for xi, yi in zip(x, y)], fill=255)
    return np.asarray(im) > 127


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('outline'); ap.add_argument('pose'); ap.add_argument('--check'); ap.add_argument('--ortho', type=float); ap.add_argument('--cy', type=float)
    a = ap.parse_args()
    O = json.load(open(a.outline))
    m = raster(bird_polys(O, a.pose), O['halfSpanM'], a.ortho, a.cy)
    r = np.asarray(Image.open(a.check).convert('L')) < 128
    print(json.dumps({'pose': a.pose, 'iou_vs_render': round(float((m & r).sum() / (m | r).sum()), 4),
                      'outline_only_px': int((m & ~r).sum()), 'render_only_px': int((r & ~m).sum())}))


def winding_raster(polys, hs, ortho, cy, res=1200):
    """Nonzero-winding fill (the canvas default), unlike PIL's even-odd: a self-overlapping folded
    wing chain fills its whole union as long as the posed sheet keeps its orientation."""
    s = res / ortho
    xs = (np.arange(res) + .5 - res / 2) / s; ys = cy - (np.arange(res) + .5 - res / 2) / s
    X, Y = np.meshgrid(xs, ys)
    total = np.zeros((res, res), bool)
    for p in polys:
        px = p[:, 1] * hs; py = p[:, 0] * hs
        wn = np.zeros((res, res), np.int16)
        x0, y0 = px, py; x1, y1 = np.roll(px, -1), np.roll(py, -1)
        for a, b, c, d in zip(x0, y0, x1, y1):
            if b == d: continue
            lo, hi = min(b, d), max(b, d)
            rows = np.nonzero((ys >= lo) & (ys < hi))[0]
            if not len(rows): continue
            yr = Y[rows]; xr = X[rows]
            xi = a + (yr - b) * (c - a) / (d - b)
            wn[rows] += np.where(xr < xi, 1 if d > b else -1, 0).astype(np.int16)
        total |= wn != 0
    return total
