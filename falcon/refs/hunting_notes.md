# Peregrine hunting behaviour: notes for the murmuration falcon

Research notes only. Morphology and dive poses are in `README.md`, `pose_spec.md` and `HANDOVER.md`; not repeated here. Nothing in the page was changed.

Conversion used throughout: 1 world unit (u) = 0.5 m, so 1 m = 2 u, 1 m/s = 2 u/s, 1 m/s^2 = 2 u/s^2. Angular rates and gains (rad/s, 1/s) do not change.

Current page falcon (murmuration.html ~261-318, read only): speed 28-32 u/s (14-16 m/s), steering gain 2.4/s on velocity error, accel cap 55 u/s^2 (27.5 m/s^2, 2.8 g), aim point = prey + 0.35 s of prey velocity, retarget on nearest bird every 1.2-1.8 s, hunt ends at 9 s (leave) / 17 s. Starlings: CRUISE 23 u/s (11.5 m/s), VMAX 30 u/s (15 m/s), x1.3 when alarmed (39 u/s = 19.5 m/s), R_FLEE 65 u (32.5 m).

## Evidence tags

- **[M]** measured: field, lab or flight-trial observation.
- **[F]** parameter fitted to measured trajectories (statistical model of real data).
- **[S]** simulation output or model assumption (not an observation).
- **[abs]** I read the abstract only.
- **[2nd]** number I only saw quoted inside another paper I read.
- **[D]** derived by me from printed numbers (arithmetic shown).

## 0. What I read, and how fully

