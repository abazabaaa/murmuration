# Peregrine (Falco peregrinus) wing poses for a Blender rig

Quantitative pose spec. Every number is tagged **[M]** measured by code or by zoom-checked landmarks on a file in this folder, **[P]** taken from a paper, or **[E]** estimated or assumed. File ids: `cmNNN` = `commons/cmNNN_*.jpg`, `Fig7` = `ponitz2014/fig007.png`, `Selim1/2` = `selim2020_fig1/2_*.png`.

## Conventions

- L = bill tip to tail tip. Full span b0 = 0.873 m [P, Mills 2018 Table 4]; b0/L is about 2.4 [M, below].
- Sweep (Lambda) = angle of a segment, seen from above or below, from the lateral axis. Positive is aft.
- Elevation = angle above the body-horizontal plane, seen from the front. Positive is up.
- "Aft of bill" positions are fractions of L along the body axis.
- Elbow and wrist angles are given as flexion from full extension. Elbow interior angle = 166 deg minus flexion [P, Tang et al.].
- Landmark measurements are 2-D. Bank, roll and foreshortening contaminate them, so the sweep and span figures carry roughly +/-10 percent.

## The five poses

### 1. Glide (full spread)
- b/L = 2.40 (cm072), 2.52 (cm028), 2.16 (cm016, banked) [M]. Use 2.4.
- Arm sweep 0 +/-5 deg. Hand sweep 10-20 deg. Whole-leading-edge sweep 5-10 deg (spread of -9 to +24 deg is bank noise) [M].
- Elevation 0 +/-10 deg. The wings are flat in head-on frames (cm047, cm012) [M].
- Wingtips 0.30-0.45 L aft of the bill, about at shoulder level [M, noisy].
- Elbow flexion 0 (interior 166 deg). Wrist flexion 0-10 deg [P, E].

### 2. Mid-downstroke (level flapping)
- Span fraction 1.0, same planform as the glide. Projected span = b0 x cos(elevation).
- Elevation crosses 0 deg at mid-stroke. cm047 shows wings flat, bank 20 deg, mean elevation about 0 deg [M].
- Total stroke amplitude 72 deg, so about +/-36 deg about horizontal [P, Mills: 0.4 pi rad from slow-motion video]. Allometry gives 70 deg [P].
- Head-on top-of-stroke frame cm181 shows +37 deg on both wings [M], which is consistent with +/-36 deg.
- Wing slightly pronated (leading edge down). Elbow flexion 0-10 deg, wrist 0-10 deg [E].
- Frequency 5.1 Hz, the maximum for the species [P, Mills Table 4]. Climbing Eleonora's falcon: 4.68 Hz [P, Hedenstrom; recalled from earlier reading, not re-verified].

### 3. Upstroke, hand-wing flexed
- Span fraction 0.5-0.7 [E, not peregrine-specific]. Basis: Hedenstrom, Johansson & Spedding 2009 give R = b_up/b_down of 0.6-0.8 at slow speed for non-passerines, falling with airspeed. Tobalske et al. 2011 say pointed-wing birds adduct the wrists and supinate the hand wing on the upstroke.
- Wrist leads, as the highest point of the wing. The hand trails aft and is swept 30-60 deg [E].
- cm126 (zoom 2.2x) shows the top-of-upstroke posture: arm near vertical, primaries trailing aft [M, qualitative].
- Joint flexion 15-37 deg at the elbow and 23-56 deg at the wrist. The wrist flexes about 1.5 times the elbow because of the radius/ulna linkage [P, Tang: 15.54/37.18 deg elbow, 22.84/55.65 deg wrist, half to full contraction]. This is a cadaver and a bionic model, so treat it as low confidence.
- Over the upstroke the arm elevation rises from about -36 to +36 deg [E, from the amplitude above].

