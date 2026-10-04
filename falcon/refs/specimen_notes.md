# Peregrine Falcon (Falco peregrinus): scaled reference notes

Machine-readable companions: `morphometrics.json` (every value with source + confidence), `manifest.json` (every image: URL, terms, scale),
`derived/` (measurement scripts, masks, planform outlines), `featheratlas/peregrine_records.json` (atlas length tables).

## 1. What was actually found (and what was not)

| Source | Result |
|---|---|
| USFWS Feather Atlas | The atlas now lives at `fws.gov/lab/featheratlas/` (not featheratlas.org). It has **no spread-wing or spread-tail scans**: each scan lays out individual feathers (10 primaries, 12 secondaries, 6 rectrices of the RIGHT wing/tail, dorsal) over a labelled 2-cm grid. 10 peregrine scans (adult female, adult male [incomplete], juvenile male) downloaded, plus the atlas length table (total feather length and vane length per feather). Largest copy served is 800 px wide (~17.8 px/cm for primaries); full-res on request only (FAQ gives featheratlas@fws.gov; I did not email). |
| Slater Museum wing/tail collection | **Exists and is the best find.** Moved to JSTOR (Sep 2024). 9 peregrine items: 4 specimens x (dorsal + ventral) spread wings + 1 fanned tail, each with a 15-cm bar (1-cm blocks, 1-mm ticks). Pulled the IIIF "full" rendering (2048x1398, the max stored). Specimens are Washington State, imaged 2009. |
| Other | Naturalis study skin ZMA.AVES.43803 (dorsal/ventral/lateral, no scale), Erxleben skeleton lithograph (no scale), two near-planform ventral flight photos (CC BY 2.0 / CC BY-SA 3.0, no scale; used for dimensionless ratios only). No other scaled spread-wing/flat-skin set was found on Commons. |

Not obtained: Birds of the World / BNA text (paywalled; only search-excerpt values, flagged "snippet"), Tucker 1998 and Tucker et al. 2000 (publisher 403 / abstract only), AVONET (bot-challenge on figshare). I did not try to bypass any of these.

## 2. Scale calibration (the part to trust or doubt)

* Slater: every frame carries a 15-cm bar. Blocks = 1 cm (label "1 cm" sits in one white block), ticks = 1 mm. Checked by eye at 5.0x (PSM 21186, box 20,1280-420,1345) and 11.0x (PSM 19885, box 20,1280-200,1340): 10 ticks per block, label inside one block. Pitch measured by code from tick and block edges: PSM 21186 49.87 px/cm, PSM 19885 38.34, PSM 22483 39.82, PSM 22661 39.53, tail PSM 23894 47.87. **Scale differs per specimen** (camera moved) so never reuse one value.
  Uncertainty about +/-0.5% from the bar; the wing sits a few mm above the bar plane, so feather-scale lengths may read 1-3% high.
* Feather Atlas: grid lines every 2 cm, axis labels every 4 cm; px/cm from the line pitch (female primaries 17.84, female tail 26.55, juvenile tail 22.94, etc.; see manifest). Atlas lengths (e.g. P9 = 27.4 cm) are measured along the curved rachis, so they run ~3% above a straight pixel measure.

## 3. Specimen metadata

Side is not stated by JSTOR; I derived it from morphology (leading edge on top: tip on the right = right wing, tip on the left = left wing, dorsal view).
PSM 21186 male, RIGHT, dorsal "above" + ventral "below". PSM 19885 female, LEFT. PSM 22483 adult female, RIGHT (JSTOR does not say above/below; a = dorsal, b = ventral by appearance). PSM 22661 female, LEFT. PSM 23894 female tail, hatch-year 1993, 12 rectrices pinned flat. Feather Atlas: BRD 2889 adult female (Jackson Co. OR), BRD 1802 juvenile male (Clatsop Co. OR), BRD 1313 adult male (OR; two primaries and several rectrices missing).

## 4. Measurements from the scans (derived/, details in morphometrics.json)

