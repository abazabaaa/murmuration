# European starling (Sturnus vulgaris) wing poses for a Blender rig

Quantitative pose spec. Every number carries a tag, a source id with figure or page, and a confidence (high / medium / low).

Tags: **[P]** reported by the cited authors (text, table, abstract or caption) | **[Z Nx]** read by me from a figure file in `figs/` or a rendered page, zoom N | **[D]** derived by me from [P]/[Z] inputs, calculation stated | **[E]** estimated, assumed, or borrowed from another species (named). Only [P] and [Z] are measurements. [D] inherits the uncertainty of its inputs. [E] is a design guess.

Source ids are listed at the end. `BG13`/`ST15` figures are in `figs/`, PDFs in `papers/`. Page numbers are PDF pages of the files in `papers/`.

## Conventions

- Bird used by BG13 and ST15 (one starling in the AFAR tunnel, 12 m/s): full span b0 = 0.382 m, mean chord 0.06 m, AR 6.4, mass 78 g, body width 0.04 m [P, BG13 p3; ST15 p8]. So S = b0^2/AR = 0.0228 m^2 and wing loading = 33.6 N/m^2 [D]. Semi-span 0.191 m. Shoulder-to-tip length L = 0.18 m (range 0.176-0.191) [E: (0.382 - 0.03 shoulder spacing)/2].
- BL = bill tip to tail tip. For the BG13 bird BL = 0.229 m [Z 3.2x, BG13 Fig 2: scale from the 60 cm field-of-view bar read at 1.5x, bill tip and tail tip digitised on the 3.2x crop; +/-5 percent]. So b0/BL = 1.67 [D]. The flock literature uses a typical BL = 0.20 m and WS = 0.40 m, b0/BL = 2.0 [P, BA08 Fig 5 caption, arXiv p29]. Use 1.7-2.0.
- Elevation = angle above the body-horizontal plane, front view, positive up. Sweep = aft angle from the lateral axis, seen from above. Tip height = vertical distance of the wingtip above (+) or below (-) the shoulder in a side view.
- Elbow and wrist angles are interior angles (180 deg = straight), as in DI91.
- Side-view photographs flatten 3-D. The near wing is also closer to the camera than the body plane, which enlarges it by an unknown few percent. Tip heights below carry +/-15 percent. Elevation, sweep and span derived from them are weaker still.
- phase t/T runs 0 = start of downstroke (wing at the top). Downstroke fraction tau = 0.46, so mid-downstroke 0.23, start of upstroke 0.46, mid-upstroke 0.73.

## Wingbeat timing (applies to every flap pose)

- Frequency 10.3, 10.7, 11.2, 11.1, 11.1 Hz at 6.2, 8.5, 10.2, 12.4, 14.1 m/s [P, RA01 Table 1, p197; one bird, 50 Hz video; table text is scrambled in the copy I read, frequencies unambiguous, see notes.md] - high for that bird.
- 13.3 Hz mean at 12 m/s, per beat 12.8, 14.7, 13.9, 11.9 Hz [P, BG13 Table 1, p5] - high. Larger than RA01, different bird and method (laser PIV tunnel, free flight).
- Frequency rises with speed over 8-18 m/s; wingbeat amplitude smallest at intermediate speeds, differences not significant [P, TO95 abstract] - medium (abstract only).
- Use 12 Hz (period 83 ms) as the default at 10-12 m/s, range 10-14 Hz [E, from the three rows above].
- Downstroke fraction tau = 0.46 (beats: 0.46, 0.47, 0.50, 0.43) [Z 1.5x (1.2x for beat 4), BG13 Fig 8, lambda_d/(lambda_d+lambda_u) from the labels 0.43/0.50, 0.38/0.43, 0.43/0.43, 0.43/0.58 m] - medium-high. The wake wavelengths sum to U/f in every beat (0.93 vs 0.938, 0.81 vs 0.816, 0.86 vs 0.863, 1.01 vs 1.008 m at U = 12 m/s) [D], so they are convected durations and the ratio is a time fraction. At 13.3 Hz: downstroke 35 ms, upstroke 40 ms [D]. Related passerine: robin tau 0.44-0.49 at 4-9 m/s [P, HE06 p269] - medium.
- Tip peak-to-peak vertical amplitude 0.28 m [P, BG13 p3; ST15 p8] - high. Strouhal number 0.30 (0.24-0.34) [P, BG13 Table 1].
- Stroke plane: side-view tip path runs about perpendicular to the body line. Tip lean aft of the body normal is 5-13 deg at the top and 21-24 deg at the bottom [Z 2-6.5x, BG13 Fig 4 frames 1a/1b; ST15 Fig 3 frames (d)/(c); see poses 2 and 4]. The body line is pitched 8.8 deg nose-up in the tunnel [P, ST15 Fig 3 caption, p10], so the tip path is within about 10 deg of vertical in the flow frame [D] - low. Stroke-plane angle ~90 deg to the flow.

