# First milestone: combined birds, hunts and headless simulation

Completed 2026-10-05 in `~/prj/murmuration-milestone`, branch
`codex/first-milestone-20261005`, based on merged main `0d3078f`.
Changes are local and uncommitted. The primary checkout and its Blender files
were not edited. This milestone combines rendering and behavior; it does not
implement the plan's later force-based flight controller or establish biological
validity.

## What is wired

- Merged main's proportional-navigation hunting, multiple strikes, flash/dodge
  responses and escape waves remain in the actual page.
- Default birds use the existing Blender-baked XYZ surfaces with near/far geometry.
  `motion=legacy` retains the earlier outlines as an explicit comparison.
- Individual flap/glide/bound scheduling uses the source-tagged Rayner speed-table
  preset, independent visual random streams and durations frozen on bout entry.
  Alarm response and bounding probabilities remain modeling choices.
- Falcon animation follows explicit position/stoop/climb/leave events, with speed
  and normalized steering demand as visual cues. Pose blending preserves the
  outgoing geometry on interruption. High steering demand can open the wings
  immediately after entering a stoop; full tuck on every strike is not asserted.
- The page links to the motion viewer. Debug metadata identifies the base revision,
  seed, static build worktree, authoring-input hashes and motion-export hashes.
- `sim/` runs actual external/inline page scripts through deterministic frame
  callbacks and input replay. JSON/CSV output records configuration and provenance.
  Both older numerical/hunt checkers use this shared host. The host captures events
  beyond the page's 400-entry ring.

## Evidence and acceptance gates

These initial records describe HTML SHA `48277251…`. The subsequent renderer
correction and its separately scoped evidence are below.

| Declared claim | Probe and raw signal | Verdict and boundary |
| --- | --- | --- |
| Integration preserves merged flight and hunt behavior in the tested cases | `node sim/differential.js --seconds 40 --cases 'seed=1&n=100&calm,seed=7&n=100&calm,seed=1&n=100&falcon,seed=7&n=100&falcon'`; 2,400 paired frames per case, exact six arrays/every baseline falcon field/full hunt history. Attacking cases captured 15 and 5 hunt events. [Raw output](verification/differential.json). | `TARGET_PASS` for these 9,600 paired frames under the same Node/viewport/frame clock. Not all possible seeds or timestep convergence. |
| Pointer replay also preserves behavior in XYZ and legacy modes | `node sim/differential.js --seconds 8 --cases 'seed=7&n=40&calm&painted,seed=7&n=40&calm&painted&motion=legacy' --inputs sim/example-inputs.json`; both 480-frame histories exactly equal. [Raw output](verification/input-replay.json). A fresh-context Sol reviewer separately ran a 40-second pointer-launched comparison in both modes, exact at all 2,400 frames each. | `TARGET_PASS` for the tested replay policy. Input delivery in a browser is unobserved. |
| Headless results are reproducible and the harness can detect faults | `node sim/check.js`; 120-frame twin replay, injected velocity divergence detected, 450 synthetic events retained, missing script/NaN/unsupported Canvas APIs rejected, invalid and zero-frame CLI timing rejected. [Raw output](verification/harness.json). Repeated eight-second CLI input replay produced trace SHA `01ff567baca21838ec339ee1ab723b79115b07b3b23cfe5aefc5bc4488dfee0f`; [JSON](verification/simulator-example.json), [CSV](verification/simulator-example.csv). | `TARGET_PASS` for these calibrated harness channels. VM/DOM stubs are not browser fidelity or a security boundary. |
| Motion geometry and transitions are actually exercised | `node motion/check.js`; 168 sampled clips, 976 face checks, four actual LOD probes, eight viewer frames; 100 gaits had mixed flap/glide modes on 575/600 frames and >90 distinct phases. Both species selected 316 near / 47 far vertices, drawing 440 / 48 faces. Interrupted falcon pose entry was continuous. | `TARGET_PASS` for execution/geometry. Atlas accuracy against the authored rig does not measure living-bird accuracy. |
| The default drawing reaches XYZ geometry and pixels depend on its vertical component | `node sim/render-check.js --canvas-module=~/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@napi-rs/canvas`; 400 actual gait samples; fresh matching histories produced identical PNG hashes; flattening Z produced a different hash. Actual viewer phase, pause/play, species and four views passed. [Raw output](verification/raster.json), ignored PNGs in `sim-output/`. | `TARGET_PASS` for native Canvas pixels and viewer JavaScript. Browser DOM/CSS, console and input delivery are unobserved. |
| Numerical and hunt tools still reach the merged implementation | Assets match both model exports. Forty-second N400 calm run: Φ .997, correlation ratios .347/.338, independent scalar agreement within 1.41e-8, independent Eq14 ratios 1.0000/1.0000. [Output](verification/flock-40s.txt). A 180-second N400 hunt run captured six strikes and three hunts; [raw events](verification/hunts-180s.json). | Runtime observations, not population calibration. Page-bin Eq14 remains `UNDER_OBSERVED` because its empty/filtered bins yield NaN. Contact, radius expansion and splitting are simulator proxies. |
| The newer untracked Blender lab contains the motion assets already wired here | Background Blender 5.2.2 read both files without saving. `blender/bird_motion_lab.blend` and `motion/birds-motion.blend` have matching base mesh/bone digest `4f101bbe…` and matching used-action keyframe digest; the full lab additionally contains the default Scene and unused actions. [Raw inventory](verification/blender-inventory.txt). | `TARGET_PASS` for those two explicit saved-data comparisons. This is not a comparison of every constraint/material or an anatomical validation. Both files were preserved. |
| Port 8765 serves the combined files | The old task-owned server PID 20020 was stopped and replaced with PID 86937 serving this worktree. HTTP 200 responses for HTML, viewer, both motion scripts and sky image byte-match disk. [Readback](verification/served-final.json). | `TARGET_PASS` for HTTP identity and asset availability at readback. Does not prove a previously open tab reloaded. |

