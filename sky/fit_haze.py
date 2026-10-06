"""Haze from the photographed treelines (step e, visibility).

    uv run python fit_haze.py HDR OSM_MAP_JSON [--reg registration.json] [--sky sky_light.json] [--out haze.json]

1. Compass: the time at which pvlib puts the sun at the elevation measured in the HDRI (sky_light.json) on the
   capture date gives the sun's azimuth; the HDRI's own sun direction then fixes north in the map.
2. Distance: for every 0.1 deg of azimuth, the distance from the camera (Poly Haven's GPS) to the first edge of
   woodland mapped in OpenStreetMap (natural=wood, landuse=forest; ways and multipolygon members), within 3 km.
3. Radiance: in each direction, the darkest foliage near the horizon (2nd percentile of radiance between 0.3 deg
   below and 1.5 deg above the horizon, over 0.3 deg of azimuth) and the sky just above (median, 3-5 deg up).
4. Fit, per channel, dark foliage = A exp(-b d) + sky (1 - exp(-b d)) by least squares over the binned medians,
   where A is the foliage's own (unhazed) radiance. Visibility V = 3.912 / b (Koschmieder, 2 % contrast).
Directions within 25 deg of the sun are left out (glare and lens flare), as are those with nothing mapped.
"""
import argparse
import datetime as dt
import json
import math

import numpy as np
import pandas as pd
import pvlib
from scipy.optimize import least_squares

from common import dir_to_equirect, read_hdr

LAT, LON = 50.797656, 33.583087                # Poly Haven, scythian_tombs_2
DAY = dt.date(2022, 10, 9)                     # date_taken 1665334140 (local wall clock stored as UTC)
ap = argparse.ArgumentParser()
ap.add_argument('hdr'); ap.add_argument('osm')
ap.add_argument('--reg', default='registration.json'); ap.add_argument('--sky', default='sky_light.json')
ap.add_argument('--out', default='haze.json')
a = ap.parse_args()
reg = json.load(open(a.reg)); sky = json.load(open(a.sky))
q = math.radians(reg['yaw'])

# 1. compass
times = pd.date_range(f'{DAY} 12:30', f'{DAY} 15:00', freq='10s', tz='UTC')
sp = pvlib.solarposition.get_solarposition(times, LAT, LON)
el_meas = sky['sun']['elevation_deg']
i = int(np.argmin(np.abs(sp['apparent_elevation'].values - el_meas)))
t_sun, az_sun = times[i], float(sp['azimuth'].values[i])
s = np.array(sky['sun']['dir']); lon_sun = math.degrees(math.atan2(s[0], s[2]))
print(f'sun at {el_meas:.2f} deg elevation: {t_sun} UTC, azimuth {az_sun:.2f} deg; page centre faces '
      f'{(az_sun - lon_sun) % 360:.1f} deg')


def page_dir(az, el):                          # compass azimuth / elevation (deg) -> page-frame unit vector
    lon = np.radians(np.asarray(az) - az_sun + lon_sun); e = np.radians(el)
    return np.stack(np.broadcast_arrays(np.cos(e) * np.sin(lon), np.sin(e), np.cos(e) * np.cos(lon)), -1)


# 2. woodland distances
d = json.load(open(a.osm))['elements']
nodes = {e['id']: (e['lat'], e['lon']) for e in d if e['type'] == 'node'}
ways = {e['id']: e for e in d if e['type'] == 'way'}
woody = lambda t: t.get('natural') == 'wood' or t.get('landuse') == 'forest'
rings = [w['nodes'] for w in ways.values() if woody(w.get('tags', {}))]
for r in d:
    if r['type'] == 'relation' and woody(r.get('tags', {})):
        rings += [ways[m['ref']]['nodes'] for m in r['members'] if m['type'] == 'way' and m['ref'] in ways]
kx = 111320 * math.cos(math.radians(LAT)); ky = 110540
segs = []
for ring in rings:
    pts = [((nodes[n][1] - LON) * kx, (nodes[n][0] - LAT) * ky) for n in ring if n in nodes]   # east, north (m)
    segs += [(pts[j], pts[j + 1]) for j in range(len(pts) - 1)]
