# First runs (2026-10-06/07): what the reviewers did

Thirteen reviews and the API probes, $8.27 of the $25 budget. Every claim below that contradicts a reviewer was checked against the page's
code or the clip's own pixels, with the magnification stated.

| run | clip | brief | S | R | rules fired |
|---|---|---|---|---|---|
| Pro 3.1 | page_calm | v0.1 (said some clips are renders) | flag | flag | S1 S3 S4, R1-R6 (S2 withheld by G1b) |
| Pro 3.1 | real_calm | v0.1 | flag | flag | S3, R3 R4 R5 R6 |
| Pro 3.1 | real_calm | v0.3 (de-primed) | flag | flag | S1-S4, R1 R3-R6 |
| Flash 3.8 | real_calm | v0.3 | approve | approve | none |

## Pro: fails real starling footage, with or without priming

On real footage of a murmuration at Strumpshaw Fen it reported "identical repeated sprites", birds that "do not
flap their wings at all", and a flock "overlaid on a still photograph" / "superimposed". Checked: at 10.2x on four
consecutive frames, and at 5.3x on its own still s6, birds are 2-6 px blobs of many different shapes in the same
frame; nothing is identical. Removing the brief's "some clips are renderings" sentence made it worse (9 rules
fired instead of 5), and it used overlay language unprompted. Its judgements follow a belief that the clip is
computer-made, not what is in the frames.

On the page it made the same kind of claim: "every bird beats its wings in perfect, locked unison" at 2 Hz, and
"all birds are the exact same size". The page gives every bird its own phase, a rate of 10-14 Hz and a size of
0.85-1.15 on top of perspective (murmuration.html:283). The 2 Hz came from two stills 0.25 s apart in real time.

## Flash: approves real footage, also from things it could not see

It described "foreground birds 15-30 px wide" with starling wings, square tails and short necks. At 10.5x on its
own still s2 the largest birds are about 5-6 px and most are 3-4 px: no tail or bill can be seen. It reported a
10-12 Hz wingbeat from two stills 0.25 s apart. Its verdict on real_calm is right; its evidence is a textbook
description. Whether it discriminates at all is unknown until it sees the page and the broken variants.

## Measurement

- Pro's code measured the page's birds at 6.75 px and 185 birds. True values: 9.9 px median span (7.8-12.5) and
  400 birds. Thresholding trims soft wingtips and merges overlapping birds.
- On real_calm Pro measured 2.5 px yet called the birds resolved; Flash measured 4.2 px. Policy S0 needs about 8 px.

## Our pipeline leaks which clips are real

Slowing a 30 fps camera clip to half speed gives 15 distinct frames a second, which the 24 fps encode pads with
duplicates (frame-to-frame difference 0.00 on every other step or so). Page clips come from 60 fps frames and have
none. Pro's "birds snap rigidly between two shapes" was this. Slowing to 0.8x instead maps a 30 fps camera exactly
onto 24 fps, and gives page and camera clips the same 30 samples a second of real time.

## Changes made because of these runs

- Policy v0.2, gate G1b: a wingbeat rate must rest on at least four cited moments, close enough to sample it, over
  two cycles. It withheld Pro's 2 Hz and Flash's 11 Hz.
- Brief v0.3: no mention of renderings; R4-R6 asked as neutral observations. Runs record the brief's hash and are
  reported per brief.
- get_frame rejects 0-1 fractional boxes (Pro sent four, which became 32 px crops of empty sky).
- make_clip refuses frame sets that are not exactly prefix_0000..N.

# Agentic video (2026-10-07): the mode the review was meant to use

The runs above used static video (every frame at a fixed rate) plus our own `get_frame` stills. Gemini 3.8 Flash
also has agentic video (`processing: "agentic"`): it moves through the clip itself, loading stretches at the frame
rate and resolution it picks. 3.1 Pro does not have it. The clip format changed at the same time (v2: real speed,
30 fps, no duplicated frames), and the brief is v0.4. One run per clip so far.

