"""Regenerate outline_scores.json for the current page outline and a legacy baseline.

usage: make_outline_scores.py --photo-dir DIR [--outline outline/peregrine-outline.json]
                              [--legacy-outline ../blender/falcon-outline.json]
                              [--out outline_scores.json]

DIR holds the *__norm.png photo masks written by silhouette.py --skydist (not in the repository).
The default outline is the current four-key falcon table. The older blender/falcon-outline.json is
scored separately as a legacy comparison. Only numbers and photo identifiers are written; no
photo-derived pixels.
"""
import argparse, hashlib, json, pathlib
from score_outline import PONITZ_TUCK, photo_list, score

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent

ap = argparse.ArgumentParser()
ap.add_argument('--photo-dir', required=True)
ap.add_argument('--outline', default=str(ROOT / 'falcon' / 'outline' / 'peregrine-outline.json'),
                help='current page outline (default: falcon/outline/peregrine-outline.json)')
ap.add_argument('--legacy-outline', default=str(ROOT / 'blender' / 'falcon-outline.json'),
                help='older two-pose page outline to retain as a labeled baseline')
ap.add_argument('--out', default=str(HERE / 'outline_scores.json'))
a = ap.parse_args()

glide, soar = photo_list(None, a.photo_dir, 'glide'), photo_list(None, a.photo_dir, 'soar')
if len(glide) != 4 or len(soar) != 3:
    raise SystemExit(f'expected 4 glide and 3 soar reference masks; found {len(glide)} and {len(soar)}')
sil = ROOT / 'falcon' / 'renders' / 'silhouettes'


def source_label(source):
    path = pathlib.Path(source).resolve()
    try:
        return path.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def sha256(source):
    digest = hashlib.sha256()
    with pathlib.Path(source).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def stoop_pose(outline):
    """Use the current tucked dive key when present; keep legacy wingStoop distinct."""
    data = json.loads(pathlib.Path(outline).read_text())
    wing = data.get('wing')
    if isinstance(wing, dict):
        for pose in ('stoop_tuck', 'stoop'):
            if pose in wing:
                return pose
    elif 'wingStoopTuck' in data:
        return 'stoop_tuck'
    elif 'wingStoop' in data:
        return 'stoop'
    raise SystemExit(f'no stoop_tuck or legacy stoop pose in {outline}')


def stoop_score(outline, pose):
    result = score(outline, pose, [])
    ratio = result['raster']['width_over_length']
    result.update(ponitz_2014_tucked_width_over_length=list(PONITZ_TUCK),
                  within_ponitz_range=bool(PONITZ_TUCK[0] <= ratio <= PONITZ_TUCK[1]),
                  ratio_over_range_top=round(ratio / PONITZ_TUCK[1], 2))
    return result


current_stoop = stoop_pose(a.outline)
legacy_stoop = stoop_pose(a.legacy_outline)
res = {
    'method': 'score_outline.py: outline filled as pushFalcon() does (nonzero), normalised by silhouette.py, '
              'whole-bird IoU after best vertical shift within +-40 px of a 400 px raster (compare.py); '
              'outline inputs are named explicitly and the current four-key outline is kept separate '
              'from the legacy two-pose outline',
    'reference_masks': f'{pathlib.Path(a.photo_dir).name}: silhouette.py --skydist normalised masks; '
                       'photo-derived pixels are not written here',
    'page_outline_source': source_label(a.outline),
    'input_sha256': {
        'page_outline': sha256(a.outline),
        'legacy_outline': sha256(a.legacy_outline),
        'model_glide_render': sha256(sil / 'glide__top.png'),
        'model_soar_render': sha256(sil / 'soar__top.png'),
        'photo_masks': {p.name: sha256(p) for p in glide + soar},
    },
    'page_outline_glide_vs_glide_photos': score(a.outline, 'glide', glide),
    'page_outline_glide_vs_soar_photos': score(a.outline, 'glide', soar),
    'model_glide_render_vs_glide_photos': score(sil / 'glide__top.png', 'glide', glide),
    'model_soar_render_vs_soar_photos': score(sil / 'soar__top.png', 'soar', soar),
    'page_outline_stoop_tuck': stoop_score(a.outline, current_stoop),
    'legacy_outline_source': source_label(a.legacy_outline),
    'legacy_outline_glide_vs_glide_photos': score(a.legacy_outline, 'glide', glide),
    'legacy_outline_glide_vs_soar_photos': score(a.legacy_outline, 'glide', soar),
    'legacy_outline_stoop': stoop_score(a.legacy_outline, legacy_stoop),
}
pathlib.Path(a.out).write_text(json.dumps(res, indent=1) + '\n')
for k, v in res.items():
    if isinstance(v, dict) and 'mean_iou' in v:
        print(f"{k:40s} {' '.join(format(p['iou'], '.3f') for p in v['photos'])}  mean {v['mean_iou']:.3f}")
for label in ('page_outline_stoop_tuck', 'legacy_outline_stoop'):
    result = res[label]
    ratio = result['raster']['width_over_length']
    print(f"{label}: pose {result['pose']}, width/length {ratio} "
          f"(Ponitz tucked {PONITZ_TUCK[0]}-{PONITZ_TUCK[1]})")
