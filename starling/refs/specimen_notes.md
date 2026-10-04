# Starling (Sturnus vulgaris) specimen references: methods, numbers, conflicts

Generated 2026-10-03. Collected and measured only; nothing built. All paths are relative to the specimen
reference folder, which is kept outside the repository (only these text files are copied here). Machine-readable results: `manifest.json` (every image, licence, scale, verification),
`morphometrics.json` (every number with unit, n or range, source and confidence), `derived/planform_stats.json`.

## 1. What is here

| folder | content | licence / use |
|---|---|---|
| `slater/` | 8 Slater Museum wing scans (4 birds x dorsal + ventral), 2048x1396, + IIIF info.json | (c) Slater Museum via JSTOR Shared Collections. **Reference-only, do not publish** |
| `naturalis/` | 13 Naturalis RMNH study-skin / spread-wing photos (GBIF media) incl. 4 spread wings with ruler | CC0 1.0 (GBIF licence field). Publishable |
| `featheratlas/` | 6 USFWS Feather Atlas scans (primaries, secondaries, tail; adult female + juvenile male) + `starling_records.json` (data table) | free to use, credit USFWS Forensics Lab (FAQ wording in manifest) |
| `other/` | 3 Concordia College skin photos (D/V/LS, 10-cm bar), 1 Rijksmuseum engraving | CC0 per GBIF/Commons, but the Concordia bar text says "copyright reserved": treat as reference-only until the museum confirms |
| `derived/masks/` | binary wing masks (white wing on black), 8 Slater + 4 Naturalis | derived from the above (Slater masks are reference-only too) |
| `derived/overlays/` | red outline on the photo (blue = excluded zone: ruler, chart, label card) | idem |
| `derived/planform_stats.json`, `planform_contours/` | per wing: L, area, chords, 41-station outline, ~400-pt (s,n) contour in cm | idem |
| `derived/crosscheck.json` | Slater vs Naturalis, published AR / wing loading | |
| `derived/published_sources/` | AVONET starling rows + per-sex stats, BirdWingData starling rows, text of the Ben-Gida / Stalnov / HANZAB sources | |
| `derived/zoom/` | every zoom crop used for verification (file name carries the box) | |
| `derived/*.py`, `run_planform_all.sh` | all scripts (run with `uvx --with numpy --with pillow --with scipy --with scikit-image python <script>`) | |
| `derived/skin_candidates.json`, `overlays_skin/`, `skin_*` | study-skin search + landmark/scale work by a helper agent (details, leads not downloaded) | |

## 2. Best spread-wing scan

**PSM 20907 dorsal** (`slater/PSM20907_male_dorsal.jpg`, JSTOR item 20907a, adult male, Washington, JSTOR record date 2009-04-21, month "Oct").
It is the only Slater starling that is an adult with no moult note. Mask: `derived/masks/PSM20907_male_dorsal_mask.png`; overlay
`derived/overlays/PSM20907_male_dorsal_overlay.jpg` (zoom-checked at the primary tips, the trailing edge, the leading edge and the root).

* Scale **123.36 px/cm** (49 tick edges of the 5-cm bar, code); block pitch 123.66; lens-model centre scale 129.3 (model, see 3.2).
  Bar read on the original at **3.0x and 9.9x**; label "PSM 20907" read at 3.3x, caption at 3.1x.
* Root: centroid of the proximal 4 % of the x extent = px [74.1, 649.1] in the 2048x1396 original (`root_point_px_original`). There is **no anatomical cut**; the proximal end is the shoulder/down-feather mass.
* Planform (bar scale / lens-model scale): root-to-tip L **15.69 / 15.36 cm**, area **85.5 / 80.3 cm2**, mean chord 5.45, **max chord 7.49 cm at 0.275 L**,
  **leading edge most forward at 0.10 L** (3.50 cm above the tip line; the leading edge stays within 3 % of L of that height over a flat top, range in JSON), wing-only AR (2L^2/A) 5.75.
* **Better CC0 alternative for absolute size**: Naturalis RMNH.AVES.259388.b (adult female) and 259485.b (male), mask + stats in `derived/`, ruler-verified.

## 3. Methods

### 3.1 Slater access
JSTOR Shared Collections "Wing and Tail Image Collection" (University of Puget Sound). Collection search through the logged-in Chrome tab, images from JSTOR's
IIIF server (width 2048 is the maximum served). Eight starling items (4 birds x a/b); **no tail items** for the starling. Item metadata read from the JSTOR item pages:

| item | specimen | sex | JSTOR description |
|---|---|---|---|
| 36061839 | 20907a | male | above; adult |
| 36064393 | 20907b | male | adult; no moult |
| 36064394 / 36064396 | 21188a / b | male, May | outer primaries sheathed at base; tail sheathed at base |
| 36064401 / 36064392 | 20462a / b | female, Jul | moult scores on P1, P5, P6, S1, S8, tail; body moult heavy |
| 36064397 / 36061840 | 23166a / b | female, Jul | P4-P9 still growing (a); b = below |

### 3.2 Scale (code, then zoom)
Each frame carries a ~5 cm black/white bar with 1-mm ticks and 1-cm blocks labelled "1 cm". `scale_bar.py` finds the bar and fits the tick edges (rising and falling edges
separately, 2 mm pitch each) and the block edges. **The tick pitch is not constant along the bar: it grows 4-7 % from the left end to the right end in all 8 frames** (always towards the frame centre = barrel-like lens distortion).
The wing lies nearer the centre, so the bar mean under-reads the local scale. `lens_model.py` fits a one-parameter radial model (principal point at the frame centre) per frame to the measured local pitch and gives a centre scale s0.
**Report both**: the bar mean is measured; s0 is a model-dependent sensitivity estimate (lengths 2-5 % smaller, areas 4-10 % smaller).

| frame | bar tick px/cm | bar block px/cm | local pitch left -> right (px/cm) | model centre px/cm | tick fit rms px |
|---|---|---|---|---|---|
| PSM20462_female_a | 139.27 | 139.64 | 135.5 -> 142.7 | 144.2 | 1.50 |
| PSM20462_female_b | 132.79 | 133.04 | 128.9 -> 136.4 | 138.3 | 1.58 |
| PSM20907_male_b | 119.52 | 119.83 | 115.7 -> 123.2 | 125.8 | 1.60 |
| PSM20907_male_dorsal | 123.36 | 123.66 | 119.5 -> 127.0 | 129.3 | 1.55 |
| PSM21188_male_a | 137.22 | 137.56 | 134.1 -> 140.1 | 141.5 | 1.30 |
| PSM21188_male_b | 137.51 | 137.87 | 134.4 -> 140.4 | 141.6 | 1.26 |
| PSM23166_female_a | 152.44 | 152.74 | 149.5 -> 155.1 | 155.9 | 1.20 |
| PSM23166_female_ventral | 152.64 | 152.90 | 149.8 -> 155.1 | 155.9 | 1.12 |

All eight bars were read on the original with the zoom tool at 2.5x to 3.2x (20907 dorsal also at 3.0x and 9.9x): five equal 1-cm blocks, 1-mm ticks, "1 cm" label, as assumed.

### 3.3 Segmentation
`segment_wings.py` (Slater): Lab colour, 2nd-order polynomial background fitted on pixels that are not wing / bar / label, wing = chroma shift (>= 3.6) OR luminance drop (>= 22); the chroma criterion separates the soft cast shadow from the feathers.
The four ventral frames also use a brightness criterion (pale feather margins). PSM 21188 b: a bay in the trailing edge (pale feather margins close to the background) is closed locally (x 400-700, y 850-1180, disc r=30); overlay checked at 3.3x.
`segment_naturalis_wings.py`: same idea; the cream-background frames (259485) use chroma >= 8 OR luminance drop >= 34 because a looser threshold swallowed the cast shadow (8-20 px halo at the leading edge, seen at 5.0x); after tightening the halo is 1-3 px. Ruler, colour chart and label cards are excluded zones (blue in the overlays).
Mask edges were zoom-checked: 20907 dorsal (tips, notches, root, trailing edge), 21188b trailing edge 3.3x; Naturalis primary tips and notches at 5.0x-6.2x.

### 3.4 Planform definitions (`planform_stats.py`)
Every wing is mirrored (when the tip points left) into a **dorsal-view right wing: tip to +x, leading edge up**. Root point R = mean of the mask pixels in the proximal-most 4 % of the x extent (Slater) or along the root-to-tip axis (Naturalis, oblique wings).
Tip T = mask point farthest from R. s along R->T, n perpendicular (+ toward the leading edge). L = |RT|. Slice extent chord and area-based chord at 41 stations; leading-edge apex = station with the largest n (excluding the inner 5 %); area from a 0.2-mm raster of the contour; AR_wing_only = 2L^2/A (the wing without the body gap).
Chord = extent of the mask along n, so it includes the notches between the primary tips and over-reads on the drooped distal wing.

