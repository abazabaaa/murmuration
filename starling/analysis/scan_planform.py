"""Leading/trailing edge of the pressed PSM 22483 wing (female, right, dorsal) in cm.

Root at the left of the scan, tip at the right, leading edge at the top.  Output frame: x = cm
from the root cut toward the tip, y = cm forward (up in the scan) from the root's leading edge.
Scale 39.8 px/cm, read off the 15 cm bar (checked at 3.1x zoom).
"""
import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

MASK = sys.argv[1]
OUT = sys.argv[2]
PX_PER_CM = 39.8
m = np.asarray(Image.open(MASK)) > 127
m = ndi.binary_fill_holes(m)
lab, n = ndi.label(m)
m = lab == (np.argmax(np.bincount(lab.ravel())[1:]) + 1)
cols = np.flatnonzero(m.any(0))
x0, x1 = cols.min(), cols.max()
xs, le, te = [], [], []
for x in range(x0, x1 + 1):
    rows = np.flatnonzero(m[:, x])
    xs.append(x); le.append(rows.min()); te.append(rows.max())
xs, le, te = map(np.asarray, (xs, le, te))
# the root is ragged (body-feather tufts, cut skin): define the root as the column where the
# leading edge first becomes smooth, i.e. drop the leftmost 3% of the length
L = x1 - x0
keep = xs >= x0 + .03 * L
xs, le, te = xs[keep], le[keep], te[keep]
xr = xs[0]
y_ref = le[: max(5, len(le) // 50)].mean()
# smooth with a running median then mean (feather scallops on the trailing edge are real but
# below the resolution the canvas or the model needs)
def smooth(a, k):
    a = ndi.median_filter(a.astype(float), size=k)
    return ndi.uniform_filter1d(a, size=k)
le_s, te_s = smooth(le, 41), smooth(te, 61)
x_cm = (xs - xr) / PX_PER_CM
le_cm = -(le_s - y_ref) / PX_PER_CM
te_cm = -(te_s - y_ref) / PX_PER_CM
span = x_cm[-1]
# resample at 81 stations
st = np.linspace(0, span, 81)
res = dict(source='PSM 22483 female right wing, dorsal (Slater Museum)', px_per_cm=PX_PER_CM,
           root_to_tip_cm=float(span), x_cm=st.tolist(),
           le_cm=np.interp(st, x_cm, le_cm).tolist(), te_cm=np.interp(st, x_cm, te_cm).tolist())
c = np.array(res['le_cm']) - np.array(res['te_cm'])
apex = st[np.argmax(res['le_cm'])]
res.update(max_chord_cm=float(c.max()), le_apex_cm=float(apex), le_apex_frac=float(apex / span),
           area_cm2=float(np.trapezoid(c, st)))
json.dump(res, open(OUT, 'w'), indent=1)
print(json.dumps({k: round(v, 3) if isinstance(v, float) else v for k, v in res.items() if not isinstance(v, list)}, indent=1))
for f in (0, .1, .2, .3, .35, .4, .5, .6, .7, .8, .9, .95, 1):
    i = int(round(f * 80)); print(f'{f:4.2f}  x {st[i]:5.1f}  le {res["le_cm"][i]:6.2f}  te {res["te_cm"][i]:6.2f}  chord {c[i]:5.2f}')