Verification used Node v20.20.1. Optional native Canvas used the existing cached
`@napi-rs/canvas` v0.1.100 rather than installing a dependency. Product hashes:

```text
murmuration.html      48277251e24ae20a617716a920ffa9e6cad1de4c5a91065afc34751c6cf0abf8
motion/motion.js       ce19dd0dd8eacfdb710ad6cb928735e70c296a8ae689b32ca224502c1e353351
motion/motion-data.js  744e92d6f4a41b651723e499025a25b05e1eaef2d77f02d89a81bca57072e1aa
```

One failed raster probe was localized to its oracle: the app intentionally draws
trails with partial background opacity, so two draws on one canvas have different
histories. The corrected probe compares fresh hosts with identical histories;
it then detects the flattened-Z sentinel without changing that auxiliary.

## Run it

Preview: <http://127.0.0.1:8765/murmuration.html?seed=1&warm=20>.
Viewer: <http://127.0.0.1:8765/motion-lab.html>.

```sh
cd ~/prj/murmuration-milestone
node sim/run.js --seconds 30 --query 'seed=1&n=100&calm&painted'
node sim/check.js
```

The [simulator guide](../sim/README.md) covers replay, CSV and optional PNGs.
The [implementation plan](REALISM_IMPLEMENTATION_PLAN.md) retains the remaining
clock/units, mechanics, local-turn, falcon energetics and empirical-validation
stages. Those remain planned. Motion currently affects geometry; coupling it to
flight forces comes later.

## Renderer performance correction

The user reported very slow animation after the initial combined app. Local
profiling isolated drawing as the dominant cost in the tested 400-bird fixture:
48 far-mesh triangles per bird meant 19,200 filled triangle subpaths per frame.
This is a local diagnosis, not direct observation of Chrome's frame rate.

