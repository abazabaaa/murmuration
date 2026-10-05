# Predator–flock interactions in starling murmurations: quantitative targets for the falcon and the escape patterns

Compiled 2026-10-05. This file adds to `research/criticality-canonical-references.md` and does not repeat it: Procaccini 2011 wave speeds (3.66–25.24 m/s, mean 13.4 m/s), the Hemelrijk 2015 headline result (zig + copying 2–7 neighbours), the Storms 2019 headline counts and the Goodenough 2017 size and duration figures are already there. Below, those papers come up only where I found new numbers in their full text.

Sources were read in full text (PMC, Springer open access or the university repository PDF) unless marked "abstract only". Every reference has a DOI, and most also have a PMID checked against PubMed. **Starling studies come first. Pigeon, gyrfalcon and other-prey studies are marked [COMPARISON].** Items that could not be verified are marked **UNVERIFIED**. Each finding ends with "→ Sim:", a measurable target or a rule change for `murmuration.html`.

How the current simulation does it (read from `murmuration.html`, for context; 1 world unit (u) = 0.5 m):
- **Falcon steering:** pure pursuit at `sp = 32` u/s (16 m/s), aiming 0.35 s ahead of a target bird. Acceleration is capped at 55 u/s² (27.5 m/s², about 2.8 g). It retargets the nearest bird every 1.2–1.8 s. A sortie lasts up to 9 s on attack, then 17 s in total.
- **Falcon timing:** the first sortie comes 14–20 s after start, then one every 28–52 s.
- **Starling response:** an isotropic radial repulsion `W_FLEE·fear²` inside `R_FLEE = 65` u (32.5 m). Alarm raises alignment, cohesion, the acceleration cap and top speed, and decays at 0.7 /s. There is no copying of escape manoeuvres between neighbours.

---

## 1. Catalogue of collective escape patterns: frequency per attack, duration, spatial scale, propagation

### Takeaway
Starling flocks show 6–9 named escape patterns. Their frequency is graded by threat:
- **Before or around an attack:** blackening and wave events. Blackening is the most common pattern; waves cluster about 13 s from an attack.
- **Right after a fast attack from above:** flash expansion, and only flash expansion. It follows 25% of attacks and splits the flock in about 22% of cases.
- **Under RobotFalcon pursuit:** collective turns (49–64% of events), compacting (20–27%) and splits (10–12%) dominate.
- **Rare:** vacuoles (5 of 795 events) and cordons.

Durations are seconds (a wave event about 3.5 s, a collective turn about 1 s). Flock dilution follows an attack by about 15 s.

