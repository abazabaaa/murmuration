"""Convert a closed wing contour in (s, n) cm (s root->tip, n + toward the leading edge; dorsal
right wing, as written by the specimen agent's planform_stats.py) into the station format the
falcon pipeline uses: x_cm from the root, le_cm / te_cm forward of the root leading edge.

usage: contour_to_planform.py CONTOUR.json OUT.json [--n 81] [--drop 0.03]
"""
import argparse, json
import numpy as np
from scipy import ndimage as ndi

ap = argparse.ArgumentParser()
ap.add_argument('contour'); ap.add_argument('out'); ap.add_argument('--n', type=int, default=81); ap.add_argument('--drop', type=float, default=.03)
a = ap.parse_args()
P = np.asarray(json.load(open(a.contour))['points'], float)
s, n = P[:, 0], P[:, 1]
s0, s1 = s.min(), s.max(); L = s1 - s0
# dense column scan of the polygon: for each s, the max (leading) and min (trailing) crossing
grid = np.linspace(s0, s1, 1200)
le, te = np.full(grid.shape, np.nan), np.full(grid.shape, np.nan)
A_, B_ = P, np.roll(P, -1, 0)
for k, x in enumerate(grid):
    c = (A_[:, 0] - x) * (B_[:, 0] - x) <= 0
    c &= A_[:, 0] != B_[:, 0]
    if not c.any(): continue
    t = (x - A_[c, 0]) / (B_[c, 0] - A_[c, 0]); y = A_[c, 1] + t * (B_[c, 1] - A_[c, 1])
    le[k], te[k] = y.max(), y.min()
ok = ~np.isnan(le) & (grid >= s0 + a.drop * L)
g, le, te = grid[ok], le[ok], te[ok]
def smooth(v, k): return ndi.uniform_filter1d(ndi.median_filter(v, size=k), size=k)
le_s, te_s = smooth(le, 21), smooth(te, 31)
xr = g[0]; y_ref = le_s[:10].mean()
xs = np.linspace(0, g[-1] - xr, a.n)
res = dict(source=a.contour, x_cm=list(np.round(xs, 3)), le_cm=list(np.round(np.interp(xs + xr, g, le_s) - y_ref, 3)),
           te_cm=list(np.round(np.interp(xs + xr, g, te_s) - y_ref, 3)))
x, l_, t_ = map(np.asarray, (res['x_cm'], res['le_cm'], res['te_cm']))
res['root_to_tip_cm'] = round(float(x[-1]), 3); res['area_cm2'] = round(float(np.trapezoid(l_ - t_, x)), 2)
res['max_chord_cm'] = round(float((l_ - t_).max()), 3); res['max_chord_at'] = round(float(x[np.argmax(l_ - t_)] / x[-1]), 3)
res['le_apex_at'] = round(float(x[np.argmax(l_)] / x[-1]), 3)
json.dump(res, open(a.out, 'w'), indent=1)
print({k: res[k] for k in ('root_to_tip_cm', 'area_cm2', 'max_chord_cm', 'max_chord_at', 'le_apex_at')})