Far rendering now compiles the mesh's disconnected surface parts once. Wings and
tail use their boundary loops when projected triangle orientations agree; folded
or overlapping sheets keep triangle paths. Body and bill use projected convex
hulls. All paths still come from the sampled XYZ surfaces, orientation, bank and
perspective. The existing 26 CSS-pixel LOD threshold, nearby full meshes, bird
count, pixel density, color bins and simulation rules remain the same. Far hulls
are a presentation approximation; the measured silhouette bound applies to the
explicit test matrix, not every possible pose. The debug FPS counter now divides
by elapsed wall time, rather than the capped physics timestep.

| Declared claim | Probe / raw signal | Evidence boundary |
| --- | --- | --- |
| The optimized drawing reduces native Canvas cost by at least 30% in the declared fixture | Independent sequential 2048×1217 CSS, DPR2, N400, seed1, calm, warm20; 20 warm-up and 120 measured calls. Draw median 17.272 → 7.544 ms (56.3% reduction); p95 20.437 → 11.450 ms. Step medians 1.645/1.553 ms, analysis 4.845/4.772 ms. [Before](verification/performance-before.json), [after](verification/performance-after.json). | `TARGET_PASS` for isolated page functions under Node20.20.1 / native Canvas0.1.100. Not browser FPS; loop scheduling, display compositing, real input and image decoding are unobserved. Counters include warm-up calls. |
| Tested far silhouettes stay within 0.5 CSS px of the initial XYZ triangles; tested near glyphs remain identical | Independent transparent-glyph raster comparison at 8× sampling, same CSS projection/LOD, 200 far cases varying both species, depth, pose/gait weight, heading/pitch and bank: maximum directed foreground-mask distance 0.17678 CSS px, no failures. Eight near cases: zero different pixels. Flattened-Z sentinel: 731 different pixels, at least one directed distance >1.5 CSS px. [Raw](verification/performance-glyph-8x.json). | `TARGET_PASS` for this mask oracle and case matrix. At DPR2, four cases had a single diagonal-pixel distance 0.7071 px; supersampling localized this discrepancy to pixel quantization. [Initial DPR2 result](verification/performance-glyph-dpr2.json). The bounded search returns Infinity beyond its radius, serialized as null in the sentinel result; the recorded bound, not null, is the interpretation. |
| Physics and hunts match the pre-optimization XYZ page | Actual frame callback differential, 40 seconds / 2,400 paired frames per case; seed1 N400 calm and seed7 N100 forced-falcon, both with pointer/key replay. Exact six trajectory arrays, every falcon field including nested motion/typed arrays, and full hunt histories; 9 and 5 captured events. [Raw](verification/performance-differential.json). | `TARGET_PASS` for those histories. Recursive value comparison replaced an invalid object-identity comparison across VM hosts; a deliberately perturbed nested falcon motion array was then rejected at frame1. [Calibration](verification/performance-calibration.json). |
| Default rendering remains XYZ-dependent, and the new files are served | Native fresh-run pixels repeat exactly; flattened-Z pixels differ; actual drawing samples 400 gaits. [Raster](verification/performance-raster.json). HTTP assets byte-match disk. [Readback](verification/performance-served.json). | `TARGET_PASS` for these channels. Chrome automation remained blocked by enforced security-policy verification; a previously open tab still needs reloading. |

Current HTML SHA: `d24849dffb2feb6882cece1fa00f56852a5d22f3ddd840559ecd4e05aacf8646`.
Motion script/data hashes are unchanged. `sim/check.js` passes, including the
existing geometry, gait, interruption, event-ring and negative-control gates.
A synthetic 100 ms frame interval reports 10 FPS in the actual debug text,
confirming the wall-time counter correction without changing the physics clock.

`sim/profile.js` now provides a reusable local function profiler. It defaults to
the strict non-rasterizing host; supply `--canvas-module=/absolute/path` (or
`CANVAS_MODULE`) for actual native drawing costs. It deliberately does not infer
browser FPS from its wall times. Research-informed motion and hunt behavior are
preserved; the later fixed-tick controller remains planned.
