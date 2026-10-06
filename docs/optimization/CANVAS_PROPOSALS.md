# Canvas and draw-path optimization proposals

Scope: source-led triage for the dirty milestone worktree at
`~/prj/murmuration-milestone`, branch
`codex/first-milestone-20261005`, based on `0d3078f`. The page reviewed here is
`murmuration.html` SHA-256
`d24849dffb2feb6882cece1fa00f56852a5d22f3ddd840559ecd4e05aacf8646`.
This note adds proposals only; it changes no product source.

## Evidence boundary

**Verified:** in the recorded Node 20.20.1 / native Canvas 0.1.100 fixture
(2048×1217 CSS, DPR 2, seed 1, calm, N=400, warm 20, 120 measured calls), the
contour renderer changed draw median/p95 from 17.272/20.437 ms to
7.544/11.450 ms. Physics medians were 1.645/1.553 ms. Raw records are
`docs/verification/performance-before.json` and
`docs/verification/performance-after.json`, summarized in
`docs/FIRST_MILESTONE.md`. This is isolated native Canvas function timing; it
does not establish Chrome frame rate. Browser automation was blocked by the
security-policy check.

The current source selects 47 unique far vertices and 48 faces, versus 316
vertices and 440 faces near (`motion/check.js:39-49`). `pushMotion` samples and
projects each selected vertex (`murmuration.html:961-975`); far rendering then
builds projected hulls/loops or falls back to triangles
(`murmuration.html:935-959`). The canvas groups birds into six depth-bin paths
and fills each bin once (`murmuration.html:977-1003`). `sim/profile.js` times
whole `step`, `draw`, and `analyse` functions, not draw sub-stages.

A separate N=1000 native isolated run at the same viewport/DPR is recorded in
`docs/verification/performance-scale-n1000.json`. Read-back confirms the current
HTML hash, Node 20.20.1, native Canvas 0.1.100, and the 20 warm-up / 120 measured
frame fixture. Draw median/p95 was 14.528/17.502 ms and step median was 5.160 ms;
analyse median was 29.645 ms from four samples. No new timing profile was run
for this note.

## Ranked experiments

Ranks favor low-risk falsification first. Savings are hypotheses; no proposal
has a measured post-contour speedup.