| Source | Access | Caveat |
|---|---|---|
| Brighton, Thomas, Taylor 2017 PNAS | Full text (PMC5754800); equations read from the MathML | Supplement not read. Fig/Table numbers not recoverable from the PMC text, so I cite section names |
| Brighton & Taylor 2019 Nat Commun (Harris' hawk) | Full text (PMC6560099) | Hawk, used for contrast and for a measured delay |
| Brighton, Chapman, Fox, Taylor 2021 JEB (gyrfalcon vs peregrine) | Full text (PMC7938797) | Only 4 peregrines, towed lure |
| Brighton et al. 2022 bioRxiv (raptors vs bat swarms) | Full text of preprint | Preprint, Swainson's hawk, not a falcon |
| Mills, Hildenbrandt, Taylor, Hemelrijk 2018 PLoS CB | Full text (PMC5896925) incl. Methods and Appendix K | Figures not seen; Table 1 read as text |
| Mills, Taylor, Hemelrijk 2019 J Avian Biol | Full text (PMC7613156) | Starling catch-success percentages are in figures only (not read) |
| Ponitz et al. 2014 PLoS ONE | Full text (PMC3914994) | One trained falcon, 60 m dam |
| Tucker 1998 JEB 201:403 | **Abstract only** | Theory of "ideal falcons" |
| Tucker, Cade & Tucker 1998 JEB 201:2061 | **Abstract only** | Gyrfalcon, not peregrine |
| Tucker et al. 2000 JEB 203:3755 | **Abstract only** | Wild peregrine approach paths |
| Alerstam 1987 Ibis 129:267 | **Abstract only** (abstract text via ResearchGate page) | Only measured wild stoop speeds I found |
| Zoratto et al. 2010 J Avian Biol 41:427 | **Abstract only** (paywalled) | See section 3. An academia.edu page carries AI-generated "key takeaways" (60.9% vs 18.8%, 2.4 min, 86.8 s vs 157.7 s). Unverified, one of its lines is plainly wrong, so I did not use them |
| Procaccini et al. 2011 Anim Behav 82:759 | Full text (open Taverne PDF at Groningen) | Same Rome roost data as Zoratto and Storms |
| Storms et al. 2019 Behav Ecol Sociobiol | Full text (PMC6404399) | Supplement not read; Fig. 2 pie counts not readable as text |
| Storms et al. 2024 J R Soc Interface (RobotFalcon) | Full text (PMC11061643) | Robot predator |
| Papadopoulou et al. 2022 PLoS CB (pigeons, HoPE) | Full text (PMC8782486) | Pigeons |
| Papadopoulou et al. 2022 R Soc Open Sci (pigeons) | Full text, searched not read line by line | Pigeons |
| Papadopoulou et al. 2026 Commun Biol (starlings, StarEscape) | Full text (PMC13448496) | Parameter table is in a supplement I did not read |
| Hemelrijk et al. 2015 BES (StarDisplay waves) | Full text (PMC4564680) | Model |
| Attanasi et al. 2014 Nat Phys | Full text (PMC4173114), relevant passages | Turning flocks; I could not confirm the turns were predator-triggered |
| Dekker 2009 PhD thesis, Wageningen (WUR edepot 51224) | Full text; read Ch. 3, 7, 9, 11 and the synthesis | Primary field data, mostly shorebirds and ducks, not starlings |
| Carere et al. 2009 Anim Behav 77:101 | **Abstract only** | |

Not found in any accessible source: a numeric attack altitude above a starling flock, absolute speeds for Storms' "slow/medium/high" attack classes, and the nine strategy names in Zoratto 2010.

## 1. Attack guidance: proportional navigation

### 1.1 Law (Brighton et al. 2017, "Peregrine Terminal Attack..." intro; Mills 2018 Eq. 1, 9, 12)

2D, scalar. gamma = bearing of the attacker's velocity, lambda = bearing of the line of sight (LOS) to target, both in an inertial frame:

    gamma_dot(t) = N * lambda_dot(t)                    (PNAS Eq. 1; Mills Eq. 1)
    a_centripetal(t) = N * v(t) * lambda_dot(t)         (PNAS, section "Optimization of the navigation constant")

3D vector form (Mills 2018, Methods B and C, Eq. 9 and 12). Acceleration is always perpendicular to the falcon's velocity v, so speed is set separately:

    lambda_dot_vec = (r x v_rel) / |r|^2
    a_cmd = N * (lambda_dot_vec x v)

The printed sign convention is ambiguous after text extraction. I checked by hand: with r = prey - falcon and v_rel = v_prey - v_falcon, a stationary prey off to the +x side of a falcon flying along +y gives a_cmd = +N s^2/d along +x, i.e. the turn is toward the prey. Unit-test this when coding it.

Related laws in the same papers:

- Proportional pursuit (PP): gamma_dot = -K * delta, delta = deviation angle between velocity and LOS. Fits peregrines worse than PN.
- Mixed PN+PP (Harris' hawk, Gyrfalcon paper): gamma_dot = N*lambda_dot - K*delta.
- Effective navigation constant N' = N * v * cos(delta) / v_c, v_c = closing speed. Linear-quadratic theory: N' = 3 minimises control effort for a non-manoeuvring target. Equivalent: N_opt = 3 * v_c / (v * cos(delta)). Stationary target: v_c = v cos(delta), so N_opt = 3. Retreating target: N_opt < 3. Stoop with negligible prey speed: N_opt ~ 3. (Gyrfalcon paper, Introduction.)
- Missiles use 3 <= N <= 5. PN needs only the LOS rate: no range, no target speed (PNAS Conclusions).

### 1.2 Constants as reported

| Quantity | Value | Tag | Source |
|---|---|---|---|
| N, peregrines, all passes, 1.0% error tolerance | median 2.6 (Q1 1.5, Q3 3.2) | F | PNAS, "Sensitivity of method" |
| N at 0.5% tolerance (shorter fits) | median 2.5 (1.5, 3.9) | F | same |
| Share of fitted N below the missile band 3-5 | about two-thirds | F | PNAS, "Optimization of the navigation constant" |
| N by target type (stationary vs manoeuvring) | both median 2.6; no effect of target type (p=0.38) or mean groundspeed (p=0.79) | F | same |
| N, aerial (towed) targets, 4 peregrines, 13 flights | median 2.8 (1.6, 3.1); global fit 3.0 | F | Gyrfalcon paper, Results |
| N, naive gyrfalcons, 13 birds, 20 flights | median 1.2 (0.5, 1.4); global 1.1 | F | same |
| N, Harris' hawk (mixed law, global fit) | N=0.7, K=1.2 1/s | F | Brighton & Taylor 2019 |
| Samples | 8 captive peregrines, GPS 5 Hz; 33 passes at stationary targets, 22 at manoeuvring targets | M | PNAS, Methods |
| PN vs PP, passes fitted within 1.0% error | PN 46 of 55, PP 35 of 55 | F | PNAS |
| Duration of PN-fitted terminal phase | median 4.9 s (3.3, 8.8) | F | PNAS |
| Length of PN-fitted terminal path | stationary median 47 m (31, 71) = 94 u; manoeuvring median 114 m (45, 200) = 228 u | F | PNAS |
| LOS steadiness on live attacks (video) | held within +/-3 deg over the last 1-2 s | M | PNAS, Fig. 2 text |
| Demanded centripetal acceleration | did not exceed g by more than a factor 2.5 until within striking distance (<= ~2.5 g = 24.5 m/s^2 = 49 u/s^2) | F | PNAS |
| Path shape | curves of increasing radius toward stationary targets; not Tucker's decreasing-radius spiral | M | PNAS |
| Medians of fitted N are within ~15% of the LQ optimum | N=2.6 vs 3 | F | PNAS |

Lower N in practice: PNAS argues low gain is affordable because speeds are low and tolerates noisy LOS-rate estimates (error amplification is proportional to N). Gyrfalcon paper: low N (~1) promotes tail-chasing and is not thrown off by jinking; high N (~3) suits quick interception after a stoop.

### 1.3 Delays

- Peregrine: no delay identified. The 5 Hz GPS (+/-0.1 s sync) cannot resolve it; fits are "nominally lag-free". Sensitivity test with an artificial 0.2 s lag: fit worsened (median error 1.1% vs <1.0%) and median N fell from 2.6 to 2.3 [F, PNAS].
- Harris' hawk (250 Hz video, 5 birds, 50 flights): LOS-to-track correlation peaks at median 0.16 s (IQR 0.12-0.22); global mixed-law fit tau = 0.09 s; PN-alone fit median ~0.10 s [F, Brighton & Taylor 2019]. Hawk, not falcon.
- Mills 2018 model: baseline response delay (and LOS differencing time) tau = 50 ms [S, assumed]; tested 0.1, 25, 100, 150 ms. Visual error: LOS direction error uniform in [0, 0.007 rad] (0.4 deg), from a pigeon motion-detection threshold of 8 deg/s over 50 ms [S, assumed; their own App. F calls it "somewhat arbitrary"].
- Mills 2018 result: with tau ~ 0, high N costs nothing; longer delay or larger visual error pushes the optimal N lower [S].

### 1.4 How attacks begin

- Wild/trained peregrines use a mix: of 12 opportunistic live hunts by the captive birds, 4 (33%) began with a stoop, 8 (67%) as level chases (1 from a perch). Stationary-lure flights: 35% stoop, 19% low swoop, 46% level chase. If the first attack fails it is usually followed by a series of swoops, "as is also typical of natural hunting" [M, PNAS, first Results section]. 0 of 12 live hunts killed (captive birds not encouraged to hunt; PNAS notes wild success "upward from 8%").
- Tucker et al. 2000 [abs, M]: wild peregrines approached robin-sized and smaller prey from up to 1500 m holding the head straight along curved paths resembling a logarithmic spiral. PNAS (full data) finds no constant-deviation-angle rule and increasing, not decreasing, radius.

## 2. Stoop physics and speeds

### 2.1 Measured speeds (separate from simulated)

| Quantity | Value | Tag | Source |
|---|---|---|---|
| Wild peregrine stoops, tracking radar | mean ~25 m/s over four stoops (peregrine and goshawk), 40-110 s long, dive angles 13-64 deg, height loss 450-1080 m; peregrine max over 10 s intervals 31-39 m/s (62-78 u/s) | M, abs | Alerstam 1987 |
| Trained peregrine, 60 m dam dive (stereo high-speed video) | accelerated 15.0 to 22.5 m/s (30 to 45 u/s) over 18.55 m of drop (6.8 m/s^2); path angle 50.75 deg at max speed; then 22.5 to 19.4 m/s in 1.2 s | M | Ponitz 2014, Results (Fig. 8-10) |
| Same dive, largest accelerations | 11.5 m/s^2 (~1.2 g) at a path correction; 9.3 m/s^2 in the pull-out | M | Ponitz 2014 |
| Trained gyrfalcon, optical tracker, 11 dives | speed limits 52-58 m/s (104-116 u/s) in the 7 fastest; dives from up to 500 m at 17-62 deg; held constant speed for a few s starting 100-350 m above ground; decelerated at mean -0.95 g | M, abs | Tucker, Cade, Tucker 1998 |
| Peregrine top level speed | 27.6 m/s (55 u/s) | 2nd | quoted in Mills 2018 App. K, source not named there |
| Starling flocks, undisturbed | 7-12 m/s (14-24 u/s) | M | Attanasi 2014 |
| Starling flock speed | 10.6 m/s | 2nd | Ballerini 2008, via Hemelrijk 2015 |
| Predator (falcon) speed | 11-15 m/s (22-30 u/s); context and citation not stated in the extracted text | 2nd | Hemelrijk 2015 |
| Peregrine wing shapes vs speed | diamond up to ~190 km/h, tuck up to ~240 km/h, full fold to 320+ km/h | 2nd | Ponitz 2014 Introduction (literature, not measured in that study) |

No peer-reviewed measurement of a wild peregrine exceeding ~39 m/s was found. Mills 2018 App. K says the same ("no peer-reviewed articles include measures of the peak performance of falcons in a stoop") and cites an unpublished 108 m/s.

### 2.2 Model and simulated speeds

| Quantity | Value | Tag | Source |
|---|---|---|---|
| "Ideal falcon" vertical-dive top speed, 0.5-2.0 kg | 89-112 m/s (parasite drag coeff 0.18); 138-174 m/s if 0.07. 1 kg bird reaches 95% of top speed after ~1200 m (38 s and 322 m at 15 deg; 16 s and 1140 m at 90 deg) | S, abs | Tucker 1998 |
| Same model, pull-out at top speed from vertical | lift 18x weight, 60 m altitude lost | S, abs | Tucker 1998 |
| Mills 2018 flight model, level max speed | falcon 29 m/s (58 u/s), starling 23 m/s (Results); 28.4 and 24 m/s (App. K) | S | Mills 2018 |
| Same, vertical-dive terminal speed | falcon 123 m/s, starling 52 m/s (Results); 122 m/s (App. K) | S | Mills 2018 |
| Same, minimum sustained speed | falcon 7.3, starling 4.5 m/s | S | Mills 2018 App. K |
| Sim start speeds | falcon 16 m/s, starling 11 m/s | S | Mills 2018 Methods |
| Model load factor at 20-22 m/s | falcon 2.5 (excl. gravity) vs measured 1.15 (incl. gravity) in Ponitz's pull-out; Mills notes real birds probably pull out below max | S vs M | Mills 2018 App. K |
| StarEscape predator speed | 1.3x the target's speed ("e.g.") | S | Papadopoulou 2026 |
| HoPE predator speed | pursuit 1.0x, attack 1.5x flock speed; pigeon cruise 16 m/s | S | Papadopoulou 2022 PLoS CB, parameter table |

Measured (wild max ~39 m/s, trained gyrfalcon 58 m/s) and simulated (100+ m/s) stoop speeds differ by a factor 2-3. The simulated values are terminal-velocity estimates; do not use them as screen speeds.

### 2.3 Why stoop (Mills et al. 2018, Results and Table 1)

All [S]. Falcon attacks one starling in open 3D space; falcon controller = pure PN with N in [1, 20], altitude above prey -200 to 1500 m, horizontal offset 0-800 m. Catch = within 0.2 m. Failure = 40 s, or near-miss (<5 m, then prey inside a 45 deg rear cone).

| Prey motion | Optimal N | Optimal start altitude | Horizontal distance | Intercept speed |
|---|---|---|---|---|
| Straight | 1-6 (flat optimum) | 150-200 m (300-400 u) | 70-90 m | 35-45 m/s (70-90 u/s) |
| Smooth turning | 5.6 | 350 m (700 u) | 0-200 m | 50-55 m/s (100-110 u/s) |
| Non-smooth jinking | 2.8 | ~1500 m (3000 u) | 641 m | >105 m/s (>210 u/s) |

- Starling model prey: stays within +/-20 m of start altitude; mean load factor 3.4 in both turning modes; roll acceleration 27 rad/s^2 (smooth) vs 2012 rad/s^2 (jinking).
- At equal airspeed the starling can always turn tighter than the falcon. The falcon matches the starling's roll acceleration only by diving near terminal speed (Results, Fig. 3).
- Optimal N falls as stoop speed rises. Minimax strategy: stoop from high at N ~ 3, which is near-optimal against all three prey motions. This matches empirical median 2.6 and the LQ optimum 3.
- Mechanism tests: horizontal attack at 112 m/s initial speed gives 61% vs 64% for a steep dive at the same speed, so descent angle is not the key; speed is. Capping load factor to level-flight values: 42%; capping roll acceleration: 51%; fast but capped: 31%; plain level flight (30 m/s): 26%.
- Delay: if tau = 0.1 ms, 100% catch even from a low (<200 m) dive. At the default 50 ms, a high-altitude stoop at N ~ 3 is needed. Optimal altitude falls if vision or control error rises.
- For N < 2 the falcon dives below prey then loops upward to intercept, "regularly observed in nature" (Mills Results, citing field reports; S2 Fig).
- Mills et al. 2019 [S]: three start positions (1500 m up/50 m out, 200 m/100 m, 50 m/200 m). Catch success highest from altitude for every prey. Starling is the second-easiest prey after mallard. High-to-low altitude gain: mallard x1.2, chaffinch x7.5. A generic raptor does best at 60-80 m/s rather than above 80 m/s. Prey flies erratically for 10 s before the falcon starts.

## 3. Peregrines attacking starling flocks (Rome roost data and related)

Two urban winter roosts, Rome: Termini (~20,000 starlings, 2 peregrines) and EUR (~60,000 starlings, up to 5 peregrines). Video Jan-Mar 2006 and Dec 2006-Mar 2007, 53 + 57 sessions. Camera 200 m to ~1 km from the flock. Procaccini 2011, Storms 2019 and Zoratto 2010 all use this dataset.

### 3.1 Hunting sequences and success

"Hunting sequence" = from the falcon starting to pursue a flock until it catches a bird or withdraws (Storms 2019; Procaccini 2011).

| Quantity | Value | Tag | Source |
|---|---|---|---|
| Sequences recorded, overall success | 328 sequences, 23.1% | M, abs | Zoratto 2010 abstract |
| Sequences with known outcome | 52 successful, 165 unsuccessful: 24.0% | M, D | Procaccini 2011, Table 2 |
| Success by sequence features | higher when sequence <1.5 min, <3 attacks, no other falcon hunting; higher on singletons than flocks, but most sequences target flocks | M, abs | Zoratto 2010 |
| Most frequent and most successful of 9 strategies | "surprise attack" (names of the other eight not available to me) | M, abs | Zoratto 2010 |
| Surprise as the common attack on flocks | cited | 2nd | Hemelrijk 2015 |
| Sequences analysed in detail | 67 (of 182 recorded); 210 attacks and 795 flock events reported in Results (I assume these belong to the 67) | M | Storms 2019 |
| Attacks per analysed sequence | 210 / 67 = ~3.1 | D | assumes the assignment above |
| Attacks classified | 175 | M | Storms 2019 |
| Attacks within 5 s of another ("repetitive") | 55 of 175 (31%); the 5 s threshold came from the distribution of inter-attack times | M | Storms 2019 |
| RobotFalcon pursuit of starling flocks | 23 chases, mean 80.2 +/- 8.0 s; 20 s to 2 min; 368 collective-escape patterns | M (robot) | Storms 2024 Table 2; Papadopoulou 2026 |
| Real peregrine hunts on starlings in the same comparison | 46 hunts, 452 escape patterns (~9.8 per hunt) | M | Storms 2024 Table 2 |

Success rates of peregrines elsewhere (context only; most are not flocks of starlings):

| Context | Success | Source |
|---|---|---|
| Spring migrants, Alberta, mostly waterbirds | 7.7% of 674 hunts | Dekker thesis Ch. 3 [M] |
| Dunlin flocks, BC coast | 14.4% of 652 hunts; adults 26.8% (164), first-year 9.0% (399) | Dekker Ch. 7-9 [M] |
| Same, surprise vs open attack | 23.6% vs 9.1%; 44% when using dike or vegetation cover; 10-11% over open mud and ocean (synthesis). An earlier 302-hunt subset gave 8.0% of 287 over open mud and ocean, 33.3% (5 of 15) for surprise attacks over salt marsh | Dekker synthesis and Ch. 7 [M] |
| Breeding pair, Alberta | 30.3% of 386 hunts, rising 21.9% to 39.1% over 7 years | Dekker Ch. 10 [M] |
| All peregrine hunts pooled in thesis | 11.7% | Dekker Table 16.1 [M] |
| Rudebeck 7.5% (253); Cresswell & Whitfield 6.7% (368); mean of 23 studies 23.7% | | [2nd] via Dekker |
| Lone prey vs flock members | lone individuals killed more often | Dekker abstract [M] |

### 3.2 Attack classes (Storms 2019)

Classified by speed (slow/medium/high) and position relative to the flock (below/side/above), only for attacks lying mainly in a vertical or horizontal plane. Speed classes are relative visual categories; no m/s were printed.

| Class | Count of 175 | Share |
|---|---|---|
| From above | 121 | 69% |
| From the side | 36 | 21% |
| From below | 18 | 10% |
| Medium speed | 144 | 82% |
| Low speed | 16 | 9% |
| High speed | 15 | 9% |

Conflict: Procaccini 2011 Fig. 2a (same footage, N=175 sequences) reports attacks per sequence: lateral 1.5, above 0.8, below 0.33 (57%, 30%, 13% [D]). The two tallies disagree on whether "above" or "side" dominates. Both agree "below" is rarest (10-13%). I cannot tell from the text which classification rule differs.

### 3.3 Escape patterns (Storms 2019 Table 1 definitions, Results, Discussion)

Patterns as listed in Storms' Table 1 (the text counts seven types); 795 flock events reported. Blackening most common (N=289), vacuole least (N=5). Order of decreasing frequency in the Discussion: blackening, wave, split, flash expansion, cordon, vacuole.

| Pattern | Definition | Timing / trigger | Numbers |
|---|---|---|---|
| Flash expansion | starlings suddenly move radially outward | only ever after an attack, never before; 4-10x faster after an attack than the other patterns; more likely after high-speed attacks and attacks from above than from side or below | 25% of attacks followed by one; 83.3% of flash expansions directly preceded by an attack; 78.3% of them did not split the flock |
| Split | one flock becomes several | usually follows flash expansion; more common at the big roost (EUR) | 119 events in the transition analysis |
| Blackening | flock or part darkens | clusters from 4 s before to 2 s after an attack; independent of attack speed or position | most common |
| Wave (agitation) | dark bands propagate across the flock | before and after attacks; most likely for medium-speed attacks | mean 3.5 +/- 0.23 s long, 2.88 +/- 0.19 pulses, inter-pulse 0.86 +/- 0.44 s (ImageJ); occurred ~12.6 s after one attack and ~13.9 s before the next (n=54) |
| Vacuole | hole in a polarised flock | rare, very large flocks | N=5 |
| Cordon | two large parts joined by a thin string | follows column-shaped flocking (Papadopoulou 2026) | |
| Flock dilution | flock spreads and lightens | 15.0 +/- 2.4 s after an attack | |
| Merge | subflocks rejoin | after splits | |

More attacks per sequence gives more blackening, waves and flash expansions. Wave presence did not reduce success in Storms (small sample) but did in Procaccini: success 0.14 with a wave (11 of 79) vs 0.30 without (41 of 138) [M, D from Table 2]. Waves occurred on 77% of observation days [M, Procaccini]. Share of sequences with a wave: Table 2 gives 79 of 217 (36%) [D]; the text prints 42% of 329 sequences and 0.66 waves per sequence, and also says 210 of 329 sequences "triggered" waves. These do not reconcile; I use Table 2.

Wave direction (210 events, Procaccini Appendix A2): 142 downward escaping + 12 oblique down, 38 up + 9 oblique up, 9 horizontal; 0 toward the falcon. Mean 0.67 downward waves per sequence vs 0.22 upward (Fig. 2b).

RobotFalcon on starlings (Papadopoulou 2026, 19 flocks of ~20-2000): flash expansion at the strike point, mostly on the flock periphery; waves only in the largest flock; collective turns most common; evasive moves are level turns, dives, and diving turns; flocks often become columnar (vertically elongated). Pigeons (HoPE): two further patterns, early splits and collective turns, at large distance from the predator.

### 3.4 Dekker's field accounts of attacks on dense flocks (Dunlin, not starling) [M]

- 62% of Dunlin hunts at Boundary Bay were open attacks on flying flocks; 35% were low stealth attacks on resting flocks, giving 57% of the kills (Ch. 9).
- On a flying flock the falcon usually patrolled back and forth 10-100 m above the Dunlins to get into position, then stooped vertically on rigid wings, held either open or tucked (paraphrased). Most skirted the outside edge and aimed at the flock's bottom. Some stooped at the top; the flock caved in and flattened low over the water (Ch. 9, Fig. 9.1).
- After a stoop the falcon can: seize at once or double back to a downed bird; pursue a single bird that split away; regain altitude for another vertical stoop at the same flock; attack another flock; or leave (Ch. 9).
- Birds at the trailing end of a fleeing flock can be seized when overtaken (Ch. 9).
- Series of stoops: an immature male made ~30 stoops in 2.5 h without a catch; others 22 and 33 consecutive stoops (Ch. 9).
- Definitions: "stoop" = wings pulled in and held rigid, plunging; "swoop" = wings keep beating, speed burst up or down. The classic teardrop stoop usually starts from high soaring and seldom happens in close pursuit of flying birds. In close pursuit the falcon swoops instead, and after a miss it climbs straight back up on the momentum of its downward pass (paraphrased, Ch. 3).
- Most stoops at ground-level prey "levelled out well before the target was reached" and the falcon sailed the last stretch low; terminal stage marked by "an abrupt change of direction" (Ch. 3, synthesis).
- Between swoops at a dodging shorebird, pursuer and pursued were often >50 m apart (100 u); the peregrine swoop was "over-powered" and often widely missed (Ch. 3, 11).
- Persistent pursuits (>6 swoops) were 2.5% of peregrine hunts on small shorebirds and passerines (Ch. 11).

## 4. Altitude, targeting, and who triggers escape

### 4.1 Altitude above the flock at attack start

No numeric altitude above a starling flock was found. Best proxies:

| Proxy | Value | Tag | Source |
|---|---|---|---|
| Positioning above Dunlin flock before the stoop | 10-100 m (20-200 u) above | M | Dekker Ch. 9 |
| Long-distance flapping descent, start altitude | usually 50-150 m (100-300 u) | M | Dekker Ch. 3 (method c) |
| Stoop from high soaring | up to an estimated >2 km; 22-25% of hunts at Beaverhills Lake; 77% of attacks by a nesting pair began from high soaring | M | Dekker Ch. 3, 10 |
| Starling attacks classed "from above" | 69% (or 30% per Procaccini) | M | Storms 2019; Procaccini 2011 |
| RobotFalcon approach altitude | high >50 m vs low <50 m: no effect on how often the flock escaped collectively (high altitude did cause earlier flight initiation) | M (robot) | Storms 2024 |
| Optimal sim stoop altitude vs lone prey | 150-200 m straight prey, ~350 m smooth, ~1500 m jinking | S | Mills 2018 |

### 4.2 Targeting rule

- Dekker [M]: falcons skirt the flock's edge and aim at its bottom or top rather than its centre; on ducks, "aiming its attack at a bird on the outside of the string"; trailing birds seized; kills mostly of lone, isolated or split-off birds; every Merlin kill on Dunlins was a single bird isolated from the flock.
- Zoratto 2010 [abs]: success higher on singletons, though most hunts are directed at flocks.
- Papadopoulou 2026 [S model, data-informed]: predator "locks into its closest sturnoid" after shadowing; flash expansions occur where the robot attacks, mostly at the periphery.
- Papadopoulou 2022 PLoS CB [S]: two rules tested, "chase" (nearest pigeon at every step) and "lock-on" (nearest at attack start). Reports both gave similar results.
- Brighton et al. 2022 preprint [M, Swainson's hawk vs free-tailed bats; preprint]: hawks did not steer after the bat they grabbed. They steered with PN at N ~ 2 toward a fixed point in the swarm, and the bat on the collision course is the one caught ("target selection emerges from the geometry"). Lone bats were 13% of attacks (62 attacks), consistent with edge individuals being met first, with no success difference (38% vs 22%, p=0.39). Not a falcon; treat as analogy.

Net: attackers use the flock's near edge on their line of approach, not the centroid. Evidence that falcons pick stragglers on purpose is mixed; evidence that stragglers and isolated birds are caught more often is consistent.

### 4.3 Who triggers escape, and propagation speed

Measured:

- Waves start near the attacking falcon and propagate away from it: 0 of 210 toward the falcon; the pulse start is typically closer to the falcon than the flock centre (Procaccini Fig. 3, Table A2).
- Single-pulse relative speeds, 15 pulses from several wave events, metric scale from the falcon's body length (36-48 cm): range 3.66-25.24 m/s (7-50 u/s), mean 13.04 m/s (26 u/s) (Procaccini Table 1). These are lower bounds (up to 40% underestimate from perspective, 7-17% from falcon size). Hemelrijk 2015 quotes this mean as 13.4 m/s [2nd]. Pulse emission 1.27 per s (21 events, range 0.5-2.95); one event lasted 19.2 s with 20 pulses (Table A1).
- Wave speed did not correlate with falcon-to-flock distance (Procaccini).
- Waves "often" exceed the flock's own speed (the "Trafalgar effect"); flock speed 7-12 m/s (Attanasi) or 10.6 m/s.
- Turning information in flocks (not clearly predator-triggered): propagates linearly, almost undamped, at 20-40 m/s (40-80 u/s); the first birds to turn are physically close to each other; flock speed 7-12 m/s; no correlation between the two; a 400-bird flock is swept in "little more than half a second" (Attanasi 2014).
- Dunlin waves 14.6 m/s and starling 15 m/s are the same order [2nd, Hemelrijk 2015].

Topological and model values [S]:

- Starlings interact with 6-7 nearest neighbours, not with all birds within a distance (Ballerini 2008) [2nd].
- StarDisplay (Hemelrijk 2015): a wave is reproduced by individuals copying a roll-away "zig" (half a zigzag) from only their 2-7 nearest neighbours; no long-range "chorus-line" anticipation is needed. Wave speed ~ NND / reaction time = 1.1 m / 0.076 s = 14.5 m/s [D, their own arithmetic]. Speed rises with the number of neighbours copied and with NND, falls with reaction time and cue-identification time, and does not depend on flock size (500-8000). Table 2 reproduces each measured speed with NND 0.71-1.93 m and a copy range of 2-7 neighbours.
- Parameters in that model: reaction time 0.076 s (SD 0.01) [startle reaction to a light stimulus, Pomeroy & Heppner; species not stated in the text I read; 2nd]; cue identification 0.05 s [assumed]; zig sideways 0.25 s, zig back 0.30 s, refractory 1.0 s [assumed]; default NND 1.3 m; empirical NND 0.68-1.51 m [2nd, Ballerini 2008]; copy range 6.
- The wave is an orientation wave (birds rolling, exposing more wing area, giving a dark band), not a density wave. Speed-up-forward copying produced no visible wave.
- StarEscape (Papadopoulou 2026): each bird has 7 topological neighbours; alertness rises with proximity to the predator, a bird escapes with probability set by alertness or by copying its closest escaping neighbour; alarmed birds update more often; refractory period after an escape. Reported outputs: sim flock speed 9.5 +/- 0.32 m/s, NND 0.86 +/- 0.08 m. Collective turns and splits start from one to a few early responders at similar positions relative to the predator.
- HoPE (pigeons): avoid the predator's heading with a force independent of distance; the observed "closer predator, more turns away" emerges from coordination. Predator cycle: pursue 30 s at distance 30-40 m, attack 20 s, retreat; reported pigeon avoidance range 50 m.

## 5. Gaps and contradictions

1. No measured numeric altitude above a starling flock, and no absolute speed for Storms' speed classes.
2. Storms 2019 and Procaccini 2011 disagree on whether "above" or "side" is the commonest attack direction.
3. Measured stoop speed (<= 39 m/s wild, 58 m/s trained gyrfalcon) vs simulated terminal speeds (>100 m/s): a gap of 2-3x. Only trained/captive dives were instrumented at high speed.
4. Peregrine reaction delay is unidentified in the data; the 50 ms figure is a modelling assumption.
5. All peregrine guidance data are from captive birds chasing lures or stationary targets, plus 12 opportunistic live hunts.
6. Wave speeds were measured from a single camera at 200-1000 m; Procaccini calls them lower bounds.
7. Wave-vs-success link: Procaccini 14% vs 30% (significant); Storms 2019 found no difference in a smaller sample.
8. Zoratto 2010 full text not accessed; hunt duration and attacks-per-sequence figures beyond the abstract are unavailable. Its sequence count is 328 (abstract); Procaccini reports 329 for the same dataset.
9. Procaccini's printed wave frequency per sequence (42%, 0.66, "210 of 329") does not reconcile with its own Table 2 (79 of 217 sequences with a wave).
10. The Papadopoulou 2026 (StarEscape) parameter values (predator distance, bearing, attack duration, reaction frequencies) are in a supplement I did not read. Only the structure and the 1.3x attack-speed example are in the main text.

## 6. Implications for murmuration.html

Applied on 2026-10-05, except rows 16 (slower relaxation) and 17 (drawn catches). The row-1 gain is fixed at the measured 2.6 rather than row 2's adaptive formula, which stalled at its floor when the falcon started alongside the flock. The page's measured outcome is in the root README ("The falcon"). The table below is the original proposal: values are suggestions mapped to the code as it was, in metres and world units (0.5 m/u). The "Evidence" column shows the tag.

| # | Page element now | Finding | Suggested parameter or behaviour | Evidence |
|---|---|---|---|---|
| 1 | Steering: aim at `prey + v*0.35`, `a = (dir*sp - v)*2.4`, cap 55 | Peregrines steer by PN on LOS rate, no lead and no range needed | `lambdaDot = cross(r, vRel) / dot(r, r)`, `a = N * cross(lambdaDot, v)`; N = 3 for strikes. Sign check: stationary target to the right must turn the falcon right. Keep speed control separate (PN is perpendicular to v) | F (N median 2.6-2.8, global 3.0); S (optimum ~3) |
| 2 | Fixed gain | Optimal N = 3 v_c / (v cos delta), lower for tail-chases | Per frame `N = clamp(3 * Vc / (speed * cosDelta), 1.2, 3)`; use the floor 1.2 (gyrfalcon median) in a tail-chase after a miss | F, D |
| 3 | No delay, no noise | Delay ~0.05-0.16 s; LOS error ~0.007 rad | Compute lambdaDot from a 0.05-0.10 s old sample (3-6 frames at 60 fps); add 0.007 rad (0.4 deg) random LOS error | S (50 ms), F (hawk 0.09-0.16 s) |
| 4 | Accel cap 55 u/s^2 (2.8 g) | Demanded centripetal accel <= ~2.5 g until striking range; measured pull-outs 1.2 g | Cap ~49 u/s^2 (24.5 m/s^2) for the PN turn; allow more only once within striking distance | F, M |
| 5 | Speed 28-32 u/s throughout | Wild stoop max 31-39 m/s; mean ~25 m/s; level max ~28 m/s | Two speeds: shadow/approach 28-32 u/s (14-16 m/s, kept; ratio to starling cruise 1.2-1.4 matches StarEscape x1.3 and Mills' 29/24); strike pass 60-80 u/s (30-40 m/s) for ~1-2 s. Do not go above ~80 u/s. Alarmed starlings reach 39 u/s, so a 30 u/s falcon is below their top speed | M (Alerstam), S (ratios) |
| 6 | Pass geometry | At 70 u/s the falcon crosses `R_FLEE` (65 u) in about 1 s | Consider raising `R_FLEE` toward 100-120 u (50-60 m). Basis is weak and pigeon-only: HoPE parameter d_max_e = 50 m (listed as "minimum distance for predator avoidance") and the 60 m window used for the RobotFalcon pigeon analysis. No starling reaction distance was found | S, 2nd |
| 7 | Retarget every 1.2-1.8 s; hunt = 9-17 s with ~10 strikes | Real hunts: ~3 attacks per sequence (D, 210/67); 31% of attacks within 5 s of the last; success higher with <3 attacks and <1.5 min | Per hunt 1-4 strikes (mean ~3). Chain 30% of strikes within 5 s; space the rest by >= 5 s. Hunt cap ~90 s. Replace the 1.2-1.8 s timer with phases: position, stoop/PN pass (3-5 s), zoom climb, reposition | M, D |
| 8 | PN pass length | Terminal PN phase: median 4.9 s; path 47-114 m | Lock on at ~100-230 u range; hold the lock for the whole pass (3-5 s); no retarget until closest approach | F |
| 9 | After a miss | Falcon mounts at once, trading speed for height, then swoops again; 50+ m between swoops | On closest approach: pitch up 30-60 deg, decay speed to shadow speed, climb to 20-200 u above the flock top, then re-lock. Gap >= 100 u between passes | M (Dekker) |
| 10 | Spawn height | Positioning 10-100 m above the flock before a stoop; approach descents start 50-150 m up | Loiter/pre-stoop height above flock top 20-200 u (10-100 m); keep the current off-screen entry | M (Dekker, dunlins) |
| 11 | Attack direction (always from the entry side) | Above vs side vs below: 69/21/10% (Storms) or 30/57/13% (Procaccini) | Draw 50% from above, 39% side, 11% below (midpoint of the two disagreeing tallies; not itself measured). Slow/medium/high = 9/82/9% | M, D |
| 12 | Target = nearest bird, `dd > 196` filter | Edge birds on the approach line; locked through the pass; lone/trailing birds caught more | Lock on to the nearest bird on the falcon's side at stoop start. Do not bias toward stragglers beyond what geometry gives (evidence for deliberate straggler choice is mixed) | M, S, preprint |
| 13 | Flee force radial, `W_FLEE*fear^2/d` | Flash expansion follows only ~25% of attacks, mainly fast ones from above; 78% do not split | Gate the radial burst: probability ~0.25 per strike, higher for strike speed >60 u/s and for above-attacks | M |
| 14 | `alarm[]` spreads only by distance to falcon | Escape spreads by copying the 6-7 nearest neighbours; hop = 0.076 s reaction + 0.05 s cue ID | Seed alarm in birds nearest the falcon; each bird copies the max alarm among its 6-7 nearest neighbours after ~0.13 s (0.076 reaction + 0.05 cue ID, the latter assumed). Tune copy range (2-7 neighbours) and spacing until the wave front travels at the measured mean 26 u/s (13 m/s), inside the measured 7-50 u/s (3.7-25 m/s). One hop of 1.1 m per 0.126 s is only ~9 m/s [D], so copying from several neighbours is what lifts the speed (StarDisplay) | M (13 m/s, 3.7-25), S (mechanism) |
| 15 | Wave look | Orientation wave: birds roll away from the falcon; pulses ~1.27/s (inter-pulse 0.86 s); 2-3 pulses (mean 2.9, max 20); mean 3.5 s; waves in ~36-42% of hunts; start near falcon, travel away | Use `bank[]`: copied roll-away "zig" 0.25 s out + 0.30 s back, refractory 1.0 s; repeat the seed every ~0.8 s, 2-3 times; trigger in ~40% of hunts; direction away from the falcon, ~3x more often downward than upward | M, S |
| 16 | `alarm` decays at 0.7/s | Flock dilution 15 s after an attack; blackening from 4 s before to 2 s after a strike | Slow the relaxation of the cohesion boost to ~10-15 s so the flock stays compact between chained strikes; raise cohesion 4 s before a strike | M |
| 17 | No catch | If a catch is ever shown: success per hunt 23-24% at the Rome roost; 14% with a wave vs 30% without | Probability of a take per hunt ~0.2; halve it if a wave fired | M |
| 18 | Hunt interval 28-52 s | No measured inter-hunt gap in sources read | Keep; not constrained by the sources | gap |

Unit cheat sheet: 10 m = 20 u; 50 m = 100 u; 100 m = 200 u; 15 m/s = 30 u/s; 25 m/s = 50 u/s; 39 m/s = 78 u/s; 2.5 g = 24.5 m/s^2 = 49 u/s^2; 0.05 s delay = 3 frames at 60 fps.

## References

Peer-reviewed and theses (DOI where one exists):

- Brighton CH, Thomas ALR, Taylor GK (2017) Terminal attack trajectories of peregrine falcons are described by the proportional navigation guidance law of missiles. PNAS 114(51):13495-13500. doi:10.1073/pnas.1714532114 (full text)
- Brighton CH, Taylor GK (2019) Hawks steer attacks using a guidance system tuned for close pursuit of erratically manoeuvring targets. Nat Commun 10:2462. doi:10.1038/s41467-019-10454-z (full text)
- Brighton CH, Chapman KE, Fox NC, Taylor GK (2021) Attack behaviour in naive gyrfalcons is modelled by the same guidance law as in peregrine falcons, but at a lower guidance gain. J Exp Biol 224(5):jeb238493. doi:10.1242/jeb.238493 (full text)
- Brighton CH, Kloepper LN, Larkman L, Zusi L, McGowan K, Taylor GK (2022) Steering clear of the confusion effect: aerial predators target fixed points in dense prey aggregations. bioRxiv. doi:10.1101/2022.02.19.481128 (preprint, full text)
- Mills R, Hildenbrandt H, Taylor GK, Hemelrijk CK (2018) Physics-based simulations of aerial attacks by peregrine falcons reveal that stooping at high speed maximizes catch success against agile prey. PLoS Comput Biol 14(4):e1006044. doi:10.1371/journal.pcbi.1006044 (full text)
- Mills R, Taylor GK, Hemelrijk CK (2019) Sexual size dimorphism, prey morphology and catch success in relation to flight mechanics in the peregrine falcon: a simulation study. J Avian Biol 50(3). doi:10.1111/jav.01979 (full text)
- Tucker VA (1998) Gliding flight: speed and acceleration of ideal falcons during diving and pull out. J Exp Biol 201:403-414. doi:10.1242/jeb.201.3.403 (abstract only)
- Tucker VA, Cade TJ, Tucker AE (1998) Diving speeds and angles of a gyrfalcon (Falco rusticolus). J Exp Biol 201:2061-2070. doi:10.1242/jeb.201.13.2061 (abstract only)
- Tucker VA, Tucker AE, Akers K, Enderson JH (2000) Curved flight paths and sideways vision in peregrine falcons (Falco peregrinus). J Exp Biol 203:3755-3763. doi:10.1242/jeb.203.24.3755 (abstract only)
- Alerstam T (1987) Radar observations of the stoop of the peregrine falcon Falco peregrinus and the goshawk Accipiter gentilis. Ibis 129:267-273. doi:10.1111/j.1474-919X.1987.tb03207.x (abstract only)
- Ponitz B, Schmitz A, Fischer D, Bleckmann H, Brucker C (2014) Diving-flight aerodynamics of a peregrine falcon (Falco peregrinus). PLoS ONE 9(2):e86506. doi:10.1371/journal.pone.0086506 (full text)
- Zoratto F, Carere C, Chiarotti F, Santucci D, Alleva E (2010) Aerial hunting behaviour and predation success by peregrine falcons Falco peregrinus on starling flocks Sturnus vulgaris. J Avian Biol 41:427-433. doi:10.1111/j.1600-048X.2010.04974.x (abstract only)
- Carere C, Montanino S, Moreschini F, Zoratto F, Chiarotti F, Santucci D, Alleva E (2009) Aerial flocking patterns of wintering starlings, Sturnus vulgaris, under different predation risk. Anim Behav 77:101-107. doi:10.1016/j.anbehav.2008.08.034 (abstract only)
- Procaccini A, Orlandi A, Cavagna A, Giardina I, Zoratto F, Santucci D, Chiarotti F, Hemelrijk CK, Alleva E, Parisi G, Carere C (2011) Propagating waves in starling, Sturnus vulgaris, flocks under predation. Anim Behav 82:759-765. doi:10.1016/j.anbehav.2011.07.006 (full text)
- Storms RF, Carere C, Zoratto F, Hemelrijk CK (2019) Complex patterns of collective escape in starling flocks under predation. Behav Ecol Sociobiol 73:10. doi:10.1007/s00265-018-2609-0 (full text)
- Storms RF, Carere C, Musters R, Hulst R, Verhulst S, Hemelrijk CK (2024) A robotic falcon induces similar collective escape responses in different bird species. J R Soc Interface 21(214):20230737. doi:10.1098/rsif.2023.0737 (full text)
- Papadopoulou M, Hildenbrandt H, Sankey DWE, Portugal SJ, Hemelrijk CK (2022) Self-organization of collective escape in pigeon flocks. PLoS Comput Biol 18(1):e1009772. doi:10.1371/journal.pcbi.1009772 (full text)
- Papadopoulou M, Hildenbrandt H, Sankey DWE, Portugal SJ, Hemelrijk CK (2022) Emergence of splits and collective turns in pigeon flocks under predation. R Soc Open Sci 9(2):211898. doi:10.1098/rsos.211898 (full text, skimmed)
- Papadopoulou M, Hildenbrandt H, Storms RF, Carere C, Verhulst S, Hemelrijk CK (2026) A mechanistic understanding of collective escape in starling flocks. Commun Biol 9(1). doi:10.1038/s42003-026-10173-4 (full text; supplement not read)
- Hemelrijk CK, van Zuidam L, Hildenbrandt H (2015) What underlies waves of agitation in starling flocks. Behav Ecol Sociobiol 69(5):755-764. doi:10.1007/s00265-015-1891-3 (full text)
- Attanasi A, Cavagna A, Del Castello L, Giardina I, Grigera TS, Jelic A, Melillo S, Parisi L, Pohl O, Shen E, Viale M (2014) Information transfer and behavioural inertia in starling flocks. Nat Phys 10(9) (page range omitted: the PubMed record's range looks wrong). doi:10.1038/nphys3035 (full text, relevant passages)
- Dekker D (2009) Hunting tactics of Peregrines and other falcons. PhD thesis, Wageningen University. ISBN 978-90-8585-328-2. https://edepot.wur.nl/51224 (no DOI; full text; chapters rest on earlier journal papers)

Works quoted second-hand (not read): Ballerini et al. 2008 PNAS 105:1232 (topological range 6-7, flock speed 10.6 m/s, NND 0.68-1.51 m); Pomeroy & Heppner (reaction time 76 ms to a light stimulus; year and species not stated in the text I read); Potts 1984 Nature 309:344 (chorus-line hypothesis); Rudebeck 1950/51 Oikos; Cresswell & Whitfield 2000; White et al. 2002 (mean success 23.7%).
