# Common starling model

A parametric Blender model of a common starling (*Sturnus vulgaris*) in seven flight poses. Its proportions come from measured references, and it exports plan-view outlines in the format `murmuration.html` reads (see "Outline export" below). The page draws the 15-point version (`outline/starling-low15.json`): `flap_mid` on the downstroke, blended to `upstroke` on the way up.

- `starling.blend`: the model in the glide pose. It has an armature with humerus, forearm and hand bones per wing, five feather bones per wing, and a tail with a fanned shape key. Materials and cameras are included; there are no actions and no saved UI layout.
- `renders/`: final renders.
  - `sheet_silhouettes_top.png`, `_front.png`, `_side.png`: outlines, each labelled with its measured value and target.
  - `sheet_shaded_below.png`, `sheet_shaded_above.png`: shaded renders.
  - `silhouettes/metrics.json`: the per-pose measurements.
- `outline/`: the outline table for the page, a 15-point version and the checks.

## Where the proportions come from

| quantity | value | source |
|---|---|---|
| wing planform | RMNH.AVES.259388.b, adult female, spread right wing: 17.2 cm root to tip, 87.9 cm², mean of the ventral and dorsal photographs, scaled from the ruler in frame | Naturalis Biodiversity Center (CC0). Photographs of two more wings agree on the chord distribution: RMNH.AVES.259485.b (Naturalis, CC0) and PSM 20907 (Slater Museum, reference only); see `analysis/planforms/`. |
| in-flight wing root | inner leading edge straight from the body to the wrist; trailing edge leaves the body 0.59 L behind the bill (root chord 7.8 cm, 0.39 L) | `analysis/flight_planform.py`, from the flight photos. The pressed specimen's root is cut at the skin. |
| span | 0.382 m | Ben-Gida et al. 2013 wind-tunnel bird; 37.8–38.4 cm in the literature |
| total length L | 0.20 m, bill tip to tail tip in flight | 19–23 cm published (museum lengths include a stretched neck); photo fits 18.8 and 19.8 cm on the two cleanest photos |
| span / length | 1.91 for the rest planform (1.90 as posed in flap_mid), 1.88 in the glide | 1.82 from published lengths; 2.09–2.24 from three fully spread flight photos |
| wing root on the body | leading edge leaves the body 0.20 L behind the bill; shoulder joint 0.29 L | median of 7 flight photos |
| wing area | 219 cm² including the body strip, aspect ratio 6.7 | Ben-Gida 2013 implies 228 cm², AR 6.4 (4% more) |
| body | 4.0 cm wide at most; bill 0.15 L (culmen 30 mm), 6.6 mm wide | Ben-Gida 2013; AVONET (Tobias et al. 2022) |
| tail | 65 mm, closed width 3 cm, square tip, spreads to a 50° half-angle | AVONET 65.8 mm; Feather Atlas rectrix widths (USFWS) |
| joints | humerus 28, ulna 34, carpometacarpus 21 mm; wrist 5.4 cm from the root | skeleton measurements in `refs/morphometrics.json`; specimen scan |
| poses | see the table below | `refs/pose_spec.md` (Ben-Gida 2013, Stalnov 2015, Dial 1991, Tobalske 1995 and 2011, Hedenström 2006) |

## Poses

Measured on the model (`renders/silhouettes/metrics.json`). Tip heights are taken at the wingtip against the shoulder joint.

| pose | b/L | span, share of full | tip above shoulder (cm) | tip aft of shoulder (cm) | target |
|---|---|---|---|---|---|
| glide | 1.88 | 0.99 | +1.1 | 2.9 | b/L 1.8–2.2; arm 7–11° aft as in the photo fits |
| flap_top | 1.31 | 0.69 | +12.8 | 1.7 | tip +12 to +16 cm, 1.3–2.9 cm aft |
| flap_mid | 1.90 | 1.00 | −0.2 | −0.3 | full span, chord pitched 13° down |
| flap_bottom | 0.74 | 0.39 | −14.3 | 6.1 | tip −14.5 to −16.5 cm, about 6.3 cm aft |
| upstroke | 1.03 | 0.54 | +3.0 | 7.6 | span 0.40–0.60 of full, hand swept 45–60° |
| upstroke_top | 1.15 | 0.61 | +11.2 | 3.8 | span recovering from 0.5 to 0.7 |
| bound | 0.32 | 0.17 | +0.3 | 11.3 | wings folded, span 0.12–0.20 of full |

In the bound the folded wingtips reach 0.86 L from the bill, between the tail base (0.68 L) and the tail tip. The forearm (34 mm) is longer than the humerus (28 mm), so a tightly folded wrist sits about 0.7 cm ahead of the shoulder. The tips cross the midline by 2 cm over the tail.

## Validation

The validation compares whole top-view outlines (IoU), with every outline scaled to the same half-span. The results are in `analysis/validation_scores.json`.

| comparison | IoU per photo | mean |
|---|---|---|
| model glide vs 5 glide photos (01, 02, 03, 04, 06) | .613, .606, .573, .701, .609 | .621 |
| the page's old 11-point outline vs the same photos | .695, .631, .429, .649, .482 | .577 |
| model posed with each photo's fitted wing angles | .804, .724, .624, .852, .631 | .727 |
| model flap_top vs photo 08 (top of downstroke), as posed / pose-matched | .635 / .720 | |
| the page's outline vs photo 08 | .618 | |

Unlike the falcon, the starling photos are mostly not flat, symmetric glides:
- In 01 and 04 the wings are raised. That shortens the projected span, so normalising by half-span inflates the photo's body and tail. It also favours the page's short-winged outline on 01.
- 03 is banking, with its tail yawed and fanned to one side.
- 06 carries food and has its legs down, with the tail fanned and pitched.

