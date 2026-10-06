"""Rebuild the starling model and everything derived from it.

    uvx python starling/build_all.py [--refs DIR] [--blender PATH]

Steps (Blender runs headless, `--background --factory-startup`, through blender/run_headless.py):
  1. analysis/make_params_starling.py        -> blender/params_starling.json
  2. silhouettes, top/front/side, 1200 px     -> renders/silhouettes/ (+ metrics.json)
  3. shaded renders from below and above      -> renders/shaded/
  4. outline export for murmuration.html      -> outline/starling-outline.json
  5. the .blend in the glide pose             -> starling.blend
  6. outline vs render check, 15- and 13-point outlines -> outline/check.json, starling-low15/13.{json,png}
  7. contact sheets                           -> renders/sheet_*.png
  8. with --refs (the photo masks, kept outside the repository): photo validation
     -> analysis/validation_scores.json, overlays in analysis/validation/ (ignored)
  9. refresh the page's embedded bird tables from the model exports
"""
import argparse, json, os, pathlib, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
BL, AN, OUT = HERE / 'blender', HERE / 'analysis', HERE / 'outline'
PY = ['uvx', '--with', 'numpy', '--with', 'pillow', '--with', 'scipy', '--with', 'scikit-image', 'python']
POSES = ['glide', 'flap_top', 'flap_mid', 'flap_bottom', 'upstroke', 'upstroke_top', 'bound']
ap = argparse.ArgumentParser()
ap.add_argument('--refs', help='murmuration-refs/starling (needs masks/*__norm.png)')
ap.add_argument('--blender', default=os.environ.get('BLENDER', '/Applications/Blender.app/Contents/MacOS/Blender'))
a = ap.parse_args()
TMP = pathlib.Path(tempfile.mkdtemp(prefix='starling_'))


def run(cmd, **kw):
    print('+', ' '.join(map(str, cmd)).replace('\n', ' ')[:160], flush=True)
    return subprocess.run(list(map(str, cmd)), check=True, **kw)


def blender(name, scripts, after='', poses=BL / 'poses_starling.json', **g):
    job = {'dir': str(BL) + '/', 'scripts': scripts, 'after': after,
           'globals': {'PREFIX': 'Starling', 'PARAMS': str(BL / 'params_starling.json'), 'POSES_PATH': str(poses),
                       'BIRD_DIR': str(BL) + '/', 'ONLY': None, **g}}
    p = TMP / f'{name}.json'; p.write_text(json.dumps(job))
    r = run([a.blender, '--background', '--factory-startup', '--python', BL / 'run_headless.py', '--', p],
            capture_output=True, text=True)
    if 'Traceback' in r.stdout + r.stderr:
        sys.exit(r.stdout[-3000:] + r.stderr[-3000:])


BASE = ['bird_build.py', 'bird_render.py', 'bird_measure.py']
run(['uvx', '--with', 'numpy', 'python', AN / 'make_params_starling.py'])
blender('silhouettes', BASE + ['bird_sheet.py'], OUT_DIR=str(HERE / 'renders/silhouettes'), VIEWS=['top', 'front', 'side'], RES=1200)
blender('shaded', BASE + ['starling_look.py'], OUT_DIR=str(HERE / 'renders/shaded'),
        after=f"VIEWS=('below','above'); RES=(1200,800); exec(open('{BL}/bird_beauty.py').read())")
blender('outline', BASE + ['bird_outline.py'], OUT_JSON=str(OUT / 'starling-outline.json'))
blender('save', BASE + ['starling_look.py'], OUT_DIR=str(TMP), BLEND=str(HERE / 'starling.blend'),
        after=f"exec(open('{BL}/bird_save.py').read())")

# outline vs the silhouettes it was read from (nonzero fill, same framing as the top camera)
chk = r'''
import json, sys, numpy as np
from PIL import Image
sys.path.insert(0, sys.argv[1]); import outline_raster as R
P = json.load(open(sys.argv[2])); O = json.load(open(sys.argv[3])); hs = P['wing']['half_span']
cy = (P['body']['y_bill'] + P['tail']['y_base'] - P['tail']['length']) / 2; res = {}
for p in O['wing']:
    m = R.winding_raster(R.bird_polys(O, p), O['halfSpanM'], round(2.43 * hs, 4), cy, res=1200)
    r = np.array(Image.open(f'{sys.argv[4]}/{p}__top.png').convert('L')) < 128
    res[p] = round(float((m & r).sum() / (m | r).sum()), 4)
json.dump({'iou_outline_vs_render': res, 'fill': 'nonzero', 'raster_px': 1200}, open(sys.argv[5], 'w'), indent=1); print(res)
'''
run(PY + ['-c', chk, AN, BL / 'params_starling.json', OUT / 'starling-outline.json', HERE / 'renders/silhouettes', OUT / 'check.json'])
run(PY + [AN / 'lowpoly.py', OUT / 'starling-outline.json', '--out', OUT / 'starling-low15.json', '--poses', ','.join(POSES),
          '--m', '7', '--res', '360', '--perim', '0.0015'])
