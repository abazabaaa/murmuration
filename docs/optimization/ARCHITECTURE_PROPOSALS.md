# Renderer and execution architecture proposals

Status: proposals, not implemented or measured. Scope: the XYZ page at HTML SHA
`d24849dffb2feb6882cece1fa00f56852a5d22f3ddd840559ecd4e05aacf8646`.
The fixed local native-Canvas fixture (N400, 2048×1217 CSS, DPR2, seed1 calm,
20 warm-up/120 measured draws) improved from 17.272 to 7.544 ms median and
20.437 to 11.450 ms p95. Those are isolated drawing times, **not Chrome FPS**.
Browser frame pacing, compositing, GPU work, input latency and image decoding
remain unmeasured because Chrome automation was blocked by security-policy
verification. See [milestone evidence](../FIRST_MILESTONE.md) and the
[before](../verification/performance-before.json) / [after](../verification/performance-after.json)
records. None of the options below has a claimed speedup.

## Decision order

| Rank | Hypothesis and investment | Trigger for a prototype |
| --- | --- | --- |
| 0 | Measure actual Chrome first; no architectural change. | Always. The 7.54 ms native draw does not identify the browser bottleneck. |
| 1 | Smaller Canvas work within the current path; low migration risk. | Chrome shows main-thread JS/path or raster cost in `draw()`, with spare room elsewhere. |
| 2 | Canvas `OffscreenCanvas` in a dedicated worker; moderate migration. | Main-thread drawing blocks input or produces long frames, and worker 2D path support is verified on target browsers. |
| 3 | WebGL2 instanced XYZ meshes with clip atlas; substantial renderer rewrite. | Same-density Chrome profiling shows Canvas raster/path construction remains limiting after rank 1, or larger N is a product requirement. |
| 4 | Simulation plus rendering in a worker; substantial state migration. | `step()` or `analyse()` measurably blocks the main thread, or worker rendering alone merely moves the bottleneck. |
| 5 | GPU simulation or WASM; research counterbets. | Measured CPU simulation dominates at required N and deterministic behavior has an explicit migration budget. |

Rank is a test order, not a prediction that Canvas will beat WebGL. Keep the
current Canvas implementation as the visual and behavior oracle while a
candidate is under development. A prototype only earns promotion after the
acceptance matrix below. The present `draw()` creates paths for N birds, samples
motion vertices, applies `birdFrame()` and `P()`, groups six depth/color bins,
then draws the falcon and optional correlation panel; a WebGL rewrite must
account for all of these, not merely make an instanced mesh appear.

## 1. Further Canvas work (supported first bet)

Hypothesis: reduce per-frame projection, hull sorting, path creation or 2D
raster work while retaining the current camera, 26 CSS px LOD boundary,
six-bin back-to-front fill order, color, DPR, density and visual feedback trail.
Instrument `pushMotion()`, `appendFar()`, `ctx.fill/stroke`, sky feedback and
panel separately in Chrome before editing. Candidate experiments: reuse safe
scratch arrays and compiled topology; precompute immutable indices/adjacency;
skip projection work for conclusively offscreen birds; cache only invariant
styles or background assets. A path of animated XYZ vertices is not invariant,
and clipping must account for wings that cross the viewport edge. Avoid
coarse phase/pose quantization without declaring a fidelity change. The
existing far-contour optimization is already in place; another large gain is
only a hypothesis. Preserve per-bird `Motion.sampleGait()` phase, flap/hold
weight and bank, and `Motion.sampleFalcon()`'s captured `from` surface on an
interrupted pose.

## 2. OffscreenCanvas worker (adjacent bet)

