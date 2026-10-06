"""Bake what the page needs to light birds from the photographed sky (step c).

    uv run python bake.py HDR [--reg registration.json] [--curve tone_curve.json] [--out sky_light.json]

All directions are in the page's frame (x right, y up, z away from the viewer, camera pitched up).
  sun:        unit direction and elevation of the luminance-weighted centroid of pixels above 10 % of the peak
  irradiance: E(n) = sum L(w) max(0, n.w) dw over the whole map, on a 32 x 16 equirect grid of normals n,
              linear HDR units (the sun included)
  view:       linear sky radiance behind each part of the frame, 96 x 40 cells over the 3840 x 1600 image
  tone:       code (0-255) per channel at 64 log-spaced radiances; below the darkest fitted pixel the curve is
              extended as a power law fitted to the lowest decade of data (marked by `extrapolated_below`)
"""
import argparse
import json
import math

import cv2
import numpy as np

from common import JH, JW, dir_to_equirect, equirect_to_dir, luminance, read_hdr, reproject

ap = argparse.ArgumentParser()
ap.add_argument('hdr')
ap.add_argument('--reg', default='registration.json')
ap.add_argument('--curve', default='tone_curve.json')
ap.add_argument('--out', default='sky_light.json')
a = ap.parse_args()
reg = json.load(open(a.reg)); pose = (reg['yaw'], reg['pitch'], reg['roll'])
eq = read_hdr(a.hdr)
if reg['mirror']:
    eq = eq[:, ::-1].copy()
H, W = eq.shape[:2]
q = math.radians(reg['yaw'])


def to_page(d):                                  # common.reproject turns page directions by +yaw about y
    x, y, z = d[..., 0], d[..., 1], d[..., 2]
    return np.stack([math.cos(q) * x - math.sin(q) * z, y, math.sin(q) * x + math.cos(q) * z], -1)


def from_page(d):
    x, y, z = d[..., 0], d[..., 1], d[..., 2]
    return np.stack([math.cos(q) * x + math.sin(q) * z, y, -math.sin(q) * x + math.cos(q) * z], -1)


# sun
L = luminance(eq)
m = L > .1 * L.max()
vv, uu = np.nonzero(m)
wts = L[m]
dirs = equirect_to_dir(uu + .5, vv + .5, W, H)
s = (dirs * wts[:, None]).sum(0); s /= np.linalg.norm(s)
sun = to_page(s)
cos_lat = np.cos((0.5 - (np.arange(H) + .5) / H) * np.pi)
dO = np.broadcast_to((2 * np.pi / W) * (np.pi / H) * cos_lat[:, None], (H, W))
sun_rgb = (eq[m] * dO[m][:, None]).sum(0)        # its irradiance at normal incidence (excess over nothing)
print('sun page dir', sun.round(4), 'elevation %.2f deg' % math.degrees(math.asin(sun[1])), 'pixels', m.sum(),
      'normal irradiance', sun_rgb.round(3))

# irradiance table over normals, from a 512 x 256 map plus the sun pixels at full resolution
small = cv2.resize(np.where(m[..., None], 0, eq), (512, 256), interpolation=cv2.INTER_AREA)
hs, ws = small.shape[:2]
cl = np.cos((0.5 - (np.arange(hs) + .5) / hs) * np.pi)
dOs = np.broadcast_to((2 * np.pi / ws) * (np.pi / hs) * cl[:, None], (hs, ws)).ravel()
ds = equirect_to_dir(*np.meshgrid(np.arange(ws) + .5, np.arange(hs) + .5), ws, hs).reshape(-1, 3)
Ls = small.reshape(-1, 3)
GW, GH = 32, 16
gu, gv = np.meshgrid(np.arange(GW) + .5, np.arange(GH) + .5)
nrm_page = equirect_to_dir(gu, gv, GW, GH)               # grid laid out in the PAGE frame
nrm = from_page(nrm_page).reshape(-1, 3)
cosw = np.clip(nrm @ ds.T, 0, None)
E = (cosw * dOs) @ Ls + np.clip(nrm @ s, 0, None)[:, None] * sun_rgb[None]
E = E.reshape(GH, GW, 3)
print('irradiance up %s down %s toward camera %s' % tuple(
    np.round([E[0].mean(0), E[-1].mean(0), E[GH // 2, GW // 2]], 3).tolist()))

# sky radiance behind the frame
view = cv2.resize(reproject(eq, 960, 400, *pose), (96, 40), interpolation=cv2.INTER_AREA)

# tone curve, extended below the data
tc = json.load(open(a.curve))
lo = min(tc['report'][c]['radiance_range'][0] for c in 'RGB')
grid = np.exp(np.linspace(np.log(1e-4), np.log(64), 64))
tone = {}
for c in 'RGB':
    xs, ys = np.array(tc['curves'][c]['log_radiance']), np.array(tc['curves'][c]['code'])
    r0 = tc['report'][c]['radiance_range'][0]
    sel = (xs >= np.log(r0)) & (xs <= np.log(r0 * 10)) & (ys > 0)
    g, lc = np.polyfit(xs[sel], np.log(ys[sel]), 1)
    code = np.interp(np.log(grid), xs, ys)
    below = grid < r0
    code[below] = np.exp(lc) * grid[below] ** g
    tone[c] = code.round(3).tolist()
    print(c, 'toe exponent %.2f below %.3f' % (g, r0))

json.dump(dict(
    source=dict(hdr=a.hdr.split('/')[-1], registration=reg),
    sun=dict(dir=sun.round(5).tolist(), elevation_deg=round(math.degrees(math.asin(sun[1])), 3),
             normal_irradiance=sun_rgb.round(4).tolist()),
    irradiance=dict(w=GW, h=GH, layout='normal n = (cos lat sin lon, sin lat, cos lat cos lon), lon = (0.5 - (col + .5) / w) 2pi, lat = (0.5 - (row + .5) / h) pi',
                    rgb=E.round(4).reshape(-1, 3).tolist()),
    view=dict(w=96, h=40, rgb=view.round(4).reshape(-1, 3).tolist()),
    tone=dict(radiance=grid.round(6).tolist(), extrapolated_below=lo, **tone),
), open(a.out, 'w'))
