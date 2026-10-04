"""Reduce a full outline (bird_outline.py JSON) to a small symmetric whole-bird polygon per pose.

The polygon is: nose (on the axis), then M points down the right side, mirrored for the left,
so N = 1 + 2M points (M = 7 gives 15).  Vertex k means the same anatomical point in every pose,
because each pose starts from the same material points of the full outline (fixed mesh vertices:
bill tip, wing leading-edge root, wrist, tip, trailing edge at the wrist, trailing-edge root, tail
corner, ...) and is then refined locally (Nelder-Mead) to maximise IoU against the full outline,
filled with the nonzero rule as canvas does.

usage: lowpoly.py OUTLINE.json --out LOW.json [--poses a,b,c] [--m 7] [--res 360]
"""
import argparse, json
import numpy as np
from scipy.optimize import minimize
from outline_raster import bird_polys, pairs


def wind(polys, X, Y):
    out = np.zeros(X.shape, bool)
    for p in polys:
        a = p[:, 0]; w = p[:, 1]                       # rows = a (along), cols = w (across)
        wn = np.zeros(X.shape, np.int16)
        for x0, y0, x1, y1 in zip(w, a, np.roll(w, -1), np.roll(a, -1)):
            if y0 == y1: continue
            lo, hi = (y0, y1) if y0 < y1 else (y1, y0)
            m = (Y >= lo) & (Y < hi)
            xi = x0 + (Y - y0) * (x1 - x0) / (y1 - y0)
            wn += (m & (X < xi)) * (1 if y1 > y0 else -1)
        out |= wn != 0
    return out


