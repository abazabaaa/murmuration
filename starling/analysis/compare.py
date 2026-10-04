"""Overlay normalised planforms (from silhouette.py *__norm.png) and score them.

usage: compare.py MODEL_NORM REF_NORM [REF_NORM ...] --out overlay.png
Planforms are already scaled to half-span = 1 and aligned on the symmetry axis with the
head up, so IoU measures shape alone.  The vertical offset is optimised (photos and renders
put the span-centre at different points along the body).
"""
import argparse, json
import numpy as np
from PIL import Image


def load(p):
    return np.asarray(Image.open(p).convert('L')) > 127


def best_iou(a, b, max_shift=40):
    best = (0, 0)
    for dy in range(-max_shift, max_shift + 1, 1):
        bb = np.roll(b, dy, axis=0)
        i = (a & bb).sum(); u = (a | bb).sum()
        if i / u > best[0]: best = (i / u, dy)
    return best


ap = argparse.ArgumentParser()
ap.add_argument('model'); ap.add_argument('refs', nargs='+'); ap.add_argument('--out', required=True)
a = ap.parse_args()
m = load(a.model)
res = []
tiles = []
for r in a.refs:
    ref = load(r)
    iou, dy = best_iou(m, ref)
    ref = np.roll(ref, dy, axis=0)
    rgb = np.full(m.shape + (3,), 255, np.uint8)
    rgb[ref & ~m] = (220, 60, 60)        # photo only: red
    rgb[m & ~ref] = (60, 90, 220)        # model only: blue
    rgb[m & ref] = (40, 40, 40)          # both: dark
    tiles.append(rgb)
    res.append(dict(ref=r, iou=round(float(iou), 4), shift=int(dy)))
Image.fromarray(np.concatenate(tiles, axis=1)).save(a.out)
print(json.dumps(res, indent=1))