Dorsal wings, root-to-tip along image x (root = median edge of the cut end; includes scapulars):

| specimen | semi-span (cm) | one-wing area (cm2) | mean chord (cm) | AR wing-only (2L2/A) | max chord excl. inner 10% (cm, / L) |
|---|---|---|---|---|---|
| 21186 male R | 36.9 | 416 | 11.3 | 6.56 | 16.8, 0.454 |
| 19885 female L | 47.9 | 647 | 13.5 | 7.08 | 18.5, 0.387 |
| 22483 female R | 46.8 | 597 | 12.8 | 7.34 | 17.7, 0.378 |
| 22661 female L | 46.0 | 606 | 13.2 | 6.99 | 17.4, 0.377 |

Chord/semi-span at span fraction 0.05 / 0.3 / 0.5 / 0.7 / 0.9 (4 wings, M first): 0.46,0.40,0.31,0.27,0.17 | F: 0.38-0.40, 0.35-0.38, 0.30-0.31, 0.24-0.27, 0.14-0.16. 41-point leading/trailing-edge outlines per wing are in `derived/planform_stats.json`.
Chord = vertical mask extent, so it over-reads on the drooped distal wing (about 5-10% at the tip region). The root includes scapulars/tertials.

Cross-checks that make me trust the scale: 2 x one-wing area = 832 cm2 (male) vs published S = 897 cm2 incl. body; females 1194-1294 vs 1183 (large females); implied wingspans (2L + ~10 cm body) are 83 cm (M; BOW 87.1 +/-5.5) and 102-106 cm (F; BOW 99.7 +/-4.8), i.e. within about 1 SD. The scan chord (female 17.4-18.5 cm) is close to BOW "wing width" 16.9 +/-0.6 cm, though BOW's definition is not visible.
The male specimen has a short arm relative to its hand (semi-span 36.9 vs longest primary ~25 cm); it may not be fully extended. For a base planform I would use PSM 22483 (right female, cleanest outline, no scapular bulge distortions).

Fanned tail PSM 23894: bounding box 41.2 x 22.5 cm, 562 cm2, outer-tip angular span ~162 deg: an **artificial flat fan**, not an in-flight maximum. Feather tips 19.5-22.3 cm from the base blob centroid (embedded bases included); central pair shorter (~16.5 cm).
Closed-tail width: no published value. Two central rectrices side by side = 2 x max vane width of R1 = 5.8 cm (juvenile male) to 6.5 cm (adult female), from Feather Atlas widths (female R6..R1: 3.21, 3.32, 3.76, 3.79, 3.78, 3.24 cm). Natural fanned width is geometry only (2L sin(theta/2)); I found no measured value.

## 5. Published morphometrics (full list with citations in morphometrics.json)

