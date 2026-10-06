Historical entries below describe the earlier motion-only worktree at base 668e2b5. Current merged-hunt integration evidence is appended below and recorded in docs/FIRST_MILESTONE.md; historical verdicts do not transfer to the new app automatically.

observation: Published starling studies support intermittent flapping, with glides distinct from folded-wing bounds.
status: verified
chain: Tobalske 1995 publisher/PubMed abstract reports 8–18 m/s tunnel trials and all three nonflapping postures; Rayner 2001 author-uploaded full-text Table 1 reports one bird's mean bout timings on printed p.197. Public abstracts and web text were read; original Tobalske PDF remains inaccessible. This confirms observations in those experiments, not a wild-flock distribution.
why non-obvious: Gliding is real but does not imply a fixed universal duty cycle or simultaneous pauses across a flock.

observation: No direct natural-starling-flock wingbeat-phase measurement was located in this search.
status: probed
chain: Separate Luna searches inspected natural-flock turning papers and the 2024 small-group wind-tunnel study; the former filter flap oscillations, and the latter explicitly says it could not measure pairwise phase. Shorebird null phase tests and ibis position-dependent synchrony are adjacent evidence, not starling proof.
why non-obvious: Synchronized turning and heading are different observables from synchronized wingbeats; absence in this search is not proof of absence.

observation: A first table transcription shifted the Rayner frequency values by one speed column.
status: verified
chain: Comparison against the PDF reader's manifest showed the mismatch; original full-text numeric groups include 6.2 m/s continuous flapping at 10.3 Hz, then 8.5/10.2/12.4/14.1 at 10.7/11.2/11.1/11.1 Hz. Corrected source targets and regenerated assets; no public claim of the erroneous values was made.
why non-obvious: Flattened PDF tables can omit dash-filled columns, so agreement between restatements is insufficient.

observation: The new motion code preserved flight trajectories in two deterministic 20-second comparisons.
status: verified
chain: node motion/check.js /tmp/murmuration-before-motion.html compares commit 668e2b5's actual page script against the changed page with DOM stubs, same viewport/seed, calm and falcon queries. All px/py/pz/vx/vy/vz arrays and falcon position/prey matched exactly. Native Canvas separately rendered actual draw paths. Offline evidence only; browser controls are unobserved.
why non-obvious: Adding individualized gait randomness can accidentally alter the simulation RNG; these streams are separate.

observation: Baked XYZ interpolation approximates this Blender rig within 2.1 mm in sampled cycles and dive transitions.
status: verified
chain: Live Blender bake compares 96 withheld phases per clip against evaluated mesh vertices, preserving a 3 mm assertion. Raw maxima: starling flap1.536mm, falcon flap1.502mm, tuck1.570mm, pullout2.093mm. Native starling action keyframes separately matched the browser atlas within1.51micrometres after undoing display translation. These are rig-consistency measurements, not anatomical accuracy.
why non-obvious: A smooth animation can still flatten or mis-time a stroke; shape interpolation and empirical validity require different checks.

observation: Independent saved-file checks confirmed selected Blender/browser correspondence and detected intentional failures.
status: verified
chain: Fresh-context reviewer opened birds-motion.blend in background Blender5.2.2; all37 starling exported action knots differed by at most1.60micrometres; seven falcon shape knots by0.273mm. Wrong-phase sentinel displaced0.291619m; injected vx[0]+.01 caused trajectory equality assertion failure. Actual nativeCanvas defaultdraw reached sampleGait100 times for100birds, legacydraw0; flattenedZ changed raster hash. Snapshot motion-data.js SHA256744e92d6f4a41b651723e499025a25b05e1eaef2d77f02d89a81bca57072e1aa.
why non-obvious: A rendered silhouette alone cannot distinguish true XYZ motion from a 2D fallback; these probes calibrated their observation channels. Browser layout/clicks and dense native-action interpolation remain unobserved.

