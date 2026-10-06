"""Fit the page's cheap per-bird lighting rule to the Cycles reference renders (step e).

    uv run python fit_birds.py RENDERS.json [--sky sky_light.json] [--out bird_light.json]

Model, per channel, with E(n) the baked irradiance table (sky_light.json) and v the view direction (camera to
bird, page axes):
    n  = the bird's up vector, turned to face the camera (the wing surface we see)
    L  = (a * rho + b) * E(n) / pi  +  (c * rho + d) * E(-v) / pi  +  g * sun_glint + fresnel term
    sun_glint = sun normal irradiance * max(0, n . h)^k,  h = halfway between the sun and -v
    + fr * sun_glint * (1 - h . -v)^5  (Schlick's Fresnel rise at grazing: the backlit rim near the sun)
a, c weight the diffuse light on the seen wing and on the side facing the camera; b, d (and g) are the albedo-free
part, the plumage's specular reflection of the sky. Fitted jointly over the three grey albedos (0.03, 0.05, 0.10)
by least squares on luminance, k by grid search; scored by 5-fold cross-validation, in radiance and in 8-bit codes
through the page's tone curve, and on the model's own plumage (starling_look) as rho = its effective albedo.
"""
import argparse
import json
import math

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('renders')
ap.add_argument('--sky', default='sky_light.json')
ap.add_argument('--out', default='bird_light.json')
a = ap.parse_args()
R_all = json.load(open(a.renders))
GLINT = .3                                     # renders brighter than this (luminance) are sun glints off a wing panel;
lum = lambda r: float(np.dot(r['g05'][:3], [.2126, .7152, .0722]))   # the rule leaves them out (see the report)
R = [r for r in R_all if lum(r) <= GLINT]
S = json.load(open(a.sky))
E = np.array(S['irradiance']['rgb']).reshape(S['irradiance']['h'], S['irradiance']['w'], 3)
GH, GW = E.shape[:2]
sun = np.array(S['sun']['dir']); sunE = np.array(S['sun']['normal_irradiance'])
tone_r = np.array(S['tone']['radiance'])
tone = np.stack([np.array(S['tone'][c]) for c in 'RGB'], -1)


def irr(n):
    """Bilinear lookup of E at unit normal n (page axes)."""
    lon = math.atan2(n[0], n[2]); lat = math.asin(max(-1, min(1, n[1])))
    u = (0.5 - lon / (2 * math.pi)) * GW - .5; v = (0.5 - lat / math.pi) * GH - .5
    u0 = math.floor(u); v0 = min(max(math.floor(v), 0), GH - 2); fu = u - u0; fv = min(max(v - v0, 0), 1)
    g = lambda i, j: E[j, i % GW]
    return ((1 - fu) * (1 - fv) * g(u0, v0) + fu * (1 - fv) * g(u0 + 1, v0) +
            (1 - fu) * fv * g(u0, v0 + 1) + fu * fv * g(u0 + 1, v0 + 1))


def code(L):
    return np.stack([np.interp(np.log(np.maximum(L[..., c], 1e-6)), np.log(tone_r), tone[:, c]) for c in range(3)], -1)


def feats(r, k):
    v = np.array(r['view']); up = np.array(r['up'])
    n = up if up @ -v > 0 else -up
    h = sun - v; h /= np.linalg.norm(h)
    return (irr(n) / math.pi, irr(-v) / math.pi, sunE * max(0.0, float(n @ h)) ** k,
            sunE * max(0.0, float(n @ h)) ** k * (1 - max(0.0, float(h @ -v))) ** 5)


ALB = {'g03': .03, 'g05': .05, 'g10': .10}


def design(rows, k):
    X, Y = [], []
    for r in rows:
        f1, f2, f3, f4 = feats(r, k)
        for key, rho in ALB.items():
            for c in range(3):
                X.append([rho * f1[c], f1[c], rho * f2[c], f2[c], f3[c], f4[c]]); Y.append(r[key][c])
    return np.array(X), np.array(Y)


def predict(p, r, rho, k):
    f1, f2, f3, f4 = feats(r, k)
    return (p[0] * rho + p[1]) * f1 + (p[2] * rho + p[3]) * f2 + p[4] * f3 + p[5] * f4


def fit(rows, k):
    X, Y = design(rows, k)
    p, *_ = np.linalg.lstsq(X, Y, rcond=None)
    return p


def cv(rows, k, folds=5):
    idx = np.arange(len(rows)); errs = []
    for f in range(folds):
        test = [rows[i] for i in idx if i % folds == f]; train = [rows[i] for i in idx if i % folds != f]
        p = fit(train, k)
        for r in test:
            for key, rho in ALB.items():
                errs.append((predict(p, r, rho, k), np.array(r[key][:3])))
    pr = np.array([e[0] for e in errs]); tr = np.array([e[1] for e in errs])
    return pr, tr


best = None
for k in (1, 2, 4, 8, 16, 32, 64):
    pr, tr = cv(R, k)
    e = float(np.sqrt(((pr - tr) ** 2).mean()))
    print('k %3d  CV rms radiance %.4f' % (k, e))
    if best is None or e < best[0]:
        best = (e, k)
k = best[1]
p = fit(R, k)
pr, tr = cv(R, k)
dcode = code(pr) - code(tr)
const = np.array([[r[key][:3] for key in ALB] for r in R]).reshape(-1, 3)
base = float(np.sqrt(((const - const.mean(0)) ** 2).mean()))
rep = dict(n=len(R), glints_left_out=dict(n=len(R_all) - len(R), share=round(1 - len(R) / len(R_all), 3),
                                          threshold_luminance=GLINT), k=k, params=dict(zip(['a', 'b', 'c', 'd', 'g', 'fr'], [round(float(x), 5) for x in p])),
           cv_rms_radiance=round(best[0], 5), spread_of_renders_rms=round(base, 5),
           cv_rms_code=round(float(np.sqrt((dcode ** 2).mean())), 2),
           cv_p90_abs_code=round(float(np.quantile(np.abs(dcode), .9)), 2),
           cv_median_abs_code=round(float(np.median(np.abs(dcode))), 2),
           mean_render_code=[round(float(x), 1) for x in code(tr).mean(0)])

# the model's own plumage: what single albedo does the rule need, and how well does it then do?
look = np.array([r['look'][:3] for r in R])
best_rho = min(np.linspace(0, .2, 81), key=lambda rho: (((np.array([predict(p, r, rho, k) for r in R]) - look) ** 2).mean()))
lp = np.array([predict(p, r, best_rho, k) for r in R])
rep['look'] = dict(effective_albedo=round(float(best_rho), 4),
                   rms_code=round(float(np.sqrt(((code(lp) - code(look)) ** 2).mean())), 2))
# how much albedo matters: the same configurations at 0.03 and 0.10
lo = np.array([predict(p, r, .03, k) for r in R]); hi = np.array([predict(p, r, .10, k) for r in R])
rep['albedo_sensitivity'] = dict(code_at_003=[round(float(x), 1) for x in code(lo).mean(0)],
                                 code_at_010=[round(float(x), 1) for x in code(hi).mean(0)])
print(json.dumps(rep, indent=1))
json.dump(rep, open(a.out, 'w'), indent=1)
