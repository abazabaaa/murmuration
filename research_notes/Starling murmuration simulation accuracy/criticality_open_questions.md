# Criticality in starling flocks: open empirical and theoretical questions, and the critiques

Compiled 2026-10-05 as an extension of `research/criticality-canonical-references.md` (sections c and e). Papers already annotated there are cited only for new numbers or corrections. Every number has a DOI, arXiv ID or PMID/PMCID link. **UNVERIFIED** marks a number I could not trace to the primary text. Lines starting "→ Sim:" give the implication for `murmuration.html`, as a measurable target or a model change. The app constants used for comparison come from the source: `M = 0.5` m per world unit, `W_ALI = 18`, `NOISE_TAU = 4` s, `W_SPD = 1.5` on the flock-mean speed plus `W_SPD4 = 0.002` cubic per bird, and the comment `D ≈ W_ALI · 3.5 u²` ≈ 63 u²/s ≈ 15.8 m²/s.

---

## Q1. Attanasi et al. 2014 Nature Physics 10:691: published values of c_s, attenuation and a/c_s

### Takeaway
The journal version is paywalled and I could not read its tables or SI. No published-version numbers could be checked independently. The best available values are still the arXiv:1303.7097 table: c_s = 9.41 to 21.32 m/s over 12 events, mean 15.0 ± 4.2 m/s (SD, computed here). a/c_s is 25 to 100 ms with a mean of about 50 ms. Attenuation is described as "negligible" and never given as a coefficient. The 2025 follow-up by the same group cites the journal paper as "c_s ∈ [10:20] m/s", which matches the arXiv numbers. A new finding: the same flocking events appear in Mora et al. 2016 sampled at 0.2 s, where Φ = 0.957 to 0.997. At 170 Hz the same events read Φ = 0.757 to 0.959. This is a direct, event-matched measurement of how much the sampling rate lowers Φ.

