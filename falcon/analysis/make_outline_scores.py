"""Regenerate outline_scores.json: the page's outline and the model renders against the photo sets.

usage: make_outline_scores.py --photo-dir DIR [--outline blender/falcon-outline.json] [--out outline_scores.json]

DIR holds the *__norm.png photo masks written by silhouette.py --skydist (not in the repository).
Only numbers are written; no photo-derived pixels.
"""
import argparse, json, pathlib
from score_outline import PONITZ_TUCK, photo_list, score

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent

ap = argparse.ArgumentParser()
ap.add_argument('--photo-dir', required=True)
ap.add_argument('--outline', default=str(ROOT / 'blender' / 'falcon-outline.json'))
ap.add_argument('--out', default=str(HERE / 'outline_scores.json'))
a = ap.parse_args()

glide, soar = photo_list(None, a.photo_dir, 'glide'), photo_list(None, a.photo_dir, 'soar')
sil = ROOT / 'falcon' / 'renders' / 'silhouettes'
stoop = score(a.outline, 'stoop', [])
ratio = stoop['raster']['width_over_length']
res = {
    'method': 'score_outline.py: outline filled as pushFalcon() does (nonzero), normalised by silhouette.py, '
              'whole-bird IoU after best vertical shift within +-40 px of a 400 px raster (compare.py)',
    'page_outline_glide_vs_glide_photos': score(a.outline, 'glide', glide),
    'page_outline_glide_vs_soar_photos': score(a.outline, 'glide', soar),
    'model_glide_render_vs_glide_photos': score(sil / 'glide__top.png', 'glide', glide),
    'model_soar_render_vs_soar_photos': score(sil / 'soar__top.png', 'soar', soar),
    'page_outline_stoop': dict(stoop, ponitz_2014_tucked_width_over_length=list(PONITZ_TUCK),
                               within_ponitz_range=bool(PONITZ_TUCK[0] <= ratio <= PONITZ_TUCK[1]),
                               ratio_over_range_top=round(ratio / PONITZ_TUCK[1], 2)),
}
pathlib.Path(a.out).write_text(json.dumps(res, indent=1) + '\n')
for k, v in res.items():
    if isinstance(v, dict) and 'mean_iou' in v:
        print(f"{k:40s} {' '.join(format(p['iou'], '.3f') for p in v['photos'])}  mean {v['mean_iou']:.3f}")
print(f"stoop width/length {ratio} (Ponitz tucked {PONITZ_TUCK[0]}-{PONITZ_TUCK[1]})")
