# Murmuration realism implementation plan

Prepared 2026-10-05. This is a proposed implementation sequence, not a claim that the simulator is biologically validated. No product code was changed while preparing it.

Implementation update: the combined rendering/hunting milestone and reusable headless simulator are now recorded in [FIRST_MILESTONE.md](FIRST_MILESTONE.md). Port 8765 was switched to the new milestone worktree after its checks passed. The baseline section below preserves the pre-implementation inspection; stages beyond that first milestone remain proposed.

## Baseline and reconciliation

The other agent's app is merged and pushed: primary checkout `main` and the GitHub `main` branch both resolve to `0d3078f2841f022a78fd6a1c478d9540fedab404`. That merge includes `aade3d3` (falcon hunting/escape) and the earlier intermittent-flight merge `29e5dd6`. Primary checkout `~/prj/murmuration` retains an existing modified `blender/falcon.blend`; the final state refresh also found an untracked `blender/bird_motion_lab.blend`. Preserve both files and inventory the latter before selecting the authoritative authored motion asset.

At inspection, port 8765 serves `/private/tmp/murmuration-wired-20261005`, based on `425fe07` with uncommitted Blender-motion changes. The HTTP HTML hash matches that worktree (`770401b42635c07e22cb09737ba2d0702fc3b5011d606cfdbceb16993f8e4cff`), not merged main (`f3a939e26a1ea715e9f7500aaab12af8d074a2eb2b7eb00ffe523b369ef958fa`). Thus the current served app has 3D motion but the older pursuit behavior; merged main has the newer pursuit/escape behavior but uses 2D outlines. Neither version contains the whole intended next app.

Implementation must start from the merged revision in a fresh worktree, preserve both current checkouts, and port the motion assets/controller selectively. Do not merge the stale motion HTML wholesale: it would replace the new hunt controller. Change the preview server only after the combined build passes checks, and show its commit, worktree and asset revision together.

## Present code and what it establishes

| Surface | Current implementation | Evidence boundary |
| --- | --- | --- |
| Flock | Seven nearest neighbors, separation/alignment/cohesion, persistent OU noise, flock-mean speed control; main `murmuration.html:206,480` | Useful mechanistic model with measured observables; matching one correlation ratio does not validate its individual-flight mechanics. |
| Environment | Waypoints, global centering/rejoining and camera-frustum forces; main `murmuration.html:247,496,557,571,628` | Presentation constraints influence flight and therefore statistics. |
| Gaits | Main has independent 10–14 Hz beats, 10–16-beat bursts, 0.5–1 s glide/bound pauses; motion worktree has Rayner speed-table scheduling and XYZ geometry | Both are currently visual behavior: a gliding bird receives the same force rules as a flapping one. Bound probability and alarm rules are estimates. |
| Body motion | Main bank uses `atan(lat/9)`; wave roll is added during drawing; main `murmuration.html:474,652,866` | World accelerations are in u/s² at 0.5 m/u; denominator 9 is not physical gravity in those units. Roll and trajectory need a shared flight controller. |
| Falcon | Position → stoop → climb → leave, PN gain 2.6, delay/noisy LOS, speed targets and contact proxy; main `murmuration.html:278,383` | Research-informed guidance, with estimated flight envelope and sensing parameters. Closest approach is not observed capture. |
| Falcon shape | Main's four outline poses selected by downward velocity; `murmuration.html:875` | Hunt state, speed, load and shape are not yet consistently connected. |
| Bird geometry | Motion worktree's Blender bake has XYZ, two LODs, phase samples and source hashes | Atlas error against the authored rig is small; skeletal limits, feather folding and biological motion remain partly inferred. |
| Measurements | `murmuration-check.js`, `murmuration-falcon.js`, `murmuration-assets.js`, motion checks | Existing tools mix deterministic accounting checks, simulation outcomes and reference comparisons. They need explicit assertions and comparable observation definitions. |

Fresh baseline probes on merged main:

