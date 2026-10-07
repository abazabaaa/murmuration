# Starling murmuration realism policy (video review)

**Version 0.4 (2026-10-07).** Gates check each claim's own evidence, after the independent Codex reviews showed claims
slipping past them: an S2 fault with no rate was never checked (G1c); wingbeat moments and artefacts outside the clip
were counted (G3); "more than 1 s" admitted exactly 1 s (G1b). Resolvability is now checked against the reviewer's
own measured span (G4), an undecided scope leaves its rules undecided, and S cannot approve when S1, S2 and S4 are out
of scope (Decisions): before, S approved distant specks on flock motion alone, which U2 rules out.

**Version 0.3 (2026-10-07).** G1b also covers a reported rate of zero: in the first agentic review the reviewer
reported 0 Hz for the page, which skipped the v0.2 check entirely.

**Version 0.2 (2026-10-06).** G1 now also checks the moments a wingbeat rate is measured from (G1b). Why: in the
first review (page_calm, Pro) the reviewer read 2 beats per second from two stills 0.25 s apart in real time, which
cannot show a 10-14 Hz wingbeat; the page's birds beat at 10-14 Hz with random phases (murmuration.html:283).
Version 0.1 was written before any clip was reviewed. The outcomes expected on the
control clips are pre-registered in `controls.json`, so the policy can be judged by whether it passes real footage
and catches the deliberately broken clips, not by whether it likes the page.

## Purpose

A clip of a starling murmuration is reviewed on two questions, which get separate verdicts:

- **S. Does it read as starlings?** Would an experienced birder take these for European starlings (*Sturnus
  vulgaris*) flying in a murmuration: their shape, their flight and how the flock moves?
- **R. Could it pass as real footage?** Would a viewer take the clip for video of a real scene: the birds' scale,
  tone and number, the light, the camera and the absence of rendering artefacts?

A clip can read as starlings and still not pass as real footage (a good animation), and the reverse (real
footage of something else). Neither verdict is a single overall impression: each comes from the clauses below.

The reviewer (Gemini) only reports what it sees, with timestamps and the stills it inspected. It decides nothing.
A deterministic engine (`engine.py`) applies the compiled rules (`ruleset.json`) to those observations, and checks
the evidence against facts about the clip that the reviewer never states (its sampling rate, which stills exist).

## How reviewers must report

- **Timestamps.** Every observation cites at least one moment as `MM:SS.s` in video time. An observation with no
  valid timestamp is treated as not made.
- **Stills for fine detail.** Claims about the shape or attitude of individual birds (S1, S4) must cite stills the
  reviewer requested with `get_frame` and actually looked at, by their id. A claim about bird shape made from the
  video alone is withheld, because the video is sampled at a fraction of the resolution of a still.
- **Real time.** Clips play at real speed (format v2; v1 clips were slowed to half speed). Rates are wingbeats per
  second of real time.
- **Unknown is an answer.** When something cannot be judged from the clip (birds too small to resolve, no predator
  in view), the field is null. Nulls are never treated as passes: a rule that needs a null field routes the clip to
  human review.
- **Search** is for general facts about real starlings and murmurations, never for the clip or this prompt.

## S. Reads as starlings

**S0. Resolvability (scope, not a rule).** Individual birds are *resolved* when their outline (wings, body, tail)
can be made out in a still, roughly 8 px or more from wingtip to wingtip. S1, S2 and S4 apply only to clips with
resolved birds. A dense, distant flock of 1-3 px specks can still be judged on S3.

**S1. Silhouette.** Resolved birds have the starling outline: short, triangular, pointed, slightly swept-back
wings; a short square tail; a compact body with a short neck and a pointed bill. Long tails, broad rounded wings,
or shapes that are not birds are a fault.

**S2. Flight mode.** Starlings flap rapidly (about 10-14 beats per second in cruising flight) in bursts of 10-16
beats, separated by short glides or bounds (wings briefly spread or folded). A flock whose birds never change pose,
or all beat in unison, or flap slowly and deeply like a large bird (under about 6 beats per second) is a fault.
A wingbeat rate can only be reported if the clip samples fast enough to show it (see gate G1).

**S3. Flock motion.** The flock moves as one coherent, highly aligned group whose outline changes fluidly; density
varies smoothly (denser cores, sparser edges); neighbours keep a fairly even spacing (about one body length to a
few) and turn together. Birds that jitter, jump between frames, pass through each other, reverse instantly or move
independently of their neighbours are a fault.

**S4. Attitude variety.** At any moment, resolved birds show a range of attitudes: some banking, wings at different
points of the stroke, different angles to the camera. Many birds drawn as identical copies (same pose, same angle)
are a fault.

