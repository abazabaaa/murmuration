"""Recover the tone curve from linear HDR radiance to the page's 8-bit sky (step b).

    uv run python fit_curve.py HDR JPEG [--tonemapped PH_JPG] [--reg registration.json] [--out tone_curve.json]

Both images are brought to 1920x800 (the JPEG area-averaged by 2). Only smooth pixels are used
(the 60 % lowest local gradient) and none with any channel at 250 or above. Per channel, an
isotonic (monotone) regression maps log radiance to code. Reported: in-sample RMS, and held-out
RMS when fitted on the left half and tested on the right (the sun side). Also tried: sRGB with a
fitted exposure, and (with --tonemapped) the page's JPEG as a per-channel curve of Poly Haven's
tone-mapped JPG.
"""
import argparse
import json

import cv2
import numpy as np
from scipy.optimize import minimize_scalar
from sklearn.isotonic import IsotonicRegression

from common import JH, JW, luminance, read_hdr, read_rgb8, reproject

ap = argparse.ArgumentParser()
ap.add_argument('hdr')
ap.add_argument('jpeg')
ap.add_argument('--tonemapped')
ap.add_argument('--reg', default='registration.json')
ap.add_argument('--out', default='tone_curve.json')
a = ap.parse_args()
reg = json.load(open(a.reg))
pose = (reg['yaw'], reg['pitch'], reg['roll'])

w, h = 1920, 800
eq = read_hdr(a.hdr)
if reg['mirror']:
    eq = eq[:, ::-1].copy()
lin = reproject(eq, w, h, *pose)
jp = cv2.resize(read_rgb8(a.jpeg).astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
full = read_rgb8(a.jpeg)

g = cv2.GaussianBlur(np.log(luminance(lin) + 1e-4), (0, 0), 1.5)
grad = np.hypot(cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1))
sat = cv2.resize((full.max(-1) >= 250).astype(np.float32), (w, h), interpolation=cv2.INTER_AREA) > 0
ok = (grad <= np.quantile(grad, .6)) & ~sat & (lin.min(-1) > 0)
cols = np.broadcast_to(np.arange(w), (h, w))
left = ok & (cols < w // 2); right = ok & (cols >= w // 2)


def iso(x, y):
    return IsotonicRegression(out_of_bounds='clip').fit(x, y)


rep = dict(pixels=int(ok.sum()), pose=pose)
curves = {}
for c, name in enumerate('RGB'):
    x = np.log(lin[..., c]); y = jp[..., c]
    m = iso(x[ok], y[ok])
    ins = float(np.sqrt(((m.predict(x[ok]) - y[ok]) ** 2).mean()))
    mh = iso(x[left], y[left]); r = mh.predict(x[right]) - y[right]
    held = float(np.sqrt((r ** 2).mean()))
    grid = np.linspace(np.log(1e-3), np.log(lin[..., c][ok].max()), 256)
    curves[name] = dict(log_radiance=grid.round(5).tolist(), code=m.predict(grid).round(3).tolist())
    rep[name] = dict(in_sample_rms=round(ins, 2), held_out_rms=round(held, 2), held_out_bias=round(float(r.mean()), 2),
                     radiance_range=[float(lin[..., c][ok].min()), float(lin[..., c][ok].max())])

    def srgb_err(lk):
        v = np.clip(lin[..., c][ok] * np.exp(lk), 0, 1)
        s = np.where(v <= .0031308, 12.92 * v, 1.055 * v ** (1 / 2.4) - .055) * 255
        return float(np.sqrt(((s - y[ok]) ** 2).mean()))
    rep[name]['srgb_exposure_rms'] = round(minimize_scalar(srgb_err, bounds=(-8, 8), method='bounded').fun, 2)

G = lin[..., 1][ok]
rep['dark_end'] = dict(share_below_0p05=float((G < .05).mean()), darkest=float(G.min()))
print(json.dumps(rep, indent=1))

if a.tonemapped:
    tm = read_rgb8(a.tonemapped)
    if reg['mirror']:
        tm = tm[:, ::-1].copy()
    tmv = reproject(tm.astype(np.float32), w, h, *pose)
    r2 = {}
    for c, name in enumerate('RGB'):
        m = iso(tmv[..., c][ok], jp[..., c][ok])
        r2[name] = round(float(np.sqrt(((m.predict(tmv[..., c][ok]) - jp[..., c][ok]) ** 2).mean())), 2)
    rep['page_as_curve_of_polyhaven_tonemapped_rms'] = r2
    print('page JPEG as a per-channel curve of the Poly Haven tone-mapped JPG, RMS codes:', r2)

json.dump(dict(report=rep, curves=curves), open(a.out, 'w'))