The pose-matched row is the fairer test of the model's shape. It poses each wing with the arm and hand angles and the foreshortening fitted to that photo (`analysis/photo_fits/`), and picks the best of four tail spreads. On the two cleanest photos it reaches .80 and .85.

The wing planform alone fits the photos with a 2D rig (`analysis/fit_pose.py`): .84 and .90 on photos 01 and 04, .67–.77 on the others.

## Outline export for `murmuration.html`

`outline/starling-outline.json` uses the shape the page's falcon table uses: flat `[a, w]` pairs in full-spread half-spans (0.191 m), right side only.
- `a` is forward from the shoulder line (model y = 0).
- `w` is to the right.
- `noseA` is 0.306 and `tailTipA` is −0.741, so the bird is 1.047 half-spans long.

| key | content |
|---|---|
| `wing.<pose>` | 113 points per pose: 57 leading-edge points from root to tip (point 56 is the leading edge at the tip station, within 0.005 half-spans of the outermost point), then 56 trailing-edge points from the tip back to the root. They are the same mesh vertices in every pose, so point i is the same place on the wing throughout. |
| `body` | 50 points, the right edge from the bill tip to the rump |
| `tail`, `tailFan` | 18 points each, closed and fully fanned, with equal counts; `tailFanOfPose` gives each pose's spread |

Filled with the non-zero rule (both wings and the body as separate paths), the table matches the model's top silhouettes with IoU 0.9935–0.9963 in every pose (`outline/check.json`).

To draw the table with the page's `wp()`, `a` and `w` must share one unit, so `len = span / 2`. Before this model the page used `SPAN = 1.3, LEN = 1.05`. Its 11-point polygon ran from a = +0.5 to −0.62, so it drew a span/length of 1.3 / (1.12 × 1.05) = 1.10, where the measured value is 1.91.

`outline/starling-low15.json` is a 15-point whole-bird polygon per pose: the nose, then seven right-side points mirrored. The vertices start on the nose, neck, wing leading-edge root, wrist (leading edge), tip, wrist (trailing edge), trailing-edge root and tail corner. A Nelder–Mead fit then moves them to maximise IoU against the full outline, with no self-crossings, no point past the midline, every point within 0.02 half-spans of the bird's bounding box, and a small perimeter cost. The perimeter cost keeps zero-area slivers out, because they would show under a 1 px stroke.

| pose | glide | flap_top | flap_mid | flap_bottom | upstroke | upstroke_top | bound |
|---|---|---|---|---|---|---|---|
| IoU vs full outline | .959 | .951 | .950 | .969 | .913 | .925 | .943 |

`outline/starling-low13.json` drops the neck vertex (13 points); its IoUs are in the file, .909–.955.

## Rebuilding

```
uvx python starling/build_all.py [--refs DIR] [--blender PATH]
```

This runs Blender 5.2 headless (`--background --factory-startup`) through `blender/run_headless.py`. It regenerates, in order:
1. `blender/params_starling.json`, from `analysis/make_params_starling.py`.
2. The silhouettes, the shaded renders and the outline table.
3. `starling.blend`.
4. The 15- and 13-point outlines and the contact sheets.
5. With `--refs` pointing at the normalised photo masks, the validation.
6. The page's embedded bird tables, via `node murmuration-assets.js --write`.

Run `node murmuration-assets.js` from the repository root to check that the page
uses the current `flap_mid`, `upstroke`, `glide` and `bound` shapes from
`outline/starling-low15.json` and the current peregrine dive keys. The page's
wingbeat (10–14 Hz) blends `flap_mid` and `upstroke`. Between bursts of 10–16 beats
each bird pauses for 0.5–1 s in `glide` or `bound`, following the flap-glide-bound
schedule in `refs/pose_spec.md` (RA01 Table 1, TO95). The share of bounds rises with
speed; that trend is from TO95, but the numbers are an estimate. Frightened birds
flap without pausing. The schedule changes only the drawing, not the flight model.

The Blender scripts are species-neutral copies of the falcon's: `bird_build.py`, `bird_render.py`, `bird_measure.py`, `bird_sheet.py`, `bird_beauty.py` and `bird_outline.py`. Their falcon-scale constants became parameters with the falcon's values as defaults, and the builder reproduces every falcon metric. `starling_look.py` holds the plumage, and `bird_tune.py` measures a batch of candidate poses in one run.

The analysis scripts run with uvx:

```
uvx --with numpy --with pillow --with scipy --with scikit-image python <script>
```

The reference images and photo masks are not copied here. `refs/*manifest*.json` lists each image's URL, author and licence. The Slater Museum images are © Slater Museum and were used for reference only; only measurements taken from them are stored here. Pose targets are in `refs/pose_spec.md`, morphometrics in `refs/morphometrics.json`.

## Limits

- **Length.** The flight length L is the least certain number: span/length is 1.82 from published lengths and 2.09–2.24 from the fully spread photos. 0.20 m sits between them.
- **Estimated pose details.**
  - The glide's 6° dihedral and each pose's tail spread are estimates.
  - The upstroke poses rest on a robin proxy (Hedenström 2006) and on Dial 1991.
- **Validation photos.** The photo validation rests on five glide photos of mixed quality. 05 was dropped because its body axis is tilted in the frame (12–15°).
- **Plumage.** The plumage is a winter adult reduced to a few shader rules: glossy black, pale spangles, buff feather tips and a grey-brown underwing.
