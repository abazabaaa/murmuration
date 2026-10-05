# Criticality in starling flocks: canonical references and what they mean for `murmuration.html`

Compiled 2026-10-05. Every citation below was checked against a DOI, journal page, PubMed/PMC record or arXiv full text. Numbers quoted come from the paper text (arXiv or PMC full text) unless marked **unverified**. Where the arXiv preprint rather than the journal version was the source of a number, this is flagged, because a few values (notably the turn propagation speeds) differ slightly between versions.

Conventions: Φ polarization; C(r) connected velocity correlation; ξ the zero of C(r) (Cavagna 2010 definition) unless stated; L flock linear size (largest inter-bird distance); r₁ nearest-neighbour distance; n_c number of interacting neighbours; J alignment coupling; g speed stiffness; c_s turn propagation speed; z dynamic critical exponent.

---

## (a) Annotated bibliography, in order of importance

### Core STARFLAG / Rome COBBS results on starlings

**1. Cavagna A, Cimarelli A, Giardina I, Parisi G, Santagati R, Stefanini F, Viale M (2010). Scale-free correlations in starling flocks. *PNAS* 107(26):11865–11870. doi:10.1073/pnas.1005766107. arXiv:0911.4393.**
24 flocking events, N = 122–4268 birds, L = 9.1–85.7 m, 10 fps stereo, tracking efficiency 0.77. Φ = 0.96 ± 0.03 (SD over flocks; individual events 0.844–0.995). Orientation correlation length ξ = aL with a = 0.35 (Pearson r = 0.98, n = 24, P < 10⁻¹⁶); speed correlation length ξ_sp = 0.36 L (r = 0.97). Rescaled C(r/ξ) collapses across flocks; the asymptotic decay exponent is γ = 0.19 ± 0.08 (orientation) and 0.19 ± 0.11 (speed), statistically indistinguishable from γ = 0 (RCS 0.045 vs 0.059). Centre-of-mass speeds 6.8–19.1 m/s. Criticality claim: scale-free correlations (ξ ∝ L, power-law C∞ ~ r^−γ with γ ≪ 1) imply the flock "behaves as a critical system, poised to respond maximally". Control parameter named: *noise* ("the key point is not the rule, but the noise"). Explicitly notes that fixed-speed models (Vicsek) cannot produce the observed speed correlations at all.

**2. Bialek W, Cavagna A, Giardina I, Mora T, Silvestri E, Viale M, Walczak AM (2012). Statistical mechanics for natural flocks of birds. *PNAS* 109(13):4786–4791. doi:10.1073/pnas.1118633109. arXiv:1107.0604.**
Maximum-entropy (Heisenberg-model) fit to the single number C_int (mean alignment with the first n_c neighbours; e.g. C_int = 0.99592 for one snapshot of event 28-10, giving J = 45.73 at n_c = 11). With border birds' directions fixed, predicts the full C(r), ξ ∝ L, and the non-monotonic four-point correlation with no free parameters. Averaged over flocks n_c = 21.2 ± 1.7; J and n_c show no trend with L, N or density; n_c^(−1/3) is independent of r₁ while a metric range r_c scales with r₁ (confirms topological interaction). Calibration on a self-propelled-particle simulation shows ME overestimates the true n_c by ~2.7× (because birds move and carry information), so n_c^ME = 21.6 corresponds to a true n_c ≈ 7.8, consistent with Ballerini's 7.0 ± 0.6. Criticality content: ξ ∝ L for orientation is the Goldstone mode of a broken continuous symmetry, *not* fine tuning; this paper is the source of "scale-free orientation correlations are generic in the ordered phase".

**3. Bialek W, Cavagna A, Giardina I, Mora T, Pohl O, Silvestri E, Viale M, Walczak AM (2014). Social interactions dominate speed control in poising natural flocks near criticality. *PNAS* 111(20):7212–7217. doi:10.1073/pnas.1324045111. arXiv:1307.5563.**
Extends the ME model to full velocity vectors: H = (J/4V²) Σ n_ij |v_i − v_j|² + (g/2V²) Σ (v_i − V)². Q_int (mean squared velocity difference to neighbours, normalised by V²) ~ 10⁻². Speed fluctuations obey ξ_bulk ~ r_c √(J n_c / g); critical point at g = 0. Fitting the observed speed variance gives **g/(J n_c) ~ 10⁻³**, "and this is typical": the social coupling exceeds the individual speed restoring force by three orders of magnitude. Predicted C_sp(r) and ξ_sp vs L match data with no free parameter. Dynamical SPP simulations (N up to 16384) confirm ξ_sp grows as g → 0 and saturates at a value ∝ L. Criticality content: *the speed degree of freedom is poised near the g = 0 critical point*; the orientation degree of freedom is not critical (Goldstone). Control parameter: g (relative to J n_c).

**4. Attanasi A, Cavagna A, Del Castello L, Giardina I, Grigera TS, Jelić A, Melillo S, Parisi L, Pohl O, Shen E, Viale M (2014). Information transfer and behavioural inertia in starling flocks. *Nature Physics* 10:691–696. doi:10.1038/nphys3035. arXiv:1303.7097 (preprint title "Superfluid transport of information in turning flocks of starlings").**
12 turning events, N = 50–595, 170 Hz cameras, Φ = 0.76–0.96 (lower than the 10 Hz data because wing-beat noise is resolved). Ranking birds by turning time gives x(t) = [r(t)/ρ]^(1/3) ∝ t: linear dispersion, with c_s in the range **≈ 10–20 m/s** (table in arXiv v1: 9.4–21.3 m/s; the 2025 follow-up by the same group cites "c_s ∈ [10:20] m/s" for this paper). Peak radial acceleration decays negligibly from first to last bird (no attenuation). The turn starts from a few spatially localised birds (mutual distance of the top-5 does not scale with L). a/c_s = 25–100 ms (mean ≈ 50 ms), comparable to starling reaction times. Theory: an inertial term (generalized moment of inertia χ, "spin" = curvature) added to alignment gives a d'Alembert equation with c_s² = a²J/χ; using J = ε/(1−Φ) predicts c_s/a ∝ 1/√(1−Φ), verified (R² = 0.74, P = 3.1×10⁻⁴). Criticality content: none directly; it argues the *high order* (Φ → 1) is what makes propagation fast, which is the opposite of a near-ordering-transition picture.

