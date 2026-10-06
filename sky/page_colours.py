"""The page's bird colours over the photographed sky, from the measurements in this directory.

    uv run python page_colours.py RENDERS.json [--sky sky_light.json] [--haze haze.json] [--fit bird_light.json]

Per depth bin (murmuration.html draws birds in 6 bins over 37.5-100 m):
    L = L_bird exp(-beta d) + L_sky (1 - exp(-beta d)),   code = the recovered tone curve of L
L_bird: mean linear radiance of the starling model in its own plumage over the Cycles renders, sun glints left out
        (they are 6 % of renders; see bird_light.json). The renders show no usable dependence on the bird's place
        in the frame or orientation beyond that mean (cross-validated rule error 0.052 vs spread 0.057).
L_sky:  median sky radiance behind the part of the frame the flock uses (rows 100-1150 of 3840x1600).
beta:   haze. The treelines give only an upper bound (haze.json: the darkest foliage of the wood 139 m away is
        2.45 % of its sky in blue, so airlight there is at most that): beta <= 1.8e-4 /m. The page uses half of it;
        both ends are printed.
"""
import argparse
import json
import math

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('renders')
ap.add_argument('--sky', default='sky_light.json')
ap.add_argument('--haze', default='haze.json')
a = ap.parse_args()
R = json.load(open(a.renders)); S = json.load(open(a.sky)); Hz = json.load(open(a.haze))
lum = lambda v: float(np.dot(v[:3], [.2126, .7152, .0722]))
ok = [r for r in R if lum(r['g05']) <= .3]
L_bird = {k: np.mean([r[k][:3] for r in ok], 0) for k in ('look', 'g03', 'g05', 'g10')}
view = np.array(S['view']['rgb']).reshape(S['view']['h'], S['view']['w'], 3)
rows = slice(int(100 / 40), int(1150 / 40) + 1)
L_sky = np.median(view[rows].reshape(-1, 3), 0)
near = Hz['bins'][0]
bound = -math.log(1 - near['ratio'][2]) / near['d']        # blue: the strictest
beta = bound / 2
tone_r = np.array(S['tone']['radiance']); tone = np.stack([np.array(S['tone'][c]) for c in 'RGB'], -1)
code = lambda L: np.array([np.interp(math.log(max(L[c], 1e-6)), np.log(tone_r), tone[:, c]) for c in range(3)])
ZMIN, ZMAX, NB, U = 75, 200, 6, .5
d = [(ZMIN + (b + .5) / NB * (ZMAX - ZMIN)) * U for b in range(NB)]


def bins(Lb, bt):
    return [code(Lb * math.exp(-bt * x) + L_sky * (1 - math.exp(-bt * x))) for x in d]


out = dict(L_bird_look=L_bird['look'].round(4).tolist(), L_sky=L_sky.round(4).tolist(), beta_bound=bound, beta=beta,
           bin_distance_m=[round(x, 1) for x in d],
           page=[[int(round(v)) for v in c] for c in bins(L_bird['look'], beta)],
           no_haze=[[round(float(v), 1) for v in c] for c in bins(L_bird['look'], 0)],
           haze_at_bound=[[round(float(v), 1) for v in c] for c in bins(L_bird['look'], bound)],
           albedo_003=[round(float(v), 1) for v in code(L_bird['g03'])], albedo_010=[round(float(v), 1) for v in code(L_bird['g10'])],
           sky_code=[round(float(v), 1) for v in code(L_sky)])
print(json.dumps(out, indent=1))
json.dump(out, open('page_colours.json', 'w'), indent=1)