## The poses

### 1. Glide

No starling glide measurements were found. Span and tail follow the jackdaw (wing loading 29.9 N/m^2 vs 33.6, AR 6.1 vs 6.4 [D from RH01 Table 2: 0.18 kg, 0.059 m^2, 0.60 m]), so speeds map with a factor of 0.94 [D]. Starlings glide at 8-18 m/s [P, TO95 abstract].

- Span fraction b/b0 = 1.239 - 0.0488 V (V in m/s, glide range 6-11, N = 66, r^2 = 0.79) [P, RH01 Fig 2, p1158; jackdaw] - high for the jackdaw. For the starling [D]: 6 m/s 0.95 | 7 0.90 | 8 0.85 | 9 0.80 | 10 0.75 | 11 0.70 | 12 0.65 | 13 0.60 (12 and above is extrapolated). Rig default at 9-10 m/s: **0.78**, range 0.70-0.85. Confidence - medium for the trend, low for the exact values on a starling.
- Wing area ratio S/Smax = -0.014 + 0.97 (b/bmax) [P, RH01 Fig 4, p1160; reduced major axis, N = 66], so area falls about in proportion to span - high for the jackdaw. Manually flexed jackdaw wing: S = 0.0665 b^2 + 0.0316 b + 0.0156 (m, m^2; r^2 = 0.99, N = 15) [P, RH01 Fig 3].
- Hand sweep: if the whole span loss came from the wrist, with the arm half of the semi-span [E] and the hand and primaries the other half, then sweep = acos((b/b0 - 0.5)/0.5): 26 deg at 0.95, 37 at 0.90, 46 at 0.85, 53 at 0.80, 60 at 0.75 [D]. This is an upper bound, because the elbow also folds and the primaries close up. Rig target 30-45 deg at span 0.78. Confidence - low. Tune it to hit the span fraction, do not trust the angle.
- Arm (humerus) sweep: no glide data. In flapping the humerus holds 55 deg protraction through the downstroke [P, DI91 abstract]. DI91 does not define the reference axis in the abstract. I read it as 55 deg from the aft body axis, so 35 deg aft of lateral [E]. Use 0-35 deg aft for the glide and check against the span ratio. Confidence - low.
- Elbow and wrist: maximum extension seen in flapping is elbow 120 deg, wrist 160 deg [P, DI91 abstract]. Use as the extended reference for the glide [E]. Confidence - low.
- Front-view dihedral: not found. Use 5 deg (0-10) at the wrist, tips level [E] - low.
- Tail: furled at 9 m/s and above in the jackdaw, spread at 6.1 m/s with 2.1 times the folded area, area falls linearly from 0.0107 m^2 (6 m/s) to 0.0059 (9) [P, RH01 p1159, Fig 5]. Starling equivalent: fan 0-0.25 at 9-10 m/s, 1.0 below about 7 m/s [E]. Maximum apex angle on starlings: about 62 deg [P, MR01 Fig 1 data, theta 1-31 deg is the half-angle; Fig 3 caption gives apex 50 deg for theta 25 deg] - medium. Map fan = apex/62 deg.
- Feet retracted at 8.5 m/s and above (jackdaw) [P, RH01 p1158].
- Measure on the model: tip-to-tip distance / full span (target 0.78); wrist-to-tip angle seen from above; wing planform area ratio (target 0.74); tail apex angle.

### 2. flap_top (start of downstroke, t/T = 0)

