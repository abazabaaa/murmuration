"""Find the yaw, pitch and roll that reproject the HDRI onto murmuration-sky.jpg.

    uv run python register.py HDR JPEG [--tonemapped PH_JPG] [--out registration.json]

Scores normalised cross-correlation of log luminance at 960x400 (the JPEG area-averaged by 4).
With --tonemapped, also reprojects Poly Haven's own tone-mapped JPG at the same pose and reports
how closely it matches murmuration-sky.jpg (step b0: was the page's JPEG made from it?).
"""
import argparse
import json

import cv2
import numpy as np
from scipy.optimize import minimize

from common import JH, JW, luminance, read_hdr, read_rgb8, reproject

ap = argparse.ArgumentParser()
ap.add_argument('hdr')
ap.add_argument('jpeg')
ap.add_argument('--tonemapped')
ap.add_argument('--out', default='registration.json')
a = ap.parse_args()

eq = read_hdr(a.hdr)
jp = read_rgb8(a.jpeg).astype(np.float32)
assert jp.shape[:2] == (JH, JW), jp.shape
w, h = 960, 400
target = np.log(luminance(cv2.resize(jp, (w, h), interpolation=cv2.INTER_AREA)) + 1)
eqs = cv2.resize(eq, (2048, 1024), interpolation=cv2.INTER_AREA)


def ncc(a_, b_):
    a_ = a_ - a_.mean(); b_ = b_ - b_.mean()
    return float((a_ * b_).sum() / np.sqrt((a_ * a_).sum() * (b_ * b_).sum()))


def score(p, src, ww=w, hh=h, tgt=None):
    im = reproject(src, ww, hh, *p)
    return ncc(np.log(luminance(im) + 1e-3), target if tgt is None else tgt)


best = None
small = cv2.resize(target, (240, 100), interpolation=cv2.INTER_AREA)
for mirror in (False, True):
    src = eqs[:, ::-1].copy() if mirror else eqs
    for yaw in np.arange(0, 360, 2.0):
        s = score((yaw, 14.29, 0), src, 240, 100, small)
        if best is None or s > best[0]:
            best = (s, mirror, yaw)
print('coarse best: ncc %.3f mirror %s yaw %.0f' % best)
_, mirror, yaw0 = best
if mirror:
    eq = eq[:, ::-1].copy(); eqs = eqs[:, ::-1].copy()
res = minimize(lambda p: -score(p, eqs), [yaw0, 14.29, 0.0], method='Nelder-Mead',
               options=dict(xatol=.01, fatol=1e-5, initial_simplex=[[yaw0, 14.29, 0], [yaw0 + 1, 14.29, 0],
                                                                     [yaw0, 15.29, 0], [yaw0, 14.29, 1]]))
yaw, pitch, roll = res.x
out = dict(yaw=round(yaw, 3), pitch=round(pitch, 3), roll=round(roll, 3), mirror=bool(mirror),
           ncc_960x400=round(-res.fun, 4), hdr=a.hdr.split('/')[-1])
print('fine: yaw %.3f pitch %.3f roll %.3f ncc %.4f' % (yaw, pitch, roll, -res.fun))

if a.tonemapped:
    tm = read_rgb8(a.tonemapped)
    if mirror:
        tm = tm[:, ::-1].copy()
    full = reproject(tm.astype(np.float32), JW, JH, yaw, pitch, roll)
    d = full - jp
    sky = luminance(jp) < 250
    out['tonemapped_vs_page'] = dict(
        median_abs_code=float(np.median(np.abs(d[sky]))),
        rms_code=float(np.sqrt((d[sky] ** 2).mean())),
        mean_code_rgb=[float(x) for x in d[sky].mean(0)],
        ncc_log=ncc(np.log(luminance(full) + 1), np.log(luminance(jp) + 1)))
    print('Poly Haven tonemapped JPG vs page JPEG:', out['tonemapped_vs_page'])
json.dump(out, open(a.out, 'w'), indent=1)