S = np.array(segs)                             # (n, 2, 2)
print('woodland rings', len(rings), 'segments', len(S))
azs = np.arange(0, 360, .1)
dist = np.full(len(azs), np.nan)
P0, P1 = S[:, 0], S[:, 1]
for k, az in enumerate(azs):
    ux, uy = math.sin(math.radians(az)), math.cos(math.radians(az))
    e = P1 - P0; den = e[:, 0] * uy - e[:, 1] * ux
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (e[:, 0] * P0[:, 1] - e[:, 1] * P0[:, 0]) / den
        sg = (ux * P0[:, 1] - uy * P0[:, 0]) / den
    ok = (np.abs(den) > 1e-9) & (sg >= 0) & (sg <= 1) & (t > 20) & (t < 3000)
    if ok.any():
        dist[k] = t[ok].min()

# 3. radiance
eq = read_hdr(a.hdr)
if reg['mirror']:
    eq = eq[:, ::-1].copy()
H, W = eq.shape[:2]


def from_page(v):
    x, y, z = v[..., 0], v[..., 1], v[..., 2]
    return np.stack([math.cos(q) * x + math.sin(q) * z, y, -math.sin(q) * x + math.cos(q) * z], -1)


def sample(az, el):
    u, v = dir_to_equirect(from_page(page_dir(az, el)), W, H)
    ui = np.clip(u.astype(int), 0, W - 1); vi = np.clip(v.astype(int), 0, H - 1)
    return eq[vi, ui]


fol = np.full((len(azs), 3), np.nan); skyr = np.full((len(azs), 3), np.nan)
for k, az in enumerate(azs):
    if np.isnan(dist[k]):
        continue
    A_, E_ = np.meshgrid(az + np.linspace(-.15, .15, 7), np.arange(-.3, 1.5, .02))
    px = sample(A_, E_).reshape(-1, 3)
    fol[k] = np.percentile(px, 2, axis=0)
    A_, E_ = np.meshgrid(az + np.linspace(-.15, .15, 7), np.arange(3, 5, .1))
    skyr[k] = np.median(sample(A_, E_).reshape(-1, 3), axis=0)
off_sun = np.abs((azs - az_sun + 180) % 360 - 180) > 25
use = ~np.isnan(dist) & off_sun
print('directions used', int(use.sum()), 'of', len(azs), '; distance range %.0f-%.0f m' % (np.nanmin(dist[use]), np.nanmax(dist[use])))

# 4. fit on distance bins (medians), per channel
edges = np.array([0, 150, 250, 350, 500, 700, 1000, 1400, 2000, 3000])
out = dict(sun_time_utc=str(t_sun), sun_azimuth=az_sun, page_centre_azimuth=(az_sun - lon_sun) % 360,
           directions=int(use.sum()), bins=[], channels={})
ratio = fol / skyr                             # foliage as a share of its own horizon sky
for lo, hi in zip(edges[:-1], edges[1:]):
    m = use & (dist >= lo) & (dist < hi)
    if m.sum() >= 15:
        out['bins'].append(dict(d=float(np.median(dist[m])), n=int(m.sum()),
                                ratio=[round(float(x), 4) for x in np.median(ratio[m], axis=0)],
                                ratio_iqr=[[round(float(x), 4) for x in np.percentile(ratio[m][:, c], [25, 75])] for c in range(3)]))
bd = np.array([b['d'] for b in out['bins']]); br = np.array([b['ratio'] for b in out['bins']])
for c, name in enumerate('RGB'):
    # ratio = A' exp(-b d) + 1 - exp(-b d), with A' the unhazed foliage/sky ratio
    f = lambda p: p[0] * np.exp(-p[1] * bd) + 1 - np.exp(-p[1] * bd) - br[:, c]
    r = least_squares(f, [.05, 1e-4], bounds=([0, 0], [1, .01]))
    J = r.jac; cov = np.linalg.pinv(J.T @ J) * (r.fun ** 2).sum() / max(len(bd) - 2, 1)
    b, sb = r.x[1], math.sqrt(max(cov[1, 1], 0))
    out['channels'][name] = dict(A=round(float(r.x[0]), 4), beta_per_m=float(b), beta_se=float(sb),
                                 V_km=round(3.912 / b / 1000, 2) if b > 0 else None,
                                 airlight_37m=round(1 - math.exp(-b * 37), 4), airlight_100m=round(1 - math.exp(-b * 100), 4))
print(json.dumps(out, indent=1))
np.savez_compressed(a.out.replace('.json', '_samples.npz'), az=azs, dist=dist, fol=fol, sky=skyr, use=use)
json.dump(out, open(a.out, 'w'), indent=1)