| clip | S | R | rules fired | control |
|---|---|---|---|---|
| real_calm | needs review (S1 unknown) | approve | none | PASS |
| page_calm | flag | flag | S4, R3 (S2's "0 Hz" withheld under policy v0.3) | (no hard expectation; R5 may fire and did not) |
| page_trail | flag | flag | S1-S4, R1-R5 | PASS (R4 had to fire, and did) |

**On real footage it reported what is there.** Birds 1-3 px in the high ribbon, 2-5 px in the core, larger at the
fringe; tail, neck and bill "cannot" be made out, so S1 stays unknown rather than passing or failing. It tracked
one bird across stills two frames apart and said the flock does not beat in unison. Its 12 Hz was withheld by G1b
(frames two apart cannot sample 12 Hz), which was right: its own up/down sequence implies about 7.5 Hz.

**On the page it still makes claims the pixels contradict.**
- page_calm S2: "wings remain completely rigid ... 0 Hz". At 10.2x on four consecutive frames (00:00.50-00:00.60)
  several birds change from Y to x to lambda shapes frame by frame; a few hold one pose, which is the page's glide
  pause (0.5-1 s). The page beats at 10-14 Hz (murmuration.html:283).
- page_calm S4: "all wings remain outstretched". Same frames: poses vary.
- page_trail S3/R4: "frozen in place for the first 2.4 seconds, then abruptly jumps at 00:02.5". The clip's
  frame-to-frame change is between 0.25 and 0.94 on every step for all 4 s; nothing freezes or jumps.

**One artefact spills into unrelated clauses.** page_calm and page_trail are the same seed, window, 400 birds and
motion (their frame-to-frame change profiles match); the trail clip only adds ghost trails. Yet adding trails flipped
S1 (silhouette) and S3 (flock motion) from clear to fired. Nothing about bird shapes or trajectories changed: the
reviewer that passed real footage still lets one visible fault colour its other judgements.

**Two things changed at once.** The static runs used v1 clips (half speed, duplicated frames in camera clips); the
agentic runs use v2 clips. "Agentic mode is more grounded" is confounded with "v2 has no duplicate-frame tell". One
static Flash run on the v2 real_calm clip (about $0.35) would separate them.

**Policy v0.3.** G1b now also covers a reported rate of zero: "no flapping" needs four moments over more than 1 s,
because glide pauses last up to 1 s. page_calm's "0 Hz" rested on two moments 0.6 s apart and is withheld.

**What holds up so far.** Real footage is no longer failed, the trail control is caught, and R3 (about 250-300
birds counted; the page has 400) is a fair tell. Single runs; agreement across repeats is unmeasured.

## Three runs each (agentic Flash, brief v0.4, policy v0.3)

| clip | S decisions | R decisions | rules fired (of 3 runs) | control |
|---|---|---|---|---|
| real_calm | approve 2, needs review 1 | approve 3 | none | PASS 3/3 |
| page_calm | flag 3 | flag 3 | R3 3, S4 3, S1 2, R1 2, R4 2, R5 2, S2 1, S3 1 | no hard expectation |
| page_trail | flag 3 | flag 3 | R4 3 (required), S1 3, S3 3, S4 3, R1 3, R3 3, R2 2, R5 2, S2 2, R6 1 | PASS 3/3 |

At the verdict level it is consistent: real footage is never failed, the page is always flagged on both axes, and
the trail is always caught. At the clause level the page's tells sort into three groups:

- **True of the page.** R3, too few birds (it counts 200-300; the page has 400; 3/3). R5, no motion blur on wings
  (the page draws none; 2/3). These are the two the page can act on.
- **Plausible, unchecked.** S1 "straight, blunt-tipped cruciform wings, elongated tubular bodies" (2/3) and R4 "hard
  polygonal edges, duplicated silhouette geometry" (2/3): every bird is the same polygon model, so at about 7-10 px
  this may be fair. Worth a zoomed side-by-side with real birds before acting on it.
- **Contradicted.** S4 "all wings outstretched, no stroke-phase variety" (3/3): at 10.2x on consecutive frames
  several birds change pose frame to frame, though the flap may be weak at this size. R1 "birds scale up two- to
  three-fold between 00:00.5 and 00:03.5 without forward translation": the simulation shows the flock receding
  (median depth 155 -> 201) and the median span shrinking from 12.7 to 9.9 px.

# Corrections from two independent reviews (2026-10-07)

Two Codex sessions (gpt-6-astra and gpt-6.1-sol, reasoning effort xhigh, read-only, with their own measurements:
`scratchpad/codex_review/{astra,sol}/report.md`) re-checked everything above. They agree on the following, and
the earlier text is wrong where it says otherwise.

**Mistakes in this file.**
- "True values: 9.9 px median span" compared Pro's measured blob width with the page's *nominal full-spread*
  span. The visible polygon at that moment measures 6.82 px median, so Pro's 6.75 px was right.
- The "about 7.5 Hz" read off one up/down sequence is not a measurement either: too few, unevenly spaced samples.
- Static Flash's two stills (00:00.25 and 00:00.50 of the half-speed clip) were 0.125 s apart in real time, not
  0.25 s. Its own code measured a largest-birds median of 4.2 px (maximum 8.3 px), so "largest about 5-6 px" was
  too precise.
- R1 ("birds grow two- to threefold"): the nominal span does shrink (12.7 -> 9.9 px) as the flock recedes, but the
  drawn area of each bird grows 2.68x (3.8 -> 10.2 px^2) as the birds turn to show more of their wings, and the
  birds read fuller and darker. A 2-3x linear growth is wrong; "the birds look bigger" is a fair reading.
- The trail clip's extra S1/S4 failures are not one fault spilling into unrelated clauses: ghosts really do turn
  each silhouette into a multi-pronged shape. The halo claim above is withdrawn.

**A harness bug produced one of the "false" observations.** get_frame seeks by time, so requests at 00:00.50,
.53, .57, .60 returned frames 15, 16, 18, 18 (and 3.50-3.60 returned 105, 106, 108, 108). Run 062607 compared the
two identical frames, found zero change and called the wings frozen. Stills must be chosen by frame index.

**The other false claims stay false, but for understandable reasons.** Page birds do change shape frame to frame
(half are flapping at any moment, phases are uncorrelated, outlines move 0.5-1.4 px between frames), but at
7-10 px the change is small, a silhouette repeats twice per wingbeat (its 20-28 Hz component aliases at 30 fps),
and a third of the birds are in glide pauses. "Rigid" and "all outstretched" overstate a weak cue; slowing the
wings is not the fix. Stage B's own measurements contradicted these claims (still-to-still differences of 33-36,
non-identical masks) and the final answer kept the prose anyway, because stage B is told to cite stage A's notes,
not to overturn them. One "frozen" measurement tracked a patch of sky.

