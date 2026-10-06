"""How varied birds look within one frame: the axis angle and elongation of each isolated bird.

    uv run python -I measure_attitude.py IMAGE[:x0,y0,x1,y1] ... [--maxrow 0.75] [--json out.json]

Birds are found as dark blobs against the sky (luminance under 0.6 of a 61-px median background), then
isolated ones are kept: area within 0.4-2.5x the frame's median blob area and at least 30 px. For each blob,
second moments give the main-axis angle and the elongation sqrt(l1 / l2). Per frame the report gives:
  angle_sd     the axial circular SD of blob angles, degrees: how much the birds' wing lines disagree. It
               does not depend on how the camera was rolled.
  bars         the share of blobs that are flat level bars: elongation over 4 and within 10 deg of the frame's
               mean axis.
  elong        elongation quartiles.
An optional crop box limits the search (the flock region of a photo); --maxrow drops rows below that share of
the height (the treeline in the page's frames).
"""
import argparse
import json
import math

import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('images', nargs='+')
ap.add_argument('--maxrow', type=float, default=1.0)
ap.add_argument('--json')
a = ap.parse_args()


def measure(path, box=None):
    im = cv2.imread(path, cv2.IMREAD_COLOR)
    if im is None:
        raise FileNotFoundError(path)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    H, W = g.shape
    x0, y0, x1, y1 = box or (0, 0, W, int(H * a.maxrow))
    g = g[y0:y1, x0:x1]
    bg = cv2.medianBlur(np.clip(g, 0, 255).astype(np.uint8), 61).astype(np.float32) + 1
    mask = ((g / bg) < .6).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    areas = st[1:, cv2.CC_STAT_AREA]
    if len(areas) < 10:
        return None
    med = np.median(areas[areas >= 30]) if (areas >= 30).any() else 0
    ang, el, length = [], [], []
    for k in range(1, n):
        ar = st[k, cv2.CC_STAT_AREA]
        if ar < 30 or ar < .4 * med or ar > 2.5 * med:
            continue
        x, y, w, h = st[k, :4]
        m = (lab[y:y + h, x:x + w] == k).astype(np.uint8)
        mo = cv2.moments(m, binaryImage=True)
        mu20, mu02, mu11 = mo['mu20'] / ar, mo['mu02'] / ar, mo['mu11'] / ar
        t = .5 * math.atan2(2 * mu11, mu20 - mu02)
        d = math.sqrt(((mu20 - mu02) / 2) ** 2 + mu11 ** 2)
        l1, l2 = (mu20 + mu02) / 2 + d, max((mu20 + mu02) / 2 - d, 1e-6)
        ang.append(t); el.append(math.sqrt(l1 / l2)); length.append(4 * math.sqrt(l1))
    if len(ang) < 10:
        return None
    ang = np.array(ang); el = np.array(el)
    z = np.exp(2j * ang).mean()
    R = abs(z); mean = np.angle(z) / 2
    sd = math.degrees(math.sqrt(-2 * math.log(max(R, 1e-9))) / 2)
    off = np.degrees(np.abs((ang - mean + np.pi / 2) % np.pi - np.pi / 2))
    return dict(image=path.split('/')[-2] + '/' + path.split('/')[-1], n=len(ang), length_px_median=round(float(np.median(length)), 1),
                angle_sd=round(sd, 1), mean_axis_deg=round(math.degrees(mean), 1),
                bars=round(float(((el > 4) & (off < 10)).mean()), 3),
                elong=[round(float(q), 2) for q in np.quantile(el, [.25, .5, .75])])


out = []
for spec in a.images:
    path, _, box = spec.partition(':')
    r = measure(path, tuple(map(int, box.split(','))) if box else None)
    if r:
        out.append(r)
        print(json.dumps(r))
    else:
        print('too few birds:', spec)
if a.json:
    json.dump(out, open(a.json, 'w'), indent=1)