**5. Cavagna A, Del Castello L, Giardina I, Grigera T, Jelic A, Melillo S, Mora T, Parisi L, Silvestri E, Viale M, Walczak AM (2015). Flocking and turning: a new model for self-organized collective motion. *J. Stat. Phys.* 158:601–627. doi:10.1007/s10955-014-1119-3. arXiv:1403.1202.**
The Inertial Spin Model (ISM): dv_i/dt = (1/χ) s_i × v_i; ds_i/dt = v_i × [(J/v₀²) Σ n_ij v_j − (η/v₀²) ds_i/dt... + noise]. Quasi-equilibrium dispersion ω(k) = −iγ ± √((J/χ)a²k² − γ²), γ = η/2χ. Underdamped (small η) → linear waves c_s = a√(J/χ); overdamped limit → Vicsek (diffusive, ω = i(J/η)a²k²). Reduces to Toner–Tu at large scales. Numerical: only the underdamped regime lets one bird's turn elicit a collective turn.

**6. Cavagna A, Giardina I, Grigera TS (2018). The physics of flocking: Correlation as a compass from experiments to theory. *Physics Reports* 728:1–62. doi:10.1016/j.physrep.2017.11.003.**
The group's own synthesis: static correlations (Sec. 2), information propagation and the ISM (Sec. 3), space–time correlations (Sec. 4). Useful for definitions (connected correlation with instantaneous spatial mean, the sum rule forcing a zero of C(r), finite-size ξ estimators) and for the explicit statement that Vicsek and Toner–Tu both have scale-free orientation correlations yet fail to reproduce linear turn propagation.

**7. Cavagna A, Culla A, Feng X, Giardina I, Grigera TS, Jelić A, Melillo S, Parisi L, Pisegna G, Postiglione L, Villegas P (2022). Marginal speed confinement resolves the conflict between correlation and control in collective behaviour. *Nature Communications* 13:2315. doi:10.1038/s41467-022-29883-4. arXiv:2101.09748.** (Author list from PubMed record PMID 35538068; verify order against the journal page.)
New 2019–2020 data extend the size range to **N = 10–3000**. Mean flock speed ≈ 12 m/s with flock-to-flock fluctuations ≈ 2 m/s; Φ typically > 0.9; mean speed independent of N (Spearman r_S = −0.13, p = 0.21); ξ_sp ∝ L (r_P = 0.97, p < 10⁻⁹). Elongation: main-axis aspect ratio L₁/L₂ typically **6–8**. Shows that the linear (Bialek 2014) speed control fails: scale-free correlations need g < 1/L_max², but then the entropic s² Jacobian drives the typical group speed of small flocks far above v₀ (s_typ = ½v₀[1 + √(1 + 4T/(N g v₀²))]); g = 10⁻³ was the only stiffness giving scale-free ξ_sp at all sizes, and it produces implausible speed distributions. Replaces it by a *marginal* potential V = λ(v_i·v_i − v₀²)⁴/v₀⁶ (zero curvature at v₀, steep beyond), which gives ξ_sp ∝ L at the experimental Φ and a mean speed almost independent of N, with no fine tuning. Methods note: with their alternative estimator ξ = r₀/3, flocks have ξ ≈ L/9 (since r₀ ≈ L/3). Criticality content: a **zero-temperature (zero-noise) critical point** for the speed modulus; one gets there simply by lowering the noise, which also raises Φ. Control parameter: noise T (and the shape of the confinement, not its stiffness).

**8. Cavagna A, Culla A, Di Carlo L, Giardina I, Grigera TS (2019). Low-temperature marginal ferromagnetism explains anomalous scale-free correlations in natural flocks. *Comptes Rendus Physique* 20(4). doi:10.1016/j.crhy.2019.05.008. arXiv:1812.07522.**
Lattice/mean-field version of item 7: a ferromagnet whose single-site modulus potential is marginal develops a T = 0 critical point with divergent modulus susceptibility and correlation length (ξ_sp ~ T^(−1/2) in mean field) while ordinary behaviour at T_c is unchanged. See also the RG study, Cavagna et al. (2022) *Phys. Rev. E* 106:054136, doi:10.1103/PhysRevE.106.054136 (arXiv:2202.04605): upper critical dimension d_c = 2, so in d = 3 the exponents are free-field (ν = 1/2, η = 0).

**9. Mora T, Walczak AM, Del Castello L, Ginelli F, Melillo S, Parisi L, Viale M, Cavagna A, Giardina I (2016). Local equilibrium in bird flocks. *Nature Physics* 12:1153–1157. doi:10.1038/nphys3846. arXiv:1511.01958.**
Dynamical maximum entropy on 14 events (N = 50–595, Φ = 0.957–0.997, v₀ = 8.5–29.2 m/s, r₀ = 0.62–1.24 m, 0.2 s sampling). Interaction J_ij = J exp(−k_ij/n_c) with k_ij the topological rank. Finds the orientation relaxation time τ_relax **more than an order of magnitude shorter** than the neighbour-rearrangement time τ_network, so equilibrium (fixed-network) inference is valid on the interaction scale; the 0.2 s sampling is itself of order τ_relax. Justifies treating flock orientations as a local quasi-equilibrium Heisenberg system.

**10. Ballerini M, Cabibbo N, Candelier R, Cavagna A, Cisbani E, Giardina I, Lecomte V, Orlandi A, Parisi G, Procaccini A, Viale M, Zdravkovic V (2008). Interaction ruling animal collective behavior depends on topological rather than metric distance: evidence from a field study. *PNAS* 105(4):1232–1237. doi:10.1073/pnas.0711437105. arXiv:0709.1916.**
Anisotropy of the nearest-neighbour distribution decays to isotropy after 6–7 neighbours regardless of density; metric range scales with r₁, topological range does not. n_c = 7.0 ± 0.6 as quoted in Bialek 2012. Simulations show topological interaction keeps cohesion under the density changes caused by predation.

**11. Ballerini M, Cabibbo N, Candelier R, Cavagna A, Cisbani E, Giardina I, Orlandi A, Parisi G, Procaccini A, Viale M, Zdravkovic V (2008). Empirical investigation of starling flocks: a benchmark study in collective animal behaviour. *Animal Behaviour* 76(1):201–215. doi:10.1016/j.anbehav.2008.02.004. arXiv:0802.1667.**
10 events, N = 448–2631 (table: 448–2631 internal birds). Shape: thickness I₁ = 5.3–19.0 m, aspect ratios I₂/I₁ = 2.8 ± 0.4 and I₃/I₁ = 5.6 ± 1.0 (95% CI), i.e. proportions 1 : 2.8 : 5.6, independent of N and V; I₁ ∝ V^(1/3) (R² = 0.97). Orientation: |I₁·G| = 0.93 ± 0.04 (flock plane parallel to ground), |V·G| = 0.13 ± 0.05, |V·I₁| = 0.19 ± 0.08; no correlation between elongation axis and velocity. r₁ = 0.68–1.51 m, density 0.04–0.80 birds/m³ (ρ ∝ r₁⁻³), neither depending on N. Hard-core exclusion comparable to wingspan (0.4 m; densest flocks r₁ ≈ 3.5 body lengths ≈ 1.7 wingspans). Border denser than centre. Speeds 6.9–15.2 m/s. Turns follow equal-radius paths: the velocity rotates relative to the flock axes, the flock banks (I₁ tilts) during the turn.