**Why the page does not look like the footage (measured at 0.5 s, decoded pixels).**

| | real_calm | page_calm |
|---|---|---|
| bird blob size, median (P90) | 3.2 px (6.7-8.2) | 5.5-7.4 px (12.4-17.0); drawn polygons 10.5 px |
| marks in frame | about 2,300-2,600 | 400 birds |
| contrast of a bird against its sky | 0.27 | 0.78 |
| depth spread in the flock | layered: ribbon 2.4 px, core 3.8, fringe 4.2 | depths 145-171 (P10-P90), tone constant (RGB 12-14 at every depth) |
| sky from frame to frame | changes (noise, compression, motion) | identical (a still photograph) |
| motion blur | some | none: each frame is one instant |

The birds are drawn at twice life size (`SPAN = 1.63`, murmuration.html:214), then enlarged 1.23x more at this
window (`sizeK`, line 99). Both reviewers rank undoing that first; on its own it gives a small flock of specks, so
it needs more birds, a flock that spreads over more of the frame, a short exposure (motion blur), and tone that
fades with distance. Moving the camera back alone shrinks the flock without making it denser. `?n=3000` alone
changes the route and brought the flock closer (birds got bigger), and the neighbour search is quadratic: 1.6 ms
per physics step at 400 birds, 24 ms at 3,000, before drawing.

