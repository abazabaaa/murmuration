# Peregrine falcon model

A parametric Blender model of a peregrine falcon (*Falco peregrinus*). Its proportions come from measured references, and `murmuration.html` draws its falcon from this model's top-view outline (see "Outline export" below).

- `peregrine.blend`: the model in the glide pose. It has an armature with shoulder, elbow and wrist bones per wing, five feather bones per wing, and a tail with a fanned shape key.
- `renders/`: final renders.
  - `sheet_silhouettes_top.png`, `sheet_silhouettes_front.png`: outlines, each labelled with its measured value and target.
  - `sheet_shaded_below.png`, `sheet_shaded_above.png`: shaded renders.
  - `silhouettes/metrics.json`: the per-pose measurements.

## Where the proportions come from

| quantity | value | source |
|---|---|---|
| wing planform | PSM 22483, female right wing, pressed: 46.9 cm root to tip, 594 cm² | Slater Museum scan; the 15 cm scale bar reads 39.8 px/cm |
| total length L | 0.46 m | female 45–58 cm (USDA FEIS) |
| span, full spread | 1.03 m, b/L 2.24 | Birds of the World female 99.7 ± 4.8 cm |
| wing root, leading and trailing edge | 0.19 L and 0.56 L behind the bill | 5 flight photos and specimen skins |
| head, body and tail widths | width profile along the body | photos 03–06 (closed tails), see `analysis/` |
| tail | 0.34 L long, about 6 cm wide closed | White 1968; Feather Atlas rectrix widths |
| joints | humerus 9.1, ulna 10.6, carpometacarpus 6.4 cm | Royal BC Museum female means |
| glide and soar angles | glide: hand swept 10° aft; soar: close to the scan shape | 2D rig fitted to 7 flight photos (`analysis/photo_fits`) |
| flapping and stoop poses | ±36° stroke; tucked width/L 0.26–0.36; M-shape b/L 1.2–1.7 | `refs/pose_spec.md` (Mills 2018, Ponitz 2014, Selim 2020) |

## Validation

The validation compares whole outlines (IoU), with every outline scaled to the same half-span. The results are in `analysis/validation/`.

| comparison | IoU |
|---|---|
| model glide vs 4 glide photos | 0.71–0.80, mean 0.78 |
| model soar vs 3 soaring photos | 0.79–0.83, mean 0.80 |
| the 11-point dart the page first used vs the same photos | 0.16–0.24, mean about 0.20 |

## Rebuilding

The files in `blender/` run inside Blender 5.2, for example through the Blender MCP. Run `exec()` on `falcon_build.py` with `PARAMS` set to `params_falcon.json`. Then run `falcon_render.py`, `falcon_measure.py` (with `POSES_PATH` set) and `falcon_sheet.py` or `falcon_beauty.py`.

`analysis/make_params.py` regenerates `params_falcon.json` from the scan and the measured profiles. Run the analysis scripts with uvx:

```
uvx --with numpy --with pillow --with scipy --with scikit-image python <script>
```

The reference images are not copied here. `refs/*manifest*.json` lists each image's URL, author and licence. The Slater Museum scans are © Slater Museum and are for reference only.

## Scoring an outline table

`analysis/score_outline.py` scores any outline table against the normalised photo masks. It fills the outline as `pushFalcon()` in the page does (both wings plus one body-and-tail polygon, nonzero rule, summed over the subpaths), then passes that raster through `silhouette.py` itself, so the outline is normalised by the same code as the photos. The score is `compare.py`'s whole-bird IoU. It reads both the page's table (`wingGlide`, `wingStoop`) and the newer `wing: { <pose>: [...] }` shape; a silhouette image in place of the json is scored the same way.

```
PY="uvx --with numpy --with pillow --with scipy --with scikit-image python"
$PY analysis/score_outline.py ../blender/falcon-outline.json glide --photo-dir MASKS --set glide
$PY analysis/score_outline.py outline/peregrine-outline.json glide --photos MASKS/03_*__norm.png [--tail-fan 0.5] [--out scores.json] [--overlay analysis/validation/x.png]
$PY analysis/make_outline_scores.py --photo-dir MASKS      # rewrites analysis/outline_scores.json
```

`MASKS` is the directory of `*__norm.png` files that `silhouette.py --skydist` wrote from the reference photos. They are not in the repository, and an `--overlay` image contains them, so keep it in `analysis/validation/` (ignored).

