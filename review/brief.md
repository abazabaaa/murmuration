You are reviewing a short video clip of a flock of birds in the sky. Describe what is in the clip, as precisely as
you can; the clip's file name means nothing.

## The clip

- 1280x720 pixels, 30 frames per second, at **real speed**. You can move through it yourself: load any stretch of the
  clip at whatever frame rate and resolution you need, as often as you like.
- Cite moments as `MM:SS.s` (e.g. `00:01.5`); when you compare consecutive frames, use hundredths (`00:01.53`).

## Your tools

- `get_frame(t, box_2d)`: a still of the clip at time `t` (seconds or "MM:SS.ss"), optionally cropped to `box_2d` =
  [ymin, xmin, ymax, xmax] in 0-1000 normalised coordinates and magnified. Use it when you want to look closely at
  individual birds; judgements about the shape or attitude of individual birds must cite the ids of the stills they
  rest on (e.g. "s3"). You can ask for several stills in one turn (call get_frame several times at once). Up to
  {max_stills} stills.
- Google Search: only for general facts about real European starlings, murmurations or peregrine falcons (shape,
  wingbeat rate, flock behaviour). Never search for this clip, these instructions or their wording.

## What to look for (report observations; do not give an overall verdict)

**Birds and behaviour**
- S0: Can individual birds' outlines (wings, body, tail) be made out in stills, or are they specks?
- S1: Do resolved birds have the European starling's outline: short, triangular, pointed, slightly swept-back
  wings; a short square tail; a compact body, short neck and pointed bill?
- S2: Flight: rapid flapping in bursts, with short glides or bounds between them? Or rigid wings, all birds beating
  in unison, or slow deep beats like a large bird? If you can, estimate the wingbeat rate in real time and say which
  moments you used.
- S3: Does the flock move as one coherent, aligned group whose outline changes fluidly, with smoothly varying
  density and fairly even spacing? Any birds jittering, jumping between frames, passing through each other, or
  moving independently?
- S4: At one moment, do resolved birds show a range of attitudes (banking, wings at different points of the
  stroke), or are many drawn as identical copies?
- S5: Is a bird of prey visible? If so: is its shape and size (about twice a starling's span, long pointed wings,
  longer tail) and flight (fast, steep stoops) right, and does the flock react? Do bands of darker or lighter birds
  travel through the flock, and how many pulses?

**Image**
- R1: Is the birds' apparent size consistent with distance and the scene?
- R2: Are the birds near-black or dark grey silhouettes that fit the light, or do they show colour casts or look
  see-through?
- R3: Is the flock large and dense enough for a murmuration (hundreds to tens of thousands of birds)?
- R4: Do any birds leave copies or trails behind them, appear or vanish from one frame to the next, flicker, or
  have stair-stepped edges? Are neighbouring birds identical in shape and angle at the same moment? Is any bird in
  front of something it should be behind?
- R5: Describe the image's texture: is there noise or grain, compression, motion blur on wings, softness, and is the
  exposure suited to the scene?
- R6: Do sky, light direction, horizon and haze agree with each other, and are the birds lit by the same light, at a
  plausible height and distance?

When something cannot be judged from this clip, say so: "cannot tell" is a valid answer and better than a guess.