**Harness flaws to fix before more runs.** Stills by frame index, with a consecutive-frame burst; stage B must
reconcile its measurements with stage A's notes; gates must apply to claims, not just to the numeric rate (a
"rigid" claim with a null rate still fires S2; wingbeat and artefact timestamps outside the clip are not checked;
"more than 1 s" accepts exactly 1 s); the schema's per-clause `holds` makes the model decide each clause; R3's
"hundreds" already admits 400 birds; and control PASS needs required findings, not just the absence of forbidden
ones.

# Realism pass, step by step (2026-10-07)

Four drawing-only URL flags, each measured before the next with `pixel_metrics.py`, which treats every clip alike
(background: the median of the 16 neighbouring frames, each shifted to undo the camera's pan; birds: darker than it by
12 grey levels). Defaults are untouched: a default frame renders pixel-identically to before (0 of 3.8 M pixels
differ), and `murmuration-check.js` / `murmuration-falcon.js` / `murmuration-assets.js` give the same output as before
the change.

- `?life`: birds and falcon at life size, with no extra enlargement in small windows.
- `?shutter[=MS]`: a camera exposure (default 1/60 s); birds are drawn at 5 instants over it and averaged.
- `?grain[=K]`: camera noise over the frame, calibrated to the real clip's frame-to-frame sky change.
- `?n=1600` with seed 5 (the only one of 24 seeds whose 1,600-bird flock stays in frame for t 10-14 s).

At frames 15 and 105 (0.5 s and 3.5 s):

| clip | marks | median size | contrast | flock extent (P5-P95) | sky change |
|---|---|---|---|---|---|
| real_calm | 1,960-2,390 | 2.4-3.2 px | 0.16-0.26 | 500-560 x 450-530 px | 0.68 |
| page_calm (default) | 110-250 | 7.1-9.8 px | 0.78-1.0 | 160-210 x 130-200 | 0.03 |
| + ?life | 300-340 | 2.4-3.2 px | 0.29-0.61 | 150-180 x 110-190 | 0.03 |
| + n=1600 (seed 5) | 1,130-1,150 | 2.4-3.2 px | 0.24-0.50 | 230-270 x 190-210 | 0.08 |
| + ?shutter | 1,090-1,150 | 2.4-3.8 px | 0.23-0.39 | 230-270 x 190-210 | 0.08 |
| + ?grain | 1,090-1,130 | 2.4-3.8 px | 0.23-0.39 | 230-270 x 190-210 | 0.65 |

Clips: page_calm_life `d0e65ce6`, page_calm_n1600_life `6c579b92`, ..._shutter `2312dc68`, ..._shutter_grain
`d6c4f997` (clips/key.json). Seen at about 20x (3x nearest-neighbour crop, then 6.6x), the page's birds are now grey
specks of the real birds' size and character instead of dark line-drawn crosses.

Still different:
- **The flock is half the real one's width and height** (a quarter of its area) and its core half as dense. Bird size
  now matches, so in angle the real flock is about twice as wide *relative to its birds*: the page needs a flock about
  twice as many bird-spans across. (Matching size fixes the ratio of distance to focal length, not the distance; the
  real lens is unknown.) At the page's spacing that needs several thousand birds; the page caps N at 3,000 and its
  neighbour search is quadratic.
- **The real camera pans** to follow the flock (1.9 px a frame, about 180 px over 4 s); the page's camera is fixed.
- Nearer page birds are still darker than real ones (contrast 0.39 at frame 105 against 0.16).

Live speed. **Corrected:** the first figures here (47 ms a frame at 1,600 birds, "the live page runs slow") were
taken with the tab in the background, where Chrome throttles it. In the foreground (1200x793 at dpr 2, frames counted
over 3 s on a 120 Hz display): default 400 birds 120 fps, also with `?life&shutter&grain`; 1,600 birds with all three
102 fps; 5,000 birds `?life&grain` 86 fps, with `?shutter` too 33 fps. The page slows its clock only below 30 fps, so
all of these run at real speed. Node timings (in its `vm` sandbox) also overstate the browser's: the 10 s warm-up of
5,000 birds took 4.4 s in Chrome (~7 ms a step) against ~30 ms a step in node.