- `node murmuration-assets.js`: STARLING and FALCON tables match their model exports.
- `node murmuration-check.js murmuration.html 40 'seed=1&calm&n=400'`: mean polarization 0.997; speed 22.90 u/s = 11.45 m/s; velocity-fluctuation RMS 2.08 u/s = 1.04 m/s; flock size 49.5 u = 24.75 m; orientation/speed correlation ratios 0.351/0.341; mean nearest-neighbor distance 2.87 u = 1.44 m. This is one seed and one sampling window, not a population estimate. Independent correlation accounting agreed; the page-bin Eq14 diagnostic printed NaN and needs localization before becoming a gate.
- `node murmuration-falcon.js 180 'seed=1&n=400'`: six strikes in three completed hunts, above-attack peak median 35.0 m/s, guided approach median 88 m and 3.7 s. No wave pulses occurred, so this run cannot validate wave speed. The README's 16-seed aggregate was source-reviewed, not independently rerun here.
- Browser pixels/interactions for the newly merged app were not observed; source review and these Node probes are separate from browser validation.

## Research-to-implementation map

| Reference and scope | Use in this plan | Do not infer |
| --- | --- | --- |
| [Ballerini 2008](https://doi.org/10.1073/pnas.0711437105), wild-starling spatial structure | Topological neighborhood size and neighbor-direction anisotropy; density/neighbor tests | That exactly seven equally weighted omnidirectional neighbors is a complete sensory model. |
| [Cavagna 2010](https://doi.org/10.1073/pnas.1005766107), 24 natural flock events | Compare polarization distribution and full orientation/speed correlation curves across flock sizes; empirical mean Φ 0.96±0.03 and correlation-size slopes about 0.35/0.36 | A single seed with the correct zero crossing establishes all flock realism. |
| [Attanasi 2014](https://doi.org/10.1038/nphys3035) and [2015](https://doi.org/10.1098/rsif.2015.0319), natural turns | Local initiation, curvature propagation, equal-radius turning; directional-information speed about 20–40 m/s in the 2014 events | Those directional turn waves are the same observable as predator agitation/darkening waves, or that wingbeats synchronize. |
| [Tobalske 1995](https://doi.org/10.1242/jeb.198.6.1259), tunnel starlings, abstract accessible | Distinct glide/partial-bound/bound states; increasing bound share with speed is a qualitative constraint | Exact bounds probability, wild-flock duty factor or joint limits from the abstract. |
| [Rayner 2001](https://doi.org/10.1093/icb/41.2.188), Table 1, p.197, one tunnel bird, readable author-uploaded text | A named flap-glide preset; bout-time anchors and qualitative within-cycle acceleration/deceleration | A universal speed law, population variance, or mandatory timing for a flock. |
| [Ben-Gida 2013](https://doi.org/10.1371/journal.pone.0080086), [Stalnov 2015](https://doi.org/10.1371/journal.pone.0134582), continuous flapping at 12 m/s | Stroke excursion, phase timing and sampled force/kinematic envelope | Independent population replication: the papers appear to share experimental material; gliding duty data; exact anatomical limits. |
| [Friman 2024](https://doi.org/10.1073/pnas.2319971121), solo/pairs/trios in a tunnel | Sensitivity experiment for position-dependent cadence/effort, after basic flight calibration | Apply a V formation to a large murmuration or infer phase-locking; their event synchronization was insufficient. |
| [Brighton 2017](https://doi.org/10.1073/pnas.1714532114), tracked trained/captive peregrine terminal attacks | PN trajectory validation and navigation-gain sensitivity | Its fitted median gain is a directly measured law for every wild hunt; a configured gain readback proves correct guidance. |
| [Mills 2018](https://doi.org/10.1371/journal.pcbi.1006044), physics-based simulation | Wingbeat-averaged lift/thrust/drag, roll/load constraints and guidance/flight separation; sensing-delay sensitivity | Treat the assumed 50 ms delay as a measured peregrine latency, or mean modeled load factor 3.4 as measured lateral dodge acceleration 3.4 g. |
| [Ponitz 2014](https://doi.org/10.1371/journal.pone.0086506), one trained 22.5 m/s dive; existing photos/pose fits | Validate a moderate-speed dive and pullout trajectory/shape; retain uncertainties | That its measured posture validates a maximum-speed tuck at 90+ m/s. |
| [Procaccini 2011](https://doi.org/10.1016/j.anbehav.2011.07.006), [Storms 2019](https://doi.org/10.1007/s00265-018-2609-0), observed predator responses; [Hemelrijk 2015](https://doi.org/10.1007/s00265-015-1891-3), explanatory model | Compare escape types and agitation fronts; distinguish measured frequencies from copied-roll mechanism assumptions | Tune one radial-radius threshold and call that the same field-classified flash expansion. |
| [Papadopoulou 2026](https://doi.org/10.1038/s42003-026-10173-4), field observations plus StarEscape | Read supplement and pinned public model before choosing local alertness, escape/refractory and neighbor-update parameters | Copy its reported simulation outputs into an empirical target column. |

The PDFs and access notes already collected are in `~/prj/murmuration-refs/starling/intermittent-flight/README.md`. Tobalske full text and some joint studies remain inaccessible; do not invent missing numerical limits. Before implementation of flight/escape modules, retain the relevant full papers and supplements with hashes and page/table anchors. StarEscape links its versioned model/data on Zenodo and public repositories; use those archives rather than an unpinned moving branch.

## Ordered implementation changes

### 0. Combine the two existing apps without changing flight behavior

Deliverable: merged hunting/escape code plus baked XYZ rendering and the motion viewer in one fresh branch.

- Preserve main's hunt modes, PN sensing queue, target selection, escape waves and event logging.
- Choose a single starling gait controller. Port the motion controller rather than running `paused/ptime/pw` and `Motion.gait` concurrently; normalize individual cadence variation against the correct initialization range. Keep stable IDs and independent RNG streams.
- Feed main's `bank + waveRoll` into the 3D renderer initially. Connect falcon animation directly to position/stoop/climb/leave events, then select shape within each event by speed and load. Replace the stale motion controller's descent-only hunt detection.
- Update both Node harnesses to load external motion scripts before the page code. Current hunt harness only extracts the inline script.
- Show commit, configuration seed, worktree and motion input hashes in a developer status view.

Gate: compare all six flight arrays and the complete hunt event sequence against merged main for seeds 1/7, calm and attacking, at matching dt and durations; rendering/controller consolidation must not consume flight RNG or change guidance. Exercise every hunt mode and interrupted pullout. Compare near/far silhouettes and observe browser controls when access is restored. Preserve the legacy renderer as an explicit comparison mode.

### 1. Make time, units and measurements reliable

Deliverable: a small `sim/` core with shared units/configuration and one fixed-step clock, without retuning behavior.

- Keep current world coordinates but centralize `METRES_PER_UNIT=.5`, physical gravity and conversions. Physical gravity is 19.62 u/s², not 9 u/s². Distinguish net acceleration, lift acceleration and load factor.
- Use an accumulator with fixed physical steps, starting at 120 Hz as a candidate. Compare 60/120/240 Hz offline and retain the cheapest converged step; do not borrow Mills' numerical step without matching its very different controller. Render with interpolation. Cap work per frame and record overload rather than silently changing simulated time.
- Queue pointer/lure/hunt inputs at simulation ticks and replay the same timestamped input stream in comparisons. Replace wall-clock lure expiry with simulation-time expiry. Main currently reads `performance.now()` inside `step` and launches hunts directly from pointer callbacks; fixed physics ticks alone cannot make these interactions invariant to rendering rate.
- Separate deterministic integrator convergence from stochastic population comparisons. Use noise-free, scripted fixtures first. Equal seeds at different timesteps do not supply the same forcing history: main draws fresh OU and sensory random values per step. For coupled stochastic trajectories, generate a common physical-time noise/sensor stream and aggregate OU innovations consistently for coarser steps; otherwise compare ensembles with uncertainty, not pointwise paths. Introduce separate subsystem streams only after the legacy refactor gate passes. Declare observation times and numerical tolerances before the probe.
- Timestamp/interpolate LOS samples and divide angular differences by their actual sample separation; sample noise/sensors independently of render rate.
- Compute continuous closest approach on relative-motion segments, with substeps for curved near passes; record geometric contact separately from a modeled capture decision. At36m/s, a 60 Hz step spans 0.6 m, larger than the 0.2 m contact criterion.
- Assign monotonic event and hunt IDs. Fix ring-buffer consumers so long runs do not stop observing newly shifted events after400 entries. Scope strike gaps to their hunt.
- Turn accounting diagnostics into assertions with known-bad sentinels. Measure visibility/framing-force contributions, nearest-neighbor geometry, gait occupancy, speeds, load, roll and contact.

Gates: identical physical results at 30/60/144 Hz rendering with fixed physics ticks; integration-convergence bounds declared before comparisons; contact crossing and near-miss fixtures; delayed-LOS fixtures; more than 400 events consumed exactly once. Explain the existing Eq14 NaN before asserting that diagnostic. Refactoring must preserve the old baseline at the old timestep; timestep changes are compared for convergence, not byte equality.

### 2. Improve individual gait scheduling and phase transitions

Deliverable: `sim/starling-gait.js` and source-tagged presets in `research/targets.json`.

- Keep independent wingbeat phases. Support continuous flap, flap-glide, partial-bound and bound. Retain a continuous-flap12m/s experimental preset separately from Rayner's intermittent preset.
- Use Rayner's observed means as bout-time anchors:8.5m/s1.14/.64s;10.2m/s1.05/1.01s;12.4m/s1.35/.58s;14.1m/s2.06/.23s. Freeze a sampled bout duration on entry; avoid changing its deadline unpredictably every frame as speed changes.
- Treat interpolation, individual/bout variability, low-speed threshold, partial-bound blending and bound probability as explicit estimates. Compare narrower/wider distributions and alternative bounds probabilities. Report actual realized flapping duty separately from the paper's reported mean duty.
- Schedule transitions through bounded pose trajectories; stop advancing the active stroke during a settled pause. Resume with a continuous recovery path instead of an arbitrary hidden-phase jump. Alarm, climb and high lift demand can curtail a pause; response thresholds remain modeling choices pending data.
- Do not impose a phase-locking rule. Friman supports a later cadence/effort experiment, not phase synchronization. Record phase-order statistics to detect accidental synchronization in our code.

Gates: speed-bin bout/occupancy outputs agree with the chosen preset within its declared modeling tolerance; continuous mode has no pauses; low-load glide and folded bound remain visually distinct; no geometry jumps under interrupted transitions; known synchronized/flattened-Z controls fail the relevant checks. Existing atlas interpolation <3 mm remains a numerical rig gate, not biological validation.

### 3. Couple posture and flight mechanics

Deliverable: `sim/flight-controller.js`, opt-in first, using wingbeat-averaged forces rather than full per-feather CFD.

- Interpret flock/escape accelerations as guidance requests. Flight control converts them to feasible lift, roll and thrust commands; gravity and drag then determine actual acceleration. Avoid adding gravity twice to the existing net-acceleration requests.
- Derive bank from the required lift direction and air-relative velocity. For a level coordinated turn, validate `tan(bank)=lateralAcceleration/9.81` in SI units. Include weight support when reporting load factor; a fixed 3.4 g sideways shove is not the same as load factor 3.4.
- Give flap/glide/bound different thrust and lift envelopes. A glide can preserve speed while losing height, or slow while supporting weight; it should not receive an invisible cruise-speed correction that provides energy. Bounding retains body/tail aerodynamic estimates and gravity, not full spread-wing lift.
- Start with measured species mass/proportions from the existing manifests and conservative aerodynamic coefficients from Mills' model. Mark fitted/model coefficients. Solve required span/effort within the permitted envelope; request flapping when a glide cannot meet lift/turn demand.
- Log energy, work, speed and height by gait. Compare a single-bird Rayner-like case to the reported qualitative speed/height exchange before enabling the controller for a whole flock. Do not force every bird to ±1 m/s because one tunnel bird did so.
- Keep flock-only speed control as a comparison preset. Recalibrate social speed fluctuations jointly with this change so the local physical controller does not erase long-range correlations.

Gates: unpowered trajectories do not spontaneously gain mechanical energy in still air; turning/body bank agree with requested and achieved acceleration; lift limits constrain maneuvers; flap can restore energy; changes in gait produce measurable speed/height differences. Run calm correlation and predator-response checks after each added term. Wind and gusts are deferred until this still-air model is stable.

### 4. Make collective turns and escape originate locally

Deliverable: `sim/flock.js` and `sim/escape.js` with separate directional-turn and agitation-wave measurements.

- Introduce local informed birds or local environmental cues for initiating a turn. Replace the global heading-position lag formula with neighbor-transmitted curvature/turn response in the experimental realism preset.
- Compare a finite-response heading controller against an inertial-curvature controller motivated by Attanasi. Promote whichever matches held-out turn trajectories and remains stable; behavioral inertia is a competing implementation, not a foregone finding.
- Preserve topological interaction while testing visible-neighbor selection, anisotropy and neighbor persistence. Obtain sensory parameters from a species-specific source or a clearly tagged modeling source before setting a field-of-view angle. Use synchronous/double-buffered response updates so array order cannot create faster information transfer.
- Evolve alertness, response latency and refractory state per bird. Preserve localized jinks, collective turns/dives and flash expansion as different responses, informed by observed classifications and StarEscape structure. Read the 2026 supplement/code before assigning its parameters.
- Remove camera-frustum forces from the scientific preset; use camera motion/zoom to keep the flock visible. Any roost attraction should be a named environmental force, with contribution logged. Cinematic framing remains available as a separate preset.

Gates: local initiation precedes downstream responses; turn-front speed is measured in the flock frame and compared to Attanasi's directional-information observable. Agitation-front speed is measured separately against Procaccini/Hemelrijk methodology. Track equal-radius turn structure, spatial response origins, neighbor turnover and shape changes. Compare with copying disabled, global cues disabled, and shuffled bird IDs. A numerical pointwise roll wave alone does not pass the collective-turn gate.

### 5. Improve falcon energetics and pose selection together

Deliverable: `sim/falcon.js` retains PN guidance while sharing feasible-flight control and using explicit animation events.

- Keep proportional navigation and validate its vector sign/geometry on stationary and moving synthetic targets. Compare the law's predicted heading rate, not the configured gain counter. Examine navigation gain, sensing delay and noise separately;50ms is a simulation prior.
- Replace target-speed-driven stoop/zoom behavior with gravity, aerodynamic drag and feasible lift/thrust so kinetic energy gained by losing altitude, less aerodynamic losses, can support the zoom climb. Validate the moderate-speed Ponitz dive first.
- Choose wing spread/tuck and tail fan from physical speed, load demand and hunt phase. Pullout must open wings to meet lift demand; interruptions preserve current geometry. Do not force full tuck merely because vertical speed is negative.
- Keep observed Rome attack-direction tallies as separate presets rather than treating their midpoint as a measured frequency. Separate captive terminal-guidance calibration from wild-flock hunt outcomes.
- Report geometric contact, attempted strike, capture model and hunt success separately. Do not lower contact probability arbitrarily to make 23% appear in the scorecard. Expand sensing/target-selection hypotheses only after trajectory and contact measurements are reliable.

Gates: PN-only steering is perpendicular to velocity as intended; delay/noise tests exercise the correct sampling channel; moderate dive trajectory and energy budget are plausible within stated limits; no instantaneous impossible pullout; multi-seed complete-hunt analysis with uncertainty. Asterisks remain on aggregate comparisons whose source context or field classification differs from our metric.

### 6. Fit the rig to more observations and remove folding shortcuts

Deliverable: better `starling/blender/poses_starling.json`, species rig constraints and regenerated motion atlases.

- Reconcile image-derived top/bottom tip heights with the reported 74° flapping-angle convention before imposing both. Use exact shoulder/wingtip definitions, perspective uncertainty and source images; do not declare conflicting coordinates a rig error without resolving the measurement convention.
- Fit multiple views jointly: silhouette, shoulder-relative height, upstroke span, wrist/primary sweep and tail fan. Reserve whole photo/view sequences for validation rather than neighboring frames from the same fitted sequence. Record view geometry and landmark uncertainty.
- Prioritize the missing starling mid-upstroke span and glide/bound posture. Existing robin/jackdaw proxies remain labeled until direct starling measurements are obtained.
- Replace `scale_x` chord-compression folding with articulated elbow/wrist and feather fan/overlap constraints where reference geometry supports it. Prevent visible inversions/intersections; do not invent anatomical joint-limit ranges from external photos.
- Add pose families for speed/lift demand and left/right asymmetry only as conservative, source-tagged hypotheses. Native Blender and runtime use the same authored trajectories/keys; changes are exported with input hashes and confidence metadata.

Gates: held-out multiview landmark/silhouette residuals improve beyond measurement uncertainty; no negative scaling, flipped triangles or conspicuous folding intersections; atlas and native animation agree; near/far LOD shape differences stay under a predeclared screen-space tolerance. Biological validity requires new direct observations where we currently have proxies; small bake error cannot fill that gap.

### 7. Validate realism across regimes and keep it interactive

Deliverable: a reproducible benchmark/validation matrix with a small preview inspector.

- Acquire and inventory empirical data before claiming empirical holdout validation. Candidate sources are Cavagna's supporting flock data, Attanasi's turning-event supplements and StarEscape's empirical/simulated archive ([Zenodo 19628928](https://doi.org/10.5281/zenodo.19628928)); their usable file-level coverage remains to be checked. Create a manifest of source DOI, file/hash/license, original event/flock/bird IDs, experimental context and provenance. Split measured data by original event or bird, not video frame, and prevent shared Rome/AFAR observations from crossing splits or becoming independent replicas. A single-bird Rayner table cannot establish held-out population validity.
- For each empirical target, name the observation transform (3D trajectories, projected 2D video, digitized figure or field classification), preprocessing, calibration/holdout IDs and predeclared residual tolerance. Reproduce the paper's observable before comparing: radius expansion and geometric contact are simulator proxies until linked to field classifications. If only figures are available, include digitization uncertainty and restrict the claim to agreement with those figures. Stages 3–6 remain experimental until their reference data and quantitative criteria exist.
- Fix a training/calibration simulator seed set and a separate held-out seed set for robustness; this does not replace held-out measured data. Measure calm flight, prescribed local turns, single-bird intermittent flight, and multi-strike hunts separately. Use flock sizes 100/400/1000/1600 and smaller deterministic mechanics fixtures; add 3000-bird performance runs separately.
- Match distributions, not just one score: mean speed, speed fluctuations, Φ, nearest-neighbor spacing/direction, full normalized correlation curves and correlation-size slope, turn-radius distribution, neighbor persistence, gait occupation/dwell, achieved load/roll, escape latencies/fronts and complete-hunt metrics. Carry source contexts and empirical uncertainty into targets.
- Keep measured observations, derived quantities, author-model outputs and our estimates in separate target fields. Do not count related Rome datasets or shared tunnel material as independent replications.
- Make neighborhood search faster with an exact spatial index and deterministic distance/ID tie-breaking; compare every selected topological neighbor against brute force on randomized and adversarial layouts before replacement. Preserve the science while expanding visible flock sizes.
- Retain two geometry LODs and benchmark the actual Canvas path costs. Only move drawing to instanced WebGL if profiling shows a meaningful bottleneck; preserve the trajectory and silhouette oracles.
- Inspector: physical vs cinematic preset, seed/revision, a chosen bird's gait/speed/height/lift demand, and a selectable falcon trajectory. Normal app UI remains simple.
- Browser gate: page identity, external assets, no console/runtime errors, desktop/mobile canvas, controls and attacks, actual screenshot comparison. Existing Chrome automation is blocked by managed-preferences verification; passing offline Canvas is not a substitute.

## Release sequence and priorities

Implement 0 → 1 → 2 first: one combined app, reliable instruments, researched individualized gait. Then 3 as opt-in mechanics, with 4 and 5 calibrated against it. Improve 6 where observations can actually constrain the rig. Apply 7's matrix throughout; optimize only after profiling.

Suggested reviewable changesets: (A) integration, (B) clock/units/events/contact, (C) gait presets/transitions, (D) bank/energy/flight envelope, (E) local turn/escape mechanisms, (F) falcon physical flight and animation, (G) multiview rig fitting, (H) exact neighbor acceleration and final browser validation. Each changeset has its own evidence statement and gate; a passing shipment never implies every biological claim passed.

The first visible milestone is newer hunting/escape behavior plus the existing 3D birds, with meaningful flap/glide variation. The next realism milestone is that posture, energy and trajectory agree: a glide really glides, a bank really turns, and a pullout really consumes the speed gained in a dive.