### Criticality in other collective systems used as comparators

**12. Mora T, Bialek W (2011). Are biological systems poised at criticality? *J. Stat. Phys.* 144(2):268–302. doi:10.1007/s10955-011-0229-4. arXiv:1012.2242.**
Review of inverse (max-ent) models of protein families, retinal neurons and flocks; argues that data-fitted models sit near critical points in parameter space, and proposes Zipf's law / divergent specific heat as general signatures. For flocks it uses the 2012 model; the flock argument is essentially the Goldstone/scale-free one.

**13. Attanasi A, Cavagna A, Del Castello L, Giardina I, Melillo S, Parisi L, Pohl O, Rossaro B, Shen E, Silvestri E, Viale M (2014). Finite-size scaling as a way to probe near-criticality in natural swarms. *Phys. Rev. Lett.* 113:238102. doi:10.1103/PhysRevLett.113.238102. arXiv:1412.6975.**
Midges (Chironomidae, Ceratopogonidae), low Φ. Susceptibility proxy χ = (1/N) Σ_{i≠j} δφ_i·δφ_j θ(r₀ − r_ij) ranges 0.12–5.6 vs 0.1 for non-interacting; χ grows with N and ξ with L without saturating. Control parameter x = r₁/body length is *measured* and decreases with N along a finite-size critical line x_max(N). FSS fits: natural swarms ν = 0.35 ± 0.1, γ = 0.9 ± 0.2, x_c = 12.5 ± 1.0; 3-d Vicsek ν = 0.75 ± 0.02, γ = 1.6 ± 0.1, x_c = 0.421 ± 0.002. States plainly that this FSS test *cannot be done on bird flocks* because the control parameter is not measurable and density is irrelevant (topological interaction).

**14. Cavagna A, Conti D, Creato C, Del Castello L, Giardina I, Grigera TS, Melillo S, Parisi L, Viale M (2017). Dynamic scaling in natural swarms. *Nature Physics* 13:914–918. doi:10.1038/nphys4153. arXiv:1611.08201.**
Space–time correlation C(k,t) in midge swarms (N = 100–300) collapses as f(k^z t); τ_k ~ k^(−z) with **z = 1.12 ± 0.16** (collapse optimum 1.2), versus z = 1.96 ± 0.04 for 3-d Vicsek at its finite-size critical point. Relaxation is non-exponential (flat at short t: "spin-wave remnants") → inertial, non-dissipative dynamics. Introduces the "near-critical censorship of hydrodynamics": with ξ ~ L the hydrodynamic regime kξ ≪ 1 is inaccessible.

**15. Cavagna A, Di Carlo L, Giardina I, Grigera TS, Melillo S, Parisi L, Pisegna G, Scandolo M (2023). Natural swarms in 3.99 dimensions. *Nature Physics* 19:1043–1049. doi:10.1038/s41567-023-02028-0. arXiv:2107.04432.**
One-loop RG of an incompressible active theory with inertial spin coupling: a new fixed point with **z = 1.35** in d = 3 (1.73 without inertia, 2 without activity). Re-analysis of the swarm data with 8 new events (largest N = 780) and reduced-major-axis regression gives **z_exp = 1.37 ± 0.11** (the 2017 least-squares value was biased low); ISM simulations give 1.35 ± 0.04. Underdamped regime holds while ηL^z ≪ 1.

### Information transfer, waves, shape, predation (behavioural literature)

**16. Cavagna A, Cimino G, Cristín J, Fiorini M, Giardina I, Giustiniani A, Grigera TS, Melillo S, Palombella RA, Parisi L, Ponno A, Scandolo M, Stamler ZS (2025). Spin-waves without spin-waves: a case for soliton propagation in starling flocks. arXiv:2505.19665 (v2, Aug 2025). Journal status unverified.**
New panning stereo rig: 9 flocks, N = 180–1514, acquisitions up to 12.5 s (vs 3 s before). The spontaneous C(k,ω) is **Lorentzian with half-width ω_L ~ k²** (overdamped), with no spin-wave peaks (which, for c_s = 10–20 m/s and k = 3 m⁻¹, would sit at 30–60 rad/s), yet imposed turns still propagate linearly. Wing-flap peak at ≈ 68 rad/s (10 Hz) is not a spin wave. Reconciled by adding a quartic alignment term (Fermi–Pasta–Ulam–Tsingou): small fluctuations are overdamped by a low J, large perturbations propagate as solitons via a large J₄. Predicts again c_s ~ 1/√(1−Φ). Strongly relevant: it says the linear ISM is *not* the right model of spontaneous fluctuations.

**17. Attanasi A, Cavagna A, Del Castello L, Giardina I, Jelić A, Melillo S, Parisi L, Pohl O, Shen E, Viale M (2015). Emergence of collective changes in travel direction of starling flocks from individual birds' fluctuations. *J. R. Soc. Interface* 12:20150319. doi:10.1098/rsif.2015.0319. arXiv:1410.3330.**
Spontaneous turns are initiated by birds at the elongated tips of the flock, which deviate from the mean heading more often; turns follow equal-radius paths and redistribute risky positions.

**18. Cavagna A, Giardina I, Ginelli F (2013). Boundary information inflow enhances correlation in flocking. *Phys. Rev. Lett.* 110:168107. doi:10.1103/PhysRevLett.110.168107. arXiv:1206.6314.**
Explains the anomalously small γ ≪ 1: a *dynamical field on the boundary* of a 3-d Heisenberg system drives long-wavelength spin waves from border to bulk and gives γ → 0, which neither equilibrium theory nor Toner–Tu/Vicsek achieve (they give γ ≈ 1 in d = 3 for the Goldstone mode). Suggests the flock is kept in a state of permanent excitation (exogenous or endogenous).

**19. Cavagna A, Del Castello L, Dey S, Giardina I, Melillo S, Parisi L, Viale M (2015). Short-range interactions versus long-range correlations in bird flocks. *Phys. Rev. E* 92:012705. doi:10.1103/PhysRevE.92.012705. arXiv:1407.6887.**
Full functional form of the ME interaction: decays exponentially over a few topological neighbours; introduces the J_ij = J exp(−k_ij/n_c) form used in item 9.

