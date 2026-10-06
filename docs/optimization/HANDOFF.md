# Murmuration optimization handoff

Prepared 2026-10-05. The next agent should **optimize the integrated app without
changing flight, hunts, individualized gait, XYZ motion or presentation quality**.
The proposals below are experiments, not promised speedups. The running app was
left unchanged during this exploration.

## Start here

Source checkout: `~/prj/murmuration-milestone`, branch
`codex/first-milestone-20261005`, Git base `0d3078f2841f022a78fd6a1c478d9540fedab404`.
The integration is dirty and uncommitted: **Git HEAD alone cannot reconstruct it**.
Primary `~/prj/murmuration` and its Blender files are separate;
preserve them. Port 8765 serves this milestone checkout. Do not change other
agents' servers or publish/merge changes as part of this handoff.

Frozen current HTML SHA-256:
`d24849dffb2feb6882cece1fa00f56852a5d22f3ddd840559ecd4e05aacf8646`.
Motion script SHA: `ce19dd0dd8eacfdb710ad6cb928735e70c296a8ae689b32ca224502c1e353351`.
Motion data SHA: `744e92d6f4a41b651723e499025a25b05e1eaef2d77f02d89a81bca57072e1aa`.
The HTML's embedded `revision.worktree` is historical build metadata, not proof
of where an extracted copy is running. Hash the actual files.

The portable package contains:

- `app/`: the complete runtime, shared simulator/checkers, motion atlas/rig,
  species source inputs/reference manifests, proposal notes and raw evidence.
- `baseline/`: frozen **current** HTML, viewer, motion scripts and sky image.
  Use this as the optimization oracle, never a moving checkout.
- `historical/`: merged main's earlier HTML, the pre-contour XYZ runtime when
  available, and rejected-trial timings. These are historical context.
- `SOURCE_STATE.json`, `TRACKED_CHANGES.patch`, `MANIFEST.json`: checkout identity,
  dirty state, tracked changes and checksums. Full files also cover untracked work.
- `verify-package.py` and `glyph-compare.js`: portable integrity and native
  cross-page silhouette probes. No `/tmp` input is needed after extraction.

The package omits `.git`, dependencies, other agents' configuration, old rendered
photo trees, full species Blender scenes and external PDFs. The motion rig and
source parameters are included. Read `CREDITS.md` and the reference manifests;
optimization does not establish anatomical or aerodynamic validity.

From the extracted package root, before editing:

```sh
python3 verify-package.py .
cp -R app ../murmuration-optimization-candidate
cd ../murmuration-optimization-candidate
node sim/check.js
```

Keep the package pristine and work in that separate candidate. To compare from
the candidate directory, set an absolute `PACKAGE` path to the extracted package:

```sh
PACKAGE=/absolute/path/to/murmuration-optimization-handoff-20261005
node sim/differential.js --baseline "$PACKAGE/baseline/murmuration.html" --current murmuration.html --seconds 40 --cases 'seed=1&n=400&calm&painted,seed=7&n=100&falcon&painted' --inputs sim/example-inputs.json
```

Optional native Canvas requires an existing `@napi-rs/canvas` provider; it is not
bundled. On this Mac the existing module was:
`~/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@napi-rs/canvas`
(0.1.100, Node20.20.1). Discover rather than install by default:

```sh
node -e 'console.log(require.resolve("@napi-rs/canvas"))'
CANVAS_MODULE=/absolute/path/to/@napi-rs/canvas
export CANVAS_MODULE
node "$PACKAGE/glyph-compare.js" --baseline="$PACKAGE/baseline/murmuration.html" --current="$PWD/murmuration.html"
node sim/render-check.js --output=/absolute/output/candidate
node sim/profile.js --html="$PWD/murmuration.html" --n=400 --width=2048 --height=1217 --dpr=2 --frames=600 --canvas-module="$CANVAS_MODULE"
```

If the provider is absent, strict-host behavior tests still run; label native
pixel/timing gates unobserved. There is no `package.json` or dependency install
required for the ordinary simulator. Use explicit `--baseline` in a package
without Git. Timing arguments now validate before implicit Git extraction;
the negative controls assert the actual error channel.

## Evidence available now

The source and raw results are in `app/docs/verification/` in the package
(or `docs/verification/` in the source tree):

