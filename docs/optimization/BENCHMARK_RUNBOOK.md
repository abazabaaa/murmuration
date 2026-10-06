# Performance and fidelity runbook

This is a handoff procedure for optimizing the current integrated murmuration page. The reference is the **frozen, dirty integrated page**, not Git `0d3078f` (which predates integration) and not a moving checkout. A faster candidate passes only when the same workload and quality gates pass. Preserve raw JSON, images, scripts, hashes, and any failure output.

## Freeze and identify the comparison

Before editing, copy the complete served tree into a read-only reference directory and a separate writable candidate directory. Include `murmuration.html`, `motion-lab.html`, `motion/`, `sim/`, the reference images/scenery, and supporting page scripts. Do not silently substitute a painted scene for a photo scene. Record `git rev-parse HEAD`, `git status --short`, `shasum -a 256` of every copied file, the source dirty diff, date, OS/architecture, CPU, power/thermal state, Node version, browser version, Canvas provider version/path, display resolution, device pixel ratio, and rendering backend. A manifest should state which files are reference, candidate, or harness; the candidate must change only declared product files. Rehash immediately before each comparison.

The historically recorded integrated HTML SHA-256 was `d24849dffb2feb6882cece1fa00f56852a5d22f3ddd840559ecd4e05aacf8646` (`docs/FIRST_MILESTONE.md`); verify the actual snapshot rather than assuming it still matches. `docs/verification/performance-before.json` and `performance-after.json` measure an earlier renderer correction. They are context, not the new baseline. `/tmp/murmuration-performance-20261005/` is a local scratch artifact and must not be a required input for a portable handoff.

Keep the reference and candidate trees parallel. `sim/page.js` resolves `<script src>` relative to each HTML file; a lone HTML copy breaks or changes the test. Keep the exact baseline `motion/` scripts next to its HTML. Record the complete query string and input replay hash with each result. The same host and probe revision must be used for both arms; if the harness itself changes, validate it and rerun both arms.

## Establish the behavior gate first

From the candidate tree, these commands match the current CLI syntax (the differential options use **spaces**, while profiler options use **equals**):

```sh
node sim/check.js
node motion/check.js
node sim/differential.js --baseline /absolute/reference/murmuration.html --current /absolute/candidate/murmuration.html --seconds 40 --cases 'seed=1&n=400&calm&painted,seed=7&n=100&falcon&painted' --inputs sim/example-inputs.json
node sim/differential.js --baseline /absolute/reference/murmuration.html --current /absolute/candidate/murmuration.html --seconds 40 --cases 'seed=1&n=400&calm&painted&motion=legacy,seed=7&n=100&falcon&painted&motion=legacy' --inputs sim/example-inputs.json
```

Replace the absolute paths with the frozen package paths. Extend the case list to high N, near-camera and active hunt/turn scenarios after confirming the page supports each query. The current differential runner uses actual page RAF callbacks in a virtual host and checks every frame: exact `px,py,pz,vx,vy,vz`, every reference falcon field recursively (including typed arrays), and complete hunt history. It does **not** compare `stats`, `simT`, DOM output, pixel output, or browser delivery; inspect these separately if an optimization can affect them. A known-bad velocity or nested falcon-field perturbation in an expendable copy must be detected. The existing `sim/check.js` already includes a velocity sentinel and ring-event boundary check. Do not call a shortened or reduced-N run equivalent to the 40-second gate.

For a rendering-only change, preserve the native raster gate. Discover an already installed provider without installing one:

```sh
node -e 'try { console.log(require.resolve("@napi-rs/canvas")) } catch (_) { process.exitCode = 1 }'
```

If that fails, inspect configured local dependency paths and set `CANVAS_MODULE` to the absolute module directory. Record `require('.../package.json').version` for the resolved provider. In each tree, from that tree root:

```sh
CANVAS_MODULE=/absolute/path/to/@napi-rs/canvas node sim/render-check.js --output=/absolute/output/reference
CANVAS_MODULE=/absolute/path/to/@napi-rs/canvas node sim/render-check.js --output=/absolute/output/candidate
```

This gate proves each arm reaches XYZ gait geometry, repeats fresh-run pixels, responds to a flattened-Z negative control, and exercises viewer handlers. The existing script does not compare reference and candidate PNGs. Compare aligned images yourself at fixed history/viewport/DPR and test cases spanning near and far birds, silhouettes, bank, pitch, gait phase, falcon attack, trail accumulation, and motion-lab views. If a renderer deliberately changes far contours, reuse the independent glyph comparison method and its original-space distances: proposed acceptance is at most **0.5 CSS px** foreground-mask distance across a declared, held-out far-case matrix; near geometry should remain pixel-identical where no near change is intended. Include an intentionally flattened-Z candidate that fails. A pixel hash difference alone does not quantify visual distance, and identical native pixels do not establish browser layout.

## Isolated CPU/native Canvas measurements

`sim/profile.js` currently accepts `--html=`, `--mode=xyz|legacy`, `--n=`, `--width=`, `--height=`, `--dpr=`, `--frames=` and `--canvas-module=`. Use the same command for each arm, changing only the HTML path and output filename:

```sh
node sim/profile.js --html=/absolute/reference/murmuration.html --mode=xyz --n=400 --width=2048 --height=1217 --dpr=2 --frames=600 --canvas-module=/absolute/path/to/@napi-rs/canvas > /absolute/output/reference-profile.json
node sim/profile.js --html=/absolute/candidate/murmuration.html --mode=xyz --n=400 --width=2048 --height=1217 --dpr=2 --frames=600 --canvas-module=/absolute/path/to/@napi-rs/canvas > /absolute/output/candidate-profile.json
```

The profiler constructs a page with `seed=1&calm&warm=20&painted&n=...`; startup advances private `simT` through 1,200 warm-up steps. It then calls `step(1/60,t)`, `analyse(t)` every 30 iterations, and `draw()` directly with `t=20+(i+1)/60`. It does not advance the host's virtual `performance.now()` or run RAF. The actual loop caps `dt` at 1/30 s and calls `analyse` only when the panel is visible and simulated-time cadence is reached (`0.5` s, or `1` s above N1500); the profiler bypasses that policy. Pointer-lure expiry, timers, callback scheduling, and interleaved app work can therefore differ from production. The 20 unmeasured calls are additional direct calls; **counters include them**. Native Canvas includes raster work but not browser GPU composition. Without `--canvas-module`, the strict host only counts Canvas calls and timings are not raster costs.

At `--frames=120`, `analyse` has only four measured samples; a p95 from four samples is not a tail estimate. Even 600 frames yields only 20 analysis samples. Use dedicated longer runs or an instrumented RAF/page trace for analysis tails. Keep per-call samples, not only medians, so each arm can report sample count, median, p95 with a stated quantile rule, spread, and run-to-run variability. Do not sum independent p95s into a frame p95. Log startup/first-frame separately because the function profiler begins after warm-up and excludes asset loading, path/cache construction, image decode, and first paint.

Use a fixed matrix, changing one axis at a time: N100/400/1000/1600 (plus a separately labelled 3000 stress case), default and near-camera framing, calm and hunt/turn input histories, native Canvas and strict host, XYZ and legacy, CSS 1440×900 DPR1 and 2048×1217 DPR2, painted and actual scenery/image load. The page clamps N to 20–3000 and DPR to at most 2, so verify the reported actual N and pixel dimensions instead of trusting requested settings. `sim/profile.js` hardcodes calm/painted/seed1 and cannot by itself run hunt, near-camera, or real-image cases; add a separate probe or browser trace for those rows. The native host does not decode the photographic image, so browser or another real-image probe is required for that row. Motion-lab is a distinct page and needs its own render/interaction timing. Never label a changed fixture as the same workload.

For timing comparisons, let the machine idle and serialize all timed processes. Run at least four paired blocks in **A-B-B-A** order, then reverse initial arm in the next block. Use independent fresh processes, capture raw outputs and thermals, and compare within-block ratios before pooling. The success threshold should be agreed before seeing candidate numbers: suggested gate is at least 25% lower median draw time on the declared N400/DPR2 native fixture, no material regression in step/analysis or startup, and no regression over 5% in the important other matrix rows. Report confidence/spread rather than hiding overlapping runs. A fast strict-host result alone is not a win.

## RAF, browser, and worker evidence

Add an end-to-end measurement of actual frame callbacks on both arms with fixed replayed input. Record per-frame wall duration for simulation, analysis, draw, total callback; callback interval; dropped/late frames; heap/GC pauses; canvas allocation; and first interactive frame. Distinguish a virtual `sim/page.js` trace (deterministic JavaScript, no compositor) from a browser performance trace (scheduling, display, GPU and event delivery). A 60 Hz target has a 16.67 ms frame budget, but a 16 ms `draw()` median does not mean 60 FPS. For browser claims, use the same browser profile, viewport, DPR, visible foreground tab, warm/cold-cache policy, power mode, 30–60 second steady and hunt windows, and a separate cold start. Record at least p50/p95 callback and presentation intervals, frames over budget, worst stalls, and visible artifact checks. If browser automation is policy-blocked, mark this `UNOBSERVED`; do not promote VM/native results to browser FPS.

If a candidate moves simulation or geometry to a worker, measure end-to-end input-to-visible-frame latency and age of each consumed snapshot, including backlog under high N and hunt bursts. State the ownership and ordering rule (tick ID, input timestamp, snapshot ID); prove that old worker messages cannot overwrite newer state and that dropping intermediate snapshots does not lose hunt events. Exercise worker unavailable/restart/fallback, tab pause/resume, resize/DPR change, and capture/transfer overhead. Compare paired traces to the same state and event oracle at the intended tick boundaries. Reduced main-thread cost with stale or missing visible state fails the same-quality gate.

## Decision record

For every candidate, report: exact snapshot and harness hashes; changed files; workload/query/input hash; environment; raw timing and image paths; behavior and negative-control verdicts; isolated/native/RAF/browser evidence labels; observed quality differences; startup and memory cost; and unresolved boundaries. Mark each claim `SOURCE_ONLY`, `OFFLINE_VM`, `NATIVE_RASTER`, `BROWSER_OBSERVED`, or `UNOBSERVED`. Reject a candidate that misses exact behavior, the visual bound, or the declared performance threshold. If a proposed optimization changes simulation semantics or visual quality on purpose, obtain a new explicit oracle and acceptance envelope before comparing speed.