**20. Cavagna A, Duarte Queirós SM, Giardina I, Stefanini F, Viale M (2013). Diffusion of individual birds in starling flocks. *Proc. R. Soc. B* 280:20122484. doi:10.1098/rspb.2012.2484.**
Individual birds diffuse through the flock (super-diffusive relative motion); vertical fluctuations are strongly suppressed by gravity (used to justify planar turning in item 4).

**21. Procaccini A, Orlandi A, Cavagna A, Giardina I, Zoratto F, Santucci D, Chiarotti F, Hemelrijk CK, Alleva E, Parisi G, Carere C (2011). Propagating waves in starling, *Sturnus vulgaris*, flocks under predation. *Animal Behaviour* 82(4):759–765. doi:10.1016/j.anbehav.2011.07.006.**
329 hunting sequences by peregrines over two Rome roosts, 210 triggering wave events. Waves originate at the predator and always move away from it; single-pulse velocity up to 25 m/s (range 3.66–25.24 m/s, mean 13.4 m/s as quoted by Hemelrijk et al. 2015), faster than the flock (≈ 10.6 m/s); frequency 0.7–2 pulses/s; waves correlate with reduced capture success. Interpreted as density waves (later revised, item 22).

**22. Hemelrijk CK, van Zuidam L, Hildenbrandt H (2015). What underlies waves of agitation in starling flocks. *Behav. Ecol. Sociobiol.* 69:755–764. doi:10.1007/s00265-015-1891-3.**
In StarDisplay (2000 birds, NND 1.3 m, reaction time 76 ms, cue identification 50 ms), agitation waves appear only if birds *repeat* an escape manoeuvre of 2–7 nearest neighbours, and only for a roll-sideways-and-back ("zig") manoeuvre: the dark band is an **orientation wave** (change of projected wing area), not a density wave; speeding-up-forward produces no visible wave. Wave speed rises with the number of neighbours copied and with NND (0.7–2 m), falls with reaction/cue time, is independent of flock size, and spans the empirical 3.7–25 m/s. Back-of-envelope: NND/reaction time = 1.1 m / 0.076 s ≈ 14.5 m/s.

**23. Storms RF, Carere C, Zoratto F, Hemelrijk CK (2019). Complex patterns of collective escape in starling flocks under predation. *Behav. Ecol. Sociobiol.* 73:10. doi:10.1007/s00265-018-2609-0.**
182 hunting sequences, 67 analysed frame by frame: 795 collective events, 210 attacks. Blackening most common (n = 289), vacuole rarest (n = 5). Wave events last 3.5 ± 0.23 s with 2.88 ± 0.19 pulses, 0.86 s apart; they occur ≈ 13 s before/after attacks and are most likely for medium-speed attacks. Flash expansion is the only pattern that follows an attack immediately (and more for fast attacks from above: 121/175 attacks from above, 144 at medium speed); 78.3% of flash expansions do not lead to a split. Flock dilution takes 15.0 ± 2.4 s after an attack.

