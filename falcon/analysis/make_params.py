"""Compose params_falcon.json for falcon_build.py from the measurements.

Sources (see refs/*/notes.md, poses.md and analysis/fits3):
  wing planform  PSM 22483 female right wing, Slater Museum scan, 39.8 px/cm (bar checked at 3.1x),
                 root trailing-edge lobe replaced as in fit_pose.flight_te (tucks under in flight)
  length L       0.46 m: female 45-58 cm (FEIS); with the scan's 46.9 cm root-to-tip this gives a
                 full-spread span of 1.03 m (BOW female 99.7 +/- 4.8 cm) and b/L 2.24 (1.9-2.4 sources)
  body/head/tail half-widths along the axis, in L, from photos 03/04/05/06 (closed tails)
  wing root      leading edge at 0.19 L from the bill, trailing edge 0.56-0.61 L (specimen agent + photos)
  tail           0.34 L long (White 1968), closed width ~6 cm (Feather Atlas R1 vane widths)
  joints         humerus 9.1, ulna 10.6, carpometacarpus 6.4 cm (Royal BC Museum female means)
"""
import json, pathlib
import numpy as np

HERE = pathlib.Path(__file__).parent
SCAN = json.load(open(HERE / 'scan_planform_22483.json'))
L = 0.46

x = np.asarray(SCAN['x_cm']); le = np.asarray(SCAN['le_cm']); te = np.asarray(SCAN['te_cm'])
# root trailing edge: clip only the tertial/scapular bulge (scan -18.4 cm at 4.7 cm); a -17 cm root
# chord puts the trailing-edge root at 0.19 + 0.37 = 0.56 L, inside the photos' 0.56-0.61 L
inner = x < 12
te[inner] = np.maximum(te[inner], np.interp(x[inner], [0, 12], [-17.0, np.interp(12, x, te)]))
# root leading edge: the scan's first ~12 cm carry scapular/cut-skin lumps; replace them with a
# cubic fitted to 0-24 cm, blended back to the scan by 16 cm
sel = x < 24
c3 = np.polyfit(x[sel], le[sel], 3)
w = np.clip((x - 10) / 6, 0, 1)
le = np.where(x < 16, (1 - w) * np.polyval(c3, x) + w * le, le)

# scan cm -> bird m.  Shoulder joint sits at scan (-1, -3) cm and at bird (0.035, 0).
JX, JY = -1.0, -3.0
SH_X = 0.035
def to_bird(xs, ys):
    return SH_X + (np.asarray(xs) - JX) / 100, (np.asarray(ys) - JY) / 100

xb, leb = to_bird(x, le); _, teb = to_bird(x, te)
hs = float(xb[-1])
root_le_y = float(leb[0])                      # leading-edge root, bird y
y_bill = root_le_y + 0.19 * L                  # LE root at 0.19 L aft of the bill tip

joints = {k: to_bird(*v) for k, v in dict(elbow=(7.5, -5.5), wrist=(17.0, -1.5), tip=(x[-1], (le[-1] + te[-1]) / 2)).items()}

# body: half-width / half-height profile (m) against t = 0 bill tip .. 1 tail base (0.66 L)
V = np.array([0, -.033, -.06, -.10, -.145, -.20, -.30, -.40, -.50, -.60, -.66])
hw_L = np.array([.013, .039, .057, .070, .085, .108, .120, .112, .100, .088, .080])   # photos 03-06, chest/belly interpolated under the wing
hh_over_hw = np.array([1, .95, .92, .88, .85, .85, .87, .85, .75, .55, .40])
z_c = np.array([.004, .006, .008, .009, .008, .005, 0, -.003, -.004, -.001, .002])
tail_len = 0.34 * L
params = {
    '_sources': __doc__,
    'L': L,
    'wing': {'half_span': hs, 'root_x': float(xb[0]), 'thick_root': 0.11, 'thick_tip': 0.035, 'camber': 0.045, 'dihedral': 0.0,
             's': (xb / hs).tolist(), 'le': (leb / hs).tolist(), 'te': (teb / hs).tolist()},
    'body': {'bill_to_tailbase': 0.66 * L, 'y_bill': y_bill, 'belly_flat': .92,
             't': (-V / .66).tolist(), 'halfwidth': (hw_L * L).tolist(), 'halfheight': (hw_L * L * hh_over_hw).tolist(),
             'zcentre': z_c.tolist(), 'bill_r': 0.0072, 'bill_len': 0.021, 'bill_droop': 48},
    'tail': {'y_base': y_bill - 0.66 * L + 0.012, 'length': tail_len + 0.012, 'base_halfwidth': 0.036, 'tip_halfwidth': 0.028,
             'fan_half_angle': 38, 'tip_round': 0.03, 'z': 0.003},
    'rig': {'body_tail_y': y_bill - 0.66 * L, 'body_head_y': y_bill - .05, 'shoulder': [SH_X, 0.0, 0.006],
            'elbow': [float(joints['elbow'][0]), float(joints['elbow'][1]), 0.004],
            'wrist': [float(joints['wrist'][0]), float(joints['wrist'][1]), 0.002],
            'tip': [float(joints['tip'][0]), float(joints['tip'][1]), 0.0],
            'blend': 0.04, 'root_center': SH_X + 0.04, 'root_blend': 0.03},
}
out = HERE.parent / 'blender' / 'params_falcon.json'
json.dump(params, open(out, 'w'), indent=1)
print(f'half-span {hs:.3f} m  span {2 * hs:.3f} m  span/L {2 * hs / L:.2f}  bill y {y_bill:.3f}  tail tip y {y_bill - L:.3f}')
print('joints', {k: (round(float(a), 3), round(float(b), 3)) for k, (a, b) in joints.items()})
print('wing root chord', round(float(leb[0] - teb[0]), 3), 'max chord', round(float((leb - teb).max()), 3))
