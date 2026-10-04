"""Fit the falcon wing rig to a flight photo's silhouette, one wing at a time.

The model wing is the scanned planform (scan_planform_22483.json, cm) skinned to a 2D copy of
the Blender rig: shoulder -> elbow -> wrist -> tip, smoothstep weights in the rest-pose span
coordinate exactly as falcon_build.py assigns them.  Photo frame comes from silhouette.py:
symmetry axis, head up, lengths in units of the bird's total length L (bill tip = 0, tail tip = -1).

Free parameters, per photo: L_cm (bird length in cm, sets scale), shoulder position (U_s, V_s);
per wing: shoulder/elbow/wrist rotations (deg, + = toward the head) and a span foreshortening k.

usage: fit_pose.py PHOTO [--bluesky] --out DIR [--name NAME]
"""
import argparse, json, pathlib, sys
import numpy as np
from PIL import Image
from scipy.optimize import differential_evolution
from skimage.draw import polygon as fill_poly

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import silhouette as S

HERE = pathlib.Path(__file__).parent
SCAN = json.load(open(HERE / 'scan_planform_22483.json'))
# joints in scan cm (x from root cut toward tip, y forward from the root leading edge)
JOINTS = dict(shoulder=(-1.0, -3.0), elbow=(7.5, -5.5), wrist=(17.0, -1.5))
BLEND, ROOT_BLEND = 4.0, 3.0                     # cm, as in the Blender rig


def flight_te(x, te):
    """The pressed scan's tertial/scapular lobe (inner 10 cm of trailing edge) tucks under the
    body in flight; every photo fit showed it as model-only area.  Replace it with a straight
    run from 13.5 cm behind the root leading edge to the scan's own trailing edge at 10 cm."""
    te = te.copy()
    t10 = np.interp(10, x, te)
    inner = x < 10
    te[inner] = np.maximum(te[inner], -13.5 + (t10 + 13.5) * x[inner] / 10)
    return te


def outline_cm():
    x, le, te = map(np.asarray, (SCAN['x_cm'], SCAN['le_cm'], SCAN['te_cm']))
    te = flight_te(x, te)
    return np.r_[x, x[::-1]], np.r_[le, te[::-1]]


def smoothstep(x, a, w):
    t = np.clip((x - a + w) / (2 * w), 0, 1); return t * t * (3 - 2 * t)


def weights(x):
    xs, xe, xw = JOINTS['shoulder'][0], JOINTS['elbow'][0], JOINTS['wrist'][0]
    r_s, r_e, r_w = smoothstep(x, xs + ROOT_BLEND + 1, ROOT_BLEND), smoothstep(x, xe, BLEND), smoothstep(x, xw, BLEND)
    return np.stack([1 - r_s, r_s * (1 - r_e), r_e * (1 - r_w), r_w])      # body, humerus, forearm, hand


def rot(a):
    c, s = np.cos(a), np.sin(a); return np.array([[c, -s], [s, c]])


def pose_wing(th_s, th_e, th_w, k):
    """Posed outline in scan cm (rest frame), angles in degrees, CCW (+) swings the tip forward."""
    x, y = outline_cm()
    P = np.stack([x, y], 1)
    W = weights(x)
    S_, E, Wr = (np.array(JOINTS[j]) for j in ('shoulder', 'elbow', 'wrist'))
    Rs, Re, Rw = rot(np.radians(th_s)), rot(np.radians(th_e)), rot(np.radians(th_w))
    # chain: each bone's transform maps rest points to posed points
    def T_h(p): return (p - S_) @ Rs.T + S_
    E1 = T_h(E[None])[0]; Rse = Rs @ Re
    def T_f(p): return (p - E) @ Rse.T + E1
    W1 = T_f(Wr[None])[0]; Rsew = Rse @ Rw
    def T_w(p): return (p - Wr) @ Rsew.T + W1
    out = W[0, :, None] * P + W[1, :, None] * T_h(P) + W[2, :, None] * T_f(P) + W[3, :, None] * T_w(P)
    out[:, 0] = S_[0] + (out[:, 0] - S_[0]) * k            # foreshortening (dihedral / bank) about the shoulder
    return out


def photo_frame(path, bluesky):
    img = Image.open(path)
    m = S.segment(img, skydist=True)
    iou, th, c = S.symmetry_axis(m)
    res, (u, v), _ = S.measure_planform(m, th, c)
    L = res['nose'] - res['tail_tip']
    U, V = u / L, (v - res['nose']) / L
    return dict(U=U, V=V, sym_iou=iou, res=res, mask=m)


R = 500                                           # raster px per L
LMIN, LMAX = 36, 60
CUT_U = .12                                       # compare wings outboard of |U| = 0.12 L (body half-width ~0.115 L)


def raster(U, V, shape):
    g = np.zeros(shape, bool)
    i = np.clip(((-V + .05) * R).astype(int), 0, shape[0] - 1)
    j = np.clip((U * R).astype(int), 0, shape[1] - 1)
    g[i, j] = True
    return g