Grain calibration has a known bias: the real clip's sky change is measured after a sub-pixel shift (to undo the pan),
whose interpolation smooths noise, and the page's is not shifted. So 0.68 slightly understates the real flicker, and
0.65 is on the low side of matched.

The numbers in this section and in "Corrections from two independent reviews" above differ (e.g. real bird size 3.2 vs
2.4-3.2 px, contrast 0.27 vs 0.16-0.26) because they use different background estimates (the reviewers' 9x9 spatial
median vs the pan-corrected temporal median here); compare within a section, not across.

Measurement note: the first version of `pixel_metrics.py` used a median over the whole clip as the background. On
real_calm that turned cloud edges into a 58,000 px "bird" (the pan), so its first figures for the real clip (densest
cell 1.0, sky change 1.08) were wrong; the table above uses the pan-corrected background.

# More birds (2026-10-07)

**Neighbour search.** Above 1,000 birds an exact grid search replaces the all-pairs loop. It is checked bit for bit:
every bird's position, velocity, alarm and bank equal the old code's once a second for 40 s (seeds 1, 3 with
`noise=1.5`, 7 calm, 5 at 1,600 birds, 2 at 1,600 with hunts; 20 s at 3,000). Node (`vm` sandbox, slower than Chrome), per physics step: 1,600
birds 9.4 -> 8.8 ms, 3,000 25 -> 16.6 ms, 5,000 ~30 ms, 10,000 ~61 ms. The gain is modest because at these sizes most of
the step is per-bird work (the noise generator alone is ~20 %), not the neighbour search. The cap is now 10,000.

**Framing big flocks.** Above the old cap of 3,000 the flock spanned half the frame, flew out of it (10-36 % of 5,000
birds at once) and, looping at cruise speed (turn radius ~60+ u), came in to the near limit where its birds drew 1.4x
too large. Only for N > 3,000: waypoints nearer the middle (`WAY_X` .35) and farther off (depth 160-195), and the near
limit at 130 u instead of 75. Flocks of 3,000 or fewer fly exactly as before (same bit-for-bit checks).

At t 10.5 and 13.5 s, 1200x793 window, extent as P5-P95 of bird positions in 1280x720 clip pixels:

| birds | extent | median depth | worst out of frame | seeds |
|---|---|---|---|---|
| 1,600 | 223-257 x 184-200 | 161-195 | 0 % (seed 5; most seeds 10-40 %) | 1-24 |
| 5,000 | 225-418 x 215-309 | 157-178 | 3-13 % | 1-4 |
| 10,000 | 279-471 x 186-374 | 145-182 | 9-19 % | 1-2 |
| real_calm | 500-560 x 450-530 | (bird size matches the page at 145-195) | partly out at the top | |

So more birds closes part of the gap and no more: extent grows as N^(1/3) (1,600 -> 5,000 measured 1.42x, predicted
1.46x), and matching the real extent at this flock shape and spacing would take roughly 20,000-30,000 birds. The rest
would need a flatter, more spread-out flock (a physics change) or a camera that follows a flock allowed to roam.

**Found in passing (default page, not changed):** the waypoint is re-picked whenever the flock is within 100 u of it,
and new waypoints (depth 125-195) are usually within 100 u of a flock at depth 100-170, so for long stretches a new
waypoint is chosen every step (81 in 2 s at 400 birds, seed 1). During those stretches the drive's smoothing restarts
each step and the flock steers at a target that jumps every frame, in effect toward the average waypoint. The flight
statistics in the README were measured with this behaviour.

# Camera that follows the flock (2026-10-07)

`?follow`: the view pans (yaw only) toward the flock centre's bearing, critically damped at 1.2 rad/s, within the
sky photograph's spare width (+-20.6 deg at 1200x793; the photo has no spare height, so no tilt). The flight is
unchanged: positions and velocities are bit-identical to the reference with and without `?follow` (400 and 1,600
birds, 40 s), except that flocks over 3,000 birds then keep the full-width waypoints. The pointer lure and the click
that picks a falcon's prey use the panned view. The pan limit is computed at layout from the photo's known size, so a
warm-up before the photo loads pans the same as the node scanner (t 10 s, seed 1, 5,000 birds: -4.71 deg in both).

