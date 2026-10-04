"""Turn the pressed-specimen planform into the in-flight planform used by both the photo fits
and make_params_starling.py.

The pressed RMNH 259388.b wing narrows to a point at its root (chord 1.4 cm at x = 0): the
preparation keeps only the humeral stub.  In flight the inner wing (propatagium in front,
tertials behind) runs straight into the body: the photos put the leading edge root at ~0.20 L
and the trailing edge root at 0.55-0.70 L (median 0.62) behind the bill.  The defaults give a root
chord of 7.6 scan-cm: 7.8 cm (0.39 L) on the model, trailing edge root at 0.59 L.
  leading edge  x < 5.4 cm (root to wrist): straight from ROOT_LE to the scan's edge at the wrist;
                the pressed propatagium/coverts make a bump there that every photo fit showed as
                model-only area (flight photos: the inner leading edge runs straight to the wrist)
  trailing edge x < 4.3 cm: straight from ROOT_TE at x = 0 to the scan's own edge at 4.3 cm
usage: flight_planform.py SCAN.json OUT.json [--root-te -6.4] [--root-le 1.2]
"""
import argparse, json
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('scan'); ap.add_argument('out'); ap.add_argument('--root-te', type=float, default=-6.4); ap.add_argument('--root-le', type=float, default=1.2)
a = ap.parse_args()
S = json.load(open(a.scan))
x, le, te = (np.asarray(S[k], float) for k in ('x_cm', 'le_cm', 'te_cm'))
xw = 5.4; le_w = np.interp(xw, x, le)
le2 = np.where(x < xw, a.root_le + (le_w - a.root_le) * x / xw, le)
xe = 4.3; te_e = np.interp(xe, x, te)
te2 = np.where(x < xe, a.root_te + (te_e - a.root_te) * x / xe, te)
res = dict(source=S['source'] + ' | in-flight root rebuilt by flight_planform.py', root_te_cm=a.root_te, root_le_cm=a.root_le,
           x_cm=list(np.round(x, 3)), le_cm=list(np.round(le2, 3)), te_cm=list(np.round(te2, 3)))
json.dump(res, open(a.out, 'w'), indent=1)
ch = le2 - te2
print('root chord', round(ch[0], 2), 'le root', round(le2[0], 2), 'area', round(np.trapezoid(ch, x), 1), 'max chord', round(ch.max(), 2))