- Tip height +13.1 cm (frame 1a) and +16.0 cm (ST15 frame d); at BL = 0.229 m these are +0.57 and +0.70 BL, or 0.69 and 0.84 semi-span [Z 6.5x, BG13 Fig 4 frame 1a; Z 2.2x, ST15 Fig 3 (d)]. Use +12 to +16 cm, central +14 cm - medium. After allowing for near-wing enlargement the central value may be nearer +12.5 cm [E].
- Elevation of the shoulder-to-tip line +45 deg (38-60) [D: asin(h/L), h = 11-16 cm, L = 17.6-19.1 cm] - low. It is large because the tip is only 0.6-0.85 of L above the shoulder. I cannot separate a straight arm at +45 deg from a folded arm at +60 deg in a side photo.
- Humerus elevation +80 to +90 deg above horizontal; elbow and wrist interior angles 90 deg or less (cineradiography, 9-20 m/s) [P, DI91 abstract] - medium (abstract only; the abstract says "extended to 90 deg or less", I read it as folded to 90 deg or less). Consistent with the photos: BG13 Fig 4 frame 1a at 6.5x shows a wrist bulge on the leading edge and primaries splayed aft.
- Tip aft of the shoulder by 0.06-0.13 BL (1.3-2.9 cm) [Z 6.5x and 2.2x, same frames], so the hand leans aft of the body normal by 5-13 deg in side view. 3-D hand sweep 5-15 deg [D] - low.
- Front-view projected span = (0.03 + 2 L cos(elevation))/b0 = 0.75 at +45 deg, 0.55 at +60 deg [D] - low.
- Tail: no data; use fan 0.3 [E].
- Measure on the model: tip height above the shoulder in BL (target +0.60); humerus elevation (+85 deg); elbow and wrist interior angle (90 deg).

### 3. flap_mid (mid-downstroke, t/T = 0.23)

- Span fraction 1.0 by definition of the span ratio R = b(mid-upstroke)/b(mid-downstroke) [P, HE06 methods; HGRS06 pp536-537]. Maximum span 0.382 m for the BG13 bird [P, BG13 p3] - high.
- Wingtip passes below the beak here, which is how RA01 counted wingbeats [P, RA01 section 'Starling flight in a wind tunnel', pp195-196] - medium. So the tip height is about 0 relative to the shoulder [D, symmetric stroke] - medium.
- Humerus horizontal, humeral protraction 55 deg, elbow 120 deg, wrist 160 deg (maximum extension) [P, DI91 abstract] - medium.
- Pronation: the chord at 2/3 semi-span points leading-edge-down 13 deg to the horizontal flow, giving a local angle of attack of 15 deg. Vertical wing-section speed there is 6.2 m/s at 12 m/s flow [Z 1.55x, BG13 Fig 5b]. I checked the sign: atan(6.2/12) = 27.3 deg minus 13 deg = 14.3 deg, matching the 15 deg label. Relative to the body line (pitched 8.8 deg nose-up [P, ST15]) the chord is then about 22 deg leading-edge-down [D] - medium for 13 deg, low for 22 deg.
- Tip zigzag angle phi = 26-34 deg, mean 31 deg [P, BG13 Table 1; assumes constant vertical speed, not measured] - medium.
- Front-view dihedral 0 deg; hand sweep 10-20 deg [E, same value as the falcon spec; no starling measurement] - low.
- Measure on the model: tip height (0), elbow/wrist interior angles (120/160), chord pitch at 2/3 span (13 deg LE-down in the flow frame).

### 4. flap_bottom (start of upstroke, t/T = 0.46)

- Tip depth -16.0 cm (BG13 frame 1b, tip fades into the dark floor, +/-1.5 cm) and -14.7 cm (ST15 frame c); at BL = 0.229 m these are -0.70 and -0.64 BL, or -0.84 and -0.77 semi-span [Z 5.4x, BG13 Fig 4 frame 1b; Z 1.9x, ST15 Fig 3 (c)]. Use -14.5 to -16.5 cm, central -15.5 cm - medium.
- Cross-check against the published amplitude: top + bottom = 13-16 + 15-16 cm = 28-32 cm, vs 28 cm peak-to-peak [P, BG13 p3] - supports the scale and the BL calibration to +/-10 percent.
- Elevation of the shoulder-to-tip line -55 deg (-46 to -65) [D: asin(h/L)] - low. With the top value the total tip-line excursion is about 100 deg (90-125). An independent check: 0.28 m peak-to-peak with L = 0.18 m gives +/-51 deg if symmetric [D].
- Humeral depression stops at about -20 deg below horizontal; the distal wing keeps descending by humeral rotation and wrist adduction [P, DI91 abstract] - medium.
- Tip aft of the shoulder by 0.27-0.28 BL (6.2-6.4 cm) [Z 5.4x and 1.9x]. The wing hangs with its tip trailing 21-24 deg aft of the body normal in side view. 3-D hand sweep 25-50 deg [D, strongly dependent on L at this high elevation] - low. Primaries fan and trail (BG13 Fig 4 frame 1b, Fig 2 and Fig 5a all show a broad fan with the trailing edge angled aft).
- Front-view projected span = 0.62 b0 at -55 deg [D] - low.
- Measure on the model: tip depth in BL (target -0.68); projected lean of the wing aft of vertical (22 deg).