def fit(path, bluesky, out, name):
    global R
    F = photo_frame(path, bluesky)
    from scipy.optimize import minimize
    R = 160
    p0 = _fit(F, None)
    R = 450
    return _fit(F, p0, out, name, path)


def _fit(F, p0, out=None, name=None, path=None):
    shape = (int(1.15 * R), int(1.3 * R))
    sides = {}
    for side in (1, -1):
        sel = side * F['U'] > 0
        g = raster(side * F['U'][sel], F['V'][sel], shape)
        from scipy import ndimage as ndi
        sides[side] = ndi.binary_closing(g, iterations=2)
    xo, yo = outline_cm()

    def model_mask(L_cm, Us, Vs, th_s, th_e, th_w, k):
        P = pose_wing(th_s, th_e, th_w, k) / L_cm
        # place: scan x -> +U from the shoulder, scan y -> +V (forward); shoulder joint at (Us, Vs)
        Sx, Sy = np.array(JOINTS['shoulder']) / L_cm
        Uw, Vw = P[:, 0] - Sx + Us, P[:, 1] - Sy + Vs
        rr = (-Vw + .05) * R; cc = Uw * R
        g = np.zeros(shape, bool)
        r_, c_ = fill_poly(rr, cc, shape); g[r_, c_] = True
        return g

    def wing_iou(g, ref, Us):
        # fixed boundary, independent of the fitted shoulder: a shoulder-relative cut let the
        # optimiser crop away its own worst-fitting root pixels by moving the shoulder outward
        cut = int(CUT_U * R)
        a, b = g[:, cut:], ref[:, cut:]
        return (a & b).sum() / max((a | b).sum(), 1)

    def obj(p):
        L_cm, Us, Vs = p[:3]
        tot = 0
        for k_, side in enumerate((1, -1)):
            th_s, th_w, kk = p[3 + 3 * k_: 6 + 3 * k_]
            tot += wing_iou(model_mask(L_cm, Us, Vs, th_s, 0.0, th_w, kk), sides[side], Us)
        return -tot / 2

    bounds = [(LMIN, LMAX), (.06, .14), (-.32, -.12)] + [(-40, 40), (-60, 30), (.75, 1.0)] * 2
    if p0 is None:
        r = differential_evolution(obj, bounds, seed=1, popsize=10, maxiter=120, tol=1e-7, polish=False, workers=1)
        print('coarse', round(-r.fun, 4), np.round(r.x, 3), flush=True)
        return r.x
    from scipy.optimize import minimize
    r = minimize(obj, p0, method='Nelder-Mead', bounds=bounds,
                 options=dict(maxiter=3000, xatol=1e-3, fatol=1e-6, initial_simplex=None))
    p = r.x
    best = dict(photo=path, iou_mean=-r.fun, L_cm=p[0], shoulder_U=p[1], shoulder_V=p[2], sym_iou=F['sym_iou'],
                span_over_length_photo=F['res']['span_over_length'])
    for k_, side in enumerate((1, -1)):
        th_s, th_w, kk = p[3 + 3 * k_: 6 + 3 * k_]
        best[f'wing{side:+d}'] = dict(th_s=th_s, th_e=0.0, th_w=th_w, k=kk,
                                      iou=wing_iou(model_mask(p[0], p[1], p[2], th_s, 0.0, th_w, kk), sides[side], p[1]))
    # overlay: photo red, model blue, both dark; left half = side -1 mirrored back
    tiles = []
    for k_, side in enumerate((-1, 1)):
        kk = 0 if side == 1 else 1
        a_, b_, c_ = p[3 + 3 * kk: 6 + 3 * kk]
        g = model_mask(p[0], p[1], p[2], a_, 0.0, b_, c_)
        ref = sides[side]
        rgb = np.full(shape + (3,), 255, np.uint8)
        rgb[ref & ~g] = (220, 60, 60); rgb[g & ~ref] = (60, 90, 220); rgb[g & ref] = (40, 40, 40)
        tiles.append(rgb[:, ::-1] if side == -1 else rgb)
    # photo body (both sides) underneath for context
    full = np.concatenate(tiles, 1)
    body = raster(F['U'] + 1.3, F['V'], (shape[0], 2 * shape[1]))
    full[body & (full.sum(2) == 765)] = (200, 200, 200)
    pathlib.Path(out).mkdir(parents=True, exist_ok=True)
    Image.fromarray(full).save(f'{out}/{name}_fit.png')
    json.dump(best, open(f'{out}/{name}_fit.json', 'w'), indent=1, default=float)
    print(json.dumps(best, indent=1, default=lambda v: round(float(v), 3)))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('photo'); ap.add_argument('--bluesky', action='store_true')
    ap.add_argument('--out', required=True); ap.add_argument('--L', type=float, nargs=2); ap.add_argument('--name', required=True)
    a = ap.parse_args()
    if a.L: LMIN, LMAX = a.L
    fit(a.photo, a.bluesky, a.out, a.name)