### 4. Early stoop, wings tucked (teardrop / diamond)
- Width/length 0.257 (Fig7 A) and about 0.36 (Fig7 B) [M, mask]. This is body plus folded wings, so span fraction is about 0.11-0.15 of b0.
- Hand sweep about 80-90 deg, primaries parallel to the body axis [P, Selim Lambda_max = 90 deg]. Wrists tucked at the shoulders.
- Wingtips end about 0.88 L from the bill, about 0.12 L short of the tail tip, with the tail furled [M, Fig7 A at 3.5x; low-medium confidence].
- Elbow interior about 129 deg or less, wrist flexion 56 deg or more [P, Tang full contraction].
- Head down, body axis near the flight path (alpha about 5 deg at equilibrium [P, Ponitz Fig 13]).
- **Caveat:** the Ponitz birds only reached 22.5 m/s (81 km/h) and showed the diamond / cupped-front shapes (Fig7 A-C). Tucker's full tuck at 190-240 km/h is not photographed in any file here.

### 5. Late stoop / pull-out, wings partly open (M-shape, cupped)
- 5a, early pull-out (Lambda_max): span/L 0.76, hands hang parallel to the body, wrists 0.14 L aft of the head top and 0.25-0.28 L off the midline. Tips about 0.10 L short of the tail tip [M, Selim2 a, zoom 4.1x]. The inboard wing is swept forward: wrists sit about 0.08 L ahead of the shoulder valley. Fig7 D (fanned tail): width/length about 0.8 +/-0.15 [M, manual, low confidence].
- 5b, further open (Lambda_min): span/L 1.62, hand sweep 52 deg measured (the figure labels it 40 deg), wrists 0.08 L aft of the head top and 0.27-0.34 L off the midline, tips 0.69-0.74 L aft of the head top [M, Selim2 b, zoom 3.0x].
- Photos agree with 5b. cm018 (zoom 8.6x): span/L 1.68, hand sweep 48-51 deg, arm forward 25-29 deg, wrist 0.09 L forward of the root, tips 0.69-0.74 L. cm070 (zoom 4.5x): span/L 1.22, hand sweep 58 deg, arm forward 10-26 deg, tips 0.72-0.78 L [M].
- Front view (cupped / M): wrists level with the back at 0.41-0.51 half-span. Hands droop about 58-61 deg below horizontal [M, Selim1 CAD]. Trunk width is 0.46 of the span (cupped) and 0.33 (M). cm192 shows this from below and ahead (foreshortened, qualitative).
- CAD plan span/L (Selim1): cupped 0.49, M-shape 0.57 [M].
- Pull-out lift: up to 18x weight at reduced span versus 1.7x at full span [P, Tucker 1998 abstract; not re-verified].

## Wingbeat cycle at a glance

| phase | wing elevation | evidence |
|---|---|---|
| Top of upstroke | +36 deg level flight; 51-77 deg in manoeuvring flaps | cm181, cm191, cm185, cm126 |
| Mid-downstroke | about 0 deg | cm047 |
| Bottom of downstroke | -36 deg nominal; take-off frames show the wing nearly vertical, down and about 29 deg forward | cm008, cm007 |
| Upstroke | rising, wrist leading, hand flexed | cm126, literature |

## Not found

- Tucker 1998 and Tucker, Cade & Tucker 1998 are paywalled. Abstracts only, no figures.
- No peregrine-specific level-cruise wingbeat frequency and no measured peregrine upstroke span ratio. The numbers above are the species maximum and a generic non-passerine range.
- No Commons photo of a true high-speed tucked stoop. Fig7 is the only stoop photo set.
- The Adana frames (cm019-027) are a banked soaring turn, not a wingbeat sequence. Their phase is not time-stamped.

## Sources

- Ponitz B, Schmitz A, Fischer D, Bleckmann H, Bruecker C (2014) PLOS ONE 9(2):e86506.
- Ponitz B, Triep M, Bruecker C (2014) Open J Fluid Dyn 4:363.
- Selim et al. (2020) arXiv:2008.03948.
- Mills R, Hildenbrandt H, Taylor GK, Hemelrijk CK (2018) PLOS Comput Biol 14:e1006044.
- Tang et al., Falco peregrinus wing skeleton (PMC10986943, PMC11630695).
- Hedenstrom A, Johansson LC, Spedding GR (2009) Bioinspir Biomim 4:015001.
- Tobalske BW et al. (2011) ch. 10 in Morphological and Behavioral Correlates of Flapping Flight.
