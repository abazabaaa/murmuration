# Peregrine falcon model

A parametric Blender model of a peregrine falcon (*Falco peregrinus*). Its proportions come from measured references, so that `murmuration.html` can later use its outline in place of the 11-point dart.

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
| the dart currently in `murmuration.html` vs the same photos | 0.16–0.24, mean about 0.20 |

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