### 5. upstroke_mid (flexed, t/T = 0.73)

No starling mid-upstroke span ratio or posture was found in open sources. TO95 measured "wingspan at mid-upstroke" at 8-18 m/s but only the abstract is open, so the numbers are not obtained. Related passerines were used.

- Span ratio R = b(mid-up)/b(mid-down) = **0.50** (range 0.40-0.60) [E, from passerines]. Robin: 0.33 +/- 0.02 at 4 m/s rising to 0.49 +/- 0.02 at 9 m/s [P, HE06 p269]. Thrush nightingale: R rises with speed, values not obtained [P, RH04 abstract]. House martin and barn swallow: the opposite trend [P, HGRS06 p545]. A starling at 8-14 m/s is near the top of the robin range. Confidence - low.
- Posture type: flexed wing with the hand swept aft, wrists adducted, rather than a tip-reversal upstroke. Pointed-wing birds adduct the wrists and supinate the hand wing [P, TO11 hummingbird section, text]; the pigeon tip-reversal is shown for slow flight [P, TO11 Fig 10.16]. For starlings at 8-20 m/s the cineradiography shows flexion of the elbow and carpometacarpus in early upstroke [P, DI91 abstract]. The only slow starling data is RA01 at 6.2 m/s (continuous, erratic flapping, no wing kinematics given), so I cannot say at what speed a tip-reversal upstroke would appear [E: below about 6-8 m/s]. Confidence - medium for flexed at 8+ m/s, low for the slow-speed claim.
- Humerus: retracts early in the upstroke to within about 30 deg of the body axis (about 60 deg aft of lateral if the angle is from the aft axis [E]), then protracts while elevating; rapid humeral counter-rotation at mid-upstroke turns the ventral wing surface to face laterally; elbow and wrist extension start sequentially after it [P, DI91 abstract] - medium. Wrist leads the wing, hand trails.
- Elbow about 90-100 deg, wrist about 90-110 deg interior at mid-upstroke [E: interpolation between the flexed top and extended mid-downstroke values of DI91] - low.
- Tip height about 0 (passing up through the shoulder level) [E: symmetric stroke] - low. Humerus elevation about +30 deg [E: midpoint of -20 and +85] - low.
- Tail: no data; fan 0.2 [E].
- Measure on the model: tip-to-tip distance / mid-downstroke tip-to-tip (target 0.50); hand sweep (45-60 deg).

### 6. upstroke_top (late upstroke, t/T about 0.88-1.0)

- Span ratio recovers from 0.5 to the flap_top value, front-view projected span 0.55-0.75 b0 [D: pose 2]. Elbow and carpometacarpus extend further and humeral protraction completes at the upstroke-downstroke transition [P, DI91 abstract] - medium.
- Humerus reaches +80 to +90 deg [P, DI91 abstract]; tip height rises to +12-16 cm [Z, pose 2].
- Pull-out postures after a bound consist of an increase in wingspan without a change in wingtip elevation [P, TO95 abstract] - medium. Use this for the span-up transition out of a bound.
- Measure on the model: the rate at which span ratio goes 0.5 to 0.7 over the last 15 percent of the cycle.

### 7. Folded / bound (intermittent flight)

Supported. Starlings alternate flapping with glides, partial-bounds and bounds from 8 to 18 m/s; glides are most frequent and longest, but the percentage of bounds rises markedly with speed [P, TO95 abstract]. A bound holds the wings tightly against the body [P, TO11 "Intermittent flight" section]. Rose-coloured starlings (Sturnus roseus) show both undulating and bounding with no systematic change over 9-14 m/s [P, EN06 abstract].