* Total length: male 36-49 cm, female 45-58 cm (USDA FEIS; same figures in BOW ID snippet); species 34-58 (Wikipedia).
* Wingspan: anatum male 87.1 +/-5.5 (n=11), female 99.7 +/-4.8 (n=14), pealei female 103.5 +/-6.4 (BOW, snippet); Mills et al. 2019 Table 1: 87.3 / 98.4 cm; species 74-120 cm.
* Folded wing chord (White 1968, Auk 85:179, tundrius): male 292-330 (mean 308.3, n=64) mm, female 331-368 (351.8, n=62); nominate male 285 +/-10.4 (BOW appendix snippet). Tail (White 1968): male 140.5 (134-154), female 167.8 (138-180) mm; tarsus 44.3 / 49.8 mm.
* Mass: male 610.9 g (n=12) / female 952 g (n=19) (White 1968); 528 / 771 g (Mills 2019); FEIS ranges 500-994 / 750-1398 g.
* Wing area (both wings + body): male 8.97 dm2, female 11.83 dm2; AR = b2/S: 8.49 / 8.18 (Mills 2019 Table 1, compiled from Pennycuick, Hedenstrom, Tucker et al. 2000 and others).
* Wing loading (BOW snippet): calculated 0.52 (M) / 0.66 (F) g/cm2.
* Bones (Royal BC Museum, n=10/sex, mm, mean): humerus 77.2 M / 90.9 F; ulna 89.8 / 105.7 (female upper range 122.4 looks like an outlier); radius 83.1 / 97.1; carpometacarpus 55.4 / 63.9; skull length 65.2 / 70.9; skull width M 36.7-38.9, F 39.2-42.3 (page's female mean 37.06 is outside its own range, so ignore it).
* Ponitz et al. 2014: investigated falcon 0.5 kg; life-size model frontal projection area 123 cm2, top-view area 411 cm2, characteristic length 0.4 m.
* Head width (soft tissue), body width, tail width: not published in anything I could read. Ventral flight photos give shoulder width ~0.23 x total length (about 10 cm on a 45-cm bird; Ponitz frontal area implies a 12.5-cm equivalent diameter including head/legs).

## 6. The five ratios

| ratio | value to use | range | basis |
|---|---|---|---|
| wingspan / total length | 2.0 (spread) | 1.9-2.3; 1.7 for a swept glide | BOW span / FEIS length: M 2.05 (1.78-2.42), F 1.94 (1.72-2.22); Mills spans: 2.05 / 1.91; Peale's (Wikipedia) 2.24 / 2.36; flight photos A,B projected 1.97 / 1.71 (swept wings) |
| tail / total length | 0.34 | 0.30-0.38 | White 1968 tail / FEIS length: M 0.33 (0.29-0.39), F 0.33 (0.29-0.37); Selim et al. 2021 "just over a third"; photo visible tail 0.39-0.44 includes undertail coverts, so over-reads |
| max wing chord / semi-span | 0.38 of root-to-tip, 0.34 of b/2 | 0.38-0.45 (scans); 0.33-0.34 (BOW wing width / (b/2)) | scans at 0.05-0.30 span; male 0.45 is a short-armed specimen |
| leading-edge root from bill tip / total length | 0.19 | 0.17-0.22 | ventral flight photos A 0.17, B 0.20; skins 0.18 (dorsal), 0.21 (ventral). Trailing-edge root at 0.56-0.61, so root chord is ~0.40 x length |
| hand-wing / total wing length | 0.66 | 0.63-0.72 | wrist at leading-edge apex in 3 scans: 0.65, 0.70, 0.72; published wing chord vs humerus+ulna (RBCM): 0.64-0.67 |

How the fractions were measured: bill tip to tail tip is the axis; fractions are projections on it. Flight photo A read at 3.4x (crop 580,490-1160,790), B at 1.8x (440,700-1540,1100) and 5.5x (560,720-820,1080); skin ventral crop at 2.65x. Tip positions of the wings (for projected span) were read from the full frame, +/-10 px on ~1000-1700 px. Perspective and banking add roughly +/-0.03 to the fractions.
Hand-wing definition: wrist (carpal joint) to tip of the longest primary; "total wing" is root-to-tip. Longest primary feather (P9, female atlas record) is 27.4 cm = 0.57-0.60 of the female root-to-tip semi-span; P10 is 94% of P9, P8 99%; secondaries 13.5-15.9 cm. Wing formula and feather lengths are in `featheratlas/peregrine_records.json`.

## 7. Caveats worth knowing before modelling

1. Subspecies and sex mix: Slater birds are Washington (anatum or pealei), White 1968 is tundrius, BOW appendix values are nominate. Use sex-specific numbers inside one source where possible.
2. The planform is a pressed, dried wing. Real in-flight wings have camber, dihedral and a more swept hand; use the chord profile for proportions, not for the 3D wing shape.
3. All Slater images are (c) Slater Museum, shared via JSTOR; treat as reference material and check JSTOR terms before redistributing. Feather Atlas is free to use per its FAQ. Commons images carry CC licences listed in manifest.json.
4. `derived/build_outputs.py` regenerates the JSON files; masks and overlays (`derived/slater_dorsal_mask_overlay.jpg`) show what was segmented.