5,000 birds, seeds 1-12, t 10-14 s: worst share of birds out of frame 0-0.4 % (fixed camera: 1.4-13 %); the pan
runs at 2.1-4.2 px a frame against real_calm's 1.9.

Clip page_calm_n5000_all_follow (`d1e389f4`; seed 1, `?life&shutter&grain&follow`), frames 15 / 105:

| | real_calm | n=5000, fixed (`3c5260df`) | n=5000, follow (`d1e389f4`) |
|---|---|---|---|
| marks | 1,960-2,390 | 1,360-2,290 | 1,960-1,970 |
| median size | 2.4-3.2 px | 3.8-4.6 px | 3.2-4.6 px |
| contrast | 0.16-0.26 | 0.37-0.44 | 0.32-0.36 |
| extent | 500-560 x 450-530 | 315-347 x 303-352 | 301-394 x 239-336 |
| densest cell | 0.28-0.38 | 0.45-0.46 | 0.39-0.47 |
| camera pan | 1.9 px/frame | 0 | 2.4 px/frame |
| sky change | 0.68 | 0.67 | 0.94 (the sky is resampled at a new sub-pixel offset each frame) |

# Gemini on the 5,000-bird clip (2026-10-07)

Agentic Gemini 3.8 Flash, brief v0.4, ruleset 0.3, stills now chosen by frame number. Clip `3c5260df`
(page_calm_n5000_life_shutter_grain: seed 6, fixed camera). Four attempts: the third timed out (client, 900 s) in its
measuring call, so three completed (that attempt's watching calls, $0.13, are in the ledger; whether the timed-out
call was billed is unknown). Spend $1.84 (ledger $8.27 -> $10.11 of $25).

| run | S (reads as starlings) | R (passes as real) | birds resolved | est. birds | wingbeat |
|---|---|---|---|---|---|
| 081349 | needs_review (S1 unknown: 4-10 px too small for tail shape) | approve | yes | ~5,000 | 12 Hz, withheld by G1 |
| 082205 | approve | approve | yes | ~4,500 | 11.5 Hz, withheld by G1 |
| 084616 | approve (birds unresolved: S1/S2/S4 out of scope) | approve | no | ~4,000 | none |

For comparison, the same harness on the default page (`82eb81f5`, before the stills fix) flagged S and R in 3/3
runs, and on real footage (real_calm) gave R approve 3/3, S approve 2 / needs_review 1. The 5,000-bird page now
draws the real footage's pattern. Every clause holds in runs 081349 and 082205: "rapid flapping at approximately
10-14 Hz ... no synchronous beating" (the page's 10-14 Hz; earlier runs said "0 Hz, rigid"), "natural distribution of
banking angles ... without identical repeated sprites", "natural motion blur along rapid wing movements" and
"natural sensor noise" (`?shutter`, `?grain`). No artefacts reported.

Caveats. An approval means the reviewer found no tells, not that its observations are true: both full runs credit
"atmospheric haze softening distant birds", and the page draws no haze. Run 084616's S approval rests on flock motion
alone because it judged birds unresolved (the scope flaw the Codex review named: `birds_resolved` takes per-bird
clauses out of scope and the axis can still approve). The claim-level gates, stage B's reconciliation with its own
measurements, and control discrimination (Codex review section C) are still unfixed. The follow clip (`d1e389f4`)
has not been reviewed.

Follow clip checked by eye: at maximum pan (frame 119) the sky reaches the frame edge (no gap); clear sky over
consecutive frames 60/61 (9.9x, box (980,120)-(1180,270)) shows the same cloud texture moved ~2 px and the grain, no
visible shimmer, so its higher sky-change figure (0.94) is resampling plus grain rather than a visible artefact.

# Harness fixes, ruleset 0.4 (2026-10-07)

From the Codex reviews' harness sections (astra 2-4 and 6-7, sol 2-4 and 6-7). No API calls; `test_engine.py` holds the
probes (11/11 pass), including each bypass the Codex reviews demonstrated.