| Rank / status | Proposal and source anchor | Predicted mechanism | Shape, phase, XYZ risk | Smallest falsifiable experiment and acceptance gate |
| --- | --- | --- | --- | --- |
| 1 · source-verified dead work; likely small | In XYZ mode, skip constructing and stroking `bodies[0..5]`. `pushMotion` only receives a fill path (`murmuration.html:996`), yet each draw allocates both arrays (`977`) and strokes every body path (`999-1003`). The body paths are used by the legacy branch (`995`). | Removes six empty `Path2D` allocations and six empty body strokes per draw in the default mode. This guarantees fewer calls; runtime benefit remains unmeasured and may be negligible. | No default geometry, phase, or XYZ data changes. Keep legacy path construction/strokes intact. | Guard the body path allocation and stroke with `legacyMotion`; compare fresh native PNG hashes in XYZ and exact legacy output against this page. Accept only if XYZ is pixel-identical, legacy remains unchanged, and paired isolated `draw` medians improve without a p95 regression. If timing is indistinguishable, retain only if the simpler source is still clearer. |
| 2 · source-backed hunch | Specialize projection of sampled vertices inside `pushMotion`. The center calls `P` for depth/LOD; then every selected vertex calls `P` again (`961-972`). In that loop `_z` is written but only `_x/_y` are consumed. | An inline projection using the same scalar expression/order could avoid a function call and global temporary writes for each far vertex (up to 47 calls per far bird) and each near vertex (316). Modern engines may inline `P` already, so benefit is uncertain. | Preserve perspective and all XYZ coordinates. Algebra/order or float precision changes could move pixels; do not replace perspective with an affine approximation. | Inline only the vertex projection, retaining the current arithmetic order; compare output PNGs and the flattened-Z sentinel, then run identical native profiles at N=400 and N=1000. Accept on exact pixels (or the established ≤0.5 CSS-px far mask gate if exactness differs only by raster quantization), unchanged step/history, and repeatable draw-median improvement. |
| 3 · source-backed hunch | Replace comparator-based `Array.sort` for the tiny far hull inputs with a stable in-place insertion sort. `appendFar` re-sorts each hull's reusable vertex list by projected x/y for each bird (`murmuration.html:935-950`); the comparator uses the mutable projected arrays. | Avoids repeated JS comparator callback dispatch while retaining the per-frame ordering needed by the dynamic projected hull. The arrays are small, and engines may optimize the existing sort; measure before keeping it. | Sorting ties/collinear projected points can alter hull membership or winding if stability differs. Keep the same x-then-y comparison and stable tie order. No pose quantization. | Implement only the stable sort behind a temporary A/B variant; run the 200-case 8× far silhouette comparison plus exact near glyphs, then paired native profiles at N=400/1000. Accept only if the current 0.5 CSS-px bound and near-pixel identity still pass and draw timing improves repeatably. |
| 4 · adjacent hypothesis | Cache the current flap-clip bracket index per gait state and advance it as phase increases, falling back to `bracket()` on wrap/backward sampling. `sampleGait` performs a binary search of 37 time knots once per bird per draw (`motion/motion.js:14-20,73-81`); phase advances monotonically modulo one in the normal page loop (`motion/motion.js:52-57`). | May remove several time comparisons per visible starling. It does not reduce vertex interpolation or Canvas path work, so expected headroom is limited. | A stale cursor at wrap, pause, direct out-of-order sampling, or an exact knot could change phase/pose. This must remain render-only and preserve the existing phase exactly. | Add a temporary cursor with the existing binary search as fallback. Compare sampled Float32 arrays over all clip knots, wrap, pause, and replay histories, plus same-fixture draw profiles. Accept only bit-identical samples and a repeatable timing gain; otherwise remove it. |
| 5 · higher-risk geometry hypothesis | Add a still-smaller far representation selected by projected span below the current 26 CSS-px threshold (`murmuration.html:963-965`). Build it from existing sampled XYZ and reduce the vertices/path segments needed for birds that occupy only a few pixels. | Fewer sampled vertices and contour commands for distant birds could scale with flock size. First count actual birds in candidate screen-size bands; if few qualify, stop before implementing. | High silhouette risk: viewpoint, bank, wing phase, and depth affect projection. Do not cache a fixed flat pose or drop the Z coordinate. | First add a cheap count-only probe over the current N=400/N=1000 fixtures. If a meaningful fraction falls below a candidate threshold, test a separate far LOD against the existing 200-pose 8× mask matrix, both species, bank/heading, and flattened-Z sentinel. Accept only with ≤0.5 CSS-px directed mask error, unchanged near glyphs, preserved XYZ sentinel, and repeatable `draw` improvement. |
| 6 · counter-inductive; do not prioritize | Cache screen-space bird sprites or quantized pose `Path2D`s in place of per-frame XYZ projection. The live path depends on gait/falcon state, heading, bank, perspective, depth bin, and animated XYZ (`murmuration.html:961-975,985-1013`). | A cached image/path could cut JavaScript path construction, but likely requires many phase/orientation/scale bins and trades CPU for memory, lookup, and raster scaling. | Direct risk to continuous phase, perspective, bank, LOD transitions, and the demonstrated flattened-Z pixel dependency. A 2D sprite cache cannot represent arbitrary depth/XYZ without an atlas approximation. | Only revisit if a targeted browser/native profile shows vertex projection/path construction remains dominant. A minimal prototype must first pass the current multi-pose mask matrix, near-pixel check, and flattened-Z sentinel; reject it on any phase stepping or loss of XYZ sensitivity. |

## Failed approaches to keep closed

The prior `boundary-native.json` variant reduced Path2D commands but measured
12.242 ms median at 1440×900/DPR2/N400 versus 12.707 ms for its same-fixture
baseline: a small difference, not a useful established win. The recorded notes
identify runtime boundary cancellation as having little benefit. The
per-bird-fill variant measured 13.511 ms and counted 64,080 Canvas fills across
140 draws, versus 8,920 for the grouped-path variant; it was slower in that
fixture. Both raw trials are under
`/tmp/murmuration-performance-20261005/` and are summarized at
`motion/OBSERVATIONS.md:49-52`. Do not retry edge cancellation or per-bird fills
without a materially different, falsifiable mechanism.

The current renderer's far-hull silhouette bound is verified only for its
declared case matrix, not every pose. Keep exact browser FPS, browser compositing,
and device behavior marked **unobserved** until a permitted live-browser
measurement is available.