def material_init(O, pose, M):
    """Starting vertices from fixed material points of the full outline."""
    wg = pairs(O['wing'][pose]); body = pairs(O['body']); t = O['tailFanOfPose'].get(pose, 0)
    tail = (1 - t) * pairs(O['tail']) + t * pairs(O['tailFan'])
    nu = (len(wg) + 1) // 2 - 1                       # LE stations 0..nu, TE nu-1..0
    LE = wg[:nu + 1]; TE = np.r_[wg[nu:nu + 1], wg[nu + 1:]][::-1]      # TE root..tip -> reversed to root..tip
    TE = wg[nu:][::-1]                                 # root .. tip (includes the tip)
    hw = lambda a: np.interp(a, body[::-1, 0], body[::-1, 1])            # body half-width at a
    # where the leading/trailing edges leave the body (first station whose |w| exceeds the body)
    def exit_pt(E):
        for p in E:
            if p[1] > hw(p[0]) + 1e-3: return p
        return E[0]
    le_root, te_root = exit_pt(LE), exit_pt(TE)
    i_wr = int(round(0.42 * nu))                      # wrist station on the rest planform (~0.42 of stations)
    wrist_le, wrist_te, tip = LE[i_wr], TE[i_wr], wg[nu]
    neck = np.array([body[np.argmin(abs(body[:, 0] - (le_root[0] + 0.25 * (body[0, 0] - le_root[0]))))][0],
                     hw(le_root[0] + 0.25 * (body[0, 0] - le_root[0]))])
    tail_base = tail[0]; tail_corner = tail[len(tail) - 1 - (len(tail) - 1) // 3]   # right tail-tip corner region
    tail_corner = tail[np.argmax(-tail[:, 0] + 2 * tail[:, 1])]                    # most aft-and-outboard tail point
    side = {7: [neck, le_root, wrist_le, tip, wrist_te, te_root, tail_corner],
            6: [le_root, wrist_le, tip, wrist_te, te_root, tail_corner],
            5: [le_root, tip, wrist_te, te_root, tail_corner],
            8: [neck, le_root, wrist_le, tip, wrist_te, te_root, tail_base, tail_corner]}[M]
    return body[0, 0], np.array(side)


def crossings(P):
    """Number of proper intersections between non-adjacent edges of the closed polygon P."""
    n = len(P); A = P; B = np.roll(P, -1, 0); c = 0
    def orient(p, q, r): return np.sign((q[..., 0] - p[..., 0]) * (r[..., 1] - p[..., 1]) - (q[..., 1] - p[..., 1]) * (r[..., 0] - p[..., 0]))
    for i in range(n):
        j = np.arange(i + 2, n) if i else np.arange(2, n - 1)
        if not len(j): continue
        o1 = orient(A[i], B[i], A[j]); o2 = orient(A[i], B[i], B[j])
        o3 = orient(A[j], B[j], A[i][None]); o4 = orient(A[j], B[j], B[i][None])
        c += int(((o1 * o2 < 0) & (o3 * o4 < 0)).sum())
    return c


def poly_from(x, M):
    nose = x[0]; side = x[1:].reshape(M, 2)
    return np.r_[[[nose, 0.0]], side, (side * [1, -1])[::-1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outline'); ap.add_argument('--out', required=True); ap.add_argument('--poses')
    ap.add_argument('--m', type=int, default=7); ap.add_argument('--res', type=int, default=360)
    ap.add_argument('--perim', type=float, default=0.003, help='penalty per half-span of perimeter')
    a = ap.parse_args()
    O = json.load(open(a.outline)); M = a.m
    global PERIM; PERIM = a.perim
    poses = a.poses.split(',') if a.poses else list(O['wing'])
    res = {'note': 'nose, then M right-side points; left side = mirror (w -> -w) in reverse order. Units: full-spread half-span; '
                   'a forward from the shoulder line. Fill nonzero (canvas default).',
           'M': M, 'N': 1 + 2 * M, 'vertexMeaning': None, 'pose': {}, 'iouVsFull': {}}
    names = {7: ['neck', 'wingLErootExit', 'wristLE', 'tip', 'wristTE', 'wingTErootExit', 'tailCorner'],
             6: ['wingLErootExit', 'wristLE', 'tip', 'wristTE', 'wingTErootExit', 'tailCorner'],
             5: ['wingLErootExit', 'tip', 'wristTE', 'wingTErootExit', 'tailCorner'],
             8: ['neck', 'wingLErootExit', 'wristLE', 'tip', 'wristTE', 'wingTErootExit', 'tailBase', 'tailCorner']}[M]
    res['vertexMeaning'] = ['nose'] + names + ['(mirror)']
    for pose in poses:
        full = bird_polys(O, pose)
        allp = np.vstack(full)
        a0, a1 = allp[:, 0].min() - .05, allp[:, 0].max() + .05; w1 = np.abs(allp[:, 1]).max() + .05
        h = max(a1 - a0, 2 * w1) / a.res
        Y, X = np.meshgrid(np.arange(a0, a1, h) + h / 2, np.arange(-w1, w1, h) + h / 2, indexing='ij')
        T = wind(full, X, Y)
        nose, side = material_init(O, pose, M)
        x0 = np.r_[nose, side.ravel()]
        if crossings(poly_from(x0, M)):
            # folded wing: the trailing-edge points lie hidden under the wing, between the tip and the
            # tail, so start them on the tip -> tail-corner edge (they keep their identity, collapsed)
            it = names.index('tip'); te = [i for i, n_ in enumerate(names) if n_ in ('wristTE', 'wingTErootExit', 'tailBase')]
            tc = names.index('tailCorner')
            for k_, i in enumerate(te, 1):
                side[i] = side[it] + (side[tc] - side[it]) * k_ / (len(te) + 1)
            x0 = np.r_[nose, side.ravel()]
        def f(x):
            P = poly_from(x, M)
            m = wind([P], X, Y)
            # keep the polygon simple and on its own side: crossings would make blends between poses
            # fold over, and a right-side vertex past the midline would cross its mirror image
            pen = 0.25 * crossings(P) + 5 * np.clip(-x[2::2], 0, None).sum()
            # no vertex may leave the full outline's bounding box: a thin spike costs almost no IoU, so
            # without this the optimiser parks unneeded vertices on a needle behind a folded bird
            aa = np.r_[x[0], x[1::2]]; ww = x[2::2]
            # a small perimeter cost: zero-area slivers (an edge doubling back on itself) cost no IoU but
            # show as lines under the page's 1 px stroke
            pen += PERIM * np.hypot(*np.diff(np.vstack([P, P[:1]]), axis=0).T).sum()
            pen += 5 * (np.clip(aa - (a1 - .03), 0, None).sum() + np.clip((a0 + .03) - aa, 0, None).sum() + np.clip(ww - (w1 - .03), 0, None).sum())
            return -(m & T).sum() / (m | T).sum() + pen
        iou0 = -f(x0)
        r = minimize(f, x0, method='Nelder-Mead', options=dict(maxiter=6000, xatol=1e-4, fatol=1e-6, adaptive=True))
        r = minimize(f, r.x, method='Nelder-Mead', options=dict(maxiter=4000, xatol=1e-5, fatol=1e-7, adaptive=True))
        res['pose'][pose] = [round(float(v), 4) for v in np.r_[r.x[0], 0.0, r.x[1:]]]
        Pf = poly_from(r.x, M); mf = wind([Pf], X, Y)
        res['iouVsFull'][pose] = round(float((mf & T).sum() / (mf | T).sum()), 4)
        res.setdefault('crossings', {})[pose] = crossings(Pf)
        print(f"{pose:14s} init IoU {iou0:.3f} -> {res['iouVsFull'][pose]:.4f}  crossings {crossings(Pf)}", flush=True)
    json.dump(res, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