Gates now check each claim's own evidence:
- **G1c:** an S2 fault (rigid, synchronised or slow wings) needs 4 moments over more than 1 s, with or without a rate.
  Before, a "rigid" claim with a null rate skipped every check (run 062354 used that route).
- **G3** now also covers wingbeat moments (dropped if outside the clip) and artefacts (an artefact at `99:99` no
  longer fires R4). G1b's "more than 1 s" no longer admits exactly 1 s.
- **G4:** `birds_resolved` must agree with the reviewer's own `bird_span_px_median` (8 px, policy S0), or the scope
  becomes unknown.
  - The engine cannot measure resolvability itself. In real_hunt, isolated blobs measure P50 7.1 px and P90 20.8 px,
    yet at 9.9x (frame 45, box (280,560)-(480,710)) they are vertical motion streaks with no outline.
  - So a pixel span counts blur and merging, not outline.
- **An unknown scope now leaves its rule unknown** whichever way the observation points (before: clear if the
  observation held, unknown if not).
- **S can no longer approve when S1, S2 and S4 are out of scope.** It goes to needs_review, with the reason on the
  card (policy U2: specks cannot be told from other flocking birds).

Stage B now:
- is told its measurements overrule its notes;
- lists any contradictions in a new optional `contradictions` field;
- must set `birds_resolved` to agree with the span it measured.

This is prompt version b2, recorded in `run.json`. It is untested until the next paid run.

Each run now also saves:
- every request body, with images replaced by their hash;
- hashes of the clip, the stills and the source files.

Not done:
- the observation-first schema redesign (astra 5, sol 4);
- carrying a gate's decision from S2 to the same claim reused under S4, which needs claim ids;
- new controls (frozen-wing, synchronised-wing, slow-wing, wrong-shape).

**Rescored saved runs** (S decision and fired rules, against the ruleset each run was scored with at the time):

| clip | run | S at run time | S, ruleset 0.4 | S if G4 used 6 px | R (unchanged) |
|---|---|---|---|---|---|
| real_calm | 055754 / 061811 / 062449 | needs_review / approve / approve | needs_review x3 | needs_review x3 | approve x3 |
| page_calm | 060034 | flag S2,S4 (0.2) | needs_review | flag S4 | flag R3 |
| page_calm | 061814 | flag S1,S4 | needs_review | flag S1,S4 | flag R1,R3,R4,R5 |
| page_calm | 062607 | flag S1-S4 | flag S3 | flag S1-S4 | flag R1,R3,R4,R5 |
| page_trail | 060126 / 061817 / 062354 | flag S1-S4 / S1,S3,S4 / S1-S4 | flag S1-S4 / S3 / S3 | unchanged | flag |
| 5,000 birds | 081349 / 082205 / 084616 | needs_review / approve / approve | needs_review x3 | needs_review x3 | approve x3 |

This revises what was reported earlier today:
- **page_calm:** "S flagged 3/3" rested on S1 and S4 judged at a self-measured 6.8-7.0 px, under the policy's own
  8 px.
- Under 0.4, page_calm's S is needs_review 2/3 and flag 1/3 (S3, flock motion). Real footage and the 5,000-bird clip
  are both S needs_review 3/3 and R approve 3/3.
- The two still differ on R: page_calm is flagged 3/3 (R3 numbers 3/3, R1 scale 2/3), while the 5,000-bird clip and
  real_calm approve.
- The 8 px threshold is the policy's, used as written. At 6 px page_calm would keep its S1/S4 flags; real_calm and
  the 5,000 clip would not change.
- This does not clear the default page's silhouettes. Measured by `pixel_metrics`, page_calm's isolated birds are
  P50 11.2 px, and the sheet crops show outlines. The dropped S1/S4 flags mean the reviewer's own reported evidence
  (6.8-7.0 px) does not meet the policy's scope rule, not that the page's birds cannot be resolved.

