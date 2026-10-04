"""Normalise the pose-matched renders with silhouette.py and score each against its own photo with compare.py.
usage: score_posed.py RENDER_DIR PHOTO_NORM_DIR OUT.json"""
import sys, glob, json, subprocess, pathlib, re
from concurrent.futures import ThreadPoolExecutor
rd, pd, out = map(pathlib.Path, sys.argv[1:4])
HERE = pathlib.Path(__file__).parent
PY = ['uvx', '--with', 'numpy', '--with', 'pillow', '--with', 'scipy', '--with', 'scikit-image', 'python']
(rd / 'norm').mkdir(exist_ok=True); (rd / 'cmp').mkdir(exist_ok=True)
renders = sorted(rd.glob('*__top.png'))
def norm(p):
    subprocess.run(PY + [str(HERE / 'silhouette.py'), str(p), '--out', str(rd / 'norm')], capture_output=True, check=True)
    return rd / 'norm' / (p.stem + '__norm.png')
def score(p):
    n = norm(p); tag = p.name.split('_')[0]; ref = next(pd.glob(f'{tag[1:]}_*__norm.png'))
    r = subprocess.run(['uvx', '--with', 'numpy', '--with', 'pillow', 'python', str(HERE / 'compare.py'), str(n), str(ref),
                        '--out', str(rd / 'cmp' / (p.stem + '.png'))], capture_output=True, text=True, check=True)
    return p.name.split('__')[0], json.loads(r.stdout)[0]['iou']
with ThreadPoolExecutor(6) as ex:
    res = dict(ex.map(score, renders))
best = {}
for k, v in sorted(res.items()):
    tag = k.split('_')[0]
    if v > best.get(tag, ('', -1))[1]: best[tag] = (k, v)
json.dump({'all': res, 'best': best}, open(out, 'w'), indent=1)
for tag, (k, v) in best.items(): print(tag, k, f'{v:.3f}', ' all:', ' '.join(f'{res[x]:.3f}' for x in sorted(res) if x.startswith(tag + '_')))
print('mean best (glide photos)', round(sum(v for t, (k, v) in best.items() if t != 'P08') / sum(1 for t in best if t != 'P08'), 3))