`transferControlToOffscreen()` can hand the visible canvas to a worker, and
a dedicated worker can use `requestAnimationFrame()` with an offscreen canvas
([transfer](https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/transferControlToOffscreen),
[worker animation](https://developer.mozilla.org/en-US/docs/Web/API/DedicatedWorkerGlobalScope/requestAnimationFrame)).
The current page calls `getContext('2d')` immediately, so the transfer must
occur *before* that call or use a newly created replacement canvas. Move the
Canvas drawing functions, sky load/decode path and viewport/DPR updates to
the worker; keep DOM HUD, links, pointer and key listeners on the main thread.
Start with simulation on main and send versioned, coalesced render snapshots
(`frameId`, `simT`, camera/layout, positions/velocities/banks/gait state,
falcon motion state). Measure serialization, transfer and dropped snapshots;
do not let delayed paints change physics. `ArrayBuffer` transfer moves
ownership and detaches the sender's buffer, so use bounded double/triple
buffers or copies until a measured need justifies shared memory
([transferables](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Transferable_objects)).
SharedArrayBuffer requires cross-origin isolation and server headers, which
would change deployment assumptions
([isolation](https://developer.mozilla.org/en-US/docs/Web/API/WorkerGlobalScope/crossOriginIsolated)).
Check `OffscreenCanvas`, worker rAF and worker 2D APIs on each target browser;
retain a main-thread Canvas fallback. Worker 2D may preserve source parity,
but moving drawing off the main thread alone may leave total raster/GPU cost
unchanged. A worker cannot directly access DOM input or the current HTML HUD.

## 3. WebGL2 instanced meshes and clip atlas (conditional investment)

Hypothesis: amortize hundreds of Canvas path submissions with instanced
triangles. WebGL2 provides [indexed instancing](https://developer.mozilla.org/en-US/docs/Web/API/WebGL2RenderingContext/drawElementsInstanced)
and [per-instance attributes](https://developer.mozilla.org/en-US/docs/Web/API/WebGL2RenderingContext/vertexAttribDivisor).
Build static near/far face index buffers for both species. Pack authored XYZ
clip frames into a GPU texture atlas indexed by species, clip, frame and vertex;
for each instance upload position, heading basis, bank, scale, clip brackets,
phase, hold mode/weight, depth bin and color. In the vertex shader, interpolate
the two flap frames and the hold surface, then apply the same orientation,
bank and perspective equations as `birdFrame()`/`P()`. Keep the CPU gait state
machine; transferring its few parameters is much simpler than porting the
deterministic simulation. For falcon pose entry, upload the captured `from`
surface as a tiny dynamic buffer/texture and blend with the destination clip
using the present smoothstep and 0.16 s transition. This is necessary for a
mid-stoop interruption to remain continuous. Preserve six bin passes and
falcon-last ordering at first; depth testing or per-pixel depth may alter the
current overlap image. The six Canvas `Path2D` fills union same-bin bird
triangles before applying the bin's translucent color (alpha 0.97 near to
0.77 far). Ordinary alpha-blended GPU triangles would darken overlaps within
a bird and between same-bin birds. A parity prototype needs a per-bin coverage
mask or equivalent stencil/offscreen union, followed by one color composite
per bin; test inter-bin ordering and the separate falcon pass too. Reproduce
near/far LOD at the current projected-size
threshold, and compare near full meshes and far contours against the Canvas
oracle. An all-triangle far mesh may change silhouettes, so either construct
equivalent GPU far geometry or declare and measure that difference.

The sky feedback trail (`ctx.globalAlpha = TRAIL`, then `drawImage(sky)`) needs
an equivalent GPU feedback pass, likely ping-pong textures, plus compatible
gradient/photo sky and panel composition. This is real rewrite cost. Context
creation can fail and contexts can be lost; add Canvas fallback and restoration
([WebGL context events](https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement)).
Check WebGL2 limits and atlas formats at runtime. Floating-point texture
*sampling* must not be conflated with rendering into floating-point textures;
float render targets can require `EXT_color_buffer_float`
([WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices)).
Do not infer GPU time from the JS draw call: use a GPU timer query when the
extension is available, otherwise report CPU submission and frame timing
separately. For a WebGL2 context, request
[`EXT_disjoint_timer_query_webgl2`](https://registry.khronos.org/webgl/extensions/EXT_disjoint_timer_query_webgl2/)
and discard disjoint or unavailable query results; the similarly named
`EXT_disjoint_timer_query` interface is for WebGL1.

## 4. Simulation worker (conditional adjacent bet)

Move `step()`, gait/falcon updates, hunt history and `analyse()` to one worker
as a first migration with the **same** capped `dt = min(elapsed, 1/30)`,
`simT` increments and ordered input delivery as the current page. Tag each
input and returned immutable snapshot with a frame sequence and simulation
time; preserve the existing order of pointer updates, falcon launches,
`step()`, conditional `analyse()` and draw. The worker must not process newer
inputs ahead of an earlier frame. Differential replay should include delayed
or coalesced pointer messages and falcon launches; their order must be defined
without silently changing the simulation. The render thread may interpolate
*only* presentation state if that is separately accepted. Do not interpolate
hunt decisions, RNG, gait state transitions or the falcon's stored pose-entry
surface. Keep the stats panel synchronized to a tagged snapshot rather than
mixing adjacent simulation times. A single worker owning both simulation and
OffscreenCanvas avoids large snapshots, but loses independent simulation/render
scheduling; profile both arrangements. Transferable buffers help avoid copies,
yet do not make main-thread waits, networked assets or worker startup free.
A fixed-tick controller is a later realism/timing change, not a prerequisite
for this performance migration; it needs its own differential and physical
behavior review.

## 5. Raster sprites, adaptive resolution, GPU compute, WASM (counterbets)

Sprite atlases could reduce path work, but discrete view/phase/bank bins cannot
represent arbitrary XYZ projection and continuous flap weights exactly. Use
only as an explicitly lower-fidelity mode with angle/phase/scale error limits,
and test falcon interruptions and side-on wing folds. Rendering at a lower DPR
or drawing fewer birds can improve cost but changes sharpness or density; label
these quality modes and never compare their FPS as an equal-fidelity win.
GPU simulation might raise the N ceiling, but neighbor selection, deterministic
RNG, hunt events, readback and exact differential verification all become
harder; WebGL2 is not a general compute API. WASM could accelerate measured
CPU loops, yet Canvas path/raster cost would remain and JS/WASM memory exchange
has a cost. Neither deserves implementation before browser profiling locates
the bottleneck.

## Measurement and acceptance gate

Run the served page in actual Chrome on a named machine/GPU, with a reloaded
tab, fixed viewport 2048×1217 CSS and DPR2, seed1 N400 calm and seed7 N100
forced falcon, plus N100/N400/N1600 scaling. Record URL, revision/hash, browser
version, power state, warm-up, canvas backing dimensions and actual visible
bird count. For each, record rAF interval distribution and presented FPS,
draw/step/analyse CPU time, p50/p95/p99 frame intervals, frames over the display
budget (16.7 ms at 60 Hz), input-to-visible-response latency, and long animation
frames where supported. The [Long Animation Frames API](https://developer.mozilla.org/en-US/docs/Web/API/Performance_API/Long_animation_frame_timing)
starts at 50 ms, so it cannot alone identify missed 16.7 ms frames. Include
GPU timing for WebGL when the extension exists and context-loss/fallback checks.
Report both absolute frame behavior and differences from the same-density,
same-shape baseline. A headless browser may validate real WebGL/worker API
execution and screenshots, but software GPU or virtual display timing is not
the target device's perceived FPS.

Keep an independent matrix: exact replay of six position/velocity arrays,
falcon nested state and hunt history for fixed inputs; animation occupancy and
distinct phase counts; same camera/projection equations at top/front/side/
quarter views; near/far boundary and folded-wing/side-on cases; falcon pose
interruptions; raster foreground-mask distances at DPR2 and 8× sampling;
sky/trail/color-bin/panel pixels, especially same-bin overlap alpha; and real
browser input/resize/readback.
Positive gates need negative controls: flatten Z (must alter pixels), perturb
a nested falcon motion value (must fail differential), rotate or mis-scale the
projection matrix (must fail glyph comparisons), and intentionally change one
gait phase or drop a snapshot (must be reported by continuity/latency checks).
Native Canvas and Node VM tests can prove deterministic output, source-level
state equality and local raster correspondence; they cannot prove Chrome FPS,
worker scheduling, GPU completion, actual compositing or visible interaction.