**S5. Predator (scope: a raptor is visible).** A peregrine falcon is about twice a starling's span, with long
pointed wings and a longer tail, flies fast and stoops steeply; the flock reacts as it approaches (birds turn
away, gaps open, the flock splits or darkens in travelling bands). A predator with the wrong shape or size, or a
flock that ignores a close pass, is a fault.

*On the card, not a rule:* orientation waves (dark or light bands travelling through the flock, usually away
from the predator, in pulses about 1 s apart), their count and interval. They occur in only some real hunts, so
their absence proves nothing, and no control clip has wrong waves to test a rule against.

## R. Passes as real footage

**R1. Scale.** Birds' apparent size is consistent with the flock's extent and with distance: farther birds look
smaller, and no bird is implausibly large next to its neighbours or the scene.

**R2. Tone and colour.** Against a bright sky, birds are near-black or dark grey silhouettes whose tone fits the
light (slightly lighter with distance and haze). Visible colour casts (purple, blue), birds that are see-through,
or tones that ignore the light are a fault.

**R3. Numbers.** A murmuration has hundreds to tens of thousands of birds; dense parts thicken optically into dark
masses. A flock too sparse or too small for a murmuration at that distance is a fault.

**R4. Rendering artefacts.** Real video has none of: ghost copies or trails behind moving birds, birds popping in
or out, flicker, stair-stepped or perfectly hard vector edges, identical repeated sprites, or birds drawn over
things they should be behind.

**R5. Camera signature.** Real footage carries a camera's marks: sensor noise or grain, compression, some motion
blur on fast wings, limited depth of field or softness, exposure suited to the scene. A perfectly clean,
noise-free, infinitely sharp image is a fault. This clause is kept apart from R1-R4 so that a missing camera look
does not hide the other findings.

**R6. Scene.** Sky, light direction, horizon and haze are consistent with each other, and the flock sits in the
scene (lit by the same light, at a plausible height and distance), not pasted over it.

## G. Gates on the evidence (applied by the engine from the clip's metadata)

**G1. Sampling.** A rate can only be seen if the clip samples at more than twice that rate. Each clip's manifest
records its real-time sampling rate (30 per second for every clip since clip format v2). A reported
wingbeat rate at or above half the sampling rate is withheld (set to unknown), and an S2 fault judged in the same
clip is set to unknown too, since the engine cannot tell whether the fault rested on the rate.

**G1b. Sampling of the cited moments.** A wingbeat rate is only as good as the moments it was read from. A
reported rate needs at least four cited moments, no two consecutive ones as far apart as half a wingbeat period
(in real time), covering at least two periods. Otherwise it is withheld as under G1, with the same consequence
for an S2 fault. A rate of zero ("no flapping") is a claim too: starlings glide for 0.5-1 s between bursts, so it needs
at least four cited moments spanning more than 1 s (v0.3; exactly 1 s is not more, v0.4).

**G1c. An S2 fault's own moments (v0.4).** Rigid, synchronised or slow wings are a claim about more than one moment,
with or without a rate: the S2 observation must itself cite at least four moments spanning more than 1 s (longer
than a glide pause). Otherwise it is set to unknown.

**G2. Stills.** An S1 or S4 judgement that cites no still the reviewer actually requested and received is withheld,
and the S verdict is then *withheld* rather than made.

**G3. Timestamps.** A judged field whose timestamps are missing or outside the clip is set to unknown. Wingbeat
moments outside the clip are dropped before G1b counts them, and an artefact with no moment inside the clip is not
counted for R4 (v0.4).

**G4. Scope consistency (v0.4).** S0 is the reviewer's judgement, but it must agree with the reviewer's own
measurement: `birds_resolved` true with a median span under 8 px, or false with 8 px or more, sets resolvability to
unknown, and then S1, S2 and S4 are unknown too (not out of scope, not clear). The engine does not measure the birds
itself: in real footage dark streaks of motion blur and pairs of touching birds measure 8-25 px without any outline
showing (real_hunt, frame 45), so a pixel span cannot stand in for the judgement.

## Decisions

Per axis (S and R separately):

| decision | S label | R label | meaning |
|---|---|---|---|
| approve | reads as starlings | passes as real | every in-scope rule is clear |
| flag | does not read as starlings | tells found | at least one rule fired; the card lists which and why |
| needs_review | needs review | needs review | no rule fired, but at least one could not be decided, or (S only, v0.4) birds are not resolved so S1, S2 and S4 were out of scope |
| withheld | withheld | withheld | the evidence for a required judgement failed a gate |

## Uncompilable

- **U1.** "Looks like the real thing overall." Not a rule: it would let a single impression override the clauses.
- **U2.** Species identity of distant specks. At 1-3 px nothing distinguishes starlings from other flocking birds;
  the clip's context decides, and S1 is out of scope.