| Fixture / claim | Raw signal and chain | Boundary |
| --- | --- | --- |
| Initial far triangles were expensive in the local N400 fixture | Independent sequential native Canvas at CSS2048×1217/DPR2, seed1/calm/warm20: draw median17.272 → 7.544 ms after current contour change, 56.3% reduction. `performance-before.json`, `performance-after.json`. | Isolated actual-page functions; not Chrome FPS. Current optimization baseline is the **after** file. |
| Current N1000 costs | Root ran `sim/profile.js --n=1000 --width=2048 --height=1217 --dpr=2` with the same native provider, 120 measured calls: draw14.528 ms, step5.160 ms, analyse29.645 ms. `performance-scale-n1000.json` includes HTML/assets and fixture. | One scale observation; four analysis samples. Supports investigating analysis bursts, not a browser-tail or scaling-law claim. |
| Current geometry fidelity in tested poses | Independent 8× native foreground-mask comparison, 200 far cases across species/poses/blends/heading/bank/depth: maximum0.17678 CSS px against pre-contour triangles; eight near cases pixel-identical. Flattened-Z control fails. `performance-glyph-8x.json`. | Declared matrix only. DPR2's diagonal-pixel artifact was resolved by supersampling without relaxing the0.5 px gate. |
| Current physics/hunts retained | Actual frame callbacks, 40s each at 60Hz for seed1/N400/calm and seed7/N100/falcon plus pointer/key replay: exact six arrays, nested falcon fields and full hunt logs. `performance-differential.json`; nested-field perturbation caught at frame1 in `performance-calibration.json`. | Baseline preservation in those histories; not biological validity or timestep convergence. |
| Browser | User reported the contour change feels better. HTTP readback matches disk. Chrome control was blocked by managed security-policy verification. | User observation and HTTP identity are separate from instrumented browser FPS. Do not bypass the policy or claim browser performance from native timing. |

## Triage and recommended work order

| Order | Approach | Why / expected mechanism | Effort and risk | Decision gate |
| --- | --- | --- | --- | --- |
| 0 | Attribute current draw stages and complete frame callbacks; acquire legitimate browser trace when available | Current profiler excludes scheduling, warm startup and live frame clock; analysis can burst at N1000. Split sampling, projection, hull/path work, Canvas fill, scenery and panel costs. | Small instrumentation; must not replace virtual simulation time with wall time. | A trace reaches actual changed paths, records hashes/counts/raw samples, separates native/RAF/browser channels, and agrees with untimed control traces. |
| 1 | Canvas CPU experiments, one at a time | Skip six empty XYZ body paths/strokes (cleanup); then test exact-expression vertex projection and stable tiny-hull insertion sort. Default draw still dominates at N400. | Small to medium. Projection arithmetic and hull tie stability can change pixels. No measured gain yet. | Exact physics/hunts, near identity and far≤0.5 CSS px; meaningful paired draw improvement. Remove complexity when timings overlap. |
| 2 | Exact unordered-pair neighbor sweep, then an exact spatial index if justified | Avoid duplicate distance arithmetic while retaining current top7. At higher N, use proven cell-distance lower bounds rather than an arbitrary search radius. | Medium. Tie order, force order and live wave-state reads must remain intact. | Brute-force neighbor IDs/distances first, adversarial ties/split clouds, then exact frame traces and measured N400/1000/2000 step benefit. |
| 3 | Exact correlation distance reuse; then a versioned analysis-only worker if bursts persist | Analysis repeats unordered distances and measured about29.6 ms/call at N1000. Live analysis runs only while the stats/debug panel is shown; this is a conditional bottleneck. A worker can preserve sample snapshots while removing main-thread stalls, but adds transfer/latency cost. | Medium. O(N²) caches cost memory; workers risk stale results. | Same analysis timestamps/curves/bins/averages, bounded snapshot age, no backlog, startup/memory accounting, and better full-frame tails. Do not silently reduce sampling frequency. |
| 4 | WebGL2 instanced XYZ rendering with per-bin coverage masks | Conditional larger investment if Canvas remains limiting at target density. GPU atlas interpolation retains per-bird phase and falcon interrupted-pose geometry. | High. Alpha union, trails, projection, GPU precision and fallback are substantial work. | Actual browser/GPU measurements plus same-quality matrix; a fast headless/software-GPU submission is insufficient. |
| 5 | OffscreenCanvas render worker / full simulation worker | Conditional if input/frame stalls remain after cheaper work; reduces main-thread occupancy, not necessarily total render cost. | Medium to high ownership/input-order changes. | Same dt/t/input ordering, versioned bounded snapshots, no dropped hunts, measured input latency and fallback. Keep fixed-tick redesign separate. |
| Defer | Phase/view-quantized sprites, lower DPR, fewer birds/K, cached neighbor IDs, GPU simulation/WASM | Some can be faster, but change fidelity/model or target an unmeasured bottleneck. | High semantic or quality risk. | Treat quality modes or model changes separately; never credit as same-workload optimization. |