- Span fraction 0.12-0.20 b0. The floor is body width / b0 = 0.04/0.382 = 0.105 [D from ST15 p8]; the folded wings add a little [E] - low.
- Posture: wing bones folded to the body, wingtips trailing along the flank toward the tail base, elbow and wrist tightly flexed [E; the wording follows TO11]. Tail furled, fan 0 [E]. No starling bound outlines or angles were found (the TO95 percentages are in a paywalled figure).
- Partial-bound (wings partly extended): span 0.3-0.5 b0 [E] - low.
- Timing: at 14.1 m/s the non-flapping pause lasts 0.23 s with a duty factor of 0.83 [P, RA01 Table 1]. At that speed these pauses are most likely bounds, but the paper's table does not label them [E].
- Measure on the model: width / length of the folded silhouette (about 0.2 including wings) and pause duration.

### 8. turn_bank

No individual starling bank angle or turning-wing posture was found.

- Flock level: flock 32-06 flew at 9.6 m/s [P, BA08 Table 1, p24]. Over the 3.6 s turn the angle between the flock's yaw axis and gravity rose from 18 to 39 deg (the flock plane rolled about 21 deg into the turn), and the centripetal acceleration peaked at 5.7 m/s^2 at t = 2.0 s [Z 3.3x, BA08 Fig 4e, arXiv p28; right axis 0-8 m/s^2 read against the 4 and 6 ticks]. Banked-turn equivalent [D: coordinated turn, tan(bank) = a/g]: bank 30 deg, radius v^2/a = 16 m, load factor 1/cos(bank) = 1.16 - medium for the numbers, low for applying them to single birds. BA08 says flocks bank into turns "even though individual birds will bank during the turn" [P, BA08 text, arXiv p10]; this is stated, not measured.
- Bank vs radius at 10 m/s [D]: 15 deg 38 m | 20 deg 28 m | 30 deg 18 m | 45 deg 10 m | 60 deg 6 m. Load factor 1.04 | 1.06 | 1.15 | 1.41 | 2.0.
- Spontaneous flock turns of 120 deg are made along equal-radius paths with each bird turning about a different centre at the same speed [P, AT15 Fig 4 and p5; text]. Event E6 tracks are tight arches 12-14 m wide that rise from 3-5 m to 11-12 m height and fall again [Z 5.5x, AT15 Fig 4b]: an inclined turning plane, not a level banked turn, so I did not use them for bank.
- Rig recommendation: roll the whole body about its long axis, default 30 deg, range 15-45 deg, symmetric wings [E]. For flapping turns, cockatoos use banked flapping turns where the heading change per wingbeat correlates with roll angle at mid-downstroke [P, HB07 abstract], and pigeons steer by whole-body rotation redirecting a fixed-direction aerodynamic force [P, RO11 abstract]. These are not starlings. Span asymmetry between inner and outer wing: not found; start with none.
- Measure on the model: body roll vs turn rate; with the wing plane normal tilted to the same roll.

## Wingbeat cycle at a glance (flapping, 10-12 m/s, tau = 0.46)

| phase | t/T | tip height | shoulder-tip elevation | humerus elevation | elbow / wrist | span vs mid-downstroke | evidence |
|---|---|---|---|---|---|---|---|
| top, start of downstroke | 0.00 | +12 to +16 cm | +45 deg (38-60) | +80 to +90 deg | <=90 / <=90 | front-view 0.55-0.75 | BG13 1a, ST15 d, DI91 |
| mid-downstroke | 0.23 | about 0 | 0 | 0 deg | 120 / 160 | 1.0 | DI91, RA01, BG13 Fig 5 |
| bottom, start of upstroke | 0.46 | -14.5 to -16.5 cm | -55 deg (-46 to -65) | about -20 deg | flexion begins | front-view about 0.62 | BG13 1b, ST15 c, DI91 |
| mid-upstroke | 0.73 | about 0 | 0 | about +30 deg [E] | about 90-100 / 90-110 [E] | 0.50 [E] | DI91, HE06 proxy |
| late upstroke | 0.88-1.0 | rising to +12 | rising | to +85 deg | extending | 0.5 to 0.7 | DI91, TO95 |