run(PY + [AN / 'plot_lowpoly.py', OUT / 'starling-outline.json', OUT / 'starling-low15.json', OUT / 'starling-low15.png'])
run(PY + [AN / 'lowpoly.py', OUT / 'starling-outline.json', '--out', OUT / 'starling-low13.json', '--poses', ','.join(POSES),
          '--m', '6', '--res', '360', '--perim', '0.0015'])
run(PY + [AN / 'plot_lowpoly.py', OUT / 'starling-outline.json', OUT / 'starling-low13.json', OUT / 'starling-low13.png'])
run(PY + [HERE / 'renders/make_sheets.py'], cwd=HERE / 'renders')

if a.refs:
    M = pathlib.Path(a.refs) / 'masks'; V = AN / 'validation'; V.mkdir(exist_ok=True)
    glide = sorted(str(p) for p in M.glob('0[12346]_*__norm.png')); top08 = sorted(str(p) for p in M.glob('08_*__norm.png'))
    for p in ('glide', 'flap_mid', 'flap_top'):
        run(PY + [AN / 'silhouette.py', HERE / f'renders/silhouettes/{p}__top.png', '--out', TMP / 'model'], capture_output=True)
    def cmp(model, refs, out):
        r = run(PY + [AN / 'compare.py', model, *refs, '--out', V / out], capture_output=True, text=True)
        return {pathlib.Path(x['ref']).name[:2]: x['iou'] for x in json.loads(r.stdout)}
    scores = {
        'model_glide_vs_glide_photos': cmp(TMP / 'model/glide__top__norm.png', glide, 'cmp_glide.png'),
        'model_flap_mid_vs_glide_photos': cmp(TMP / 'model/flap_mid__top__norm.png', glide, 'cmp_flapmid.png'),
        'old_page_outline_vs_glide_photos': cmp(AN / 'old_page_starling__norm.png', glide, 'cmp_old_glide.png'),
        'model_flap_top_vs_photo_08': cmp(TMP / 'model/flap_top__top__norm.png', top08, 'cmp_flaptop_08.png'),
        'old_page_outline_vs_photo_08': cmp(AN / 'old_page_starling__norm.png', top08, 'cmp_old_08.png'),
    }
    # pose-matched: the model posed with each photo's fitted wing angles (analysis/photo_fits)
    run(PY + [AN / 'validate_posed.py', AN / 'photo_fits', TMP / 'poses_validate.json'])
    blender('posed', BASE + ['bird_sheet.py'], poses=TMP / 'poses_validate.json', OUT_DIR=str(TMP / 'posed'), VIEWS=['top'], RES=1000)
    run(PY + [AN / 'score_posed.py', TMP / 'posed', M, TMP / 'posed_scores.json'])
    ps = json.load(open(TMP / 'posed_scores.json'))
    scores['model_pose_matched_vs_own_photo'] = {t: {'pose': k, 'iou': round(v, 3)} for t, (k, v) in ps['best'].items()}
    for f in (TMP / 'posed/cmp').glob('*.png'):
        (V / 'posed').mkdir(exist_ok=True); f.replace(V / 'posed' / f.name)
    mean = lambda d: round(sum(d.values()) / len(d), 3)
    scores['means'] = {k: mean(v) for k, v in scores.items() if k != 'model_pose_matched_vs_own_photo'}
    scores['means']['model_pose_matched_glide_photos'] = round(sum(v['iou'] for t, v in scores['model_pose_matched_vs_own_photo'].items() if t != 'P08') / 5, 3)
    scores['note'] = ('IoU of normalised top-view masks (half-span = 1), best vertical shift; photos 01-04 and 06 are '
                      'glides (05 dropped: tilted axis), 08 is the top of a downstroke. Overlays: analysis/validation/ (ignored).')
    json.dump(scores, open(AN / 'validation_scores.json', 'w'), indent=1)
    print(json.dumps(scores['means'], indent=1))
run(['node', HERE.parent / 'murmuration-assets.js', '--write'])
print('done; page tables updated; scratch in', TMP)