### Cited Findings
- Journal metadata: Nature Physics 10(9):691–696, online 27 Jul 2014, doi:10.1038/nphys3035. The editorial standfirst says the study tracks "up to 400 starlings", but the arXiv table lists events of up to 595 birds. The paywalled full text and SI were not accessible. — [Nature Physics page](https://www.nature.com/articles/nphys3035)
  → Sim: none until the journal table is obtained. Keep the arXiv-table targets below and label them "preprint".
- arXiv Table 1 (12 events, 170 Hz). N, Φ, c_s (m/s): 176, 0.806, 10.09 · 125, 0.959, 21.32 · 50, 0.866, 16.19 · 384, 0.801, 11.37 · 502, 0.841, 11.93 · 404, 0.854, 18.85 · 154, 0.940, 19.23 · 139, 0.890, 18.66 · 139, 0.808, 17.70 · 197, 0.907, 13.77 · 133, 0.793, 9.41 · 595, 0.757, 10.98. c_s comes from a fit to the linear regime of x(t). A power-law fit of the rank curve gives r(t) ~ t^3.2 on average, so x ~ t^1.07. — [arXiv:1303.7097](https://arxiv.org/abs/1303.7097)
  → Sim: target c_s = 15 ± 4 m/s (30 ± 8 u/s), range 9–21 m/s. Fit r(t) ~ t^α and require α ≈ 3 (linear front). A diffusive front gives α ≈ 1.5.
- a/c_s "ranges between 25 ms up to 100 ms, with an average around 50 ms", which is in the physiological range of starling reaction times. The authors stress that this is not itself a reaction time. — [arXiv:1303.7097](https://arxiv.org/abs/1303.7097)
  → Sim: measure a/c_s with a = mean nearest-neighbour distance. Target 25–100 ms. With a ≈ 1 m that means c_s ≈ 10–40 m/s.
- Attenuation: "the information to turn propagates across the flock with negligible attenuation" (Fig. 2d, qualitative). Appendix E defines small dissipation as η < √(ρ_s χ)/L, which is equivalent to a damping time τ = 2χ/η > L/c_s. — [arXiv:1303.7097](https://arxiv.org/abs/1303.7097)
  → Sim: ratio of peak radial acceleration, last-ranked bird / first-ranked bird. Target ≳ 0.8 (this threshold is an inference from "negligible"). Also require a damping time longer than the crossing time L/c_s, about 2 s for L ≈ 30 m.
- The 2025 preprint by the same group cites the published paper for "c_s ∈ [10:20] m/s" and restates c_s ~ 1/√(1−Φ) as "in fair agreement with experiments". — [arXiv:2505.19665](https://arxiv.org/abs/2505.19665)
- **Same events, different sampling.** Mora et al. 2016, Table S1, sampled at dt = 0.2 s, lists events with the same acquisition IDs as Attanasi 2014. Φ at 170 Hz (Attanasi) vs Φ at 0.2 s (Mora): 20110208_ACQ3 0.806 vs 0.984; 20110211_ACQ1 0.757 vs 0.971; 20110217_ACQ2 0.854 vs 0.986; 20111124_ACQ1 0.959 vs 0.993; 20111125_ACQ1 0.866 vs 0.987; 20111125_ACQ2 0.841 vs 0.957; 20111215_ACQ1 0.801 vs 0.987; 20111220_ACQ2 0.907 vs 0.984. Mora's full range over 14 events is P = 0.957–0.997, with v₀ = 8.5–29.2 m/s and r₀ = 0.62–1.24 m. Bird counts differ slightly (e.g. 179 vs 176), so the time windows may differ. — [arXiv:1511.01958](https://arxiv.org/abs/1511.01958), [arXiv:1303.7097](https://arxiv.org/abs/1303.7097)
  → Sim: the app's Φ ≈ 0.99 is **inside** the empirical 0.2 s range (0.957–0.997, median ≈ 0.986). Report Φ from 0.2 s position differences and compare against 0.96–0.997, not 0.96 alone. Only Φ at frame rate with simulated wing-beat jitter should approach 0.76–0.96.

### Inferences
- The canonical report's ranges (c_s 10–20 m/s, a/c_s 25–100 ms) stand, but should be labelled arXiv-derived. The group's own 2025 citation implies the journal version did not change them materially.
- The event-matched Φ comparison weakens the canonical report's claim that the app's Φ ≈ 0.99 "vs 0.96" is too high. 0.96 ± 0.03 is the 2010 10 fps mean, and the 2011–12 events at 5 Hz sit at 0.96–0.997.

### Gaps
- The published-version table and SI of doi:10.1038/nphys3035 were not retrieved (paywall). Whether the event count, Φ values or c_s values changed between arXiv v1 and the journal is **UNVERIFIED**. Physics Reports 728:1 (2018), which may restate them, was not checked.
- No numerical attenuation coefficient exists in the accessible text.

---

## Q2. Cavagna et al. 2025, arXiv:2505.19665 (soliton/FPUT): publication status and fitted parameters

### Takeaway
As of 5 Oct 2026 the arXiv record shows v2 (5 Aug 2025, "More experimental data added in Supplementary Material") and no journal reference. I found no published version. The paper **does not fit J, J₄, χ or η to data in physical units**. It gives only simulation-unit values and an inequality chain. The experimental claim is qualitative: ω_L ∝ k², with no fitted prefactor in the accessible text. So no effective diffusion constant can be read off the paper. An order-of-magnitude estimate from Mora 2016 gives D_eff ≈ a²/τ_relax ≈ 2–8 m²/s, against the app's ≈ 16 m²/s (inference).

### Cited Findings
- Status: v1 26 May 2025, v2 5 Aug 2025, 13 authors (Cavagna, Cimino, Cristín, Fiorini, Giardina, Giustiniani, Grigera, Melillo, Palombella, Parisi, Ponno, Scandolo, Stamler). The abstract page lists no journal-ref, only the arXiv DOI 10.48550/arXiv.2505.19665. — [arXiv:2505.19665v2](https://arxiv.org/abs/2505.19665v2)
- Dataset (SM Table 1): 9 flocks with N = 875, 1514, 180, 220, 312, 249, 598, 958, 431 and acquisition times T_MAX = 5.10, 4.45, 5.52, 11.33, 8.33, 9.99, 5.06, 12.47, 5.67 s. Recorded with a panning stereo rig, 2019–2023. — [arXiv:2505.19665](https://arxiv.org/abs/2505.19665)
  → Sim: compute C(k,ω) over windows of ≥ 5–12 s. Shorter windows cannot resolve spin-wave peaks.
- Linear theory: ω(k) = −iγ ± √((J/χ)a²k² − γ²) with γ = η/2χ. Underdamped gives c_s = a√(J/χ). Overdamped gives a Lorentzian with half-width **ω_L = (J/η) a² k²**. All 9 flocks show quasi-Lorentzian C(k,ω) with ω_L ~ k² and no spin-wave peaks. The prefactor J a²/η is not reported numerically. — [arXiv:2505.19665](https://arxiv.org/abs/2505.19665)
  → Sim: for spontaneous (unforced) flight, fit ω_L(k) = D k². The target is a central Lorentzian with no side peaks at ±c_s k. Exponent 2 ± 0.3 (tolerance is an inference).
- Model: H_v = (J/4v₀²) Σ n_ij (v_i − v_j)² + (J₄/4v₀⁴) Σ n_ij (v_i − v_j)⁴. In planar phases this gives J_eff = J + J₄ δφ². The equation of motion is χ φ̈_i = −Σ_j n_ij (φ_i − φ_j)[J + 2J₄(φ_i − φ_j)²] − η φ̇_i + noise. Without noise and dissipation this is the FPUT lattice. — [arXiv:2505.19665](https://arxiv.org/abs/2505.19665)
  → Sim: add a per-neighbour alignment torque ∝ Δφ (J + 2J₄ Δφ²) on top of the existing linear W_ALI term.
- Parameter window (Eq. 8): **J ≲ χγ²(L/a)² ≪ J₄ ≲ J/(1−Φ)**. This uses ⟨δφ²⟩ ~ (1−Φ), so small fluctuations stay overdamped while O(1) phase jumps become underdamped. — [arXiv:2505.19665](https://arxiv.org/abs/2505.19665)
  → Sim: at Φ ≈ 0.97–0.99 this allows J₄/J ≲ 30–100 (inference from Eq. 8). Scan J₄/J ∈ [5, 100].
- Simulation values (dimensionless, not physical): h = 10⁻², χ = 1.25, J = 20, v₀ = 0.1, T = 10⁻⁶, κ = 10⁴ (soft speed constraint V_c = (κ/2)(|v|−v₀)²), η = 0.7 (underdamped ISM), η = 7 (overdamped ISM and ISM+FPUT), J₄ = 10⁵. — [arXiv:2505.19665](https://arxiv.org/abs/2505.19665)
  → Sim: do not copy these numbers. J₄/J = 5000 only works because T = 10⁻⁶ makes Φ ≈ 1. At the app's noise, use the Eq. 8 window instead.
- Context: Mora 2016 infers an overdamped first-order alignment model with white noise from the same kind of data. τ_relax = (J n_c)⁻¹, "of the same order" as the 0.2 s sampling time, and the effective field equation is dπ/dt = J n_c a² ∇²π + ξ. — [arXiv:1511.01958](https://arxiv.org/abs/1511.01958)
- Follow-up preprint: a 1-d boid chain with inertia, the FPUT nonlinearity and added "active torques". It gives a dissipative non-reciprocal mKdV continuum equation in which the transfer speed rises with turning angular velocity. — [arXiv:2604.23808](https://arxiv.org/abs/2604.23808) (preprint, not peer-reviewed)

### Inferences
- **Effective orientation diffusion constant (order of magnitude, inference).** From Mora 2016, D_eff = J n_c a² ≈ a²/τ_relax. With a = r₀ = 0.62–1.24 m and τ_relax ≈ 0.2 s this gives **D_eff ≈ 2–8 m²/s**, i.e. ω_L ≈ 2–8 rad/s at k = 1 m⁻¹. The app's D ≈ 63 u²/s × 0.25 m²/u² ≈ **15.8 m²/s** is 2–8× stiffer. The app's large W_ALI was chosen to beat its long OU noise (Q8), which may be why.
- In the FPUT picture the *small-signal* J is set by spontaneous fluctuations and the *large-signal* stiffness by J₄. A single linear W_ALI cannot match both the Lorentzian width and c_s ≈ 15 m/s.

### Gaps
- No physical-unit J, J₄, χ, η or ω_L prefactor was found in the accessible v2 text and SM passages. **UNVERIFIED** whether the SM figures (Fig. S3, ω_L vs k) report a fitted coefficient.
- No journal publication was found up to Oct 2026.

---

## Q3. Hemelrijk & Hildenbrandt 2015, J Stat Phys 158:563: speed control, ξ/L slope, and whether criticality is needed

### Takeaway
StarDisplay uses a **linear, per-bird speed relaxation**, f = m·w_sp·(v₀ − v_i) along the heading, with v₀ = 10 m/s and default w_sp = 1 s⁻¹ (τ ≈ 1 s). It produces scale-free correlations with slopes **a_u = 0.44 (velocity, n = 344, r = 0.98) and a_sp = 0.41 (speed, n = 340, r = 0.96)**. These are larger than the empirical 0.35 and 0.36. The slope rises with the number of influential neighbours, with diminishing returns. Very strong speed control (w_sp = 100 s⁻¹) breaks the scale-free speed correlation, and flocks start to disintegrate. The paper presents scale-free correlation as an emergent property of biologically inspired rules plus weak speed control. It does not claim, and does not need, tuning to a critical point.

### Cited Findings
- Speed control: **f_τ = m·w_sp·(v₀ − v_i)·e_x** (e_x the forward direction), v₀ = 10 m/s. w_sp values scanned: 0, 0.001, 0.01, 0.1, 0.5, 1, 100 s⁻¹ (default 1). Noise: a white random force w_ξ·ξ̂ with ξ̂ a uniform random unit vector and w_ξ = 0.01 N. Reaction time 50 ms. Flock sizes 10–10,000, drawn from a geometric distribution. — [Hemelrijk & Hildenbrandt 2015, doi:10.1007/s10955-014-1154-0 (open PDF)](https://research.rug.nl/files/17747148/Hemelrijk_2015_JStatPhys.pdf)
  → Sim: the app applies its linear term (W_SPD = 1.5 s⁻¹) to the *flock-mean* speed and only a cubic term per bird. StarDisplay applies a linear term per bird at τ = 1 s. Add `?speed=stardisplay` (per-bird linear, 1 s⁻¹) as a third comparison arm next to linear/marginal.
- Slopes: default a_u = 0.44 (n = 344, r = 0.98, P < 0.001) and a_sp = 0.41 (n = 340, r = 0.96, P < 0.001), compared with the empirical 0.35/0.36 dashed lines. The authors write: "their slope a is greater in the model than in empirical data". — [same PDF](https://research.rug.nl/files/17747148/Hemelrijk_2015_JStatPhys.pdf)
  → Sim: the app's ξ/L ≈ 0.33–0.38 already matches the data better than StarDisplay's 0.44. Keep the target at 0.35 ± 0.03.
- Slope vs number of interaction partners n_c (machine-extracted from a table; verify against the PDF): n_c = 2 → 0.345; 4 → 0.400–0.418; 6 → 0.439; 10 → 0.462; 15 → 0.480; 20 → 0.491; 25 → 0.496 ("a diminishing increase of the slope"). — [same PDF](https://research.rug.nl/files/17747148/Hemelrijk_2015_JStatPhys.pdf) — **partly UNVERIFIED** (the extraction mixed in figure values).
  → Sim: scan K = 2…25 and check that ξ/L rises and saturates. With K = 7 the StarDisplay-like expectation is ≈ 0.44, and the app gives ≈ 0.35.
- High speed control: at w_sp = 100 s⁻¹ the speed correlation is no longer scale-free while velocity correlation stays scale-free, and "the flocks are in the process of collapsing". Abstract: "As predicted theoretically, at very high speed control the model generates a non-scale free correlation". — [RUG record, abstract](https://research.rug.nl/en/publications/scale-free-correlations-influential-neighbours-and-speed-control-/)
  → Sim: negative test. Raising per-bird speed stiffness to ~100 s⁻¹ should make ξ_sp saturate with L while ξ_u/L stays fixed.
- The extracted slopes at other w_sp (e.g. "a_u = 0.29 at w_sp = 1, n = 155, r = 0.88"; "slope 0.19 at w_sp = 100, n = 492, r = 0.659") are internally inconsistent with the default case. — **UNVERIFIED**, needs reading Table/Fig. 4 directly.

### Inferences
- The paper reproduces ξ ∝ L in an aerodynamic agent model with no parameter tuned to a transition. Together with Bialek 2012 (Goldstone), this supports "orientation scale-freeness is generic". The speed result echoes Bialek 2014 and Cavagna 2022: weak speed stiffness is required. Hemelrijk & Hildenbrandt cite Bialek 2014 but do not argue the flock is critical.

### Gaps
- An exact table of slope vs w_sp was not cleanly extracted.

---

## Q4. γ and ξ vs L after 2010: wider size ranges and other species

### Takeaway
I found **no new measurement of the starling decay exponent γ** after Cavagna 2010 (γ = 0.19 ± 0.08). Cavagna 2022 extended ξ_sp ∝ L to N = 10–3000 (r_P = 0.97) without reporting γ. In other species, scale-free ξ ∝ group size is reported for jackdaws (transit and mobbing), simulated massive fish schools and bacterial clusters, and qualitatively for a dense sheep flock. Exact jackdaw slopes remain paywalled. Midge swarms have finite-size-scaling exponents rather than slopes. Laboratory midge swarms are *not* scale-free unless perturbed.

### Cited Findings
- Jackdaws (O'Coin et al. 2023): ξ grows with group size in both transit and mobbing contexts, and the effect of polarization on ξ "is not significant". No slope values were retrievable (paywall; PubMed blocked by a captcha in this session). — [doi:10.1088/1478-3975/aca862, PMID 36541516](https://pubmed.ncbi.nlm.nih.gov/36541516/) — **slopes UNVERIFIED**
  → Sim: none until slopes are obtained.
- Jackdaws (Reynolds 2025, J R Soc Interface 22:20250020): border dynamics (birds staying longer at the border, sharp borders, denser border, NND increasing toward the centre, alignment strongest at the border) are by-products of topological interactions. In jackdaw transit flocks, nearest-neighbour velocity correlation vs a size measure has slopes 0.01 ± 0.002 and −0.006 ± 0.008. The model includes a velocity-memory timescale T and Wiener noise. — [doi:10.1098/rsif.2025.0020](https://royalsocietypublishing.org/rsif/article/22/229/20250020/235553/Topological-interactions-account-for-border) (numbers extracted by query; verify)
  → Sim: target nearest-neighbour distance rising from border to centre, and mean |u_i·u_j|/|u|² for nearest pairs higher at the border than in the bulk.
- Starlings, extended size range: ξ_sp ∝ L at N = 10–3000 (r_P = 0.97, p < 10⁻⁹), already in the canonical report. No γ re-fit is given. — [doi:10.1038/s41467-022-29883-4](https://doi.org/10.1038/s41467-022-29883-4)
- Fish (simulation, not data): massive school models of up to 50,000 swimmers with flow interactions give scale-free correlations in cohesive polarized clusters. **Fragmentation is preceded by a drop in correlation length.** Turn information propagates linearly in time "thanks to the non-reciprocal nature of the visual interactions". Merging speeds up transfer "by several fold". — [arXiv:2505.05822 / Nat Commun doi:10.1038/s41467-026-70569-y](https://arxiv.org/abs/2505.05822)
  → Sim: log ξ/L just before any split. Prediction: ξ/L falls below ≈ 0.3 before fragmentation.
- Sheep: aerial video of a dense flock under a herding dog shows "large-scale correlations spanning the entire flock" and wave-like edge fluctuations. A single flock, so no ξ-vs-L slope. — [arXiv:2002.09467](https://arxiv.org/abs/2002.09467)
- Midges: field swarms are scale-free, but laboratory swarms without perturbations have small ξ. Adding perturbations restores ξ ∝ size. N in the field datasets spans 69–781. Dynamic exponent z = 1.16 ± 0.12 (least squares) vs 1.37 ± 0.11 (RMA). — [arXiv:2602.10242 review](https://arxiv.org/abs/2602.10242)
- Chimney swifts (Evangelista et al. 2017, Proc R Soc B, doi:10.1098/rspb.2016.2602): 3-D roost-approach trajectories exist. No ξ-vs-size data was found in the accessible text. — [PMC5326531](https://pmc.ncbi.nlm.nih.gov/articles/PMC5326531/) — **no slope found**
- Pigeons: GPS flocks of ≤ 10 birds (Nagy et al. 2010) are too small for ξ-vs-L scaling. No pigeon γ was found. — [doi:10.1038/nature08891](https://doi.org/10.1038/nature08891)

### Inferences
- γ ≈ 0 has not been re-tested over more than one decade of L. The boundary-inflow explanation (Cavagna 2013) remains untested against new data. The laboratory-midge result (scale-freeness appears only under perturbation) is the clearest empirical support for "driven" correlations of the kind Cavagna 2013 proposes.

### Gaps
- O'Coin 2023 slopes, Ling 2019 RSIF jackdaw c_s values and saturation size (paywalled; the research index returned no full text).
- No 3-D chimney swift, pigeon or fish-school *field* ξ-vs-L slope was found.

---

## Q5. Responses to Klamser & Romanczuk 2021; status of Casiulis et al. 2020 and the Cavagna comment

### Takeaway
Follow-ups to Klamser & Romanczuk come mainly from the Romanczuk group and from fish work. **Poel et al. 2022** find golden-shiner schools *subcritical*, moving closer to criticality under higher perceived risk. A 2022 review chapter recasts the hypothesis as "tuning to an optimal distance from criticality". I found no rebuttal arguing that criticality is evolutionarily stable in flocks. Casiulis et al. was published as PRL 124:198001 (15 May 2020). The comment, arXiv:1912.07056 by **Cavagna, Giardina and Viale** (the canonical report's author list is wrong), has no journal reference and I found no published PRL Comment. The reply is arXiv:1912.09202. The debate stands unresolved in print.

### Cited Findings
- Poel et al. 2022, Sci Adv 8:eabm6385: golden shiners, N = 40, startle cascades measured by branching ratio and collective sensitivity. At baseline, median NND = 1.23 ± 0.3 BL and sensitivity 0.035 ± 0.007. Alarmed: NND = 0.68 ± 0.12 BL and sensitivity 0.058 ± 0.019. "Their sensitivity could be increased by a factor of 5.9 and 3.4, respectively, by becoming critical." The paper explicitly cites Klamser & Romanczuk on evolutionary instability. — [PMC9217090](https://pmc.ncbi.nlm.nih.gov/articles/PMC9217090/), [arXiv:2108.05537](https://arxiv.org/abs/2108.05537)
  → Sim: with an alarm-copying cascade, measure branching ratio b (mean number of birds triggered per triggered bird). Expect b < 1 in calm flight, rising toward 1 when `alarm` is high.
- Review chapter (Romanczuk and co-authors): "the emerging view that de-emphasizes the optimality of being exactly at a critical point and instead explores the potential benefits of … being able to tune to an optimal distance from criticality". — [arXiv:2211.03879](https://arxiv.org/abs/2211.03879)
- Fish under stress: "Experimental evidence of stress-induced critical state in schooling fish" (Lin, Escobedo, Li, Xue, Han, Sire, Guttal, Theraulaz). bioRxiv doi:10.1101/2025.02.21.639527, later published in an APS journal, doi:10.1103/nr7p-m4ff. The abstract was truncated in the index, so its numbers are **UNVERIFIED**. — [bioRxiv](https://doi.org/10.1101/2025.02.21.639527)
- Fish turning avalanches: power-law avalanche distributions with data collapse, and an Omori-law aftershock decay faster than in earthquakes. — [arXiv:2309.16455](https://arxiv.org/abs/2309.16455)
- Robot swarms (Chen et al. 2023, J R Soc Interface 20:20230176) test the criticality hypothesis with Vicsek-like robots. — [PMC10354469](https://pmc.ncbi.nlm.nih.gov/articles/PMC10354469/) (results not extracted)
- Minority-triggered reorientation (2026 preprint): agents in a highly ordered neighbourhood sometimes follow a strongly deviating neighbour. This gives heavy-tailed reorientation cascades "over broad parameter ranges" while cohesion is kept, a non-fine-tuned route to critical-like responsiveness. — [arXiv:2603.07254](https://arxiv.org/abs/2603.07254)
  → Sim: an alternative to FPUT. With probability p, align to the most-deviant of the K neighbours when local order > threshold. Measure the cascade-size distribution (power-law target).
- Casiulis, Tarzia, Cugliandolo, Dauchot, PRL 124:198001, published 15 May 2020. — [PubMed 32469593](https://pubmed.ncbi.nlm.nih.gov/32469593/), [arXiv:1911.06042](https://arxiv.org/abs/1911.06042)
- Comment arXiv:1912.07056 (Cavagna, Giardina, Viale; submitted 15 Dec 2019, single version, no journal-ref). Its arguments: (i) real flocks turn by equal-radius rotation, not rigid parallel-path rotation, because rigid rotation needs v = ωr, i.e. speeds proportional to radius; (ii) real g(r) is gas-like, not the crystalline order that produces rigid clusters; (iii) the slow network rearrangement (Mora 2016) does not imply rigid rotation, since neighbours' mutual orientations change during turns; (iv) C_sp(r) rising at large r is specific to event 28-10, while 25-10, 31-01, 17-06, 21-06 and 58-07 differ; (vi) **subtracting a Kabsch-fitted rigid rotation and translation from real displacement fields leaves the scale-free correlations essentially unchanged**, and the fitted global rotation "is always very small". — [arXiv:1912.07056](https://arxiv.org/abs/1912.07056)
  → Sim: subtract the best-fit rigid rotation from the velocity field (Kabsch) and recompute C(r) and ξ/L. Target: ξ/L changes by less than a few percent. Also check equal-radius turning: per-bird turn radii during a turn should have a coefficient of variation ≪ the spread of distances to the flock's rotation centre.
- Reply: arXiv:1912.09202 (Casiulis, Tarzia, Cugliandolo, 20 Dec 2019). Later work cites the Casiulis model as a Hamiltonian/active-Hamiltonian system (symplectic thermostatting, PRE 111:015429; reentrance, arXiv:2602.11104), not as a bird-flock explanation. — [arXiv:1912.09202](https://arxiv.org/abs/1912.09202), [arXiv:2409.14864](https://arxiv.org/abs/2409.14864), [arXiv:2602.11104](https://arxiv.org/abs/2602.11104)

### Inferences
- Cavagna 2022's marginal speed confinement needs no parameter at a special value. The approach to the T = 0 critical point is by low noise, which also raises Φ. This plausibly sidesteps the Klamser–Romanczuk repeller: their ESS lies deep in the ordered phase, which is where marginal-speed flocks get long-range speed correlation. No paper making this argument explicitly was found, so this is my inference.
- No quantitative bound on the flock-wide angular velocity in the starling data was found beyond the qualitative "always very small" Kabsch rotation.

### Gaps
- Whether the PRL published version of Casiulis et al. changed after the comment, and whether any Comment/Reply pair appeared in PRL, is **UNVERIFIED**; none was found.

---

## Q6. Scale-free chaos / harmonically confined Vicsek debate: relevance to flocks bound to a roost

### Takeaway
The "scale-free chaos" programme (González-Albaladejo, Bonilla and co-workers) concerns **low-polarization midge swarms bound to a marker**, not starlings. It is a rival to the Cavagna group's RG and inertial-spin account of swarm exponents. In the harmonically confined Vicsek model, the critical line is where the largest Lyapunov exponent vanishes. There, ξ ∝ swarm size and the static exponents match field swarms better than the ISM/RG values. The critical confinement goes to zero as N → ∞. For a polarized flock with a roost attraction, the takeaway is a warning: a confining potential can itself generate ξ ∝ L and power laws, so the app's scale-free correlations may partly come from its roost/target attraction.

### Cited Findings
- 3-D confined Vicsek (PRE 107:014209, 2023): on the critical line of confinement vs noise, swarms show scale-free chaos with "minimal correlation time, correlation length proportional to swarm size". Susceptibility, ξ, the dynamic correlation function and the largest Lyapunov exponent obey power laws. The critical line moves to zero confinement as N → ∞. — [arXiv:2208.08121](https://arxiv.org/abs/2208.08121), [PMID 36797962](https://pubmed.ncbi.nlm.nih.gov/36797962/)
- Mean-field theory (PRE 107:L062601): Landau static exponents plus dynamic z = 1 and a Lyapunov exponent φ = 0.5. The transition is at zero confinement and noise. — [arXiv:2305.14085](https://arxiv.org/abs/2305.14085)
- Extended critical region (PRE 109:014611): for finite N there are several critical lines. Critical confinement is proportional to the measurable perception range. Mixing data from different critical lines and N reproduces the measured static and dynamic exponents. — [arXiv:2309.05064](https://arxiv.org/abs/2309.05064)
- 2-D version: Entropy 25:1644 (2023). — [arXiv:2311.09135](https://arxiv.org/abs/2311.09135)
- "Whodunnit?" (Bonilla & González-Albaladejo, arXiv:2602.10242, v1 10 Feb 2026). They argue the periodic ISM and active model G give z = 1.35, ν = 0.748, γ = 1.171, close in z to field swarms (RMA 1.37 ± 0.11) but far from the measured static exponents ν = 0.35, γ = 0.9. The ISM's dynamic-correlation collapse works for all times, while field data collapse only for 0 < k_c^z t < 4, and the ISM's uniform density does not match swarm shape. Anisotropic confinement gives elongated swarms with static exponents between the 2-D and isotropic 3-D values, closer to the data. — [arXiv:2602.10242](https://arxiv.org/abs/2602.10242)
- ISM with position-dependent forces, including harmonic confinement: the Cavagna/Grigera side extends the ISM to confinement and cohesion. — [arXiv:2312.06368](https://arxiv.org/abs/2312.06368)
- Starling relevance, from the Rome group: in starlings over the roost the rotational symmetry is spontaneously broken, whereas jackdaws heading to a roost and homing pigeons "need to follow one specific direction, hence there is no spontaneous symmetry breaking", so their orientation correlations "could be quite different". — [arXiv:2101.09748](https://arxiv.org/abs/2101.09748)
  → Sim: run a control with roost/target attraction W_TGT and W_GLOBAL set to 0 (periodic or very weak confinement) and compare ξ/L and C(r) collapse. If ξ/L drops substantially, the app's scale-freeness is confinement-driven rather than Goldstone. Also log the largest finite-time Lyapunov exponent of the flock (twin-run divergence) vs W_TGT.

### Inferences
- The app's roost attraction acts like a harmonic confinement. The confined-Vicsek results say confinement plus noise can sit on a chaotic critical line where ξ ∝ L, which would be an artefact relative to the starling Goldstone mechanism. The real Rome flocks are dominated by their own symmetry-broken heading (Φ > 0.95), whereas confined-Vicsek swarms have low polarization, so the risk applies mainly if the app is run at high noise or strong W_TGT.

### Gaps
- No paper applies the confined-Vicsek analysis to polarized bird flocks or murmurations. No Cavagna-group published rebuttal of "Whodunnit?" was found (it is recent).

---

## Q7. 2020–2026 tests or disputes of "near-critical" claims in bird flocks

### Takeaway
Direct new tests on birds are scarce. The main empirical development is the Rome group's own: marginal speed confinement (2022), then overdamped spontaneous fluctuations with linear turns (2025). Both move criticality from "tuned near a transition" to "Goldstone orientation plus zero-temperature marginal speed, with nonlinear (soliton) response". Information-theoretic work shows that transfer entropy is not a clean criticality signature in flocks. Several preprints show that linear turn propagation and critical-like cascades can arise without inertia or tuning, from non-reciprocity or minority-following.

### Cited Findings
- Information flow: in finite Vicsek-type flocks, global transfer entropy "not only fails to peak near the phase transition … but remains constant from the transition throughout the entire ordered regime to very low noise values" (Sci Rep 2020, doi:10.1038/s41598-020-59080-6). — [PMC7052242](https://pmc.ncbi.nlm.nih.gov/articles/PMC7052242/)
  → Sim: do not use transfer entropy as a criticality meter. A flat TE across `?noise` values in the ordered phase is the expected result.
- "Behavior of information flow near criticality" (PRE 103:L010102, 2021) asks how information transmission behaves near the critical point. Its conclusion was not extracted (the abstract was truncated in the index). — [PMID 33601642](https://pubmed.ncbi.nlm.nih.gov/33601642/) — **UNVERIFIED**
- Non-reciprocity alone, in a "spinless" aggregation-based model, gives constant-speed turn propagation, with spectral anomalies explained perturbatively. — [arXiv:2511.17804](https://arxiv.org/abs/2511.17804) (preprint)
  → Sim: the app's topological K = 7 rule is already non-reciprocal. Measure x(t) after a forced turn without adding inertia. If α ≈ 3 in r(t) ~ t^α, the linear propagation comes from non-reciprocity and the ISM may be unnecessary for the turn target.
- Massive fish-school models: linear information propagation from non-reciprocal visual interactions, and ξ decreases before fragmentation. — [arXiv:2505.05822](https://arxiv.org/abs/2505.05822)
- Fish: subcritical schools that tune toward criticality under risk (Poel 2022, Q5); stress-induced critical state (Lin et al., Q5).
- Ant collectives (not birds): maximal response to a robotic leader at a critical group size (Nat Commun 2025). — [PMC12219395](https://pmc.ncbi.nlm.nih.gov/articles/PMC12219395/)
- Starling escape (Papadopoulou et al. 2026, Commun Biol): "flock members often differ in their evasive maneuvers and … several collective patterns arise simultaneously across a flock". — [PMC13448496](https://pmc.ncbi.nlm.nih.gov/articles/PMC13448496/) (numbers not extracted)
- Goldstone vs criticality: the Rome group states that symmetry breaking "automatically" gives scale-free orientation correlations, while speed "requires a different correlation mechanism". — [arXiv:2101.09748](https://arxiv.org/abs/2101.09748)
- Alternative "structural criticality": an aggregation model shows scale invariance rooted in its definition, unifying swarms and flocks. — [arXiv:2509.05140](https://arxiv.org/abs/2509.05140) (preprint)
- An older dissent: scale-free *speed* correlations as a phonon (broken translational symmetry) rather than near-criticality. — [arXiv:1702.08067](https://arxiv.org/abs/1702.08067)

### Inferences
- No 2020–2026 paper directly measures susceptibility vs a control parameter, Fisher information, or perturbation responsiveness in real bird flocks. The bird evidence base is still the Rome datasets plus jackdaws.

### Gaps
- No Fisher-information test on bird data was found. The Lin et al. fish results and Chen et al. robot results were not extracted in detail.

---

## Q8. Is bird behavioural noise coloured (OU-like) or white plus inertia? Single-bird autocorrelation times

### Takeaway
I found **no direct empirical evidence for persistent coloured behavioural noise in starlings**. Every model fitted to starling or pigeon trajectories uses white noise: Mora 2016 (dynamical max-ent), Cavagna 2022 simulations, Gao et al. 2024 (pigeon SDE inference). Correlated noise is acknowledged as an untested alternative. The only measured relaxation scale is starling orientation relaxation, τ_relax ≈ 0.2 s (order of magnitude). The app's NOISE_TAU = 4 s is therefore an unsupported modelling choice, about 20× longer than the inferred alignment relaxation. It is not ruled out, because the linear turn propagation and FPUT results imply memory or inertia of some kind.

### Cited Findings
- Starlings: the dynamical inference uses an overdamped Langevin equation with Gaussian white noise of covariance ∝ 4T. Sampling at dt = 0.2 s is "of the same order as the orientation relaxation time τ_relax". τ_relax = (J n_c)⁻¹ is more than 10× shorter than τ_network. — [arXiv:1511.01958](https://arxiv.org/abs/1511.01958)
  → Sim: measure the single-bird autocorrelation of the heading fluctuation π_i(t) in the flock frame, keeping only modes with k ≥ 1/r_c. Empirical target: exponential decay with τ ≈ 0.2 s (order of magnitude). With OU τ = 4 s the app will show a slow tail at ~4 s.
- Marginal-speed paper: "more complex dynamical evolutions … could be adopted, including different kinds of fluctuating terms or correlated noise". The simulations use white Gaussian noise of variance 2dTΔt. — [arXiv:2101.09748](https://arxiv.org/abs/2101.09748)
- ISM and FPUT models use white noise, ⟨ζζ⟩ = 2Tηδ(t−t′). Memory there comes from inertia (χ), not from coloured noise. — [arXiv:2602.10242 (ISM equations)](https://arxiv.org/abs/2602.10242), [arXiv:2505.19665](https://arxiv.org/abs/2505.19665)
- Pigeons (Gao, Barzel, Yan 2024, Nat Commun 15:6029): from GPS homing flights (Nagy 2010 data; one set of 8 and three sets of 7 birds; 0.2 s sampling, spline-interpolated to 0.01), sparse inference finds a second-order SDE "remarkably" similar to the second-order Vicsek model. It has alignment Â(r) = a₁(e^(−r/3) + a₂) + a₃, a cohesion term and self-propulsion s₁(|v|² + s₂) + s₃, with **additive white noise ε̂ dW_t**. Coefficients are in the SI, not extracted. — [PMC11254936](https://pmc.ncbi.nlm.nih.gov/articles/PMC11254936/)
  → Sim: pigeon data are fitted with *second-order dynamics (velocity with inertia) plus white noise*, not first-order plus OU noise. Offer `?noise=white` with a per-bird velocity relaxation time as the empirically grounded alternative.
- Jackdaws: Reynolds et al. 2022 (J R Soc Interface 19:20210745) uses an Okubo-type model with Wiener noise and qualitative parameters "set to unity". Reynolds 2025 adds a velocity-memory timescale T, i.e. an OU velocity process driven by white noise. — [PMC9019524](https://pmc.ncbi.nlm.nih.gov/articles/PMC9019524/), [doi:10.1098/rsif.2025.0020](https://doi.org/10.1098/rsif.2025.0020)
- Method caveat: naive finite-difference inference of second-order (inertial) models fails regardless of sampling rate. Higher-order estimators are needed, which matters when deciding between OU noise and inertia from trajectories. — [arXiv:1912.10491](https://arxiv.org/abs/1912.10491), [PRL 125:058103](https://pubmed.ncbi.nlm.nih.gov/32794851/)
- Midges: single-midge trajectories are Lévy-flight-like, and accelerations are consistent with a linear spring binding them to the swarm (a non-bird comparator). — [arXiv:2602.10242](https://arxiv.org/abs/2602.10242)

### Inferences
- Within the white-noise models fitted to data, the persistence of individual headings comes from the alignment relaxation (~0.2 s) and from Goldstone slow modes, not from the noise itself. An OU τ of 4 s injects power at ω ≲ 0.25 rad/s. That would show up in C(k,ω) as excess low-frequency weight beyond the Lorentzian ω_L = D k², which is a testable discriminator against the 2025 data.
- The app needed τ = 4 s plus stiff W_ALI to keep long-range C(r) (source comment). The literature instead attributes the extra long-range correlation to boundary-driven inflow (Cavagna 2013) or to marginal speed control, not to coloured noise.

### Gaps
- No starling trajectory paper reports the single-bird heading or speed autocorrelation time in seconds. Mora 2016's per-event τ_relax and J values sit in a figure that was not extracted. The pigeon SDE coefficients (SI Table 5) were not extracted. No study was found that tests OU noise against inertia on bird data.