## Flap-glide-bound schedule (Q3, Q4)

Single starling, tunnel, 50 Hz video [P, RA01 Table 1, p197; scrambled table, per-speed values below are the self-consistent ones]:

| speed m/s | duty factor | flapping s | pause s | cycle s | flaps per burst [D = flap s x Hz] |
|---|---|---|---|---|---|
| 6.2 | continuous, erratic | - | - | - | - |
| 8.5 | 0.65 | 1.14 | 0.64 | 1.78 | 12 |
| 10.2 | 0.55 | 1.05 | 1.01 | 2.06 | 12 |
| 12.4 | 0.70 | 1.35 | 0.58 | 1.93 | 15 |
| 14.1 | 0.83 | 2.06 | 0.23 | 2.29 | 23 |

- Regular undulating flight above about 7.5 m/s [P, RA01 section 'Starling flight in a wind tunnel', pp195-196]. At 12.4 m/s the glides last about 0.5 s [P, RA01 Fig 4 caption, p198].
- TO95 reports the flapping duration and the number of wingbeats per cycle are greatest at 8 m/s, which disagrees with the rising trend in RA01 above 10 m/s. Different birds and methods. For a murmuration at about 10 m/s use bursts of about 12 beats (1.0-1.4 s) and pauses of 0.6-1.0 s, duty about 0.55-0.70 [P, RA01]. Minimum-power speed about 12 m/s [P, TO95 abstract]; duty is U-shaped with speed [P, TO11].

## Tail (Q7)

- Maximum spread tested on mounted frozen starlings: half-angle theta 31 deg, apex 62 deg; tail lift coefficient (mean about 0.38) independent of spread [P, MR01 abstract]; furled at theta 1 deg [P, MR01 Fig 1 and Fig 2 data and results text] - medium. The tails were set by hand at 4.9 m/s, so this is the range, not what live birds do.
- Live use: spread at slow speed and furled at cruise, with area 2.1 times the folded area at 6.1 m/s and fully folded at 9 m/s and above (jackdaw) [P, RH01 p1159, Fig 5] - medium. The tail also serves manoeuvrability, stability, pitch control and body-drag reduction at cruise [P, MR01 introduction].
- Rig map: fan 0 = apex 0-5 deg (furled), fan 1 = apex 62 deg. Defaults: glide 9-10 m/s 0-0.25; flap 0.2-0.3; bound 0; slow glide and landing 1.0 [E].

## Wing morphing and outlines (Q6)

- Published starling photographs at the stroke extremes, CC BY: BG13 Fig 4 (four beats, top and bottom frames), ST15 Fig 3 (three beats), BG13 Fig 5a (wing pointing at the camera after the tip passes below the shoulder) and BG13 Fig 2 (late downstroke) - all in `figs/`. They show the top fan (primaries splayed aft, wrist bulge on the leading edge) and the hanging fan at the bottom.
- No open-access starling outlines at graded flexion, mid-upstroke or glide were found.
- Numeric morphing law (jackdaw): area ratio = -0.014 + 0.97 x span ratio; flexed S = 0.0665 b^2 + 0.0316 b + 0.0156 [P, RH01 Figs 3, 4].

## Gaps - where no starling data exists, and what was used

| gap | stand-in | confidence |
|---|---|---|
| Mid-upstroke span ratio and hand sweep | robin R 0.33-0.49 (HE06); thrush nightingale and house martin trends (RH04, HGRS06) | low |
| Glide span, wing area, hand sweep | jackdaw regressions (RH01) at matched wing loading; hand sweep from geometry | low-medium (span), low (sweep) |
| Front-view dihedral in glide and flap | none; 5 deg assumed | low |
| Tail fan in flight | frozen-starling range (MR01); jackdaw tail area vs speed (RH01) | low-medium |
| Elbow and wrist angles in glide | DI91 flapping extremes | low |
| Individual bank angle and turning posture | flock acceleration (BA08) with a coordinated-turn model; cockatoo (HB07) and pigeon (RO11) mechanics | low |
| Bound posture and percentage of bounds vs speed | TO95 abstract, TO11 text, RA01 pauses | low |
| Starling outlines at graded flexion | only top and bottom frames | - |
| Tip-line elevation at top and bottom | geometric estimate from photos; ST15 quotes phi from -55 to +19 deg (74 deg total) [P, ST15 p11]. The bottom matches (-55 deg), the +19 deg top does not match its own Fig 3 frames, where the wing is near vertical at the start of downstroke | low |
| Which humerus angle convention DI91 uses | abstract only; interpreted | low |