**24. Hildenbrandt H, Carere C, Hemelrijk CK (2010). Self-organized aerial displays of thousands of starlings: a model. *Behavioral Ecology* 21(6):1349–1359. doi:10.1093/beheco/arq149.** and **Hemelrijk CK, Hildenbrandt H (2011). Some causes of the variable shape of flocks of birds. *PLoS ONE* 6(8):e22479. doi:10.1371/journal.pone.0022479.**
StarDisplay: Reynolds-type rules plus simplified fixed-wing aerodynamics (banking, lift/drag, speed control), a fixed topological range of 6–7 neighbours, and roost attraction; reproduces the thin, horizontal, variable-shape flocks of Ballerini 2008 and the shape changes during turns. Also **Hemelrijk CK, Hildenbrandt H (2015). Scale-free correlations, influential neighbours and speed control in flocks of birds. *J. Stat. Phys.* 158:563–578. doi:10.1007/s10955-014-1154-0** (cited in O'Coin et al. 2023; content not read here — unverified beyond title) which reports that StarDisplay reproduces ξ ∝ L and ties the speed correlation to the speed-control term.

**25. Goodenough AE, Little N, Carpenter WS, Hart AG (2017). Birds of a feather flock together: insights into starling murmuration behaviour revealed using citizen science. *PLoS ONE* 12(6):e0179277. doi:10.1371/journal.pone.0179277.**
3,211 citizen reports (UK-dominated), 1,066 confirmed (≥ 500 birds, seen to roost). Mean 30,082 ± 6,699 (SEM) birds, maximum 750,000; mean duration 26 min ± 44 s; size peaks early February. Birds of prey present at 29.6% of murmurations; predator presence/activity explains 35–40% of the variance in size (R² = 0.401 with activity) and 26% of duration; temperature a weak negative predictor of duration; with predators present, murmurations more often end *en masse* to roost. Supports the anti-predator ("safer together") hypothesis. No 3-D kinematics.

**26. Pearce DJG, Miller AM, Rowlands G, Turner MS (2014). Role of projection in the control of bird flocks. *PNAS* 111(29):10422–10426. doi:10.1073/pnas.1402202111. arXiv:1407.2414.**
Opacity Θ′ (fraction of sky obscured, external view) of UK starling flocks: n = 118 measurements, Gaussian fit μ = 0.30, σ² = 0.059; public-domain images μ = 0.41, σ² = 0.012; overall 0.25 ≲ Θ′ ≲ 0.6, for very different sizes ("marginal opacity"). Mean-field: Θ′ ≈ 0.5 requires ρ ∝ N^(−1/2) in 3-d, so density must fall with N or shape must change; halving spacing takes Θ′ from 50% to 94%. Model: each bird steers toward the mean direction of the light/dark boundaries in its projected view, plus alignment with 4 nearest neighbours; opacity emerges independent of N, flock never fragments, and response to shocks is fast because the projection is a global interaction. Criticality content: marginal opacity is a *self-tuned, size-independent intermediate state*, an alternative "criticality-like" regulation with a different control variable (density/opacity), not a phase transition.

### Other species and critiques

**27. Ling H, Mclvor GE, Westley J, van der Vaart K, Vaughan RT, Thornton A, Ouellette NT (2019). Behavioural plasticity and the transition to order in jackdaw flocks. *Nature Communications* 10:5174. doi:10.1038/s41467-019-13281-4.**
Wild jackdaws: 6 transit flocks (N = 25–330) interact topologically with 7–8 neighbours and are ordered regardless of density; 10 mobbing flocks (N = 4–120) interact metrically with range ≈ 5 m (14 body lengths), and 154 sub-groups show an order–density transition Φ ~ ρ^β consistent with Vicsek with near-zero critical density (vanishing noise). Demonstrates that the interaction *rule* itself is context-dependent.

**28. O'Coin D, Mclvor GE, Thornton A, Ouellette NT, Ling H (2023). Velocity correlations in jackdaw flocks in different ecological contexts. *Physical Biology* 20(1):016005. doi:10.1088/1478-3975/aca862.**
In both contexts ξ grows linearly with group size (scale-free); ξ is independent of density in transit flocks but increases with density in mobbing flocks (metric interaction); polarization has no significant effect on ξ. Slopes not read here (full text behind paywall) — **slope values unverified**.

**29. Ling H, Mclvor GE, Westley J, van der Vaart K, Yin J, Vaughan RT, Thornton A, Ouellette NT (2019). Collective turns in jackdaw flocks: kinematics and information transfer. *J. R. Soc. Interface* 16:20190450. doi:10.1098/rsif.2019.0450.**
All flocks slow during turns; turn rate scales with turn angle so the turn duration is constant; initiators are anywhere in transit flocks but at the front in mobbing flocks; information-transfer speed increases with group size then saturates. Numerical c_s values not extracted (abstract only) — **unverified**.

**30. Casiulis M, Tarzia M, Cugliandolo LF, Dauchot O (2020). Velocity and speed correlations in Hamiltonian flocks. *Phys. Rev. Lett.* 124:198001. doi:10.1103/PhysRevLett.124.198001. arXiv:1911.06042.** With **Cavagna A, Giardina I, Grigera TS, Mora T, Walczak AM (2019) Comment, arXiv:1912.07056** and **Casiulis et al. Reply, arXiv:1912.09202.**
A conservative 2-d spin–velocity fluid gives bird-like velocity and speed correlation functions through rigid rotations of a moving droplet, offered as a simpler alternative to Goldstone + near-critical speed. The Comment argues rigid rotation is inconsistent with the equal-radius turns, the absence of a flock-wide angular velocity and the independence of ξ from turning in the starling data.

**31. Klamser PP, Romanczuk P (2021). Collective predator evasion: putting the criticality hypothesis to the test. *PLoS Comput. Biol.* 17(3):e1008832. doi:10.1371/journal.pcbi.1008832. arXiv:2009.02079.**
Spatial predator–prey SPP model: the group optimum (lowest capture rate) does lie near the order–disorder transition, but because of spatial structure, not maximal responsiveness; individual-level evolution of the alignment strength drives the ESS deep into the ordered phase (ESS μ_alg ≈ 4.4 vs μ_c ≈ 0.9), so the critical point is *evolutionarily unstable*. A direct challenge to criticality-as-adaptation for fission–fusion groups of unrelated individuals.

**32. Muñoz MA (2018). Colloquium: Criticality and dynamical scaling in living systems. *Rev. Mod. Phys.* 90:031001. doi:10.1103/RevModPhys.90.031001. arXiv:1712.04499.**
Balanced review; lists flocks among the systems with evidence for criticality and discusses generic scale invariance, Goldstone modes and self-organised alternatives as confounders.

**33. Cavagna A, Del Castello L, Giardina I, Grigera TS, Jelić A, Melillo S, Parisi L, Viale M (2015). Silent flocks: constraints on signal propagation across biological groups. *Phys. Rev. Lett.* 114:218101. doi:10.1103/PhysRevLett.114.218101.** Toner–Tu + spin field: second sound at short wavelengths, a gap separating first from second sound, and the existence of medium-sized "silent" flocks.

**34. Chen Y, et al. (2023). Exploring the criticality hypothesis using programmable swarm robots with Vicsek-like interactions. *J. R. Soc. Interface* 20:20230176. doi:10.1098/rsif.2023.0176.** Robotic test of responsiveness near the ordering transition (author list beyond title unverified).

**35. Papadopoulou M, et al. (2026). A mechanistic understanding of collective escape in starling flocks. *Communications Biology* (2026). doi:10.1038/s42003-026-10173-4. bioRxiv 10.1101/2024.10.27.620514.** Combines field data and a model; flock members differ in evasive manoeuvres and several collective patterns co-occur. Author list and numbers **unverified** (title/DOI from PubMed record PMID 42151575).

---

## (b) Empirical numbers with source

| Quantity | Value | Source |
|---|---|---|
| Polarization Φ (10 fps data) | 0.96 ± 0.03 (SD, 24 flocks; range 0.844–0.995) | Cavagna 2010 |
| Φ (170 Hz data, turning flocks) | 0.76–0.96 (wing-beat noise resolved) | Attanasi 2014 NatPhys |
| Φ (dynamical ME dataset) | 0.957–0.997 | Mora 2016 |
| Φ (2019–20 dataset) | typically > 0.9 | Cavagna 2022 |
| ξ (orientation) vs L | ξ = 0.35 L, r = 0.98, n = 24 | Cavagna 2010 |
| ξ_sp (speed) vs L | ξ_sp = 0.36 L, r = 0.97 | Cavagna 2010 |
| Alternative estimator | ξ = r₀/3 ≈ L/9 | Cavagna 2022 Methods |
| Decay exponent γ | 0.19 ± 0.08 (orientation), 0.19 ± 0.11 (speed); γ = 0 not excluded | Cavagna 2010 |
| N, L ranges | 122–4268 birds, 9.1–85.7 m (2010); 10–3000 birds (2022) | Cavagna 2010, 2022 |
| CoM speed | 6.8–19.1 m/s (2010); ≈ 12 m/s mean, ≈ 2 m/s flock-to-flock fluctuation (2022) | Cavagna 2010, 2022 |
| Mean speed vs N | no dependence, r_S = −0.13, p = 0.21 | Cavagna 2022 |
| Interacting neighbours | 6–7; n_c = 7.0 ± 0.6 | Ballerini 2008 PNAS (as quoted in Bialek 2012) |
| ME effective n_c | 21.2 ± 1.7 (≈ 2.7× true value; calibrated true ≈ 7.8) | Bialek 2012 |
| Example ME J | J = 45.73 at n_c = 11 for C_int = 0.99592 (flock 28-10) | Bialek 2012 |
| Speed stiffness ratio | g/(J n_c) ~ 10⁻³ | Bialek 2014 |
| Neighbour velocity similarity Q_int | ~ 10⁻² (normalised by V²) | Bialek 2014 |
| Linear control: stiffness for scale-free ξ_sp | g < 1/L_max² (g = 10⁻³ in sim units) | Cavagna 2022 |
| τ_relax vs τ_network | τ_relax > 10× shorter; τ_relax ~ 0.2 s sampling | Mora 2016 |
| Turn propagation speed c_s | ≈ 10–20 m/s (table 9.4–21.3 m/s), linear x(t) = c_s t, negligible attenuation | Attanasi 2014 NatPhys (arXiv v1 table) |
| a/c_s | 25–100 ms, mean ≈ 50 ms | Attanasi 2014 NatPhys |
| c_s vs order | c_s/a ∝ 1/√(1−Φ), R² = 0.74, P = 3.1×10⁻⁴ | Attanasi 2014 NatPhys |
| Spontaneous C(k,ω) | Lorentzian, ω_L ~ k² (overdamped); 9 flocks N = 180–1514 | Cavagna 2025 arXiv |
| Wing-beat frequency | ≈ 10 Hz (peak at 68 rad/s) | Cavagna 2025 arXiv |
| Aspect ratios | I₂/I₁ = 2.8 ± 0.4, I₃/I₁ = 5.6 ± 1.0; thickness 5.3–19 m ∝ V^(1/3) | Ballerini 2008 AnimBehav |
| Main-axis aspect ratio L₁/L₂ | 6–8 | Cavagna 2022 |
| Flock plane | |I₁·G| = 0.93 ± 0.04; |V·G| = 0.13 ± 0.05 | Ballerini 2008 AnimBehav |
| Nearest-neighbour distance r₁ | 0.68–1.51 m; mean inter-bird distance r₀ 0.62–1.24 m | Ballerini 2008; Mora 2016 |
| Density | 0.04–0.80 birds/m³, ∝ r₁⁻³, independent of N | Ballerini 2008 AnimBehav |
| Hard core | ≈ wingspan 0.4 m (body length 0.2 m) | Ballerini 2008 AnimBehav |
| Border vs centre | denser at border (r₁ rises toward centre) | Ballerini 2008 AnimBehav |
| Opacity Θ′ | 0.25–0.6; μ = 0.30, σ² = 0.059 (n = 118); μ = 0.41 (images) | Pearce 2014 |
| Agitation wave speed | 3.66–25.24 m/s, mean 13.4 m/s; 0.7–2 pulses/s | Procaccini 2011 (as quoted in Hemelrijk 2015) |
| Wave event structure | 3.5 ± 0.23 s, 2.88 ± 0.19 pulses, 0.86 s spacing | Storms 2019 |
| Reaction time used in models | 76 ms (startle), cue identification 50 ms | Hemelrijk 2015 (Pomeroy & Heppner 1977) |
| Murmuration size/duration | mean 30,082 birds, max 750,000; 26 min | Goodenough 2017 |
| Predator presence | 29.6% of murmurations; R² = 0.40 (size), 0.26 (duration) | Goodenough 2017 |
| Midge susceptibility | χ = 0.12–5.6 vs 0.1 non-interacting | Attanasi 2014 PRL |
| Midge FSS exponents | ν = 0.35 ± 0.1, γ = 0.9 ± 0.2, x_c = 12.5 ± 1.0 | Attanasi 2014 PRL |
| 3-d Vicsek FSS | ν = 0.75 ± 0.02, γ = 1.6 ± 0.1, x_c = 0.421 ± 0.002 | Attanasi 2014 PRL |
| Dynamic exponent z (midges) | 1.12 ± 0.16 (2017, LS); 1.37 ± 0.11 (2023, RMA); RG 1.35; ISM sim 1.35 ± 0.04; Vicsek 1.96 ± 0.04 | Cavagna 2017, 2023 |
| Jackdaw interaction | topological 7–8 (transit); metric ≈ 5 m (mobbing) | Ling 2019 NatCommun |
| Jackdaw ξ | ∝ group size in both contexts | O'Coin 2023 |
| Predator-evasion ESS | μ_alg ≈ 4.4 vs μ_c ≈ 0.9 (ordered phase) | Klamser & Romanczuk 2021 |

---

## (c) Criticality synthesis

Five distinct things are called "criticality" in this literature. They should not be conflated.

**1. Scale-free static correlations (Cavagna 2010).** The empirical fact: ξ ∝ L for both orientation and speed, with C(r/L) collapsing and γ ≈ 0. The 2010 paper reads this as "flocks behave as critical systems" and names *noise* as the control parameter. Strength of evidence: the ξ ∝ L result is very robust (24 flocks, two orders of magnitude in N, reproduced in 2022 on 10–3000 birds and in jackdaws). The *interpretation* as proximity to a phase transition is what has been revised by the same group.

**2. Goldstone modes, not criticality, for orientation (Bialek 2012; Bialek 2014 App. E; Cavagna 2022).** In the ordered phase of any O(n) model, fluctuations transverse to the order parameter are massless: C_π(x) ∝ 1/|x| in 3-d, so ξ ∝ L automatically. A flock with Φ ≈ 0.96 is *deep in the ordered phase*, which Cavagna 2022 states "rules out the possibility that flocks are close to an ordering transition". The orientation half of the 2010 result therefore needs no tuning. Two residual puzzles remain: (i) the measured γ ≈ 0 is much smaller than the Goldstone value γ = 1 (Cavagna 2013 PRL attributes this to boundary-driven information inflow, i.e. the flock is perpetually excited by its border); (ii) the data were taken during spontaneous display flight with turns and predators, so some fraction of the long-range correlation is driven rather than thermal.

**3. Near-critical speed control (Bialek 2014).** Speed is a modulus, not a Goldstone mode; its correlation length is finite, ξ_bulk ~ r_c √(Jn_c/g), diverging only at g = 0. The data-fitted g/(Jn_c) ~ 10⁻³ places flocks "near criticality" in the sense that the individual speed stiffness is negligible against social coupling. Control parameter: g. Debate: Cavagna 2022 shows the linear-g theory cannot simultaneously give scale-free ξ_sp and a sensible mean speed across N = 10–3000 (entropic speed blow-up ∝ 1/√(Ng)), so "flocks tune g near 0" is replaced by "the speed confinement is marginal (quartic), so its curvature is zero for *all* λ, and the only tuning is low noise". In the marginal theory the relevant critical point is at T = 0, approached by lowering noise, which also raises Φ. This is the current best explanation of the speed data and it is a *weak* form of criticality: no parameter has to be tuned to a special value; the system is driven toward a zero-temperature critical point by the same thing that makes it ordered.

**4. Finite-size scaling of susceptibility and dynamic scaling (Attanasi 2014 PRL; Cavagna 2017, 2023).** These are the strongest *statistical-physics* criticality tests in the programme, but they are on midge swarms (low Φ, metric interaction, measurable control parameter x = r₁/ℓ). Swarms sit on a finite-size critical line x_max(N); χ and ξ grow with N and L without saturation; τ ~ ξ^z with z = 1.37 ± 0.11 matched by an RG fixed point with activity + inertia (z = 1.35). The PRL states explicitly that this analysis cannot be transposed to flocks (topological interaction, no measurable control parameter, deep ordered phase). For a starling model one should therefore not expect a susceptibility peak in the usual noise-scan sense to be the empirical target.

**5. Marginal opacity (Pearce 2014).** An intermediate, size-independent opacity Θ′ ≈ 0.3–0.4 maintained across very different N. This is self-organised regulation of a global variable (projected density), not proximity to a phase transition, but it is "critical" in the colloquial sense: most configurations are either transparent or opaque, flocks sit at the boundary. It is a competing mechanism for long-range coordination (vision-based global coupling) that would also produce scale-free correlations without any Goldstone or near-critical argument. Status: supported only by 2-D opacity measurements; no 3-D test against the Rome data exists.

**Where the evidence is strong.** ξ ∝ L for orientation *and* speed; Φ ≈ 0.96; n_c ≈ 7 topological; linear, undamped turn propagation at 10–20 m/s with c_s ∝ 1/√(1−Φ); orientation relaxation faster than network rearrangement; the thin, horizontal, 1:2.8:5.6 shape.

**Where it is debated or revised.** (a) Whether anything is "tuned": the orientation part is Goldstone (no tuning), the speed part has moved from "g ≈ 0" to "marginal confinement + low noise"; (b) γ ≈ 0 vs the Goldstone γ = 1 (boundary driving vs measurement limits over one decade of L); (c) rigid rotation (Casiulis 2020) as an alternative source of correlations — rejected by the Rome group on kinematic grounds; (d) whether criticality can be selected for at all in unrelated groups (Klamser & Romanczuk 2021: no, the critical point is an evolutionary repeller in their model); (e) the ISM itself: the 2025 data show spontaneous fluctuations are overdamped (Lorentzian, ω ~ k²) even though imposed turns propagate linearly, so a linear inertial model with one J is wrong and a strongly nonlinear (FPUT/soliton) response is proposed; (f) sampling: the 2010 Φ = 0.96 is a 10 fps number; at 170 Hz the same flocks read Φ ≈ 0.8–0.96 because wing-beat jitter is resolved, so any comparison of model Φ with data must specify the time resolution.

---

## (d) Prioritized simulation enhancements, with empirical targets

The app already reproduces ξ/L ≈ 0.33–0.38 (target 0.35–0.36) and shows the far-side anticorrelation and curve collapse. The gaps are Φ ≈ 0.99 vs 0.96, |u| ≈ 1.1–1.5 m/s vs ≈ 2 m/s, and the absence of any dynamical/turning observables. Ranked by (value for matching the literature) × (ease of implementation):

1. **Replace the quadratic speed hold with a marginal speed confinement** (Cavagna 2022): per-bird force −∂/∂v [λ (v² − v₀²)⁴ / v₀⁶] (or, in the small-fluctuation limit, a force ∝ (v − v₀)³ with asymmetric sharpness) instead of W_SPD·(v − v₀) and W_SPD4. The present model already has the right instinct (W_SPD4 = 0.002 is a quartic term) but still applies a linear term to the flock mean; the paper's point is that the *curvature at v₀ must be exactly zero*. Target: ξ_sp/L ≈ 0.36 unchanged as N goes 100 → 3000; mean speed within ±2 m/s of 12 m/s at all N; single-bird speed distribution width ≈ 2 m/s; measure the speed-fluctuation variance vs N and check it does not blow up at small N (the entropic 1/√(Ng) effect). Add a `?speed=linear|marginal` switch so both can be compared.

2. **Report Φ at two effective sampling rates.** The 0.99 vs 0.96 discrepancy may be partly a resolution artefact: the field value is from 10 fps velocities, i.e. displacement over 0.1 s including wing-beat and tracking noise. Compute Φ from positions differenced over 0.1 s (and over one frame) and show both; also add a tunable per-bird wing-beat jitter (10 Hz, amplitude a few cm) to the *measured* velocity, not the dynamics. Target: Φ(0.1 s) ≈ 0.96 ± 0.03, Φ(high rate) ≈ 0.8–0.95 as in Attanasi 2014. If Φ(0.1 s) is still 0.99, then noise is genuinely too low and |u| too small (see item 3).

3. **Raise velocity fluctuations to ≈ 2 m/s rms while keeping Φ ≈ 0.96 and ξ/L ≈ 0.35.** From the header, `?noise=1.5` gives |u| ≈ 1.9 m/s but stretches the flock to L ≈ 31 m and washes out the far-side anticorrelation. The literature suggests the missing ingredient is *driven* fluctuation from the border (Cavagna 2013 PRL) and from spontaneous turn initiation at the elongated tips (Attanasi 2015): add a persistent heading perturbation to border birds (identify border via a cheap α-shape proxy, e.g. birds with fewer than K neighbours within RN or with large asymmetry of their neighbour centroid) and measure γ by the derivative of C(r/ξ) at r = ξ vs ξ across runs with N = 100…3000. Target: |u| ≈ 2 m/s, γ < 0.2, C(r/L) collapse maintained.

4. **Turn propagation measurement and the c_s ∝ 1/√(1−Φ) test.** When the flock turns (waypoint switch or falcon), rank birds by the time of their peak radial acceleration, compute x(t) = (rank/ρ)^(1/3), fit the linear regime and report c_s. Target: c_s ≈ 10–20 m/s (20–40 world units/s), attenuation of peak acceleration from first to last bird small, a/c_s ≈ 25–100 ms, and a positive correlation of c_s/r₁ with 1/√(1−Φ) across runs with different `?noise`. The present first-order alignment (Vicsek-like, ω ~ ik²) will give *diffusive*, attenuated turns; matching the data requires the next item.

5. **Add behavioural inertia (ISM) as an option.** Give each bird a spin/angular-momentum state s_i with ds/dt = (social torque from alignment) − (η/χ) s + noise and dθ/dt = s/χ, i.e. the alignment force sets the *rate of change of turning rate* rather than the heading directly (Cavagna 2015). Parameters: χ, η with the condition η < √(ρ_s χ)/L for linear propagation across the flock (Attanasi 2014 App. E). Target: linear x(t), c_s = a√(J/χ) in the 10–20 m/s window, equal-radius turning (birds' trajectories cross; flock velocity rotates relative to the body axes, Ballerini 2008). Caveat from Cavagna 2025: with a single J the spontaneous C(k,ω) will show spin-wave peaks that real flocks lack; a quartic alignment term J₄ (small J for small misalignments, large J₄ for large ones) is the proposed fix. Implement the quartic term alongside the linear one.

6. **Space–time correlation C(k,t) and the dynamic exponent.** Compute C(k,t) = (1/N) Σ_ij δv̂_i(t₀)·δv̂_j(t₀+t) sin(k r_ij)/(k r_ij) at k = 1/ξ, extract τ_k by the ∫ (dt/t) sin(t/τ) Ĉ = π/4 rule, and check (i) whether relaxation is exponential (Vicsek-like, h(x→0) → 1) or has a flat start (inertial, h → 0), and (ii) τ_k vs ξ across N for z. Empirical anchor for starlings: the 2025 preprint reports Lorentzian C(k,ω) with ω_L ~ k² for *spontaneous* fluctuations, so the starling target is z ≈ 2-like overdamped spontaneous relaxation coexisting with linear turn propagation; the z ≈ 1.35 value is for midges and should not be a starling target.

7. **Flock shape and orientation diagnostics.** Compute the three principal dimensions (thickness I₁ as the smallest extent, I₂, I₃), report I₂/I₁, I₃/I₁ and the cosines |I₁·G|, |V·G|. Targets: 1 : 2.8 ± 0.4 : 5.6 ± 1.0; |I₁·G| ≈ 0.93; |V·G| ≈ 0.13; thickness ∝ V^(1/3); L₁/L₂ ≈ 6–8 in the 2022 dataset. The current model's levelling force should give a horizontal plane; the aspect ratios probably need an anisotropic separation/cohesion (weaker vertical cohesion or a stronger vertical levelling) as in StarDisplay's aerodynamic lift/banking.

8. **Density profile and nearest-neighbour statistics.** Report r₁, ρ, the hard-core radius (P(r) → 0 below ≈ 0.4 m) and r₁ as a function of distance from the border (target: denser border, r₁ rising toward the centre). Present separation radius RS = 5 u = 2.5 m is larger than the measured r₁ = 0.7–1.5 m; consider RS ≈ 2 u with a soft core to get r₁ ≈ 1 m at N = 400 while keeping ρ ∈ 0.04–0.8 m⁻³ and independent of N (R_FLOCK ∝ N^(1/3) already does the latter).

9. **Opacity meter (Pearce 2014).** Project the flock onto the camera plane and compute the fraction of a bounding region covered by bird silhouettes of size ≈ 0.4 m × 0.2 m; target Θ′ ≈ 0.3–0.4 and roughly constant as N changes. Cheap to add; it is also a good visual-realism knob, since the Poly Haven backdrop is seen *through* the flock.

10. **Agitation-wave experiment under the falcon.** When struck, let the directly threatened birds execute a roll-sideways-and-back ("zig") manoeuvre that neighbours within the topological range copy after a 50–76 ms delay (Hemelrijk 2015); render wing area so the band is visible. Targets: wave speed 13 m/s mean (4–25 m/s range), 0.7–2 pulses/s, 2–3 pulses per event lasting ≈ 3.5 s, propagation away from the predator, no visible density wave. The existing `alarm` state is the natural hook.

11. **Max-ent inference inside the sim as a consistency check.** From a snapshot, compute C_int(n_c) for n_c = 1…30 and the ME likelihood maximum (Bialek 2012 Eq. 7 with fixed border). Target: n_c^ME ≈ 20 (≈ 3× the true K = 7) and J·n_c roughly constant across N and density. This tests whether the model's correlation structure is "Heisenberg-like" in the same way the real data are. The speed version (Bialek 2014) gives a measured g/(Jn_c) to compare with 10⁻³.

12. **Finite-size scan of a susceptibility proxy.** χ = (1/N) Σ_{i≠j} u_i·u_j θ(ξ − r_ij)/c₀ vs N and vs `?noise`. For a starling model one expects monotone growth with N (ordered phase, Goldstone) rather than a peak in noise; a peak would indicate the model is sitting near an ordering transition, which the field data say real flocks are not. Useful as a *negative* test.

---

## (e) Open questions for a broader deep-research pass

1. Published vs preprint numbers in Attanasi et al. 2014 *Nature Physics*: confirm the c_s range and table in the journal version (the arXiv v1 table gives 9.4–21.3 m/s; the 2025 preprint quotes [10:20] m/s). Confirm whether the published version changed Φ values or event count.
2. Cavagna et al. 2025 "Spin-waves without spin-waves": has it appeared in a journal; what are the fitted J, J₄, χ, η and the implied c_s; does the Lorentzian half-width give an effective diffusion constant (J/η)a² one can compare with the app's W_ALI·3.5 u² ≈ 63 u²/s?
3. Hemelrijk & Hildenbrandt 2015 *J. Stat. Phys.* 158:563 (scale-free correlations and speed control in StarDisplay): what speed-control form and what ξ/L slope did they obtain; this is the closest existing agent-based benchmark for the app.
4. O'Coin et al. 2023 and Ling et al. 2019 (RSIF): extract the ξ-vs-size slopes and the jackdaw c_s values and saturation group size; compare with starlings' 0.35 L and 10–20 m/s.
5. Any 3-D test of marginal opacity on the Rome datasets, or a 3-D opacity-vs-N relation; Pearce et al.'s later work on projection-based models (e.g. "Density distributions and depth in flocks", arXiv:1902.08181) and whether it reproduces the border density gradient.
6. γ: is there any later measurement of the correlation decay exponent over a wider range of L (the 2010 data span one decade), or a direct test of the boundary-inflow explanation (Cavagna 2013) against data?
7. Speed-fluctuation statistics: the per-bird speed distribution width (≈ 2 m/s is quoted for flock-to-flock mean speed; the single-bird distribution in Cavagna 2022 Fig. 4 needs its actual width), and whether the asymmetry of the marginal force (slow-down easier than speed-up) is visible in the data.
8. Entropic-speed effect: does the field data show *any* upward drift of mean speed at N ≲ 50 (Cavagna 2022 says none detectable)? This is a clean discriminating test for the app's speed control.
9. Noise structure: is there empirical evidence for coloured (OU-like, τ ~ seconds) behavioural noise in starlings, as the app assumes with NOISE_TAU = 4 s, versus white noise plus inertia? Cavagna 2022 explicitly lists temporally correlated or active noise as untested alternatives.
10. Evolutionary stability: are there responses to Klamser & Romanczuk 2021, and does the "marginal confinement with no fine tuning" of Cavagna 2022 sidestep their critique (no parameter needs to be at a special value)?
11. Rigid-rotation debate (Casiulis et al. 2020 vs Cavagna et al. comment): was the PRL comment published, and is there a quantitative bound on the flock-wide angular velocity in the data?
12. Papadopoulou et al. 2026 *Communications Biology* on collective escape: which manoeuvres (zig, speed-up, dive) and what fraction of flock members use each; this would refine item (d)10.
13. Fish and midge analogues (Cavagna/Grigera "scale-free chaos" controversy with González-Albaladejo & Bonilla, PRE 107:014209 and 109:014611; "Whodunnit? The case of midge swarms", arXiv:2602.10242): whether the harmonically confined Vicsek "scale-free chaos" picture implies anything for flocks with a roost attraction, which the app has.
