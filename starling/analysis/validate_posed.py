"""Pose-matched validation: pose the 3D model with each photo's fitted 2D wing angles, per side.

Writes poses_validate.json for bird_sheet.py.  Mapping from fit_pose.py (CCW + = tip forward,
hand chained on the arm, k = span foreshortening about the shoulder) to set_pose (sweep + = aft):
    humerus.sweep = -th_s,  hand.sweep = -th_w,  humerus.elev = acos(k)
Fit side +1 (+U, image right in the normalised frame) drives the model's right wing, which is also
image right in the top render.  Each photo gets the tail spreads in TAIL_FANS; the best is reported.

usage: validate_posed.py FITS_DIR OUT_POSES.json
"""
import json, math, sys, glob, pathlib
TAIL_FANS = (0.0, 0.33, 0.67, 1.0)
fits, out = sys.argv[1], sys.argv[2]
poses = {}
for f in sorted(glob.glob(f'{fits}/*_fit.json')):
    r = json.load(open(f)); tag = pathlib.Path(f).name.split('_')[0]
    sides = {}
    for sfx, key in (('R', 'wing+1'), ('L', 'wing-1')):
        w = r[key]
        sides[sfx] = {'humerus': {'sweep': -w['th_s'], 'elev': math.degrees(math.acos(min(1, w['k'])))}, 'hand': {'sweep': -w['th_w']}}
    for tf in TAIL_FANS:
        poses[f'{tag}_tf{int(tf * 100):03d}'] = {'bones': {}, 'sides': sides, 'tail_fan': tf,
                                                'target': f'{tag}: fitted per-side wing angles (fit IoU {r["iou_mean"]:.3f}), tail_fan {tf}'}
json.dump(poses, open(out, 'w'), indent=1)
print(len(poses), 'poses ->', out)
