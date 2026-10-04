"""Sheet: full outline (grey, nonzero fill) with the low-point polygon (red, numbered) per pose.
usage: plot_lowpoly.py OUTLINE.json LOW.json OUT.png"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from outline_raster import bird_polys
from lowpoly import wind, poly_from

O, Lw, out = json.load(open(sys.argv[1])), json.load(open(sys.argv[2])), sys.argv[3]
poses = list(Lw['pose']); M = Lw['M']; T = 520
try: F = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 18)
except OSError: F = ImageFont.load_default()
sheet = Image.new('RGB', (T * len(poses), T + 40), 'white'); d = ImageDraw.Draw(sheet)
for k, p in enumerate(poses):
    full = bird_polys(O, p); s = T / 2.5                      # +-1.25 half-spans across the tile
    ys, xs = np.mgrid[0:T, 0:T]; A = 0.25 - (ys + .5 - T / 2) / s; W = (xs + .5 - T / 2) / s
    m = wind(full, W, A)
    tile = np.full((T, T, 3), 255, np.uint8); tile[m] = (190, 190, 190)
    im = Image.fromarray(tile); di = ImageDraw.Draw(im)
    v = np.asarray(Lw['pose'][p]).reshape(-1, 2); x = np.r_[v[0, 0], v[1:, :].ravel()]
    x = np.r_[v[0, 0], v[1:].ravel()]
    P = poly_from(x, M)
    pts = [(T / 2 + w * s, T / 2 - (a - .25) * s) for a, w in P]
    di.line(pts + [pts[0]], fill=(220, 40, 40), width=2)
    for i, q in enumerate(pts[:M + 1]):
        di.ellipse([q[0] - 3, q[1] - 3, q[0] + 3, q[1] + 3], fill=(220, 40, 40)); di.text((q[0] + 5, q[1] - 9), str(i), fill=(0, 0, 160), font=F)
    sheet.paste(im, (k * T, 40))
    d.text((k * T + 8, 8), f"{p}  IoU {Lw['iouVsFull'][p]:.3f}  N={Lw['N']}", fill='black', font=F)
sheet.save(out); print(out)