## Sources

- BG13: Ben-Gida H, Kirchhefer AJ, Taylor ZJ, Bezner-Kerr W, Guglielmo CG, Kopp GA, Gurka R (2013) Estimation of unsteady aerodynamics in the wake of a freely flying European starling (Sturnus vulgaris). PLOS ONE 8(11):e80086. CC BY 4.0. doi:10.1371/journal.pone.0080086
- ST15: Stalnov O, Ben-Gida H, Kirchhefer AJ, Guglielmo CG, Kopp GA, Liberzon A, Gurka R (2015) On the estimation of time dependent lift of a European starling (Sturnus vulgaris) during flapping flight. PLOS ONE 10(9):e0134582. CC BY 4.0. doi:10.1371/journal.pone.0134582
- RA01: Rayner JMV, Viscardi PW, Ward S, Speakman JR (2001) Aerodynamics and energetics of intermittent flight in birds. Am Zool 41:188-204. Reference only.
- TO95: Tobalske BW (1995) Neuromuscular control and kinematics of intermittent flight in the European starling (Sturnus vulgaris). J Exp Biol 198:1259-1273. doi:10.1242/jeb.198.6.1259. Abstract only (PubMed 9319121).
- TO11: Tobalske BW, Warrick DR, Jackson BE, Dial KP (2011) Morphological and behavioral correlates of flapping flight, ch. 10 in Dyke G, Kaiser G (eds) Living Dinosaurs. Wiley-Blackwell. Reference only.
- DI91: Dial KP, Goslow GE, Jenkins FA (1991) The functional anatomy of the shoulder in the European starling (Sturnus vulgaris). J Morphol 207:327-344. doi:10.1002/jmor.1052070309. Abstract only (PubMed 29865507).
- MR01: Maybury WJ, Rayner JMV, Couldrick LB (2001) Lift generation by the avian tail. Proc R Soc B 268:1443-1448. doi:10.1098/rspb.2001.1666. Reference only (read from the PMC PDF; not stored).
- RH01: Rosén M, Hedenström A (2001) Gliding flight in a jackdaw: a wind tunnel study. J Exp Biol 204:1153-1166. Reference only.
- HE06: Hedenström A, Rosén M, Spedding GR (2006) Vortex wakes generated by robins Erithacus rubecula during free flight in a wind tunnel. J R Soc Interface 3:263-276. Reference only.
- HGRS06: Hedenström A, van Griethuijsen L, Rosén M, Spedding GR (2006) Vortex wakes of birds: recent developments using digital particle image velocimetry in a wind tunnel. Anim Biol 56:535-549. Reference only.
- RH04: Rosén M, Spedding GR, Hedenström A (2004) The relationship between wingbeat kinematics and vortex wake of a thrush nightingale. J Exp Biol 207:4255-4268. doi:10.1242/jeb.01283. Abstract only.
- BA08: Ballerini M et al. (2008) Empirical investigation of starling flocks: a benchmark study in collective animal behaviour. Anim Behav 76:201-215 (arXiv:0802.1667). Reference only.
- AT15: Attanasi A et al. (2015) Emergence of collective changes in travel direction of starling flocks from individual birds' fluctuations. J R Soc Interface 12:20150319 (arXiv:1410.3330). Reference only.
- EN06: Engel S, Biebach H, Visser GH (2006) Metabolic costs of avian flight in relation to flight velocity: a study in Rose Coloured Starlings. J Comp Physiol B 176:415-427. Abstract only.
- HB07: Hedrick TL, Biewener AA (2007) Low speed maneuvering flight of the rose-breasted cockatoo (Eolophus roseicapillus). I. Kinematic and neuromuscular control of turning. J Exp Biol 210:1897-1911. Abstract only.
- RO11: Ros IG, Bassman LC, Badger MA, Pierson AN, Biewener AA (2011) Pigeons steer like helicopters and generate down- and upstroke lift during low speed turns. PNAS 108:19990-19995. Abstract only.