### Cited Findings
**Rome, wild peregrines (Storms et al. 2019)** [Behav Ecol Sociobiol 73:10, doi:10.1007/s00265-018-2609-0, PMID 30930523, PMC6404399](https://doi.org/10.1007/s00265-018-2609-0)
- **Dataset:** two roosts, winters 2006 and 2006–07, 110 recording sessions, 16 h of 30 fps video; 182 hunting sequences, 67 analysed frame by frame; 795 collective events, 210 attacks. That is **≈ 11.9 collective events per hunting sequence and ≈ 3.8 per attack**; these two ratios are my arithmetic. → Sim: in a 9 s sortie with several strikes, expect several distinct pattern events, not one global scatter.
- **Attack geometry and speed:** 175 attacks were classified. By direction: **121 from above, 36 from the side, 18 from below**. By speed: **144 medium, 16 low, 15 high**. **55 of 175 attacks came within 5 s of another attack** ("repetitive"; the 5 s cut-off is taken from the inter-attack-time distribution). → Sim: about 69% of strikes should come from above the flock, about 31% should arrive in bursts less than 5 s apart, and the rest should be isolated.
- **Flash expansion timing:** flash expansion is the only pattern that occurs solely *after* attacks: χ²(29, N = 30) = 365.14, p < 0.001. **25% of all attacks were followed by a flash expansion, and 83.3% of flash expansions were directly preceded by an attack.** It follows an attack "four to ten times faster than any of the other patterns". → Sim: trigger flash expansion only within about 1 s of a strike, in roughly 1 in 4 strikes, with the probability weighted towards fast strikes from above.
- **Flash expansion and splitting:** flash expansion is more likely after high-speed attacks and after attacks from above than from the side or below. **78.3% of flash expansions did not lead to a split.** → Sim: target a split in ≤ about 22% of flash expansions, and let the subflocks re-merge.
- **Blackening:** blackening is the most common pattern (n = 289) and is over-represented **from 4 s before to 2 s after an attack** (χ² = 52.849, p = 0.004). It does not depend on attack speed or direction. → Sim: darkening should start *before* contact, as the falcon approaches, not only on contact.
- **Wave events: timing.** They occur on average **12.6 s after and 13.9 s before an attack** (n = 54) and are most likely around **medium-speed** attacks. Their timing relative to attacks does not differ from chance. → Sim: wave events belong to the stalking/shadowing phase, not the strike itself.
- **Wave events: structure.** A wave event lasts **3.5 ± 0.23 s** (mean ± SEM) and contains **2.88 ± 0.19 pulses** (133 pulses in total). The inter-pulse interval is **0.86 ± 0.44 s** (from ImageJ luminance). → Sim: emit 2–4 pulses per event, about 0.9 s apart.
- **Pattern order and dilution:** transitions run attack → flash expansion → split → merge → dilution. **Dilution comes 15.0 ± 2.4 s (mean ± SEM) after an attack.** Splits were more frequent at the high-pressure roost (Eur: about 60,000 starlings and 5 peregrines, against Termini: about 20,000 starlings and 2 peregrines). → Sim: after the falcon leaves, the flock should loosen over about 15 s, not snap back at once.
- **Pattern frequency rises with attack frequency:** blackening, waves and flash expansion all scale with attack frequency within a sequence. → Sim: pattern frequency should scale with the strike rate.

**Netherlands, RobotFalcon (Storms et al. 2024)** [J R Soc Interface 21:20230737, doi:10.1098/rsif.2023.0737, PMID 38689546, PMC11061643](https://doi.org/10.1098/rsif.2023.0737)
- **Starling chases:** 23 RobotFalcon chases lasted **80.2 ± 8.0 s** (mean ± SE) and produced **368 collective-escape patterns**. That is about 16 per chase, or **≈ 12 per minute** (my arithmetic). For 46 wild-peregrine hunts in Rome there were **452 patterns, ≈ 9.8 per hunt**. The model-estimated mean was **10.69 ± 0.96 escapes per chase** for starlings, against 5.92 for corvids, 3.54 for gulls and 4.32 for lapwings. The RobotFalcon and the real peregrine did not differ: t(67) = 1.11, p = 0.27. → Sim: about 10 discrete escape events per hunting sequence, and starlings should be the most reactive of the species tested.
- **Pattern mix (all four species):** **collective turn 49–64%** (defined as a heading change ≥ 90°), **compacting 20–27%**, **split 10–12%**, every other pattern < 6%. Compacting is followed by a collective turn more often than chance predicts. In starlings, attack → flash expansion → split is over-represented. → Sim: the commonest response to pursuit should be a ≥ 90° whole-flock turn, then compaction; splitting should be about 1 in 10 events.
- **Pursuit vs fly-by:** active pursuit, rather than flying nearby, increased the rate of collective escape. Approach altitude (> 50 m vs < 50 m) had no effect. → Sim: escape probability should depend on whether the falcon is chasing the flock, not only on its distance.

**Netherlands, RobotFalcon, mechanistic analysis (Papadopoulou et al. 2026)** [Commun Biol 9, doi:10.1038/s42003-026-10173-4, PMID 42151575, PMC13448496](https://doi.org/10.1038/s42003-026-10173-4)
- **Pursuits:** 19 flocks of about **20–2000 starlings**, each pursued for **20 s–2 min (mean 1 min)**. Several patterns ran at the same time in 10 of the 19 flocks.
- **Pattern definitions:**
  - Collective turns last **≈ 1 s**.
  - **Columnar flocking** (the flock stretched vertically) is a new pattern for starlings; it was known before only in dunlins.
  - Cordons formed when the top of a columnar flock turned and the bottom followed with a delay.
  - Flash expansion appeared at the attack point, usually on the periphery, while another part of the flock turned or compacted.
  - **Agitation waves were seen only in the largest flock** in the dataset.
- → Sim: escape patterns should be *local* (part of the flock flash-expands while another part turns). Waves should be enabled only for N ≳ 1000 (only the largest flock showed them; the exact N is not given).
- Vacuoles are described as "seen only in very large flocks"; they are rare (Storms 2019: n = 5 of 795). → Sim: a vacuole (a hole around the falcon) should be rare and should need a large N.

**Classical definitions in the Hemelrijk group**
- Defined across Storms 2019, Storms 2024 and Papadopoulou 2026: **blackening** (the flock or part of it darkens), **compacting** (nearest-neighbour distance falls), **dilution** (distances rise and the flock gets lighter), **cordon** (a thin string linking two large parts), **vacuole** (a hole in a polarised flock), **flash expansion** (radial outward burst), **split/merge**, **collective dive**. [Storms 2024](https://doi.org/10.1098/rsif.2023.0737), [Papadopoulou 2026](https://doi.org/10.1038/s42003-026-10173-4)
- **No "herding" pattern** is defined for starlings in any of these papers. Herding is a fish-model term (Inada & Kawachi 2002, cited in Storms 2019). "Dark bands" are the pulses of an agitation wave. → Sim: do not implement "herding" as a target. Use the 9 patterns above.

### Inferences
- **Threat ladder for a pattern-generating state machine:**
  - falcon nearby or shadowing → blackening and waves (about 13 s from a strike);
  - strike → flash expansion within about 1 s (P ≈ 0.25 per strike; higher for fast strikes from above);
  - then split (P ≈ 0.22 per flash expansion) → merge → dilution over about 15 s.
- **Expected pattern counts for a simulated sortie.** At the real rates, a 60–80 s pursuit should produce about 10–16 discrete events. The current falcon's 9 s attack phase is about one order of magnitude shorter than real hunting sequences, so rescale.
  - With the real mix of 1 FE per 4 attacks: 2–3 strikes → 0–1 flash expansions; 1–2 compactions; 1 or more ≥ 90° collective turns.

### Gaps
- **Spatial scale per pattern (m) is not given** in any of these papers: flash-expansion radius, vacuole diameter, cordon length and width, width of a dark band. Storms 2019 Table 1 (definitions) is an image; its per-pattern counts other than blackening (289) and vacuole (5) could not be extracted.
- **Durations** exist only for wave events (3.5 s), collective turns (about 1 s), dilution latency (15 s) and whole chases (60–80 s). There are no durations for flash expansion, cordon or vacuole.
- **Propagation speed** is published only for agitation waves (canonical file) and for undisturbed turns (Attanasi 2014, canonical file). None is published for flash expansion or for compaction.

---

## 2. Agitation-wave mechanism and parameters: roll ("zig"), copying range, speed, darkening optics, predator distance

### Takeaway
The dark band is an **orientation wave**, not a density wave:
- **Manoeuvre:** each bird briefly rolls to one side and back, a "zig" (half a zigzag).
- **Optics:** rolling exposes more wing area to a side-on observer. Represent the birds as spheres and the band vanishes.
- **Copying:** each bird repeats the manoeuvre of its 2–7 nearest neighbours.
- **Wave speed:** rises with copy range and with nearest-neighbour distance, falls with reaction and cue-identification time, and is independent of flock size (500–8000).
- **Damping with distance from the predator:** empirically, pulses fade as they travel. The model reproduces this only if each successive copier banks *less deeply* (0.25–4% less per copy). Lowering the probability of copying does not reproduce it.
- **Global darkness:** across the whole flock, darkness tracks wing exposure to the observer and the observer's distance, not density (r(NND, darkness) ≈ 0).

### Cited Findings
**Hemelrijk, van Zuidam & Hildenbrandt 2015** [Behav Ecol Sociobiol 69:755–764, doi:10.1007/s00265-015-1891-3, PMID 26380537, PMC4564680](https://doi.org/10.1007/s00265-015-1891-3) — details beyond the canonical summary
- **Zigzag vs zig:** a full **zigzag** (roll one side, back, other side, back) gives **double dark bands**; only the **zig** (roll one way and back) gives the single band seen in the field. → Sim: one roll pulse per bird per copy; rolling both ways gives a visibly wrong double band.
- **Optics:** "the observer will see the largest wing area once a bird has rolled 90° sidewards" (observer to the side). With birds drawn as spheres, the same transmitted zig produces **no band**. "Speeding-up-forward" also produces none. → Sim: render the band through bank-dependent projected wing area (the sim already draws `bank[i]`). Do not modulate density.
- **Parameters:**
  - Flock **2000** birds, **NND 1.3 m**.
  - Reaction time **76 ms (SD 10 ms)**; cue-identification time **50 ms**.
  - The paper states the mean repeat delay as "0.05 s + 0.076/2 = 0.043 s". **This is arithmetically 0.088 s; the printed value looks like a typo, so treat the delay as ≈ 0.09 s.**
  - Copy range = topological 6–7 neighbours outside a rear blind angle by default; range 2–7 explored.
  - NND explored **0.71–1.93 m**; flock sizes **500–8000**; 30 replicas per value.
  - → Sim: per-hop copy delay ≈ 0.05–0.09 s with σ ≈ 10 ms. Wave speed ≈ (hop distance)/(delay) ≈ 1.1–1.3 m / 0.076–0.09 s ≈ 13–17 m/s, matching the field mean of 13.4 m/s.
- **Wave speed:**
  - It rises with copy range (2 → 7) and with NND, and falls with reaction time and cue time. It does **not** change with flock size (500–8000). These two factors alone span the field range of 3.66–25.24 m/s.
  - The authors cite falcon speed during these events as **11–15 m/s**, close to wave speed; this comes from Procaccini's table and was not seen first-hand here.
  - Dunlin waves run at 14.6 m/s and starling waves at about 15 m/s [COMPARISON].
  - → Sim: wave speed (about 26–34 u/s) should be roughly 1.2–1.4× flock speed and about equal to falcon cruise speed. It must not scale with N.
- **Attack location** (rear, side or front) did not change transmission speed in the model; attacks were modelled as surprise attacks from behind, because "the surprise attack is the most common attack strategy". → Sim: no need to vary the wave rule with attack side.

**Hemelrijk, Costanzo, Hildenbrandt & Carere 2019** [Behav Ecol Sociobiol 73:125, doi:10.1007/s00265-019-2734-4](https://doi.org/10.1007/s00265-019-2734-4) (open access; PMID not checked)
- **Data and band geometry:** 16 wave events with **44 pulses**, from 5 Rome flocks; **1–6 pulses per event**. Wave events are separated by ≥ 10 s by definition. Dark bands have "an approximately fixed width" and "travel within a second over the flock". → Sim: band crossing time ≤ 1 s, so wave speed ≈ L/1 s for L ≈ 10–30 m; band width roughly constant; 1–6 pulses.
- **Pulses fade:** luminance amplitude (normalised to background) is larger at the start location than at the end. Per wave event: Wilcoxon n = 16, W = 108, p = 0.007. Per pulse: n = 44, W = 677.5, p = 0.014. → Sim: band contrast at the far side of the flock should be measurably lower than at the near side.
- **Mechanism of fading (model, 2000 birds, 7 neighbours copied):**
  - *Lowering the copy probability* (1.00 → 0.40) did **not** damp the wave: Kendall τ = −0.23, p = 0.31.
  - *Reducing the maximum bank angle per copy step* by **0–4% per step** (steps of 0.25%) did reproduce the fading: r = 0.67, p = 0.0003.
  - Interpretation: birds farther from the predator are less afraid and roll less.
  - → Sim rule: `bank_copy = bank_parent × (1 − c)` with c ≈ 0.005–0.04 per hop, or scale the roll amplitude with fear (distance to the falcon). Keep the copy probability ≈ 1.

**Costanzo, Hildenbrandt & Hemelrijk 2022** [Swarm Intelligence 16:91–105, doi:10.1007/s11721-021-00207-4](https://doi.org/10.1007/s11721-021-00207-4) — darkening optics without a predator
- **Darkness metric:** grey-scale render, Gaussian blur σ = 3 px, D = 1 − ΣI/(N_nonwhite·255). Observer about 215 m away, 30° field of view, N = 5000. → Sim: the same metric can be computed from the canvas.
- **Correlations with darkness (30 runs, two observer positions):**

  | Quantity | r with darkness |
  |---|---|
  | angle β between line of sight and mean wing-normal (up-vector) | **−0.82** |
  | distance to observer | **−0.81 to −0.83** |
  | vertical component of up-vector | +0.55 to +0.61 |
  | flock aspect ratio | −0.51 to −0.58 |
  | flock area | +0.35 to +0.47 |
  | altitude | +0.31 to +0.33 |
  | **NND (density)** | **0.00 to −0.01** |
  | flock-axis orientation α | 0.01–0.05 |

  → Sim: blackening should come from changes in bird orientation relative to the camera (bank and pitch), not from compression. A density change alone should not darken the flock.
- **Sharp turns brighten the flock:** "darkness decreases when birds roll so that the flock turns sharply", because at some point in the turn the wings are edge-on to the observer. In the paper's example frames, a bright flock (D = 0.04) had β = 85° and a dark flock (D = 0.11) had β = 58°. → Sim: in a collective escape turn, the flock should flash *lighter* when wings go edge-on, then darken.
- **StarDisplay parameters** (a useful benchmark set):

  | Parameter | Value |
  |---|---|
  | cruise speed | 13.6 m/s |
  | mass | 0.08 kg |
  | topological range | 7.4 |
  | hard-sphere radius | 0.4 m |
  | separation radius | 1.7 m |
  | rear blind angle | 36° |
  | wing area | 48 cm² |
  | wing aspect ratio | 8.33 |
  | reaction time | 0.019 s |
  | roost radius | 30 m |
  | desired altitude | 150 m |
  | integration step | 0.002 s |

**Relation to predator distance**
- Agitation pulses "tend to weaken among individuals at a larger distance from the falcon". [Storms 2024](https://doi.org/10.1098/rsif.2023.0737), citing [Hemelrijk 2019](https://doi.org/10.1007/s00265-019-2734-4)
- Waves always start at the side nearest the predator and move away from it (Procaccini 2011, canonical file). → Sim: initiate a zig at the bird(s) nearest the falcon and propagate outward; scale roll amplitude down with distance to the falcon.

### Inferences
- **Concrete zig rule.** An initiator (nearest the falcon, fear above a threshold) rolls to about 60–90° and back over a few tenths of a second.
  - The 60–90° range is my inference: 90° maximises the projected area for a side observer. The paper's roll-duration parameter t_zig is in its supplementary table, which I did not read.
  - Each of its 7 topological neighbours, after 50 ms + U(0, 76 ms), repeats the zig with the roll amplitude reduced by about 1–2% per hop. A refractory period stops re-triggering.
  - Expected: a single band at 13–17 m/s, crossing a 20 m flock in about 1.3–1.5 s, fading by about 20–50% by the far side. The 20–50% figure assumes a 1–2% reduction over about 15–30 hops and is not a published number.
- **Pulses:** about 0.86 s apart and 2–3 per event (Storms 2019). The initiator(s) re-fire every ~0.9 s while the falcon stays within threat range.

### Gaps
- **Exact roll angle and zig duration** used in StarDisplay are in the supplementary tables (S2/S3) of Hemelrijk 2015 and 2019, which I could not read. **UNVERIFIED.**
- **No empirical per-bird roll angle** exists for starlings in waves. Observers are about 1 km away (Costanzo 2022).
- **Band width in metres** is not reported.
- **The Procaccini 2011 capture-rate comparison (with vs without waves) could not be re-extracted.** The abstract was not reachable; a ScienceDirect PII guess returned the wrong paper. Storms 2019 notes that in their smaller sample "attacks with and without hunting success were equally likely to be preceded by a collective escape".

---

## 3. Papadopoulou et al. 2026 (Comm Biol) and the Papadopoulou/Hemelrijk pigeon–RobotFalcon papers: findings and inferred rules

### Takeaway
The common rule across the starling model (StarEscape) and the pigeon model (HoPE) is: **discrete, stochastic escape manoeuvres away from the predator by a few individuals, copied by their 7 topological neighbours, on top of ordinary coordination.**
- The probability of escaping rises with proximity (an alertness that accumulates and decays).
- Alarmed birds update more often: reaction time falls from 50 to 20 ms in StarEscape.
- After an escape there is a refractory period.
- Collective turns, splits, cordons, columnar flocks, compaction and dilution all *emerge* from this rule. Dilution emerges through hysteresis.
- In pigeons, a **distance-independent** turn-away rule plus alignment reproduces the empirical rise in escape frequency as the predator gets closer.
- Sharp turns by peripheral birds produce splits rather than collective turns.

### Cited Findings
**Papadopoulou, Hildenbrandt, Storms, Carere, Verhulst & Hemelrijk 2026.** *A mechanistic understanding of collective escape in starling flocks.* [Commun Biol 9(1), doi:10.1038/s42003-026-10173-4, PMID 42151575, PMC13448496](https://doi.org/10.1038/s42003-026-10173-4); preprint [bioRxiv 10.1101/2024.10.27.620514](https://www.biorxiv.org/content/10.1101/2024.10.27.620514v3.full-text).

*Field observations:*
- Individual starlings evaded with **level turns** (reversing heading without much altitude change), **dives** (dropping away from the predator) and **diving turns**. Flock members differed in their manoeuvres at the same time. → Sim: give each threatened bird a choice of turn vs dive (P_turn = p, P_dive = 1 − p), not a single radial push.

*StarEscape model rules:*
- **Coordination:** 7 topological neighbours within the field of view, with attraction, alignment and avoidance. **Avoidance applies to the closest neighbour only**, chosen to match empirical diffusion. Noise is a lateral force drawn from a uniform distribution. Agents are also attracted to the roost and to an altitude. → Sim: optionally reduce separation to the single nearest neighbour.
- **Four states:**
  1. flocking;
  2. alarmed flocking, entered as the predator approaches. Here reaction frequency rises: **reaction time falls from 50 ms to 20 ms** (bioRxiv v3, NND figure). This shrinks NND, so **compaction emerges** without any explicit cohesion change;
  3. escape;
  4. refraction: no new escape for "a few seconds" (the exact value is in the supplementary table, **UNVERIFIED**).
  → Sim: replace the present `alarm`-scaled cohesion boost (W_COH × (1 + 2·alarm)) with a higher update rate or shorter reaction delay when alarmed. The paper reports that compaction then emerges.
- **Alertness (stress):** accumulates at each reaction step by a function of distance to the predator, decays at a constant rate, and returns to 0 within a few seconds after the predator retreats. P(escape) rises with alertness. Individuals also switch to escape when an interacting neighbour escapes (**copying, topological range 7**). The copier takes the *type* of manoeuvre from the neighbour but sets its *geometry* from its own position relative to the predator. With several escaping neighbours it copies the closest. → Sim: a per-bird stress integrator s ← s + f(d)·Δt_react, s ← s·e^(−λΔt), with stochastic escape onset; copying of the escape type with own geometry.
- **Level-turn escape:** a turn of θ_esc **≈ 180°** away from the predator, its direction depending on the bird's heading relative to the predator's heading. → Sim: the escape turn is a near-reversal, not a sideways push.
- **Dive escape:** pitch down with steepness set by a smootherstep of distance to the predator (closer = steeper), with a minimum distance. Past a maximum dive distance the bird pitches back up to its preferred altitude. → Sim: dives deepen with proximity; recover altitude afterwards.
- **Predator agent ("predoid"):**
  - targets the largest flock (after a split);
  - shadows it from behind at a set distance and bearing (horizontal and vertical), matching its heading;
  - then **accelerates at 1.3× the target's speed** towards the closest sturnoid, for a fixed attack duration;
  - retreats for a fixed time, then the cycle repeats;
  - catches are not modelled.
  → Sim: replace the falcon's constant 16 m/s with phases: shadowing (≈ flock speed, behind the flock) → strike (≈ 1.3× prey speed, or a stoop, see §5) → retreat. Repeat the cycle.
- **Validation of collective motion without a predator** (18 simulated flocks): speed **9.5 ± 0.32 m/s**, **NND 0.86 ± 0.08 m**, neighbour stability **Q(3 s) = 0.58 ± 0.06**; scale-free velocity correlations. Simulations covered N = 20–5000. The hysteresis analysis used 75 simulations of 90 s pursuits with N = 100–500; 96 simulated flocks in total. → Sim: Q(3 s) ≈ 0.58 for the 4 or 6 nearest neighbours is a further target.

*StarEscape emergent results:*
- **Collective turns** spread from one or a few early responders at similar positions relative to the predator.
- **Splits** arise when (a) a level turn does not propagate fast enough, or (b) two early responders turn in *opposite* directions. Case (b) is common when the predator approaches from behind the middle of the flock. Splits almost always co-occur with collective turns. **Singletons rarely split off**, and then from the periphery of large flocks.
- **Columnar flocks** arise when neighbours share similar dive tendency (for example a spherical flock attacked from behind). **Cordons** arise when a dive spreads only into the lower part.
- **A fast attack on the bottom of the flock splits off a subflock.**
- → Sim: a strike from directly behind the flock centre should often split it into left and right halves; strikes from below should peel off a lower subflock.
- **Hysteresis:** during a collective turn the flock becomes denser, then expands through repulsion. **Dilution emerges simply from birds returning from 20 ms to 50 ms reaction time** when the predator leaves. The flock then takes a shape different from its pre-attack shape. → Sim: no explicit dilution rule is needed. Lowering the update rate after the threat should loosen the flock over about 15 s (Storms 2019 empirical latency: 15.0 ± 2.4 s).
- The authors suggest a predator attacking the thinnest part of a flock (for example a cordon), to reduce confusion, "also enhances splitting". This is an untested suggestion. → Sim: optional falcon target bias towards low-density regions.

**[COMPARISON] Pigeons: Sankey, Storms, Musters, Russell, Hemelrijk & Portugal 2021.** *Absence of "selfish herd" dynamics in bird flocks under threat.* [Curr Biol 31:3192–3198, doi:10.1016/j.cub.2021.05.009, PMID 34089647](https://doi.org/10.1016/j.cub.2021.05.009) (abstract only)
- **Design:** homing pigeons in flocks of 8–10 or 27–34; **5 Hz GPS**; 27 flights chased by the RobotFalcon, 16 control flights.
- **Result:** birds "respond[ed] strongly … by turning away from its flight direction" but showed **no increased attraction** to neighbours compared with controls. Alignment, not selfish attraction, dominates under threat.
- → Sim: under threat, raise alignment or response rate and add turn-away; do not add a centre-seeking "selfish herd" force.

**[COMPARISON] Papadopoulou, Hildenbrandt, Sankey, Portugal & Hemelrijk 2022a.** *Self-organization of collective escape in pigeon flocks.* [PLoS Comput Biol 18:e1009772, doi:10.1371/journal.pcbi.1009772, PMID 35007287, PMC8782486](https://doi.org/10.1371/journal.pcbi.1009772)
- **Empirical pigeon flocks** (43 flights, GPS every 0.2 s): mean speed **≈ 18 m/s**; NND **1.3 ± 1.8 m** (mean ± SD), with neighbours at any bearing; flock-shape angle 41 ± 23.5° (oblong to elongated).
- **HoPE model parameters:** preferred speed sampled from an interval of width 4 m/s; separation by turning when a neighbour is < 1 m; attraction ramping 2–10 m by smootherstep; 7 topological neighbours.
- **Simulated predator:** starts 5 m behind the flock, slower than the prey, attacking from left, middle or right behind. Analysis used prey within 60 m, in 10 m bins.
- **Escape rule:** a force perpendicular (±90°) to the heading, turning the bird away from the predator, applied *regardless of distance*. Combined with alignment and cohesion it reproduces the empirical rise in turn-away frequency as the predator gets closer. Without the escape rule, turning-direction frequency did not differ across distance bins (χ² = 1.875, p = 0.171); with it, it did (χ² = 10.321, p < 0.005). Consensus on escape direction rises at **20–30 m** from the predator.
- → Sim: the escape force can be a constant-magnitude lateral turn-away inside a threat radius of about 30–60 m. Coordination alone will produce the distance gradient. The present `fear²` radial falloff is not required.

**[COMPARISON] Papadopoulou, Hildenbrandt, Sankey, Portugal & Hemelrijk 2022b.** *Emergence of splits and collective turns in pigeon flocks under predation.* [R Soc Open Sci 9:211898, doi:10.1098/rsos.211898, PMID 35223068, PMC8864349](https://doi.org/10.1098/rsos.211898)
- **Empirical:** RobotFalcon approached from about 50 m behind. Over 27 attacked flights: **155 collective turns and 65 splits** (35 solitary departures, 30 subflock splits).
  - A split was counted when a bird had no main-flock member within **10 m for ≥ 2 s**. Straight flight was defined as < 10°/s.
  - Both patterns occurred over a range of predator distances. Small flocks did not split without the predator.
  - → Sim: a split detector (no member within 10 m for ≥ 2 s), plus a turn-to-split ratio of about 2.4 : 1 under attack, as a pigeon benchmark.
- **Model:** a single initiator makes a discrete, uncoordinated turn. Its angle and duration are drawn from **gamma distributions** fitted to the data. P(manoeuvre) = individual baseline × proximity.
  - Sharp turns (above the median angular velocity) raise the split probability by **28%**.
  - **Peripheral initiators split more**; central initiators produce more collective turns.
  - If fewer than half the flock follows, a subflock splits off (about 10% of simulated splits).
  - Empirical confirmation: angular velocity predicts split vs turn (GLMM β = −1.27). Centrality is significant once outliers are removed (β = −0.66, p = 0.01), especially within 100 m of the predator (β = −0.9).
  - → Sim: initiator turn rate and position control the outcome. Edge birds turning fast should produce splits; central birds should produce whole-flock turns.

### Inferences
- **Starling rule set** (StarEscape plus the pigeon results):
  - P_escape(t) from a stress integrator of distance;
  - an escape manoeuvre of either a ≈ 180° level turn or a proximity-scaled dive;
  - escape *type* copied by 7 topological neighbours, with *geometry* from their own position;
  - reaction time 50 ms → 20 ms when alarmed;
  - a refractory period of a few seconds;
  - plus Hemelrijk's zig (§2) for the wave.
- **What it replaces:** the present global radial repulsion inside 32.5 m. That repulsion is essentially a flash expansion on every strike; real flash expansion follows only about 25% of attacks.

### Gaps
- StarEscape's supplementary Table S1 (numeric values for stress accumulation, decay rate, refractory time, P_turn, attack distance, bearing, attack duration and retreat time) was **not read. UNVERIFIED.**
- No 2023–2025 Papadopoulou/Hemelrijk paper on pigeon RobotFalcon escape was found beyond the 2022 pair and the 2021 Sankey paper. A wider search (Google Scholar) may turn up later work.

---

## 4. Raptor hunting of murmurations: species, attack rate, attack types and speeds, target selection, capture success

### Takeaway
**Peregrines at Rome roosts:**
- Hunting sequences succeed in **23.1% of 328 sequences**.
- A sequence usually contains several attacks. Success is higher when sequences last **< 1.5 min**, contain **< 3 attacks** and involve no other falcon at the same time.
- The most frequent and most successful of 9 strategies is the **surprise attack**.
- **Singletons are caught more often than flock members.**
- At least one starling is caught per evening.
- Most attacks come from above at medium speed.

**UK citizen science:** sparrowhawk, peregrine and harriers were the predators associated with larger and longer murmurations.

**Confusion effect:** in a 3D human-predator game, targeting error rises with flock size (1 → 5000, no plateau) and is affected by density.

### Cited Findings
**Zoratto, Carere, Chiarotti, Santucci & Alleva 2010.** *Aerial hunting behaviour and predation success by peregrine falcons on starling flocks.* [J Avian Biol 41:427–433, doi:10.1111/j.1600-048X.2010.04974.x](https://doi.org/10.1111/j.1600-048X.2010.04974.x) (abstract only, via the academia.edu record; DOI confirmed in the Storms 2019 reference list; not in PubMed)
- **Success rate:** **328 hunting sequences, overall success 23.1%.** The Procaccini 2011 dataset of 329 sequences is presumably the same footage. → Sim: if catches are modelled, about 1 in 4–5 sorties ends in a kill.
- **What raises success:** sequences lasting **< 1.5 min**, with **< 3 attacks**, and with no other falcon hunting at the same time. → Sim: a sortie of about 1–1.5 min with 1–3 strikes is the realistic unit. Make catch probability fall with each successive strike.
- **Singletons:** hunts directed at singletons succeed more often than hunts on flocks, but most hunting sequences target flocks. → Sim: stragglers or split-off birds should carry higher catch risk; the falcon should still mostly go for the flock.
- **Strategies:** nine hunting strategies were identified. The **surprise attack** was the most frequent and the most successful. Falcons caught at least one prey item every evening. → Sim: spontaneous attacks should often start unseen, with little pre-strike alarm, and then strike.
- **Not obtained:** the definitions and per-strategy frequencies of the 9 strategies (full text paywalled).

**Storms et al. 2019** (Rome, same programme) [doi:10.1007/s00265-018-2609-0](https://doi.org/10.1007/s00265-018-2609-0)
- Attack direction: from above 121/175 (69%), side 36 (21%), below 18 (10%). Attack speed: medium 144 (82%), low 16, high 15. 31% of attacks were "repetitive" (< 5 s apart).
- **Roost-level pressure:** Eur had about 60,000 starlings and 5 peregrines; Termini about 20,000 starlings and 2 peregrines.
- → Sim: the spontaneous-attack direction mix should be 70/20/10 (above/side/below).

**Hemelrijk et al. 2015:** falcon speed during wave-generating attacks **11–15 m/s**, cited from Procaccini 2011's table (not seen first-hand). [doi:10.1007/s00265-015-1891-3](https://doi.org/10.1007/s00265-015-1891-3) → Sim: the pursuit/shadowing phase near the flock should run at about 11–15 m/s (22–30 u/s), slightly faster than the starlings. The current 16 m/s pursuit is at the top of this range.

**Carere, Montanino, Moreschini, Zoratto, Chiarotti, Santucci & Alleva 2009.** *Aerial flocking patterns of wintering starlings under different predation risk.* [Anim Behav 77:101–107, doi:10.1016/j.anbehav.2008.08.034](https://doi.org/10.1016/j.anbehav.2008.08.034) (abstract only; the author list beyond Carere and Chiarotti is from memory and **UNVERIFIED**)
- 53 days of observing incoming flocks not under direct attack; **12 flocking shapes** identified.
- **Predation success was higher at the low-predation roost.**
- Shape and size results are in §6.

**Goodenough et al. 2017** (UK citizen science) [PLoS ONE 12:e0179277, doi:10.1371/journal.pone.0179277, PMC5476259](https://doi.org/10.1371/journal.pone.0179277)
- **Predators recorded:** kestrel, peregrine, sparrowhawk, red kite, buzzard, harrier (Circus) and owl. Birds of prey were present at 29.6% of murmurations; observers also mentioned corvids (15.8%) and gulls (17.6%). Predator activity was scored on four levels: perching silent, perching calling, flying, actively engaging (flying through the flock or striking).
- **Model results:**
  - Size: the best models included harrier, buzzard and peregrine presence; adding sparrowhawk raised variance explained to 35% (presence); predator activity gave R² = 0.40.
  - Duration: harrier and peregrine *flying/engaging* entered the best model.
  - → Sim: peregrine and sparrowhawk are the key species. A harrier is a low-flying quartering predator (behaviour from general knowledge, **not quantified here**).
- **Merlin and hobby** were **not among the coded species**.

**Hogan, Hildenbrandt, Scott-Samuel, Cuthill & Hemelrijk 2017.** *The confusion effect when attacking simulated three-dimensional starling flocks.* [R Soc Open Sci 4:160564, doi:10.1098/rsos.160564, PMID 28280553, PMC5319319](https://doi.org/10.1098/rsos.160564)
- **Design:** 25 human participants "hunted" a highlighted target in StarDisplay flocks.
  - Flock sizes **1, 50, 250, 1000, 5000**; NND **0.8, 1.3, 1.8 m**. The PMC text lists "loose, normal, dense = 0.8, 1.3, 1.8 m", which looks inverted; the numeric levels themselves are reliable.
  - Each trial started 100 m from the target at equal altitude. The target's trail faded from 40 m and was invisible from 20 m.
- **Results:**
  - Targeting error rose with flock size, with **no plateau at 5000**.
  - Size and density interacted. Hunting time rose with flock size.
  - The predator's approach speed related to the target's path curvature and acceleration.
  - "Modelled starlings appear to be safer from predation in larger and denser flocks."
- → Sim: if the falcon picks targets, its tracking error or retargeting rate should grow with the number of birds near the target. Track-loss should begin at about 20–40 m from the target.

**[COMPARISON] Mills, Taylor & Hemelrijk 2019 (J Avian Biol).** Peregrines strike small agile prey more often as males. In one field study, the male made **432 of 572 solo hunts over 7 years** (140 by the female). This is quoted inside the paper, and its original source was not checked: **UNVERIFIED primary source**. [doi:10.1111/jav.01979, PMID 35873526, PMC7613156](https://doi.org/10.1111/jav.01979)

### Inferences
- **A realistic falcon sortie on a murmuration:**
  1. a surprise approach, often from above;
  2. 1–3 strikes, about 31% of them in rapid bursts less than 5 s apart;
  3. a total of up to about 1.5 min;
  4. a kill in about 23% of sequences, with catch probability higher on singletons and stragglers.
- **Spontaneous attack rate per evening:** not given numerically, but "at least one catch every evening" at a 23% success rate implies **≳ 4–5 hunting sequences per evening per roost** (my inference). Storms 2019 recorded 182 sequences across 110 sessions, about 1.7 per session, but only filmed ones were counted. → Sim: one sortie every 30–60 s is far more frequent than nature, which is acceptable for a demo but should be documented. A "realistic" mode would use one sortie every few minutes.

### Gaps
- **Merlin, hobby and sparrowhawk:** no quantitative hunting data on starling murmurations (attack rate, success, tactics) was found in the sources accessible here. Sparrowhawk and merlin hunting of flocking waders and passerines exists in the literature (for example merlins on dunlins, Buchanan et al. 1988, cited in Hemelrijk 2019) but is **not extracted**.
- **Absolute attack speeds:** wild-peregrine attack speeds on starling flocks in m/s are not published in these papers; Storms used qualitative slow/medium/high classes.
- **Target selection:** no empirical data on whether peregrines pick edge birds or stragglers inside murmurations, beyond "singletons more successful". Bat–hawk work (Brighton et al. 2021, Behav Ecol, seen only as a related-paper snippet) found lone bats attacked disproportionately (about 10% of attacks, about 0.2% of the population). [COMPARISON, **UNVERIFIED** citation details]

---

## 5. Peregrine stoop and pursuit kinematics: speeds, proportional navigation, time to intercept

### Takeaway
- **Guidance law:** peregrine terminal attacks follow **proportional navigation (PN)**: turn rate = N × line-of-sight rate, with **N ≈ 2.6–3**. Medians: 2.6 for stationary targets, 2.6–2.8 for manoeuvring targets. The global fit is N = 3.0, close to the linear-quadratic optimum N′ = 3. The line of sight is held steady to within ±3° over the last 1–2 s.
- **Stoop speeds:** measured falcon dives (gyrfalcon) reach **52–58 m/s**. Theory allows 89–112 m/s vertical, or up to 138–174 m/s with low drag.
- **What simulations show:** against erratically manoeuvring prey such as starlings, catch success is maximised by a **high-altitude stoop (≈ 1500 m) to intercept speeds > 100 m/s at N ≈ 3**. Against straight-flying prey, a low stoop (< 200 m) to 35–45 m/s is enough.
- **Duration of guided pursuit:** the PN-fitted terminal phase is typically about 5 s.

### Cited Findings
**Brighton, Thomas & Taylor 2017.** *Terminal attack trajectories of peregrine falcons are described by the proportional navigation guidance law of missiles.* [PNAS 114:13495–13500, doi:10.1073/pnas.1714532114, PMID 29203660, PMC5754800](https://doi.org/10.1073/pnas.1714532114)
- **Birds and data:** 8 captive peregrines with 5 Hz GPS and onboard video. 33 passes at stationary targets (3 birds) and 22 passes at manoeuvring targets (towed lure, 4–5 birds). 12 opportunistic live hunts.
- **Fit:** PN fits better than pure pursuit. **Median N = 2.6** (quartiles 1.5–3.9 at 0.5% error tolerance; 2.6 at 1.0%). N was not related to target type (p = 0.38) or groundspeed (p = 0.79). With a 0.2 s delay added, N = 2.3. → Sim: replace the falcon's current pure pursuit with a 0.35 s lead by PN with N = 3: a_cmd = N·V_c·(dλ/dt) ⊥ to velocity. Real-world PN with N < 3 is acceptable.
- **Fitted durations:** PN simulations covered a **median 4.9 s** of terminal flight; median fitted path length 47 m for stationary and 114 m for manoeuvring targets. → Sim: the PN-guided terminal phase should last about 5 s, over about 50–110 m.
- **Line of sight:** steady to **within ±3° over the last 1–2 s** of live attacks. → Sim: check by logging line-of-sight rate ≈ 0 in the last 1–2 s before a strike.
- **How attacks start:** only **4 of 12 (33%) live hunts began with a stoop**. All 35 flights at manoeuvring targets began as level chases. Of 26 flights at stationary targets, 9 (35%) began with a gravity-assisted stoop and 5 (19%) with a low swoop. → Sim: mix of strikes at about one-third stoops and two-thirds level/tail chases. Storms 2019's 69% "from above" includes shallow descents.
- **Acceleration:** centripetal acceleration "did not exceed gravitational acceleration by more than a factor of 2.5 until the peregrine was already within striking distance". → Sim: the present 55 u/s² ≈ 2.8 g cap is about right for approach. Allow a brief higher burst at the strike.
- Wild-peregrine success rates "range upward from 8%" (as quoted by the paper).

**[COMPARISON] Brighton, Chapman, Fox & Taylor 2021.** *Attack behaviour in naive gyrfalcons…* [J Exp Biol 224:jeb238493, doi:10.1242/jeb.238493, PMID 33536303, PMC7938797](https://doi.org/10.1242/jeb.238493)
- Reanalysed 13 peregrine flights at aerial targets: **median N = 2.8** (quartiles 1.6–3.1), global optimum **N = 3.0**. Naive gyrfalcons: median N = 1.2, global 1.1, producing tail-chasing.
- Theory: optimal N = 3·V_c/(V·cos δ). This is ≈ 3 in a high-speed stoop and **< 3 in a tail chase against a fleeing target**. Low N is less thrown by erratic jinks at close range.
- Peregrine wing loading is about 5.3 kg/m².
- → Sim: use N ≈ 3 during a stoop and N ≈ 1.5–2.5 in a level tail chase on an evasive starling.

**Mills, Hildenbrandt, Taylor & Hemelrijk 2018.** *Physics-based simulations of aerial attacks by peregrine falcons reveal that stooping at high speed maximizes catch success against agile prey.* [PLoS Comput Biol 14:e1006044, doi:10.1371/journal.pcbi.1006044, PMID 29649207, PMC5896925](https://doi.org/10.1371/journal.pcbi.1006044) — prey modelled as a **common starling**
- **Set-up:** model starling at 11 m/s, keeping within ±20 m of its altitude; model falcon starting at 16 m/s. Catch = within **0.2 m**; failure if no catch within **40 s**, or a near-miss within 5 m that leaves the prey in the falcon's 45° rear blind cone. Default visuomotor delay **50 ms**; N sampled 1–20; start altitude −200 to 1500 m; horizontal distance 0–800 m.
- **Speed advantage (model):** level flight about **29 m/s (falcon) vs 23 m/s (starling)**; terminal dive about **123 m/s vs 52 m/s**. The PMC text renders these as "2923 ms" and "12352 ms" with the separators lost; my parsing is consistent with Mills 2019's 28–29 m/s level speed and 104–111 m/s terminal speed, but is flagged.
- **Optimal attack strategies:**

  | Prey motion | Best stoop start | Intercept speed |
  |---|---|---|
  | straight flight | low, < 200 m | 35–45 m/s |
  | smooth manoeuvres | ≈ 350 m | 50–55 m/s |
  | non-smooth (erratic) manoeuvres | ≈ 1500 m | > 100 m/s |

  Stooping from too high costs little; too low costs a lot. **N ≈ 3** is the broadly optimal gain in a high-speed stoop, close to the empirical 2.6.
- **Prey manoeuvres:** smooth manoeuvres have mean load factor 3.4 and roll acceleration about 27 rad/s². Non-smooth manoeuvres have the same load factor but roll acceleration about 2012 rad/s². Erratic jinks are what make the high-speed stoop necessary.
- **Sensitivity:** a high-speed *horizontal* attack (112 m/s start) achieved 61% vs 64% for a steep dive. Limiting roll acceleration dropped success to 51%; limiting load factor to 42%; sustained level flight gave 26%.
- **Effect of delay:** with an effectively instantaneous response (0.1 ms), 100% catch was possible even from a low dive.
- → Sim:
  - real-looking stoops should start from well above the flock and arrive at 35–100+ m/s (70–200+ u/s), far faster than the current 16 m/s;
  - for visibility one may compress this, but the falcon should at least be about 2–6× flock speed at the strike;
  - escaping starlings should jink (high roll acceleration), not just turn smoothly;
  - if catch is modelled, use a 0.2 m capture radius (0.4 u) and a 50 ms falcon delay.

**Mills, Taylor & Hemelrijk 2019.** *Sexual size dimorphism, prey morphology and catch success…* [J Avian Biol 50(3), doi:10.1111/jav.01979, PMID 35873526, PMC7613156](https://doi.org/10.1111/jav.01979)
- Maximum sustained level speed **28.1 m/s (male) and 29.2 m/s (female)**; terminal speed **104 vs 111 m/s**.
- In simulation, males are better than females at catching manoeuvrable prey in level flight, through a higher roll acceleration. Both sexes improve and converge when diving.
- The main driver of variation in catch success across prey species is the **prey's ability to sustain a high centripetal acceleration** over a chase, not its peak.
- Generic-raptor optimum speed is **60–80 m/s**; > 80 m/s is detrimental. Intercepting a manoeuvring target with N ≈ 3 needs a load factor **2–3× the prey's**.
- Optimal attack altitudes tested: high (1500 m above, 50 m horizontal), moderate (200 m above, 100 m horizontal), low (50 m above, 200 m horizontal). Against a chaffinch, a high stoop gave 7.5× the success of a low one; against a mallard, only 1.2×.
- → Sim: the falcon's sustained level speed cap should be about 28–29 m/s (56–58 u/s); dive cap about 100+ m/s. A starling escape turn should sustain several g (load factor about 3.4) for about 1 s or more.

**Tucker, Cade & Tucker 1998 [COMPARISON: gyrfalcon dives].** [J Exp Biol 201:2061–2070, doi:10.1242/jeb.201.13.2061, PMID 9622578](https://doi.org/10.1242/jeb.201.13.2061)
- 11 dives by a 1.02 kg gyrfalcon from up to 500 m, at dive angles of **17–62°**. Speed limits of **52–58 m/s** in the 7 fastest dives, followed by a constant-speed phase, then deceleration at about **−0.95 g**. These are "the fastest ever measured with known accuracy in animals".
- → Sim: a measured, defensible stoop speed is about 55 m/s at a 20–60° dive angle; brake at about 1 g before contact.

**Tucker 1998 (theory).** [J Exp Biol 201:403–414, doi:10.1242/jeb.201.3.403, PMID 9427673](https://doi.org/10.1242/jeb.201.3.403)
- Ideal falcons of 0.5–2 kg reach **89–112 m/s** in a vertical dive (C_D,par = 0.18), or 138–174 m/s if C_D,par = 0.07.
- Reaching **95% of top speed** takes about 1200 m of travel: **16 s and 1140 m of altitude at 90°, 38 s and 322 m at 15°**.
- Pull-out from a vertical dive costs about **60 m** of altitude, with lift up to **18× body weight** with flexed wings.
- Braking reaches **−1.5 g** at 45° and 41 m/s.
- → Sim: a full-speed stoop needs a long approach. For a 32.5 m interaction radius, model the stoop as arriving already at speed rather than accelerating in view.

**Tucker et al. 2000 (wild peregrines).** [J Exp Biol 203:3755–3763, doi:10.1242/jeb.203.24.3755, PMID 11076739](https://doi.org/10.1242/jeb.203.24.3755)
- Peregrines approached prey from **up to 1500 m** with the head straight, along **curved, logarithmic-spiral-like paths**. This keeps the deep fovea, about **40°** off-axis, on the prey. Turning the head would raise drag by more than 50% (Tucker 2000, [doi:10.1242/jeb.203.24.3733](https://doi.org/10.1242/jeb.203.24.3733)).
- Brighton 2017 found the curved paths better explained by PN than by a constant 40–45° deviation angle.
- → Sim: a long-range approach can curve gently; switch to PN for the final 5 s.

### Inferences
- **Time to intercept,** assembled from the above (my synthesis):
  - a long stoop of tens of seconds, mostly out of view;
  - a PN-guided terminal phase of about 5 s (Brighton 2017);
  - a line-of-sight lock in the last 1–2 s.
- **Prey reaction window:** a bird 32.5 m from a falcon at 50 m/s has about 0.65 s; at 16 m/s, about 2 s. With starling reaction plus cue time ≈ 0.08–0.13 s and a 20 ms alarmed update interval (StarEscape), a bird can make 1–2 escape decisions in the 32.5 m window at stoop speed.

### Gaps
- No **field GPS data of wild peregrines hunting murmurating starlings** exist in these sources. All PN fits are on lures or robotic targets.
- Typical *stoop start altitude above a murmuration* and *strike speed at the flock* for wild falcons over roosts are not quantified.
- Measured peregrine (not gyrfalcon) maximum stoop speed is not obtained here. Ponitz et al. 2014 (PLoS ONE) is reported elsewhere but **UNVERIFIED** here.

---

## 6. Does predation pressure change flock shape, density or murmuration duration?

### Takeaway
Yes, qualitatively and with modest effect sizes:
- **Rome (Carere 2009):** the higher-predation roost had significantly more **large, compact flocks**; the lower-predation roost had more small flocks and singletons. Predator success was higher where pressure was lower.
- **UK (Goodenough 2017):** predator presence and activity are positively associated with murmuration **size** (R² ≈ 0.35–0.40) and **duration** (R² ≈ 0.26). With predators present, murmurations more often end with all birds going down to roost together.
- **Within an attack:** density rises (compacting), then falls (dilution about 15 s later). In the model this is a hysteresis effect of the change in reaction rate.
- **Darkness:** in the model, density barely changes darkness (r ≈ 0). So "blackening" observed under threat is largely an orientation effect.

### Cited Findings
**Carere et al. 2009** [doi:10.1016/j.anbehav.2008.08.034](https://doi.org/10.1016/j.anbehav.2008.08.034) (abstract only)
- 12 flock shapes. Significantly more **compact and large flocks** at the high-predation roost (Eur: 5 peregrines, about 60,000 starlings; roost data from Storms 2019). **Small flocks and singletons** were more frequent at the low-predation roost (Termini: 2 peregrines, about 20,000 starlings).
- Similar patterns occurred at both roosts **when other flocks nearby showed antipredator behaviour, even in the absence of a predator at the focal roost**, which the authors read as social information passing between flocks.
- → Sim: under a "high pressure" setting, keep N in fewer, larger, denser flocks. Optionally let a distant flock's alarm raise vigilance in the focal flock.
- **Not obtained:** the effect sizes (% compact flocks per roost) and the list of the 12 shapes.

**Goodenough et al. 2017** [doi:10.1371/journal.pone.0179277](https://doi.org/10.1371/journal.pone.0179277) (full text)
- **Dataset:** 3,211 records; 1,066 UK murmurations of ≥ 500 birds where the end was seen and all birds went to roost. Mean **30,082 ± 6,699 (SEM)** birds; mean duration **26 min ± 44 s**. UK murmurations lasted longer than non-UK ones (18 ± 2.5 min) and US/Canada ones (16 ± 3 min).
- **Predator associations:** birds of prey present at **29.6%**. Predator presence and activity correlated with size (**R² = 0.401**) and duration (**R² = 0.258**), "especially when … flying near to, or actively engaging with, starlings". In the presence-only models, adding sparrowhawk took variance explained in size to **35%**, and harrier, buzzard and peregrine entered the size model. Duration was associated with harrier and peregrine flying or engaging.
- **Other predictors:** day length predicted duration more strongly (R² = 0.384) than temperature (R² = 0.144). The end of the murmuration was seen in 67.1% of reports.
- **Ending:** with predators present, the murmuration more often ended with all birds going down to roost together rather than dispersing.
- → Sim: predator activity should *lengthen* the display and keep birds together; ending by a mass descent to roost is the predator-present outcome.
- Correlational only: larger murmurations might attract predators rather than the reverse. The authors argue for the anti-predator explanation.

**Within-attack density dynamics**
- **Compacting:** Storms 2024 ([doi:10.1098/rsif.2023.0737](https://doi.org/10.1098/rsif.2023.0737)) defines compacting as a fall in nearest-neighbour distance; it is 20–27% of RobotFalcon-elicited events. Papadopoulou 2026 ([doi:10.1038/s42003-026-10173-4](https://doi.org/10.1038/s42003-026-10173-4)) reproduces it by shortening reaction time from 50 to 20 ms.
- **Dilution:** follows an attack after **15.0 ± 2.4 s** (Storms 2019). It emerges in StarEscape through hysteresis when reaction time returns to 50 ms.
- → Sim: when alarmed, NND should fall (the canonical file's r₁ target is 0.68–1.51 m), then rise above baseline about 15 s after the falcon leaves.

**[COMPARISON] Pigeons (Sankey et al. 2021, abstract only).** Under RobotFalcon pursuit, attraction to neighbours did **not** increase over controls ([doi:10.1016/j.cub.2021.05.009](https://doi.org/10.1016/j.cub.2021.05.009)). Any compaction seen in birds is therefore probably not from a "move to the centre" rule. → Sim: produce compaction through a higher update rate, alignment and turning, not stronger cohesion.

**Confusion and density (Hogan 2017).** Simulated starlings were "safer from predation in larger and denser flocks" ([doi:10.1098/rsos.160564](https://doi.org/10.1098/rsos.160564)). This gives a functional reason for compaction under threat.

**Darkness and density (Costanzo 2022).** Darkness vs NND r ≈ 0.00; darkness vs wing-exposure angle r ≈ −0.82 ([doi:10.1007/s11721-021-00207-4](https://doi.org/10.1007/s11721-021-00207-4)). → Sim: do not use visual darkening as evidence of compaction. Measure NND directly.

### Inferences
- **A "predation pressure" knob in the simulation should:**
  1. raise the merging tendency (fewer, larger flocks);
  2. shorten reaction time when alarmed, giving compaction;
  3. lengthen the display before the descent to roost;
  4. end the display with an en-masse descent when predators were active.
- **Targets:** NND drops by a measurable fraction during alarm, then rises about 15 s after the threat ends. Display duration should be longer with predators than without (UK mean 26 min, as a scaled-time target only).

### Gaps
- No **3D metric data** (NND, aspect ratio, thickness) comparing flocks *under* vs *not under* attack were found for starlings. The Rome STARFLAG 3D datasets are of undisturbed flocks.
- Carere 2009's numeric effect sizes, and the definitions of its 12 shape classes, could not be read (abstract only).
- No quantitative NND trajectory through an attack (for example, % NND change) exists for real starlings. The only trajectory is StarEscape's simulated one, which is in the Comm Biol figure and was not digitised.

---

## Reference list (verification status)

| Ref | DOI | PubMed / PMC | Read |
|---|---|---|---|
| Papadopoulou et al. 2026 Commun Biol 9 | 10.1038/s42003-026-10173-4 | PMID 42151575, PMC13448496 | full text (+ bioRxiv v3) |
| Storms et al. 2019 Behav Ecol Sociobiol 73:10 | 10.1007/s00265-018-2609-0 | PMID 30930523, PMC6404399 | full text |
| Storms et al. 2024 J R Soc Interface 21:20230737 | 10.1098/rsif.2023.0737 | PMID 38689546, PMC11061643 | full text |
| Hemelrijk et al. 2015 Behav Ecol Sociobiol 69:755 | 10.1007/s00265-015-1891-3 | PMID 26380537, PMC4564680 | full text |
| Hemelrijk et al. 2019 Behav Ecol Sociobiol 73:125 | 10.1007/s00265-019-2734-4 | not checked | full text (Springer OA) |
| Costanzo et al. 2022 Swarm Intell 16:91 | 10.1007/s11721-021-00207-4 | not in PubMed | full text (RUG repository PDF) |
| Papadopoulou et al. 2022 PLoS Comput Biol 18:e1009772 [pigeon] | 10.1371/journal.pcbi.1009772 | PMID 35007287, PMC8782486 | full text |
| Papadopoulou et al. 2022 R Soc Open Sci 9:211898 [pigeon] | 10.1098/rsos.211898 | PMID 35223068, PMC8864349 | full text |
| Sankey et al. 2021 Curr Biol 31:3192 [pigeon] | 10.1016/j.cub.2021.05.009 | PMID 34089647 | abstract |
| Zoratto et al. 2010 J Avian Biol 41:427 | 10.1111/j.1600-048X.2010.04974.x | not in PubMed | abstract |
| Carere et al. 2009 Anim Behav 77:101 | 10.1016/j.anbehav.2008.08.034 | not in PubMed | abstract |
| Goodenough et al. 2017 PLoS ONE 12:e0179277 | 10.1371/journal.pone.0179277 | PMID 28628640, PMC5476259 | full text |
| Hogan et al. 2017 R Soc Open Sci 4:160564 | 10.1098/rsos.160564 | PMID 28280553, PMC5319319 | full text |
| Brighton et al. 2017 PNAS 114:13495 | 10.1073/pnas.1714532114 | PMID 29203660, PMC5754800 | full text |
| Brighton et al. 2021 J Exp Biol 224:jeb238493 [gyrfalcon] | 10.1242/jeb.238493 | PMID 33536303, PMC7938797 | full text |
| Mills et al. 2018 PLoS Comput Biol 14:e1006044 | 10.1371/journal.pcbi.1006044 | PMID 29649207, PMC5896925 | full text (some numbers garbled in PMC rendering, flagged) |
| Mills et al. 2019 J Avian Biol 50(3) | 10.1111/jav.01979 | PMID 35873526, PMC7613156 | full text |
| Tucker et al. 1998 J Exp Biol 201:2061 [gyrfalcon] | 10.1242/jeb.201.13.2061 | PMID 9622578 | abstract |
| Tucker 1998 J Exp Biol 201:403 | 10.1242/jeb.201.3.403 | PMID 9427673 | abstract |
| Tucker et al. 2000 J Exp Biol 203:3755 | 10.1242/jeb.203.24.3755 | PMID 11076739 | abstract |
| Tucker 2000 J Exp Biol 203:3733 | 10.1242/jeb.203.24.3733 | PMID 11076737 | abstract |
| Procaccini et al. 2011 Anim Behav 82:759 | 10.1016/j.anbehav.2011.07.006 | — | not re-read (see canonical file) |