observation: The combined XYZ app preserves merged main's flight and hunt traces in the declared first-milestone cases.
status: verified
chain: Current sim/differential.js compares actual frame callbacks against a5dedcc for seeds1/7, N100, calm/forced-falcon, 2400 frames each. All six arrays, every baseline falcon field and full hunt events match exactly; docs/verification/differential.json carries the script hashes. Input replay in XYZ and legacy modes also matches; a fresh Sol reviewer independently observed 2400 matching frames in each mode for a pointer-launched hunt. This is baseline-preservation evidence under the named clock/viewport, not empirical validity.
why non-obvious: The two original worktrees separately had the new hunting behavior and the 3D motion; a wholesale stale-HTML port could have removed hunting improvements.

observation: App drawing depends on rendering history as well as the current bird state.
status: verified
chain: A same-state repeat-draw raster assertion failed (69eef256… versus c0f1bbdd…). Source draw() uses fresh?1:TRAIL background opacity with TRAIL=.5. Fresh hosts with identical simulation and draw histories then produced identical 69eef256… PNG hashes; flattening XYZ height changed the hash to b2095c9f…. Raw calibrated results are in docs/verification/raster.json.
why non-obvious: Apparent nondeterministic pixels were an invalid idempotence assumption in the probe, not a localized motion-controller failure.

observation: The newer full Blender lab differs as a file but retains the same base motion geometry and used action curves as the exported scene.
status: verified
chain: Read-only background Blender5.2.2 inventory opened both saved files; their base mesh/bone SHA and used-action keyframe SHA matched. The full file also has a default Scene and unused actions; raw inventory is docs/verification/blender-inventory.txt. No scene was saved or live Blender changed. Constraints/materials were not exhaustively compared.
why non-obvious: Different .blend hashes alone do not establish that the browser is using stale bird geometry.


observation: Far-triangle rendering dominated the local cost of the initial combined app, and contour rendering reduced that cost in the tested fixture.
status: verified
chain: Independent sequential nativeCanvas0.1.100 / Node20.20.1 runs, 2048x1217 CSS/DPR2/N400/seed1/calm/warm20, same 120 measured calls: HTML48277251 draw median17.272ms versus HTMLd24849df 7.544ms; physics1.645/1.553ms. docs/verification/performance-before.json and performance-after.json retain hashes and raw timing. This measures local isolated functions, not Chrome FPS; the initial renderer was introduced in this milestone and its regression is not credited as an independent discovery.
why non-obvious: Reducing path calls by canceling triangle edges at runtime had little benefit, and per-bird fills were slower; compiling far mesh partitions once and retaining their animated XYZ boundaries reduced actual drawing cost.

observation: A DPR2 mask comparison overstated the tested contour silhouette discrepancy because of a diagonal pixel's quantization.
status: verified
chain: Independent baseline/current glyph probe found4/200 cases above0.5CSSpx atDPR2, max0.7071px and1-2 missing pixels. Same CSS projection/LOD at8x raster sampling measured max0.17678px, no far failures, and eight near glyphs were pixel-identical; flatteningZ changed731 pixels and exceeded the0.5px gate. Raw outputs are docs/verification/performance-glyph-dpr2.json and performance-glyph-8x.json. These are foreground-mask measurements in the declared pose matrix, not guarantees for arbitrary poses or anatomical accuracy.
why non-obvious: A thresholded one-pixel diagonal difference is not a continuous silhouette displacement of the same size; the declared0.5CSSpx gate was retained while the observation channel was refined.


observation: Correlation analysis is an important burst-cost candidate at N1000 even though drawing still has the largest median per-frame function cost in the observed fixture.
status: probed
chain: Root ran sim/profile.js --n=1000 --width=2048 --height=1217 --dpr=2 with nativeCanvas0.1.100 at HTMLd24849df; 120 measured direct calls yielded draw median14.528ms, step5.160ms and analyse29.645ms. Raw docs/verification/performance-scale-n1000.json carries the hashes/options. Analysis had only four samples; this does not establish browser stalls or p95 frame cost. The profiler bypasses the actual loop's clock/cadence.
why non-obvious: Optimizing only average draw cost can overlook an infrequent diagnostic burst; moving or accelerating analysis must preserve snapshot timestamps and diagnostic outputs.
