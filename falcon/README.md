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