Results (`analysis/outline_scores.json`, raster at 1000 px per half-span):

| comparison | IoU per photo | mean |
|---|---|---|
| page outline (`blender/falcon-outline.json`, glide) vs 4 glide photos | .724, .716, .747, .652 | .710 |
| page outline (glide) vs 3 soaring photos | .718, .696, .725 | .713 |
| model glide render vs 4 glide photos | .797, .802, .804, .709 | .778 |
| model soar render vs 3 soaring photos | .828, .788, .786 | .801 |

The page's stoop outline measures 0.794 half-spans wide by 0.906 long, a width/length of 0.876. The tucked range in Ponitz 2014 is 0.26–0.36, so it is about 2.4 times too wide for a full tuck.

Limits of the method:
- The page outline's wing tip tapers to a needle, and `silhouette.py` removes anything under 3 px before measuring the span. The measured half-span, and with it the score, therefore shifts with the raster size: the glide mean is .723, .715, .710 and .706 at 250, 500, 1000 and 2000 px per half-span.
- The normalised raster covers ±1.1 half-spans, so a bird longer than 2.2 half-spans (any tucked pose) is clipped. IoU is not meaningful for stoop poses; use the width/length figure.
- The outline is scored flat (flap angle 0) and without the page's 1 px stroke.
||||||| 9edad25

## Outline export for `murmuration.html`

The page draws the falcon from a table of plan-view outlines read off this model. To regenerate everything, from the repository root:

```
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
    --python falcon/blender/export_outline.py -- --blend falcon/peregrine.blend
uv run --no-project python falcon/outline/update_page.py
uvx --with pillow --with numpy python falcon/outline/rasterise_outline.py --out /tmp/falcon-check
node murmuration-check.js murmuration.html 30 "seed=1"
```

- `blender/export_outline.py` builds the model headless from `falcon_build.py` and `params_falcon.json`, applies every pose in `poses_falcon.json` and reads the deformed vertices with Subsurf off. It writes `outline/peregrine-outline.json`. With `--blend` it also saves `peregrine.blend` in the glide pose, with materials and cameras and no actions. `--diag DIR` writes the full-resolution chains and the rig's in-between poses; `--render DIR` renders the top silhouettes.
- `outline/peregrine-outline.json` holds flat `[a, w]` pairs in full-spread half-spans (0.5143 m): `a` forward from `aOriginM` (the centroid of the gliding silhouette, 8 cm behind the shoulder line), `w` to the right. Only the right side is stored.
  - `wing`: one chain per pose, leading edge root to tip and trailing edge tip to root. Every pose uses the same 52 of the mesh's 113 edge vertices (`wingChainIndex`), so point i is the same place on the wing in every pose. The 52 are chosen to keep the worst miss over all ten poses smallest: 0.0025 half-spans, 1.3 mm.
  - `body`: the right edge from the bill tip to the rump. `tail` and `tailFan`: the tail's right edge and tip, closed and fanned, with equal counts.
  - `keys` and `knots`: the dive sequence glide, stoop_m, pullout_early, stoop_tuck, and the tuck (0 to 1) at which the page reaches each.
- `outline/update_page.py` rewrites the `FALCON` table in `murmuration.html` from the JSON.
- `outline/rasterise_outline.py` runs the page's own `pushFalcon` under node, fills what it produces with the canvas non-zero rule and scores it against `renders/silhouettes/<pose>__top.png`.

| key pose | tuck | IoU, page outline vs model silhouette |
|---|---|---|
| glide | 0 | 0.9935 |
| stoop_m | 0.38 | 0.9936 |
| pullout_early | 0.76 | 0.9916 |
| stoop_tuck | 1 | 0.9929 |

The remaining difference is a fringe one pixel wide (about 1 mm) along the edges.

Two things the measurements settled:

- **Fill rule.** Folded wings lap over themselves and over the body. The non-zero rule fills the laps; even-odd punches holes (IoU 0.73 for pullout_early). The page fills the right wing, the left wing and the body as three separate paths, because seen from the side with the wings raised the two wings wind in opposite directions on screen and cancel where they cross in a shared path.
- **Intermediate keys.** A straight vertex blend from glide to stoop_tuck never comes closer to stoop_m than 0.062 half-spans rms (IoU 0.79) or to pullout_early than 0.084 (IoU 0.73), so the page blends through all four keys. Between neighbouring keys the blend stays within 0.030 half-spans rms (0.051 at worst) of the rig moving between the same two poses.