**Stricter control scoring** (`controls_added.json`, registered after these runs, so prospective only for unrun
controls):
- real_calm passes (R approve 3/3; S approve or scope-only review 3/3).
- **page_trail fails discrimination:** R4 fires on 100% of trail runs but also on 67% of page_calm runs (lift +33%,
  needed +50%).
  - page_calm's R4 firings are not false trails. Runs 061814 and 062607 report `duplicates` and `hard_edges`:
    "unnaturally straight-edged, polygonal contours lacking optical softness". That is the default page's clean
    vector look.
  - So page_calm is already an R4 positive, and trails cannot lift a rule that already fires. The trail control needs
    a base without that tell (for example `?life&shutter&grain`) before it can test trail detection.
  - Caution on `duplicates`: at small pixel sizes, 70% of real binary components share a shape with another, against
    29% on the page (Codex astra 7). A repeated shape is not proof of a sprite.
  - Collateral on the trail: S3 and R2.
- Card expectations checked: all pass. They are the reviewer's raw reports; G4 overrides page_calm's
  `birds_resolved`.

# Stage-B prompt b2 on a matched pair (2026-10-07)

One run each, ruleset 0.4, $0.90 (ledger $11.02 of $25).
- `contradictions` was used in both runs, once each, to correct the notes' size estimates against a measurement.
- **real_calm (093005): S approve, R approve, reported span 8.7 px.**
  - Earlier runs on the same clip reported 2.5-5.8 px. b2 was the first prompt to name the 8 px threshold.
  - In the region it measured (still s1: frame 30, box (461,432)-(666,547)), `pixel_metrics` finds 283 blobs. The 58
    of 8 px or more are in the dense band. The only 3 isolated birds measure 5.1-5.5 px.
  - At about 33x (s1 at 6.6x), the larger marks are two birds touching.
  - The reported median looks pulled over the line the prompt named.
- **page_calm (093725): S needs_review (birds unresolved, 6.6 px), R approve.**
  - The R approval rests on R5 evidence the clip does not have: "fine sensor grain ... realistic motion blur". This is
    the old clean-frame page. Earlier runs flagged R 3/3.
  - Its first answer was truncated JSON; the one-retry fix call recovered it.
- b3 drops the threshold sentence and keeps the contradictions instruction. The engine applies 8 px (G4) without the
  model seeing it. Untested.

# Defaults: the camera look (2026-10-07)

The page now defaults to what `?n=5000&life&shutter&grain&follow` showed, at the user's request after watching it
live.
- `?classic` restores the earlier defaults; `?life=0`, `?shutter=0`, `?grain=0` and `?follow=0` turn single parts
  off. The old flags (`?life` etc.) still work and are now no-ops.
- **Checks:**
  - `?classic&debug&halt&warm=10&seed=7&calm` renders identically to the old default (0 of 3.8 M pixels differ).
  - The new default with `seed=1&calm` renders identically to the old flag URL.
  - The headless checks at n=400 match the old baselines exactly (check: seed=1, seed=7&calm; falcon 120 s seed=1
    with `classic`).
- **Headless tools:** `murmuration-check.js` now defaults to `seed=1&n=400`. `murmuration-falcon.js` defaults to
  `seed=1&n=400&classic`, because its on-screen overlap counts assume a fixed camera. It warns when the query pans.
  Its hunt statistics do not depend on the view.
- **Hunts with 5,000 birds** (`murmuration-falcon.js 300 "seed=S&n=5000"`, S = 1-4, pooled; 52 strikes in 17 hunts):
  - **In the field range:** strikes per hunt 3.06 (~3); peak stoop speed from above 33.0 m/s (31-39; the single 120 s
    seed's 15.3 m/s was a small sample); hunts with waves 35% (36-42%); wave speed 12.4 m/s (13); attacks with a wave
    in the 5 s before 21% (28%).
  - **Differs:** flash expansions after 21% of strikes (Storms 34%; this page at 400 birds 26%); no split after any
    flash expansion (Storms 22%; at 400 birds 45%); hunts ending in contact 35% (23-24%); strike gaps under 5 s 43%
    (31%).
  - The no-falcon baseline of the expansion metric is 16%, so the 21% is barely above chance.
