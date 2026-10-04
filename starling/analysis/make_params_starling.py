"""Compose params_starling.json for bird_build.py from the measurements.

Sources (full citations in refs/morphometrics.json, refs/pose_spec.md):
  wing planform  RMNH.AVES.259388.b (adult female, Naturalis, CC0), mean of the ventral and dorsal
                 scans, scale from the in-frame ruler (69.1 px/cm, verified 4.5x); in-flight root
                 rebuilt by flight_planform.py (inner leading edge straight to the wrist, trailing
                 edge root 0.39 L behind the leading edge root; photo median 0.42 L)
  span           0.382 m (Ben-Gida et al. 2013 wind-tunnel bird; literature 37.8-38.4 cm)
  length L       0.20 m bill tip to tail tip in flight (flock literature 0.20 m; museum 21 cm with the
                 neck stretched; best photo fits 19.8 and 18.8 cm): span/L 1.91
  wing root      leading edge leaves the body 0.20 L behind the bill (median of 7 flight photos)
  body           max width 4.0 cm (Ben-Gida 2013); bill 0.15 L (culmen 30.2 mm), bill width 6.6 mm
                 (AVONET); cranium 19-20 mm + plumage; vent narrowing from the photos
  tail           65 mm (AVONET 65.8, HANZAB 59-68); closed width ~3 cm (rectrix width 1.45 cm,
                 Feather Atlas); square tip; spread to ~50 deg half-angle in the photos
  joints         humerus 28, ulna 34, carpometacarpus 21 mm (Balyan et al. 2024, one male); wrist
                 5.4 cm from the scan root (alula base, specimen agent)
"""
import json, pathlib
import numpy as np

HERE = pathlib.Path(__file__).parent
SCAN = json.load(open(HERE / 'scan_planform_259388b_flight.json'))
L, SPAN = 0.20, 0.382
x, le, te = (np.asarray(SCAN[k], float) for k in ('x_cm', 'le_cm', 'te_cm'))

# scan cm -> bird m.  Shoulder joint sits at scan (-0.2, -0.6) cm and at bird (SH_X, 0); the scan
# is scaled so that the tip lands on the measured half-span.
JX, JY = -0.2, -0.6
SH_X = 0.013                                    # shoulder joint 1.3 cm off the midline (body 4 cm wide)
M_PER_CM = (SPAN / 2 - SH_X) / (x[-1] - JX)
def to_bird(xs, ys):
    return SH_X + (np.asarray(xs) - JX) * M_PER_CM, (np.asarray(ys) - JY) * M_PER_CM

xb, leb = to_bird(x, le); _, teb = to_bird(x, te)
hs = float(xb[-1])
root_le_y = float(leb[0])
y_bill = root_le_y + 0.20 * L
J = dict(elbow=(2.4, 0.2), wrist=(5.4, 1.9), tip=(x[-1], (le[-1] + te[-1]) / 2))
joints = {k: to_bird(*v) for k, v in J.items()}

# body profile against d = distance from the bill tip in L (0 .. tail base)
tail_len = 0.065
y_tail_tip = y_bill - L
y_tailbase = y_tail_tip + tail_len               # where the rectrices leave the coverts
d_base = (y_bill - y_tailbase) / L
d = np.array([0, .03, .07, .11, .145, .18, .22, .30, .40, .50, .58, d_base])
hw_L = np.array([.004, .009, .015, .021, .032, .060, .072, .090, .100, .097, .078, .055])   # forehead widens fast behind the bill base (photos: 0.08-0.10 L at the wing junction);
                                                       # rump tapers into the tail (narrowest wing-tail width 0.09-0.18 L in the photos)
hh_over_hw = np.array([.9, .9, .95, 1., 1., 1., 1., .95, .9, .85, .7, .55])
z_c = np.array([.002, .002, .002, .0025, .003, .003, .003, .002, 0, -.001, -.001, .001])
params = {
    '_sources': __doc__, 'prefix': 'Starling', 'L': L,
    'wing': {'half_span': hs, 'root_x': float(xb[0]), 'thick_root': 0.11, 'thick_tip': 0.035, 'camber': 0.05, 'dihedral': 0.0,
             's': (xb / hs).tolist(), 'le': (leb / hs).tolist(), 'te': (teb / hs).tolist()},
    'body': {'bill_to_tailbase': float(d_base * L), 'y_bill': y_bill, 'belly_flat': .92,
             't': (d / d_base).tolist(), 'halfwidth': (hw_L * L).tolist(), 'halfheight': (hw_L * L * hh_over_hw).tolist(),
             'zcentre': z_c.tolist(),
             # the body taper is the bill (culmen 0.15 L); the cone only sharpens its tip and gives the outline its nose.
             # bill_droop -182 turns the cone's narrow end forward, 2 deg down; centre 6 mm behind the tip on the head axis
             'bill_r': 0.0022, 'bill_r2': 0.0003, 'bill_len': 0.012, 'bill_droop': -182, 'bill_dy': -0.006, 'bill_dz': 0.0},
    'tail': {'y_base': y_tailbase + 0.008, 'length': tail_len + 0.008, 'base_halfwidth': 0.0135, 'tip_halfwidth': 0.0155,
             'fan_half_angle': 50, 'tip_round': -0.015, 'z': 0.001},
    'rig': {'body_tail_y': y_tailbase, 'body_head_y': y_bill - .02, 'shoulder': [SH_X, 0.0, 0.003],
            'elbow': [float(joints['elbow'][0]), float(joints['elbow'][1]), 0.002],
            'wrist': [float(joints['wrist'][0]), float(joints['wrist'][1]), 0.001],
            'tip': [float(joints['tip'][0]), float(joints['tip'][1]), 0.0],
            'blend': 0.015, 'root_center': SH_X + 0.015, 'root_blend': 0.011,
            'fan_fade': [round(0.02 * hs / 0.5143, 4), round(0.07 * hs / 0.5143, 4)]},   # falcon values scaled by half-span
}
out = HERE.parent / 'blender' / 'params_starling.json'
json.dump(params, open(out, 'w'), indent=1)
print(f'half-span {hs:.4f} m  span {2 * hs:.3f} m  span/L {2 * hs / L:.2f}  scale {M_PER_CM * 100:.4f} (bird/scan)  bill y {y_bill:.4f}  tail tip y {y_tail_tip:.4f}  tail base y {y_tailbase:.4f}')
print(f'LE root y {root_le_y:.4f} (d {0.20:.2f} L)  TE root y {teb[0]:.4f} (d {(y_bill - teb[0]) / L:.3f} L)  root x {xb[0]:.4f}')
print('joints', {k: (round(float(a), 4), round(float(b), 4)) for k, (a, b) in joints.items()})
