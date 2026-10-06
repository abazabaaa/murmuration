# Actual-page simulation without a browser

This runner evaluates the app's own external and inline scripts, in page order,
inside Node's VM. A small host supplies DOM elements, a virtual monotonic clock,
timers, animation-frame callbacks and input listeners. Each frame reaches the
actual page's loop, physics, analysis and drawing. There is no separately copied
flocking or hunting algorithm.

The Luna map found the existing project Node checkers and prior motion harness;
it found no attributable Claude-created simulator in the bounded project-local
files/history search. The implementation reuses those surfaces. The primary
references for the host are [Node VM](https://nodejs.org/api/vm.html) and the
[HTML animation-frame callback algorithm](https://html.spec.whatwg.org/multipage/imagebitmap-and-animations.html#animation-frames).
This host is intentionally smaller than a browser DOM and only supports this
app's exercised APIs. It is for running trusted project code, not isolating
untrusted scripts.

## Run and replay

From the checkout root, using Node:

```sh
node sim/run.js --seconds 30 --query 'seed=1&n=100&calm&painted'
node sim/run.js --seconds 60 --query 'seed=7&n=100&falcon&painted' --format csv
node sim/run.js --seconds 10 --query 'seed=7&n=100&calm&painted' --inputs sim/example-inputs.json
```

JSON contains page/script hashes, query and actual seed, Node version, virtual
frame timing, a trajectory digest, per-second measurements and complete captured
hunt events. CSV carries metadata in comment lines followed by the measurements.
An omitted seed is replaced with `seed=1`. The host captures events before the
page's 400-event ring evicts them.

Inputs are a JSON array of objects with `atMs`, `type` and event properties such
as `clientX`, `clientY` or `key`. Events are stably sorted by time and dispatched
before the first frame whose end reaches `atMs`; thus handlers see the preceding
frame's virtual clock. The input file hash and this policy are recorded. Times
are relative to the host clock, including when `warm` has already advanced the
simulation at startup. Keep frame timing identical when comparing input replays.

`--html FILE`, `--seconds N` and `--dt-ms N` select the page, duration and frame
interval. Invalid timing and zero-frame runs fail. This milestone retains the
page's existing variable-step/capped frame loop: changing frame rate can change
the trajectory and can discard physical time on slow frames. Fixed physics ticks
and timestep convergence are the next planned stage, not an established result
of this host.

## Gates and differential comparisons

```sh
node sim/check.js
node motion/check.js
node sim/differential.js --seconds 40
node sim/differential.js --seconds 40 --cases 'seed=7&n=40&calm,seed=7&n=40&calm&motion=legacy' --inputs sim/example-inputs.json
node murmuration-check.js murmuration.html 40 'seed=1&calm&n=400'
node murmuration-falcon.js 180 'seed=1&n=400'
```

The differential runner obtains `a5dedcc:murmuration.html` from Git by default,
or accepts `--baseline FILE` / `--baseline-ref REV`. It compares all six position
and velocity arrays, every baseline falcon field and complete hunt events at
every frame, reporting the first mismatch. Identical trajectories establish
preservation of this baseline, not scientific validity. The baseline's sky image
is not present in the temporary extraction directory; that selects a painted
fallback without changing physics. Use `painted` in queries for equivalent
background loading too.

The single-command gate checks repeatability, missing assets, nonfinite drawing
arguments, unsupported Canvas methods, zero-frame rejection and event-ring
capture. Motion checks cover clip topology/loop closure, authored-rig bake error,
actual near/far selection, independent mixed gaits, alarm response, interrupted
falcon transitions and viewer controls. Deliberate bad velocity/geometry inputs
calibrate the observation channel. The legacy numerical checker retains its
independent correlation calculation; its page-bin Eq14 `NaN` means that gate is
not observed, not that the accounting passed.

## Optional PNGs

The default strict Canvas host records calls and rejects nonfinite geometry;
it does not rasterize. For pixel artifacts, supply the optional
[`@napi-rs/canvas` provider](https://github.com/Brooooooklyn/canvas):

```sh
CANVAS_MODULE=/absolute/path/to/@napi-rs/canvas node sim/render-check.js
```

Alternatively use `node sim/render-check.js --canvas-module=/absolute/path/to/module`.
If the provider is installed locally, no argument is needed. Normal simulation
commands do not depend on it. Native `sim/run.js` accepts
`--canvas-module /absolute/path/to/module`; include `painted` in its query because
photo-image decoding is not implemented in this host.

The raster probe writes ignored `sim-output/` PNGs and emits their hashes. It
checks actual default renderer sampling, deterministic fresh runs, a flattened-Z
sentinel, a pointer-launched hunt and both species in four viewer directions.
Fresh runs must have identical draw histories: the flock intentionally
accumulates trails, so repeated draws onto one surface need not be identical.

Native Canvas tests pixels and viewer JavaScript in that renderer. They do not
test browser CSS/layout, browser console, accessibility or browser input delivery.
Rig consistency likewise does not establish measured anatomy or aerodynamic
realism. Current evidence and raw outputs are in
[the milestone record](../docs/FIRST_MILESTONE.md) and `docs/verification/`.

## Local performance profiling

`node sim/profile.js --n=400 --width=2048 --height=1217 --dpr=2` separately times
actual `step`, `draw` and `analyse` functions after 20 unmeasured warm-up calls.
Use `--frames=120`, `--html=/path/to/page.html` and `--mode=xyz|legacy` to select
the comparison. The fixture uses seed1, calm, warm20, painted scenery and 60 Hz
step arguments; it calls these functions directly, rather than advancing the
page's private animation clock. It is an isolated function benchmark, not a
frame-loop or browser FPS measurement.

Supply `--canvas-module=/absolute/path/to/@napi-rs/canvas` or `CANVAS_MODULE` for
rasterization. Without it, results measure the strict call-recording host only.
Compare identical options sequentially on an otherwise idle machine. Output
records page/assets, Node/provider, viewport, median/p95/mean timings and counters;
counters include warm-up. The performance correction's before/after and independent
silhouette evidence is recorded in [the milestone record](../docs/FIRST_MILESTONE.md).
