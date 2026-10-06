# Physics performance proposals

## Scope and evidence

This is a source-grounded triage for the dirty milestone worktree at base
`a5dedcc`, current page SHA
`d24849dffb2feb6882cece1fa00f56852a5d22f3ddd840559ecd4e05aacf8646`.
No simulation, wall-time profile, browser run, or product edit was made for
this note. “Exact” below means preserving the current page's neighbor sets,
ordering, frame inputs, and resulting trajectory; it does not establish
biological validity.

The main step scans every other bird for each bird and insertion-sorts the
seven smallest squared distances ([`murmuration.html`](../../murmuration.html#L542-L550)).
Those seven neighbors feed the `RN`-limited alignment/cohesion/separation
terms, the nearest-neighbor statistic, and orientation-wave propagation
([lines 554–568](../../murmuration.html#L554-L568)). Acceleration is then
applied in a separate pass before position updates ([lines 666–690](../../murmuration.html#L666-L690)).
So the neighbor search is O(N²) even though K is fixed at 7; `RN=38` is a
cutoff on forces after the global top-K selection, not a cutoff for finding
the nearest birds ([lines 60, 224](../../murmuration.html#L60)).

Correlation analysis is also O(N²): it visits each unordered pair once to
find flock diameter and again to fill distance bins ([`analyse`](../../murmuration.html#L728-L746)).
It runs only while the stats/debug panel is visible, at 0.5 simulated-second
intervals through N=1500 and 1 second above that ([loop](../../murmuration.html#L1115-L1121)).
The documented N=400 isolated native-Canvas fixture measured draw 7.544 ms,
step 1.553 ms, and analysis 4.772 ms per sampled call; these are Node function
timings, not Chrome FPS ([milestone record](../FIRST_MILESTONE.md#L77-L101)).
The profile fixture calls analysis every 30 frames (2/s at 60 Hz)
([`sim/profile.js`](../../sim/profile.js#L12-L18)).

The flight and hunt paths contain research-linked constants and event rules:
`K=7`, the noise and acceleration model, flight speeds, falcon PN delay/gain,
strike stages, flashes, and wave rates ([flock setup](../../murmuration.html#L60-L62),
[falcon setup](../../murmuration.html#L286-L322)). A stoop locks one prey for
its whole pass; wave seeds and pointer launches also scan for a nearest bird
([launch/target selection](../../murmuration.html#L328-L390)). Motion gait,
falcon state, and positions consume the supplied `dt` during each step
([bird update](../../murmuration.html#L666-L690),
[falcon update](../../murmuration.html#L400-L476)).

## Triage portfolio

| Priority | Proposal and evidence level | Mechanism | Smallest useful experiment | Main risk and falsifier |
| --- | --- | --- | --- | --- |
| 1, supported | Compute each unordered bird-pair distance once, feed both birds' exact top-7 buffers, then run the existing force pass. **Source-derived hypothesis; unprobed.** | The current loop evaluates both `(i,j)` and `(j,i)` distances. A pair sweep ordered by larger index can feed candidates to each bird in ascending neighbor-index order, matching today's scan order. Keep strict comparisons and current float arithmetic; store per-bird top-K lists until forces are evaluated. | In a disposable worktree, compare each frame against the current page at fixed 60 Hz for seeded calm and falcon runs, including pointer replay; require exact six position/velocity arrays, every falcon field, and complete hunt history. Then benchmark identical N/viewport/DPR cases sequentially. | A changed tie order, distance rounding, or in-place position mutation breaks exactness. First differing neighbor or frame falsifies preservation. If step timing barely changes, the saved distance arithmetic was not the bottleneck. |
| 2, supported but larger | Exact 3D spatial index for K-nearest lookup. **Algorithmic hypothesis; unprobed.** | Rebuild a uniform grid or tree each step; search cells until a geometric lower bound proves every unseen point is farther than the current seventh neighbor. Preserve tie order by bird index. This can reduce candidate distances in a compact flock while leaving K and `RN` unchanged. | First compare selected neighbor IDs and squared distances against brute force over captured seeded frames, including ties and split flocks; only then run full trajectory/hunt differential and scale timings. Record candidate counts per bird. | Dense cells or broad flock extent can recover O(N²) behavior. Any omitted/reordered equal-distance candidate or need for an unproven radius invalidates the “exact” label. |
| 3, adjacent | Keep a tiny max-heap instead of insertion-sorting each candidate into seven slots. **Source-derived hypothesis; unprobed.** | Reduces top-K maintenance from up to K shifts to log K after each distance calculation; preserves the all-pairs distance scan. Encode the current stable tie rule explicitly. | Compare top-7 IDs/distances on exact snapshots, then time the step at N=100/400/1000/2000. | K is only 7 and the `d2 >= kth` early skip already avoids most shifts after filling. If distance calculation dominates, a heap may add branches without meaningful speedup. |
| 4, adjacent, diagnostics only | Reuse exact pair distances between analysis passes. **Source-derived hypothesis; unprobed.** | First pass stores Float64 squared distances and finds exact L; second pass takes square roots and bins the stored values. This retains analysis time points and formulas while avoiding recomputing coordinate deltas. | Compare `corr` fields and all bins against existing `analyse()` for identical snapshots; inspect memory and GC at each scale before timing the visible panel. | Pair storage is O(N²): about 0.64 MB at N=400 and 16 MB at N=2000 for one Float64 per unordered pair, plus indexing/runtime overhead. A bin-boundary discrepancy or allocation pressure falsifies the trade. |
| 5, counter-inductive | First establish whether physics is worth optimizing for the reported slow animation. **Evidence: local profile only.** | Existing N=400 data show drawing costs about 4.9× the step call in the declared Node/native-Canvas fixture, and Chrome FPS has not been observed. A browser trace may direct effort back to rendering or compositing instead of changing flight. | Measure the current page in the target browser with stats hidden and shown, while recording frame intervals and separating script, Canvas, and presentation costs. Keep this as a diagnostic measurement, not a claim from the Node harness. | Native Canvas rankings may not predict the browser. If browser traces show step work dominates missed frames, this bet is falsified. |

## Scale and work inventory

Counts below are static consequences of the source loops, not measured timings.
Step “directed distances” counts one candidate check for each ordered `i != j`.
Analysis counts the two unordered-pair passes per call. Expected calls/simulated
second use the current visible-panel cadence; the harness profile's cadence is
listed separately above.

| N | Step directed distance checks/frame | Analysis pair visits/call | Visible-panel calls/sim s | Analysis pair visits/sim s |
| ---: | ---: | ---: | ---: | ---: |
| 100 | 9,900 | 9,900 | 2 | 19,800 |
| 400 | 159,600 | 159,600 | 2 | 319,200 |
| 1000 | 999,000 | 999,000 | 2 | 1,998,000 |
| 2000 | 3,998,000 | 3,998,000 | 1 | 3,998,000 |

This matrix is the minimum future benchmark set for proposals 1–4. Keep seed,
calm/falcon mode, frame interval, viewport, DPR, warm-up, and measured frame
count identical between baseline and candidate. Include a forced-falcon case
and click/pointer replay at N=400 or 1000; verify hunt events, not just flock
arrays. The existing differential runner checks arrays, nested falcon state,
and hunt history, and accepts explicit baseline/current files
([`sim/differential.js`](../../sim/differential.js#L10-L40)). No timing result
should be inferred from those equality checks.

## Preserve the model and motion

Do not call a smaller K, smaller timestep, lower simulation frequency, dropped
steps, or less frequent analysis “the same simulation, optimized.” K=7 is the
model's topological interaction count. Reducing it changes which birds align,
cohere, separate, and propagate waves. The loop currently caps each frame's
physics `dt` at 1/30 second and advances once per animation frame; elapsed time
above the cap is discarded ([loop](../../murmuration.html#L1115-L1129)). A fixed
tick or lower tick rate changes the Euler flight updates, noise draws, gait
updates, and 50 ms falcon sighting history unless separately designed and
validated. It is a simulation-method change, not a neighbor-search optimization.

Likewise, reusing last frame's exact K identities is not safe: positions move
before the next search, so neighbor ranks can cross. A cache is eligible only
if it holds a proven conservative superset and re-ranks current distances every
step; then it belongs under the exact spatial-index experiment. Lowering panel
sampling frequency changes diagnostic resolution, although it need not change
physics; preserve sample timestamps for an optimization claim. Do not benchmark
the hunt-analysis script as page cost: `murmuration-falcon.js` has its own
pairwise cluster pass and is an offline diagnostic.

## Handoff

Start with proposal 1 because it offers a narrow arithmetic reduction while
retaining brute-force neighbors as a direct oracle. If exact differential
passes but measured step time does not improve at N=1000/2000, stop before
adding spatial-index complexity. If it helps, compare proposal 2 on identical
snapshots and keep the brute-force path as a debug oracle. Any optimization
must separately report source review, exact headless trajectory/hunt checks,
isolated Node timings, and target-browser frame evidence; none substitutes for
the others.