Detailed portfolios and falsifiers: `CANVAS_PROPOSALS.md`,
`PHYSICS_PROPOSALS.md`, `ARCHITECTURE_PROPOSALS.md`, and `BENCHMARK_RUNBOOK.md`
beside this file in the source tree; in the package see `app/docs/optimization/`.
The small cleanup at order1 is not expected to meet a25% performance gate alone.
Instrument before selecting the larger experiment; there is no promised gain.

## Non-negotiable preservation and measurement rules

1. Keep K7, RN force cutoff, RNG draw order, per-frame dt/t, PN gain/delay, hunts,
   escapes, wave propagation, individual phases/bouts and both species' XYZ.
   Positions integrate in a separate pass, but wave-state propagation reads live
   index-ordered state: do not parallelize/reorder it as an incidental speedup.
2. For topK ties the current ascending bird-index scan wins. An exact spatial
   query must consider distance **and index**, including cells tied at the kth
   distance. RN38 does not bound global nearest-neighbor/wave selection.
3. Preserve CSS camera/layout, the26 px LOD threshold unless separately tested,
   DPR≤2, bird count, six depth bins, falcon-last layering and TRAIL=.5.
   Canvas combines all positive-winding triangles/birds within each bin and
   applies translucent color once. GL alpha blending per triangle/instance
   darkens overlaps: use coverage union before bin compositing.
4. The glyph tool tests shape, not full scene opacity/trails. Also compare fresh
   identical-history scenes, overlapping birds, interrupted falcon poses,
   viewer controls, resize/DPR and near/far transitions. Flattened-Z and wrong
   phase/projection controls must fail their designated oracles.
5. Use the same harness revision for both arms. The differential checks baseline
   falcon fields, trajectories and hunts; it does not automatically compare
   starling gait internals, every RNG/state field, diagnostic curves or stats.
   Add gates only for declared changes, without weakening existing assertions.
6. Serialize performance runs; other agents may review source in parallel but
   must not run timed work concurrently. Use repeated A-B-B-A blocks, same seed,
   query, viewport/DPR, sample counts and scene/history. Keep raw samples and
   startup/memory costs. Suggested substantive target:≥25% lower targeted cost,
   no>5% regression in important rows; declare thresholds before results and
   report spread. Don't sum independent percentile timings into frame p95.
7. Browser evidence needs the target foreground tab/display, power state,
   browser/backend/version, loaded image, actual rAF/presentation intervals and
   input-to-visible latency. If access remains blocked, deliver verified offline
   results and leave browser acceptance explicitly outstanding.

## Rejected trials and deliverable for the next agent

Historical dynamic triangle-edge cancellation: at1440×900/DPR2/N400 draw12.242 ms
versus12.707 ms before, a weak difference, not a meaningful established win.
Per-bird fills instead of six bin paths:13.511 ms, slower. Raw trial JSONs are
in package `historical/`. Do not retry without a materially different mechanism.

Implement one declared candidate per isolated checkout/copy. Return the exact
changed files, baseline/candidate/harness hashes, matched before/after raw data,
behavior and silhouette verdicts, negative-control outputs, memory/startup and
remaining browser boundary. Keep a failed experiment's raw output and stop it
on evidence. Preserve the realism roadmap: fixed physics ticks, aerodynamic
gait coupling and better empirical anatomy are separate later changes.

Rebuild a fresh package from the source with:

```sh
python3 docs/optimization/tools/build-handoff.py --source "$PWD" --output /absolute/new/handoff-directory --historical /tmp/murmuration-performance-20261005
```

`--historical` is optional at build time. Extracted packages never require it.