### 3.5 Feather Atlas
800-px web scans (largest served; originals ~9600 px per the falcon notes), black background, grid labelled 0-2-4 cm with one cell = 1 cm. Scale from periodic fitting of the grid lines (`atlas_scale.py`), axis labels read on zoom crops (3.98x).
Secondary adult: the grid is hidden by feathers, scale from the horizontal lines in the two side margins (9 lines = 8 cm). Per-feather dimensions from the image: `atlas_feathers.py`.
Table values (TF total incl. calamus, VF vane; BRD 2881 adult female breeding plumage HY/SY, BRD 2880 juvenile male Wisconsin) are in `featheratlas/starling_records.json` and `morphometrics.json`.

### 3.6 Naturalis and other skins
Naturalis scales: TE263 chart mm ruler (0-180 mm) in the 259485 frames, Naturalis 1-cm bar frames for 259388. **Re-verified by the lead on the original**:
259485.a dorsal ruler 0 and 180 mm at 5.0x/5.5x = 89.16 px/cm; 259485.b ventral at 5.0x/5.5x = 88.36 (code baseline extent 88.39; the helper's tick fit 89.15 was 0.9 % high and is replaced);
259485.b dorsal 88.61 (code); 259388.a dorsal and 259388.b dorsal long ticks 1 cm apart at 4.6x / 4.5x = 69.2 / 69.1 px/cm. Species/sex/number labels read at 2.8x (259485.a) and 4.1x (259388.a).
Concordia EWOC_0396 bar 0 and 10 cm lines read at 5.0x at both ends = 161.97 px/cm. RMNH.5070087 has no ruler (cutting-mat grid, 1 cm presumed, **unverified**).
All scales are valid in the ruler plane only; the skin top is 2-3 cm above it (a few % magnification).

## 4. Planform results (cm; bar scale / lens-model scale where both exist)

| wing | sex | view | px/cm (bar) | root-to-tip L | area (one wing) | max chord @ frac of L | LE apex frac | AR wing-only |
|---|---|---|---|---|---|---|---|---|
| PSM20907_male_dorsal | male | dorsal | 123.36 | 15.69 / 15.36 | 85.5 / 80.3 | 7.49 @ 0.28 | 0.10 | 5.75 |
| PSM20907_male_b | male | ventral | 119.52 | 16.37 / 16.01 | 91.1 / 85.1 | 7.80 @ 0.23 | 0.20 | 5.88 |
| PSM20462_female_a | female | dorsal | 139.27 | 14.29 / 14.10 | 75.0 / 72.0 | 7.27 @ 0.17 | 0.12 | 5.44 |
| PSM20462_female_b | female | ventral | 132.79 | 15.11 / 14.88 | 80.9 / 77.0 | 7.71 @ 0.17 | 0.17 | 5.64 |
| PSM21188_male_a | male | dorsal | 137.22 | 13.75 / 13.56 | 75.0 / 72.1 | 7.21 @ 0.12 | 0.10 | 5.04 |
| PSM21188_male_b | male | ventral | 137.51 | 14.26 / 14.09 | 78.3 / 75.6 | 7.45 @ 0.12 | 0.12 | 5.19 |
| PSM23166_female_a | female | dorsal | 152.44 | 12.01 / 11.90 | 61.7 / 60.1 | 6.92 @ 0.20 | 0.15 | 4.67 |
| PSM23166_female_ventral | female | ventral | 152.64 | 12.42 / 12.31 | 64.8 / 63.2 | 6.95 @ 0.20 | 0.18 | 4.76 |
| RMNH259388b_dorsal | female | dorsal | 69.10 | 17.34 / - | 87.2 / - | 8.39 @ 0.28 | 0.28 | 6.90 |
| RMNH259388b_ventral | female | ventral | 69.10 | 17.33 / - | 89.1 / - | 8.62 @ 0.17 | 0.20 | 6.74 |
| RMNH259485b_dorsal | male | dorsal | 88.61 | 16.73 / - | 85.2 / - | 8.81 @ 0.25 | 0.25 | 6.57 |
| RMNH259485b_ventral | male | ventral | 88.39 | 16.89 / - | 86.8 / - | 8.46 @ 0.25 | 0.28 | 6.57 |

Moult state matters: only 20907 (a, b) is complete. 23166 (P4-P9 still growing) and 20462 (moulting) are short and blunt; 21188 has sheathed outer primaries. Do not use 23166 for L or AR.
Normalised 20907 dorsal: area/L^2 = 0.348, max chord/L = 0.478, max chord at 0.275 L, leading edge most forward at 0.10 L.
Naturalis wings are slimmer (area/L^2 0.29-0.30) because L includes more shoulder mass; use the distal outline (primaries, secondaries) for shape, not AR_wing_only.

## 5. Published numbers (summary; full list with sources in morphometrics.json)

| quantity | value | source (details in JSON) | confidence |
|---|---|---|---|
| total length | 21 cm (19-23; Audubon 20.6-23.1, ADW 21.5) | Audubon, ADW, Wikipedia/Feare & Craig | medium |
| wingspan | 38 cm (36-42); live bird 38.2; five literature rows 37.8-38.4 | Ben-Gida 2013; BirdWingData rows | medium |
| wing length (carpal joint to longest primary) | 129.0 +- 2.7 mm male (n=17), 127.3 +- 2.3 female (n=11) museum; live adults 131.3 +- 3.5 (n=32774; male 132.6, female 129.5) | AVONET raw rows; BTO | high |
| Secondary1 / Kipp's / hand-wing index | 79.1 mm / 49.2 mm / 38.4 | AVONET | high |
| tail | 65.8 +- 4.3 mm (60-75, n=16; male 65.2, female 67.1 n=5); HANZAB 59-68 | AVONET, ABSA/HANZAB | high |
| culmen | 30.2 +- 2.2 mm (26.1-34.0, n=16) | AVONET | high |
| tarsus | 29.0 +- 1.4 mm (n=16) | AVONET | high |
| mass | 80 g (70-100): BTO adults 85 +- 9.9 (male 87, female 82.5), AVONET 77.1 (Dunning), wind-tunnel bird 78 | BTO, AVONET, Ben-Gida | medium |
| wing area, two wings | 229 cm2 (205-250); rows 192-282 | BirdWingData, Ben-Gida (implied) | medium |
| aspect ratio | 6.4 (live bird), 5.6-6.4 from rows | Ben-Gida, BirdWingData | high / medium |
| wing loading | 30-37 N/m2 (Ben-Gida bird 33.6) | derived | medium |
| humerus / ulna / radius / carpometacarpus (GL) | 28 / 34 / 29 / 21 mm (one male, whole mm) | Balyan et al. 2024 | medium (n=1) |
| cranium | 50 mm long, 20 mm wide (skeleton) | same | medium (n=1) |
| lateral body width | 4 cm (one live bird) | Ben-Gida 2013 | medium |

## 6. Conflicts and doubts

1. **Wing length**: AVONET museum skins 128.3 mm (folded wing) vs BTO live adults 131.3 mm (male 132.6): +3 mm. Method difference (flattened/straightened wing on live birds); HANZAB (Australia) is 119-130. Use 129-132 for a flattened wing.
2. **Mass**: AVONET 77.1 g (a reference value from Dunning, not from the specimens), Ben-Gida bird 78 g, BTO UK adults 85 g (male 87). The UK ringing mean includes winter fat. Wikipedia 58-101 g. Use ~80 g.
3. **Wingspan**: ADW 40.0 and Vagasi 2016 (A-II) 42.4 cm are high next to five rows 37.8-38.4 and the measured live bird 38.2; Vagasi B-II is 35.9 (body gap excluded). Viscor 1987 is an outlier in AR (7.96) and area (192).
4. **Scan wing area vs published**: two wings of the scans = 171 (Slater 20907) to 178 cm2 (Naturalis female), 22-25 % below the published 229 cm2. The isolated wing misses the root region between the shoulder joint and the body side (guess 10-12 cm2 per wing) and the dried feathers do not fan out as in flight. Use the published area as the size target and the scans for shape.
5. **Slater scale**: the bar pitch drifts 4-7 % along the bar; bar mean vs lens-model centre scale differs 3-5 % (lengths) and 6-10 % (areas). Independent check: single-wing area of the Naturalis wings (ruler verified, 85-89 cm2) equals the Slater 20907 area at the bar scale (85.5), not at the lens-model scale (80.3); this favours the bar scale, but is one comparison.
6. **Root definition**: no anatomical cut. Dorsal and ventral L of the same bird differ by 4 % (20907: 15.69 vs 16.37 cm) and the Naturalis wings (L 16.7-17.3) keep more shoulder mass than Slater (15.7). L and AR_wing_only are therefore not comparable across sources; the half-span from the body side of the live bird is (38.2-4)/2 = 17.1 cm.
7. **Wrist**: not located reliably. An earlier estimate on the Naturalis ventral frames (junction where the stiff leading-edge shaft ends) was wrong by ~3 cm (it marks where the primary coverts hide the primary shaft) and was discarded. For Slater 20907 dorsal the alula base is at 0.28 L (+-30 px): alula-base-to-tip 11.7 cm (bar) / 11.2 (lens), so wrist-to-tip is roughly 11.7-12.7 cm, which brackets the published 12.4-13.4 cm; this is not an independent scale check. I had first read the 11.2 cm as a 12 % shortfall; that reading was wrong (alula base is not the carpal joint).
8. **Moult and age**: JSTOR notes show 3 of the 4 Slater birds are moulting or growing feathers; their L and AR are biased low. Naturalis 259388.b is a GBIF-adult female, 259485.b a male of unstated age.
9. **Pressed dried wing is not the in-flight shape** (no camber, feathers not fully fanned, flat); the in-flight aspect ratio is 6.4 for the live bird vs 5.75 wing-only for the scan.
10. **Single-individual sources**: Ben-Gida bird (78 g, span 38.2, AR 6.4, body width 4 cm; Stalnov 2015 reuses the same bird, not independent), Armenia bones (one male, whole-mm values, locality Masis, subspecies unstated and probably not the nominate form), skullsite skull (provenance unknown).
11. **ABSA/HANZAB sheet has a typo**: female "THL 51.9 - 30.5 mm" (30.5 cannot be the upper bound). The tail and wing rows were used; THL was not.
12. **Skins**: necks extended (bill-to-tail 19.6-23.1 cm vs live 19-23 with neck retracted); tails often fanned, so the tail tip is partly estimated; shoulder proxies low confidence. GBIF "preparations" fields for RMNH.AVES.259388 a/b look swapped (a = whole skin, b = spread wing; the images were trusted).
13. **Naturalis 259485.b dorsal**: label card covers part of the leading edge near the wrist; area and leading edge there are under-estimated. The ventral frame is complete.
14. **RMNH.5070087 scale** (cutting-mat grid) unverified; Concordia bar text "copyright reserved" conflicts with the CC0 licence field.
15. AVONET: the wing/tail/culmen rows come from museum skins of unstated subspecies and region; only 16 of 28 rows have tail and culmen values.
16. Tail and secondary lengths in the Feather Atlas are from one adult female (breeding plumage, HY/SY) and one juvenile male only.

## 7. Not found
Live head width / depth; live maximum body width and depth; bone lengths from a second source; Slater tail scans (none exist for the starling); an articulated skeleton photo with scale (CC0 or CC BY);
wing area by sex. Leads that were not followed (BOW paywall not bypassed, Feare & Craig book, Svensson, Nudds 2007, Swaddle & Lockwood 2003, other open skins) are listed in `morphometrics.json` -> `unverified_leads` and `manifest.json` -> `leads_not_downloaded`.

## 8. Which file to use for what (advice to the modeller)
* Wing outline / shape: Naturalis RMNH.AVES.259388.b ventral and dorsal (adult female, CC0) and 259485.b ventral (male, CC0); Slater 20907 dorsal as the cross-check (reference-only).
* Absolute sizes: published numbers in section 5 (span 38 cm, wing length 129-132 mm, tail 65 mm, culmen 30 mm, mass 80 g, wing area 229 cm2, AR 6.4), not the scans.
* Primary/secondary/tail feather lengths and widths: Feather Atlas table (`featheratlas/starling_records.json`) and `derived/atlas_feather_dimensions.json`.
* Body: skins are stretched; use `measured_study_skins` only for the trunk/head/tail proportions along the body axis.
