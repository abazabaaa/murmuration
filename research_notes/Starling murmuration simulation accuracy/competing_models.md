# Competing computational models of starling flocking, calibrated against empirical data

Scope: implementation-level rules, published parameters, which measured observables each model reproduces or fails, and what to borrow for `murmuration.html` (K = 7 topological alignment, 2.5 m metric separation, cohesion, flock-mean steering/speed/level holds, per-bird OU noise τ = 4 s, quartic speed well). Read alongside `research/criticality-canonical-references.md` §(c)–(d).

Verification status: every reference below was located in this session (DOI, arXiv ID, PMC ID or publisher page) unless marked **[unverified]**. Parameter values are quoted from the paper text retrieved in this session unless marked **[from memory]**.

---

## 1. StarDisplay (Hildenbrandt, Carere & Hemelrijk 2010) and its descendants

### Takeaway
StarDisplay is the only starling model fitted trait by trait to the Rome 3-D data (Ballerini 2008). It is a Reynolds-type force model in Newtons with an 80 g bird. Its distinctive ingredients are an adaptive radius that targets n_c = 6.5 topological neighbours, fixed-wing lift and drag with banked turns, roost attraction (separate horizontal and vertical terms), a Gaussian separation with a hard core, a 90° rear blind angle for alignment and cohesion, and a 50 ms reaction-time update on top of a 5 ms Euler step. Against 10 Rome flocks it matches 10 of 18 quantitative tests (aspect ratios, density independent of N, bearing-angle anisotropy, flock plane horizontal). It fails on the denser border, the N-dependence of I₂/I₁, flock volume/thickness (too small) and altitude variability (too level). Later versions add scale-free ξ ∝ L for velocity and speed (2015), agitation waves (2015), and multi-pattern collective escape under a robotic falcon (StarEscape, 2026, code on Zenodo).

### Cited Findings
**Rule set (Hildenbrandt et al. 2010 preprint, equation numbers as in the preprint)**
- Local frame (e_x forward, e_y side, e_z up). The bird changes heading by roll, pitch and yaw — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677) (journal version: Behav Ecol 21:1349–1359, [doi:10.1093/beheco/arq149](https://doi.org/10.1093/beheco/arq149))
- **Speed control (Eq 1):** f_τ = (m/τ)(v₀ − v_i)·e_x, a *linear* per-bird relaxation to cruise speed v₀ — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677). In the 2015 J Stat Phys version it is written f = m·w_sp·(v₀ − v_i)·e_x, with w_sp varied as the "speed control" parameter — [Hemelrijk & Hildenbrandt 2015, J Stat Phys 158:563](https://link.springer.com/article/10.1007/s10955-014-1154-0)
- **Adaptive topological range (Eqs 2–3):** R_i(t+Δu) = (1−s)·R_i(t) + s·(R_max − R_max·|N_i|/n_c), where N_i = {j : d_ij ≤ R_i}. Each bird tunes its metric radius so it sees about n_c neighbours. The paper reports the realised topological range as 6.5 ± 1 — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677)
- **Separation (Eq 4):** f_s = −(w_s/|N_i|) Σ g(d_ij)·d̂_ij, with g = 1 for d ≤ r_h (hard sphere) and g = exp(−(d−r_h)²/σ²) beyond it; σ is set so that g(r_sep) = 0.01. Separation applies all round (no blind angle). This is needed to reproduce the empirical lack of nearest neighbours directly ahead or behind: with a rear blind angle the bearing-angle fit fails (Kendall τ = −0.11, NS, vs τ = 0.72, P < 0.01 without one) — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677)
- **Alignment and cohesion** among the n_c topological neighbours, excluding a 2 × 45° rear blind angle. Cohesion is stronger for birds at the border, using a "centrality" C_i with critical value C_c = 0.35. Without this correction the interior-vs-border density contrast worsens significantly (Wilcoxon N = 60, P ≈ 0) — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677). The exact cohesion formula (C_i-weighted mean of unit vectors) is **[from memory]**.
- **Roost (Eqs 10–12):** f_RoostH = ±w_RoostH(½ + ½(e_x·n))·e_y is a *lateral* force that turns the bird back when heading outward past radius R_Roost. f_RoostV = −w_RoostV·(vertical distance)·ẑ. Vertical attraction is what flattens the flock: without it, thickness grows markedly — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677)
- **Random force (Eq 13):** w_ξ·ξ, with ξ a random unit vector, "scaled to 10% of the steering force". Steering = social + speed + roost + random (Eq 14) — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677)
- **Flight (Eqs 15–17):** L₀ = mg, D₀ = T₀ = L₀·C_D/C_L. Then L_i = (v_i²/v₀²)·mg along e_z, D_i = (C_D/C_L)·L_i along −e_x, and thrust T₀ is constant along e_x, plus gravity — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677)
- **Banking (Eqs 19–20):** roll-in angle = w_βin × |lateral acceleration a_l| × Δu; roll-out tendency grows with the current bank angle (w_βout). The ratio w_βin/w_βout sets the roll rate. After the roll, part of the lateral steering appears as extra lift (|a_l|·sin β_in), compensating the banking lift loss as in real birds — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677)
- **Integration (Eqs 22–23):** semi-implicit Euler with Δt = 5 ms: v(t+Δt) = v + (F_steer + F_flight)/m·Δt, then r(t+Δt) = r + v(t+Δt)·Δt. Steering is only re-evaluated every Δu = 50 ms (reaction time) — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677)

**Default parameter table (Table 1, physical units)** — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677)

| Δt | Δu | v₀ | m | C_L/C_D | L₀ | D₀=T₀ | w_βin | w_βout | τ (speed) | R_max | n_c | s | r_h | r_sep | σ | w_s | w_a | w_c | blind | C_c | w_ξ | R_Roost | w_RoostH | w_RoostV |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 ms | 50 ms | 10 m/s | 80 g | 3.3 | 0.78 N | 0.24 N | 10 | 1 | 1 s | 100 m | 6.5 | 0.1 Δu | 0.2 m | 4 m | 1.37 m | 1 N | 0.5 N | 1 N | 2×45° | 0.35 | 0.01 N | 150 m | 0.01 N/m | 0.2 N |

- Calibration procedure: v₀ (from Ward et al. 2004), m, C_L/C_D and reaction time are taken from the literature. w_βin/w_βout were tuned to roll rates in Rome videos, and w_a to the "high degree of polarization observed in the videos". r_sep was tuned per flock to match the empirical NND, w_RoostV to give the flat shape, and τ together with w_RoostV to give level flight when undisturbed. Social force magnitudes were scaled to about 1 N, the order of the aerodynamic forces — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677)
- r_sep → NND mapping at N = 2000: 1.6 m → 0.55 m, 2.0 → 0.65, 2.5 → 0.78, 3.0 → 0.91, 4.0 → 1.14, 5.0 → 1.42 m. The realised interaction radius R_i is about 1.35 × NND — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677)

**Observables matched / failed against 10 Rome flocks (Table 2; model value, then empirical in parentheses)** — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677)
- N, v₀ and r_sep were tuned per flock: NND 0.69 (0.68) … 1.54 (1.51) m; CoM speed 7.0–15.0 m/s matched.
- **Matched (10 tests):** I₂/I₁ and I₃/I₁ (Wilcoxon NS; e.g. M28-10 2.94/6.67 vs E 3.44/6.93); I₃/I₁ independent of N and volume; thickness–volume and volume–N correlations; balance shift (front ≈ back density); density independent of N (r = 0.32, P = 0.14 over N = 100–5000); right-skewed NND distribution (skew +0.37/+0.54 vs +0.36/+0.39); bearing angle (τ = 0.72); I₁ ⟂ flight direction.
- **Failed (8 tests):** I₂/I₁ depends on N and volume (τ = 0.51, P = 0.05); volume and thickness too small (e.g. M31-01 thickness 6.6 m vs 19.0 m empirical); **border less dense than interior** (NND 1.28 border vs 1.24 centre, P < 0.05, *opposite* to Ballerini 2008); flocks "stay too much parallel to the ground and at the same altitude"; |I₁·G| differs significantly (P = 0.03).
- Turning dynamics (qualitative only, since no time-series data were available then): bank angle correlates with path curvature. A turn loses effective lift and altitude, horizontal speed rises after the apex, the flock compresses during the turn, and aspect ratio changes. Shape relative to the heading flips during a turn (consistent with equal-radius turning). Without banking the flock goes around the roost edge in a circle and becomes oblong; without roost attraction it flies straight and thickens — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677)

**Later StarDisplay versions**
- Shape variability: banking and roost attraction drive shape changes and flock tilt — [Hemelrijk & Hildenbrandt 2011, PLoS ONE 6:e22479](https://doi.org/10.1371/journal.pone.0022479); fish/bird comparison — [Hemelrijk & Hildenbrandt 2012, Interface Focus 2:726](https://doi.org/10.1098/rsfs.2012.0025). Detailed results of both were not retrieved this session.
- **Scale-free correlations (2015):** ξ for both velocity and speed fluctuations grows linearly with flock size. More influential neighbours gives a diminishing increase in the slope of ξ_velocity vs size. **Higher speed control reduces ξ_speed**, and at very high speed control ξ_speed saturates (no longer scale-free) while the flock starts to disintegrate — [Hemelrijk & Hildenbrandt 2015, J Stat Phys 158:563, doi:10.1007/s10955-014-1154-0](https://link.springer.com/article/10.1007/s10955-014-1154-0). The numeric slopes (ξ = a·L) were not accessible (paywall; pure.rug.nl blocked).
- Diffusion of individuals within the flock compared with Rome data — [Hemelrijk & Hildenbrandt 2015, PLoS ONE 10:e0126913](https://doi.org/10.1371/journal.pone.0126913). Results were not retrieved.
- Agitation waves: the threatened bird performs a manoeuvre copied by topological neighbours — [Hemelrijk, van Zuidam & Hildenbrandt 2015, Behav Ecol Sociobiol 69:755](https://doi.org/10.1007/s00265-015-1891-3). The canonical-references report summarises this as a roll-sideways-and-back "zig" copied after a 50–76 ms delay, giving a wave speed near the empirical mean of about 13 m/s (secondary, from `criticality-canonical-references.md`). Damping of waves — Hemelrijk et al. 2019, Behav Ecol Sociobiol 73:125 (cited in the [2026 reference list](https://www.nature.com/articles/s42003-026-10173-4)).
- Empirical escape-pattern catalogue — [Storms et al. 2019, Behav Ecol Sociobiol 73, doi:10.1007/s00265-018-2609-0](https://doi.org/10.1007/s00265-018-2609-0)
- **StarEscape (2026):** "each sturnoid interacts with its 7 closest neighbors (n_topo) that are within its field of view", with alignment, attraction and avoidance. Birds yaw and roll to turn and pitch to dive or climb. The update interval is 50 ms normally and 20 ms when alarmed. Simulated flocks fly at 9.5 ± 0.32 m/s with NND 0.86 ± 0.08 m and neighbour stability Q4(3 s) = 0.58 ± 0.06. The model was compared with 19 videos of starling flocks chased by the RobotFalcon. It reproduces agitation wave, flash expansion, split, vacuole, cordon and blackening, sometimes co-occurring in one flock. The authors conclude that outcomes depend on escape-information propagation speed, the escapers' positions relative to the predator, and hysteresis — [Papadopoulou et al. 2026, Commun Biol 9:1055, doi:10.1038/s42003-026-10173-4](https://www.nature.com/articles/s42003-026-10173-4). Source code: [StarEscape v1.0.0, Zenodo doi:10.5281/zenodo.19664015](https://doi.org/10.5281/zenodo.19664015); bioRxiv preprint [doi:10.1101/2024.10.27.620514](https://doi.org/10.1101/2024.10.27.620514)
- Pigeon sibling model (HoPE) — [Papadopoulou et al. 2022, PLoS Comput Biol 18:e1009772](https://doi.org/10.1371/journal.pcbi.1009772); [R Soc Open Sci 9:211898](https://doi.org/10.1098/rsos.211898)
- No official StarDisplay GitHub repository was found. A third-party Processing port exists — [jokroese/starlings](https://github.com/jokroese/starlings). The 2026 StarEscape code on Zenodo is the first official release found.

### Inferences
- StarDisplay's *linear* per-bird speed control (τ = 1 s) contradicts the marginal-speed result (§3), and its own 2015 paper shows that stronger speed control shrinks ξ_sp. Borrow its geometry (banking, lift, roost, separation shape), not its speed law.
- StarDisplay's random force is white and small (0.01 N on an 80 g bird ≈ 0.125 m/s²). It reaches high Φ with essentially no persistent noise. Its correlations come from relaxation through neighbours plus roost-driven turning, much like the app's "driven" fluctuation idea.
- The app's RS = 2.5 m maps, in StarDisplay's Gaussian separation, to NND ≈ 0.78 m at N = 2000. The app's form differs, so this is only indicative.

### Gaps
- Numeric ξ/L slopes, Φ values and N range in Hemelrijk & Hildenbrandt 2015 J Stat Phys were not accessible.
- The exact cohesion/centrality formula and Eqs 5–9, 18–21 were partly missing from the retrieved text.
- StarEscape's full parameter table (escape-manoeuvre magnitudes) was not retrieved; the Zenodo code is the authoritative source.

---

## 2. Inertial Spin Model (ISM; Cavagna et al. 2015; Attanasi et al. 2014) and the 2025 FPUT extension

### Takeaway
The ISM replaces "alignment sets the heading rate" with "alignment sets the rate of change of turning rate". Each bird carries a spin s ⟂ v with inertia χ and friction η, and the speed is fixed at v₀. In the underdamped regime, η²/χ ≪ n_c·J·(a/L)², a turn started by one bird crosses the flock linearly at c_s = a√(n_c J/χ) with no attenuation. Equivalently c_s ∝ 1/√(χ(1−Φ)), which matches the starling turning data. The static (equal-time) properties are identical to the Vicsek model, so ISM changes dynamics but not Φ or C(r) at a given noise. Cavagna et al. 2025 found that spontaneous fluctuations in real flocks are overdamped (Lorentzian, ω ~ k²), which a single-J ISM cannot produce. A quartic (FPUT) alignment term J₄ with J ≪ J₄ fixes this: small misalignments relax diffusively, large ones propagate as solitary waves.

### Cited Findings
- **ISM equations:** dv_i/dt = (1/χ)·s_i × v_i; ds_i/dt = v_i × [(J/v₀²) Σ_j n_ij v_j − (η/v₀²) dv_i/dt + ξ_i/v₀]; dr_i/dt = v_i. Noise ⟨ξ_i·ξ_j⟩ = 2d·η·T·δ_ij δ(t−t′). |v_i| = v₀ and v·s = 0 are conserved — [Cavagna et al. 2015, J Stat Phys 158:601, arXiv:1403.1202, doi:10.1007/s10955-014-1119-3](https://arxiv.org/abs/1403.1202)
- Closed second-order form: χ v̈ + χ(v/v₀²)(v̇)² + η v̇ = (J/v₀²)(v × Σ n_ij v_j) × v + v₀ ξ^⟂ — [arXiv:1403.1202](https://arxiv.org/abs/1403.1202)
- Spin is curvature: turning radius R ~ v₀χ/|s|. χ is "the resistance of the bird to change its banking angle". With no forces, spin decays as exp(−(η/χ)t) — [arXiv:1403.1202](https://arxiv.org/abs/1403.1202)
- **Discretised scheme used in the paper (Eqs 54–56):** v(t+dt) = v + (1/χ) s × v dt; s(t+dt) = s + v × (J/v₀²) Σ n_ij v_j dt − (η/χ) s dt + v × ξ/v₀ √dt; r(t+dt) = r + v dt (forward Euler / Euler–Maruyama) — [arXiv:1403.1202](https://arxiv.org/abs/1403.1202)
- **Simulation parameters (dimensionless):** N = 512, n_c = 6 topological, v₀ = 0.1, T = 8 × 10⁻⁵, open boundaries, Φ > 0.95. Underdamped case η = 0.3, χ = 1.25, J = 0.8 (η²/χ = 7.2 × 10⁻²). Overdamped η = 15 (attenuated; the flock loses cohesion while turning) and η = 60 (no turn; the flock breaks up). Propagation fits used (χ, J) = (0.83, 1.2), (1.25, 0.8), (2.5, 0.4) at η = 0.3. dt = 0.1√(J/χ) as stated — [arXiv:1403.1202](https://arxiv.org/abs/1403.1202)
- **Regimes:** overdamped if η²/χ > n_c J (a/L)², giving exponential decay of the signal beyond k₀ = 1/(2a√(n_c Jχ)); underdamped if η²/χ ≪ n_c J (a/L)², giving linear propagation at c_s = a√(n_c J/χ) (Eq 58). Using Φ = 1 − T·J⁻¹·Tr Λ⁻¹ gives c_s = a√(n_c T Tr Λ⁻¹ / ((1−Φ)χ)) (Eq 59). Simulations confirm both — [arXiv:1403.1202](https://arxiv.org/abs/1403.1202)
- Turn-propagation measurement: rank birds by when cos(heading change) crosses 0.9, or by cross-correlating acceleration curves. The front distance is x(t) = (rank/ρ)^(1/3) and c_s is the slope of its linear part — [arXiv:1403.1202](https://arxiv.org/abs/1403.1202)
- The overdamped limit is Vicsek. On very large scales with η ≠ 0 the dynamics reduce to Toner–Tu hydrodynamics. Static properties equal Vicsek's — [arXiv:1403.1202](https://arxiv.org/abs/1403.1202)
- How parameters relate to data: Attanasi et al. 2014 (Nat Phys 10:691, cited in [arXiv:2505.19665](https://arxiv.org/abs/2505.19665); DOI 10.1038/nphys3035 **[from memory]**) measured c_s ≈ 10–20 m/s, linear x(t), negligible attenuation and c_s ∝ 1/√(1−Φ). The ISM was *fitted qualitatively*, through the functional form c_s(Φ) and the underdamped condition, not by a likelihood fit of χ, η, J in physical units.
- **2025 data and FPUT extension:** new high-resolution experiments show traveling turn waves *coexisting* with an overdamped Lorentzian spontaneous correlation (half-width ω_L ~ k²). A single-J ISM would show spin-wave peaks — [Cavagna et al. 2025, arXiv:2505.19665](https://arxiv.org/abs/2505.19665)
- FPUT pseudo-Hamiltonian: H_v = (J/4v₀²) Σ n_ij (v_i−v_j)² + (J₄/4v₀⁴) Σ n_ij (v_i−v_j)⁴. The force is F_i = −(1/v₀²) Σ_j n_ij (v_i−v_j)·[J + (2J₄/v₀²)(v_i−v_j)²], giving an effective stiffness J_eff = J + J₄δφ². The working window is J ≲ χγ²(L/a)² ≪ J₄ ≲ J/(1−Φ). In planar phases with no noise this is exactly the FPUT chain, which supports solitons — [arXiv:2505.19665](https://arxiv.org/abs/2505.19665)
- **2025 integration scheme:** the second-order Langevin form d²v/dt² = (v₀²/χ)[F − (η/v₀²)v̇ + ξ/v₀ + f_c] is integrated with a Langevin velocity-Verlet (Allen–Tildesley §9.3) using c₀ = e^{−ηh/χ}, c₁ = (χ/ηh)(1−c₀), c₂ = (χ/ηh)(1−c₁) and correlated Gaussian kicks Θ_v, Θ_a. |v| = v₀ is enforced softly with V_c = (κ/2)(|v|−v₀)². Parameters: h = 10⁻², χ = 1.25, J = 20, v₀ = 0.1, T = 10⁻⁶, κ = 10⁴; η = 0.7 (underdamped ISM), η = 7 (overdamped ISM and ISM+FPUT), J₄ = 10⁵ — [arXiv:2505.19665](https://arxiv.org/abs/2505.19665)
- The 2025 paper links FPUT alignment to the marginal speed control (§3): in both cases birds "almost ignore small fluctuations, while sharply reacting to large perturbations" — [arXiv:2505.19665](https://arxiv.org/abs/2505.19665)
- Related developments: hydrodynamics of turning flocks, coarse-grained from the ISM — [Yang & Marchetti 2015, PRL 115:258101](https://doi.org/10.1103/PhysRevLett.115.258101); "silent flocks" continuum theory — [Cavagna et al., arXiv:1410.2868](https://arxiv.org/abs/1410.2868); spin-conserving thermostat — [arXiv:2403.07644](https://arxiv.org/abs/2403.07644); ISM with position-dependent forces (cohesion, excluded volume, open boundaries) — [PRE 110:014408 (2024)](https://doi.org/10.1103/PhysRevE.110.014408); 1-D ISM+FPUT with active torques leading to a non-reciprocal mKdV — [arXiv:2604.23808 (2026)](https://arxiv.org/abs/2604.23808)

### Inferences
- Converting to physical units with a ≈ 1.2–1.5 m (interacting-neighbour distance ≈ 1.3–1.5 × r₁) and c_s = 10–20 m/s gives √(n_c J/χ) ≈ 8–15 s⁻¹. The underdamped condition then becomes η/χ ≪ c_s/L. For L = 40 m and c_s = 15 m/s the spin relaxation time χ/η must be much longer than L/c_s ≈ 2.7 s. This lines up with the app's NOISE_TAU = 4 s scale.
- Because ISM statics equal Vicsek's, adding ISM alone will *not* move Φ or |u| at fixed noise. It changes turning (linear front, equal-radius trajectories, transient Φ dips).
- The FPUT window needs J₄/J ≲ 1/(1−Φ) ≈ 25 at Φ = 0.96. The 2025 simulations use J₄/J = 5000 at T = 10⁻⁶ (very high Φ). The inequality is order-of-magnitude, and the relevant δφ is the *neighbour* phase difference, not 1−Φ, so a practical J₄/J must be tuned empirically.

### Gaps
- No published physical-unit values of χ, η, J for starlings; only the ratio constraints and the c_s(Φ) law.
- Journal publication status of arXiv:2505.19665 unknown as of Oct 2026. Its fitted Lorentzian half-width in physical units was not retrieved.

---

## 3. Marginal speed control (Cavagna et al. 2022; Bialek et al. 2014)

### Takeaway
Linear speed control V = g(v−v₀)² gives ξ_sp = r₁√(Jn_c/g). Scale-free ξ_sp then needs g ≪ 1/L_max², but small g makes the typical group speed blow up at small N, because of the entropic s² Jacobian. The marginal potential V = (λ/v₀⁶)(v² − v₀²)⁴ has zero curvature at v₀ for any λ. Low noise T alone then delivers both scale-free ξ_sp (ξ_sp ~ T^(−1/2) in mean field) and an N-independent mean speed. It also fits single-bird speed distributions at three N, where linear control is "a total disaster".

### Cited Findings
- Model: dv_i/dt = −∂H/∂v_i + η_i with ⟨η·η⟩ = 2dT·δ. H = ½J Σ n_ij (v_i−v_j)² + Σ V(v_i). Speed is *not* fixed (imitation of speed and orientation) — [Cavagna et al. 2022, Nat Commun 13:2315, arXiv:2101.09748](https://arxiv.org/abs/2101.09748); [doi:10.1038/s41467-022-29883-4](https://doi.org/10.1038/s41467-022-29883-4)
- Linear: V = g(v_i−v₀)², ξ_sp = r₁(Jn_c/g)^{1/2}, P(s) ∝ s² exp[−(Ng/T)(s−v₀)²], s_typ = ½v₀(1+√(1+4T/(Ngv₀²))). Only g = 10⁻³ gives scale-free ξ_sp at all sizes — [arXiv:2101.09748](https://arxiv.org/abs/2101.09748)
- The p = 2 "quartic O(n)" potential (v²−v₀²)² is still harmonic near v₀ (≈ 4v₀²(v−v₀)²), so it does *not* solve the problem. The marginal choice is p = 4: **V(v) = (λ/v₀⁶)(v·v − v₀²)⁴** — [arXiv:2101.09748](https://arxiv.org/abs/2101.09748)
- Marginal: P(s) ∝ s² exp[−(Nλ/(Tv₀⁶))(v₀²−s²)⁴]. s_typ ≈ v₀ for N ≫ T/(λv₀²), and s_typ ≈ v₀(T/(4Nλv₀²))^{1/8} below that crossover. Mean field gives ξ_sp ~ T^{−1/2} (a zero-temperature critical point) — [arXiv:2101.09748](https://arxiv.org/abs/2101.09748); theory: [arXiv:1812.07522](https://arxiv.org/abs/1812.07522); RG: [arXiv:2202.04605 / PRE 106:054136](https://arxiv.org/abs/2202.04605)
- **Simulation setup (Methods Eqs 18–23):** v(t+Δt) = v + Δt·F + δη, x(t+Δt) = x + Δt·v(t) (Euler–Maruyama), with σ_η² = 2dTΔt. F_int = −J Σ n_ij (v_i − v_j). Linear F_sc = 2g·v̂(v₀ − |v|); **marginal F_sc = (8λ/v₀⁶)·v·(v₀² − v²)³**. Interaction was *metric* with r_c = 1.2 (chosen for cost; n_c = 6 at t = 0, verified sharply peaked over time). Particles start polarised on a cubic lattice with spacing 1 in a periodic cubic box, N up to 3 × 10⁵. Simulation lengths were converted to metres via r₁^exp/r₁^sim, and speeds matched at the largest N — [arXiv:2101.09748](https://arxiv.org/abs/2101.09748)
- Data: starling flocks 10–3000 birds (2019–20 campaign plus earlier). Mean speed is about 12 m/s with flock-to-flock fluctuation about 2 m/s, no N dependence (Spearman r_S = −0.13, p = 0.21). ξ_sp ∝ L (Pearson 0.97) — [arXiv:2101.09748](https://arxiv.org/abs/2101.09748)
- Data-fitted speed stiffness g/(Jn_c) ~ 10⁻³ from maximum entropy — [Bialek et al. 2014, PNAS 111:7212](https://doi.org/10.1073/pnas.1324045111)

### Inferences
- Near v₀ the marginal force is F ≈ −64λ(v−v₀)³/v₀², a pure cubic, so the local stiffness is 192λ(v−v₀)²/v₀². For explicit Euler stability at dt = 1/60 s, cap that stiffness × dt below about 1, or clamp |v−v₀|.
- The app already has a quartic well with no linear term, which is the right idea. The literature point is that it must act **per bird on |v_i|**, not on the flock mean, and that ξ_sp is then controlled by T (noise), not by the well's stiffness.

### Gaps
- Numerical values of J, λ, T and Δt for the 2022 SPP runs are in the SI and were not retrieved.

---

## 4. Marginal opacity / projection model (Pearce et al. 2014)

### Takeaway
Pearce et al. drop explicit attraction. Each agent steers toward the mean direction of all light/dark boundaries in its view of the flock, plus alignment with its σ = 4 nearest (visible) neighbours, plus noise, at constant speed. This gives cohesive flocks whose opacity emerges at an intermediate, N-independent value. Starling photographs show Θ′ ≈ 0.30–0.41. The computation is global (each agent sees the whole flock), O(N²) or worse per step in 3-D. It predicts density falling with N (ρ ~ N^(−1/2) in 3-D), which conflicts with the Rome finding of N-independent density.

### Cited Findings
- **Update rule:** r^{t+1} = r^t + v₀ v̂^t with v^{t+1} ∥ φ_p·δ_i + φ_a·⟨v_k⟩^n.n. (normalised) + φ_n·η_i. Here η is a random unit vector, φ_p + φ_a + φ_n = 1, σ = 4 visible nearest neighbours (unbroken line of sight), v₀ = 1, and agents are "phantoms" (no steric repulsion in the base model) — [Pearce et al. 2014, PNAS 111:10422, arXiv:1407.2414](https://arxiv.org/abs/1407.2414); [doi:10.1073/pnas.1402202111](https://doi.org/10.1073/pnas.1402202111)
- **Projection vector:** in 2-D, δ_i = (1/𝒩_i) Σ_j (cos θ_ij, sin θ_ij) over the angles θ_ij of the 𝒩_i light/dark domain boundaries, where dark means a line of sight to infinity hits another agent of size b = 1. In 3-D the boundaries are curves on the sphere and δ is the normalised integral of radial unit vectors along them (details in SI) — [arXiv:1407.2414](https://arxiv.org/abs/1407.2414)
- Results: the swarm does not fragment for any φ_p > 0 (it does at φ_p = 0). The projection term shortens the density autocorrelation time (global coupling gives fast response). Opacity is roughly constant over N (with φ_p = 0.03 and φ_a = 0.8 in 2-D/3-D N-scans; 2-D runs used N = 100 over 4 × 10⁵ steps). Metric attraction–repulsion models instead become fully opaque at a critical N, often below 100 — [arXiv:1407.2414](https://arxiv.org/abs/1407.2414)
- Data: Θ′ of UK starling flocks μ = 0.30, σ² = 0.059 (n = 118); public-domain images μ = 0.41, σ² = 0.012; range 0.25–0.6. Opacity changes within seconds of a centre-of-mass acceleration — [arXiv:1407.2414](https://arxiv.org/abs/1407.2414)
- Mean-field: P_sky ≈ exp(−ρ b^{d−1} R). Marginal opacity implies ρ ~ N^{−1/(d−1)} (N^(−1/2) in 3-D). Halving the spacing takes opacity from 50% to 94% — [arXiv:1407.2414](https://arxiv.org/abs/1407.2414)
- Follow-up: a strictly metric-free model with a distributed motional bias (inward at the edge, *outward* in the interior) fits the published starling density variation (denser border) — ["Density distributions and depth in flocks", arXiv:1902.08181](https://arxiv.org/abs/1902.08181). Author list and journal not verified.

### Inferences
- Cost: in 3-D every agent must rasterise or merge the angular discs of all other agents, so O(N²) per step at minimum (sorting intervals in 2-D gives O(N² log N)). At N = 3000 that is about 9 × 10⁶ pair projections per step, too slow for 60 fps in JS unless approximated. A practical approximation is a coarse spherical occupancy map (e.g. 6 × 16² cube-map texels) per agent, built from a spatial grid of cell-aggregated discs. Another is computing δ for 1/k of the birds per frame. All of this is engineering inference, not from the paper.
- The predicted ρ ~ N^(−1/2) conflicts with Ballerini 2008 (density independent of N; also reproduced by StarDisplay). Pearce et al. claim "hints" of decreasing density in published data. Treat Θ′ as a *diagnostic* target before adopting projection steering.
- The 1902.08181 mechanism (edge inward, interior outward bias) is a direct candidate for fixing the denser-border failure shared by StarDisplay and probably the app.

### Gaps
- 3-D opacity cost and the full SI algorithm were not retrieved. No 3-D test of opacity on Rome data was found (as the canonical report also notes).

---

## 5. Other calibrated or data-driven models

### Takeaway
Apart from StarDisplay, ISM and marginal-speed SPP, almost no models are calibrated to *starling* data quantitatively. Vicsek-with-topological-neighbours (Ginelli & Chaté 2010), Couzin zones (2002), Bhattacharya & Vicsek 2010 and Flock2 (2024) are qualitative. Jackdaw work (Ling et al. 2019) shows interaction rules switch between topological (transit) and metric (mobbing) with context. Data-driven inference has so far produced Vicsek-like (second-order) equations, from Langevin graph networks, or interaction ranges, but on non-starling or unspecified bird data.

### Cited Findings
- Vicsek with metric-free (topological/Voronoi) neighbours — Ginelli & Chaté 2010, PRL 105 ("Relevance of metric-free interactions in flocking phenomena"), cited in [Pearce 2014 reference list](https://arxiv.org/abs/1407.2414). Not calibrated to starling observables.
- Couzin zones (repulsion/orientation/attraction, blind angle) — [Couzin et al. 2002, J Theor Biol 218:1](https://doi.org/10.1006/jtbi.2002.3065). Not starling-calibrated; StarDisplay descends from this family.
- Bhattacharya & Vicsek 2010, "Collective decision making in cohesive flocks", New J Phys: a model of synchronized landing decisions, motivated by pigeons — [ResearchGate record](https://www.researchgate.net/publication/45931271_Collective_decision_making_in_cohesive_flocks). DOI 10.1088/1367-2630/12/9/093019 **[from memory, unverified]**. Not calibrated to starling ξ/L, Φ or shape.
- Jackdaws: interactions vary with context. Mobbing flocks undergo a density-driven disorder-to-order transition matched by a generic SPP model, while transit-flock order is density-independent — [Ling et al. 2019, Nat Commun 10:5174](https://www.nature.com/articles/s41467-019-13281-4); local interaction rules — [Ling et al. 2019, Proc R Soc B 286:20190865](https://doi.org/10.1098/rspb.2019.0865). The canonical report gives topological 7–8 (transit) vs metric ≈ 5 m (mobbing).
- Fluctuation-driven 3-D flocking with scale-free correlation — [Niizato & Gunji 2012, PLoS ONE 7:e35615](https://doi.org/10.1371/journal.pone.0035615); "Stochasticity may generate coherent motion in bird flocks" — [Reynolds 2023, Phys Biol 20:025002](https://doi.org/10.1088/1478-3975/acbad7). Both are qualitative.
- Flock2 (orientation-based social flocking): neighbours create a *desire to turn* that drives an aerodynamic model. It gives spherical/ovoidal shapes and spontaneous orientation waves, and is compared with Reynolds boids on energy and frequency, not with Rome data — [Hoetzlein 2024, J Theor Biol, arXiv:2404.17804](https://arxiv.org/abs/2404.17804) ([doi:10.1016/j.jtbi.2024.111880](https://doi.org/10.1016/j.jtbi.2024.111880))
- Data-driven: the Langevin graph network infers the SDE of real bird flocks and finds it "closely resembles the second-order Vicsek model" — [Gao, Barzel & Yan 2024, Nat Commun 15:6029](https://www.nature.com/articles/s41467-024-50378-x). AgentNet (graph attention) recovers hidden interaction ranges in bird-flock data — [Ha & Jeong 2021, Sci Rep, doi:10.1038/s41598-021-91878-w](https://doi.org/10.1038/s41598-021-91878-w). Nonparametric interaction-kernel learning — [Lu et al. 2019, PNAS 116:14424](https://doi.org/10.1073/pnas.1822012116)
- Heras et al. 2019 (deep attention networks, zebrafish, PLoS Comput Biol) and Escobedo et al. 2020 (data-driven reconstruction of fish interactions, Phil Trans R Soc B) — **[unverified this session; both are fish, not starlings]**.
- Continuum: ISM-derived turning hydrodynamics generalise Toner–Tu with spin inertia — [Yang & Marchetti 2015](https://doi.org/10.1103/PhysRevLett.115.258101).

### Inferences
- The "Vicsek + inertia" family (second-order Vicsek, ISM, Gao 2024's inferred SDE) is the convergent data-driven answer: velocity dynamics are second order, with an alignment torque acting through a damped internal variable.

### Gaps
- Which bird species and dataset Gao et al. 2024 used, and the inferred coefficients, were not retrieved.
- No ML-inferred interaction rule fitted to *starling* 3-D trajectories was found (2019–2026).

---

## 6. Comparative / benchmarking studies on the same starling observables

### Takeaway
No paper benchmarks several distinct models against one starling dataset on ξ/L, Φ, shape and wave speed together. The closest are within-paper comparisons: linear vs marginal speed control on ξ_sp, mean speed and the speed distribution (Cavagna 2022); overdamped vs underdamped ISM vs ISM+FPUT on turning and C(k,ω) (Cavagna 2015, 2025); StarDisplay with and without banking, roost, border cohesion and blind angle on 18 Rome traits (Hildenbrandt 2010); and projection vs metric models on opacity (Pearce 2014).

### Cited Findings
- Linear control fits ξ_sp ∝ L only at small g, and the mean speed vs N only at large g. Marginal control fits both, plus the single-bird speed distributions at three N — [arXiv:2101.09748](https://arxiv.org/abs/2101.09748)
- Overdamped ISM (Vicsek limit) gives no collective turn and breaks the flock. Underdamped ISM gives linear propagation but spin-wave peaks absent in the data. ISM+FPUT gives both — [arXiv:1403.1202](https://arxiv.org/abs/1403.1202); [arXiv:2505.19665](https://arxiv.org/abs/2505.19665)
- StarDisplay ablations: no banking makes the flock circle the roost edge and become oblong; no roost makes it straight and thick; no border-cohesion boost gives a worse density contrast; a rear separation blind angle breaks the bearing-angle fit — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677)
- Metric attraction–repulsion models become opaque as N grows; the projection model holds opacity constant — [arXiv:1407.2414](https://arxiv.org/abs/1407.2414)
- Comparative toolkit for collective-motion data (swaRmverse R package) — [Papadopoulou, Garnier & King 2025, Methods Ecol Evol 16:29](https://doi.org/10.1111/2041-210X.14460) (from the 2026 reference list; contents not retrieved)

### Gaps
- No head-to-head benchmark across model families on the full STARFLAG/COBBS observable set exists in the retrieved literature. This is a genuine gap.

---

## 7. Practical implementation notes for 400–3000 agents at 60 fps in JS

### Takeaway
Use semi-implicit (symplectic) Euler with 2–4 substeps per 16.7 ms frame. Use a uniform 3-D hash grid with a per-bird adaptive search radius (StarDisplay's R_i rule) for k-NN, and exploit the slow rearrangement of the interaction network to refresh neighbour lists every few frames. StarDisplay itself uses Δt = 5 ms with steering updated every 50 ms. The ISM, FPUT and marginal-speed papers use explicit Euler–Maruyama or Langevin–Verlet.

### Cited Findings
- StarDisplay: Δt = 5 ms Euler, steering held for Δu = 50 ms; R_i relaxes with s = 0.1·Δu toward the radius containing n_c birds — [arXiv:0908.2677](https://arxiv.org/abs/0908.2677). StarEscape: 50 ms, or 20 ms when alarmed — [Papadopoulou 2026](https://www.nature.com/articles/s42003-026-10173-4)
- ISM: dt = 0.1√(J/χ) Euler — [arXiv:1403.1202](https://arxiv.org/abs/1403.1202). ISM+FPUT: h = 0.01 Langevin–Verlet with soft speed constraint κ = 10⁴ — [arXiv:2505.19665](https://arxiv.org/abs/2505.19665)
- Marginal SPP: Euler–Maruyama; metric neighbours were used instead of topological for speed, as there is "not great difference" at fixed density and low T — [arXiv:2101.09748](https://arxiv.org/abs/2101.09748)
- Neighbour turnover is slow: Q4(3 s) = 0.58 ± 0.06 in StarEscape flocks — [Papadopoulou 2026](https://www.nature.com/articles/s42003-026-10173-4). In real flocks the velocity relaxation time is much shorter than the network rearrangement time, which Cavagna 2022 uses to justify a fixed-network approximation — [arXiv:2101.09748](https://arxiv.org/abs/2101.09748)

### Inferences (engineering)
- **k-NN:** a hash grid with cell ≈ distance to the 7th neighbour (≈ 1.5–2 r₁ ≈ 2–3 m) means each query scans 27 cells holding about 8–30 candidates. Use a fixed-size insertion sort for the top 7. N = 3000 gives about 10⁵ distance tests per refresh, well under 1 ms in typed-array JS. StarDisplay's adaptive R_i is the natural per-bird query radius and copes with density varying across the flock (denser border, splits). A k-d tree rebuild per frame is slower in JS than a grid for this N. Refreshing lists every 2–3 frames (Verlet-list style, keeping about 2K candidates and re-ranking distances each frame) is justified by the slow network turnover.
- **Stability:** the current first-order alignment at W_ALI = 18 s⁻¹ gives W_ALI·dt = 0.3 at 60 fps, which is fine. With ISM, the fastest mode is ω_max ≈ 2√(n_c J/χ) ≈ 20–30 rad/s, so ω·dt ≈ 0.3–0.5 at 60 fps; symplectic Euler is stable for ω·dt < 2. Use 2 substeps for margin. Apply spin damping exactly as s ← s·exp(−(η/χ)dt). Keep |v| = v₀ (or the marginal well) by renormalising after the rotation update, or by rotating v about ŝ by angle |s|dt/χ (Rodrigues), which is exact for constant spin.
- FPUT and marginal-speed terms are cubic and stiffen with deviation. Clamp per-pair (v_i − v_j)² or substep when J₄δφ²·dt is large.
- If using a projection/opacity term, amortise: compute δ_i for N/4 birds per frame on a coarse spherical grid.

### Gaps
- No published browser-scale benchmark was found. All the performance numbers above are estimates, not measurements.

---

## 8. Comparison table and recommendations for `murmuration.html`

### Takeaway
No single published model reproduces every starling observable. The best composite is the app's topological K = 7 alignment and persistent noise (already matching ξ/L) plus four additions: **per-bird marginal speed confinement** (ξ_sp and mean speed across N); **ISM spin inertia with a quartic FPUT alignment term** (linear turn propagation with overdamped spontaneous fluctuations); **StarDisplay banking, lift and vertical roost forces** (flat 1:3:6 shape, altitude dips in turns); and **StarDisplay-style border-weighted cohesion or an edge-inward/interior-outward bias** (denser border). Φ and |u| are geometrically coupled: 1 − Φ ≈ ⟨u⊥²⟩/(2v²). At 11.5 m/s, |u⊥| = 2 m/s implies Φ ≈ 0.985, and Φ = 0.96 implies |u⊥| ≈ 3.2 m/s, so the two targets cannot both be hit unless the speed is lower or Φ is measured at 10 fps.

### Cited Findings
- 1 − Φ ≈ ⟨π²/v₀²⟩/2 (small transverse fluctuations π) — [arXiv:2505.19665](https://arxiv.org/abs/2505.19665)
- Φ = 0.96 ± 0.03 at 10 fps; 0.76–0.96 at 170 Hz; mean speed ≈ 12 m/s — canonical report §(b), from Cavagna 2010, Attanasi 2014 and [Cavagna 2022](https://arxiv.org/abs/2101.09748)

### Inferences

**Model × observable** (✓ reproduced in a published comparison with data; ✗ fails; ~ partial or qualitative; ? not tested)

| Model | Φ ≈ 0.96 | ξ/L orient. ≈ 0.35 | ξ_sp/L scale-free | mean speed ⟂ N | speed distribution | shape I₂/I₁, I₃/I₁ | density ⟂ N | denser border | bearing anisotropy | linear turn, c_s ∝ 1/√(1−Φ) | overdamped spontaneous C(k,ω) | agitation waves/escape | opacity Θ′ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| StarDisplay / StarEscape | ~ (tuned to video) | ✓ (linear in size; slope not retrieved) | ✓ (✗ at high speed control) | ? | ? | ✓ I₃/I₁; ~ I₂/I₁ (N-dep.) | ✓ | ✗ | ✓ | ~ (banking turns, qualitative) | ? | ✓ (waves 2015; 6 escape patterns 2026) | ? |
| ISM (single J) | set by T | same as Vicsek (Goldstone) | ✗ (fixed speed) | n/a | n/a | ? (no cohesion) | ? | ? | ? | ✓ | ✗ (spin-wave peaks) | ? | ? |
| ISM + FPUT (2025) | set by T | as Vicsek | ✗ (fixed speed) | n/a | n/a | ? | ? | ? | ? | ✓ | ✓ | ? | ? |
| SPP + linear speed control | ✓ via T | ✓ | ✓ only small g | ✗ at small g | ✗ | ? (periodic box) | n/a | n/a | n/a | ✗ (overdamped) | ~ | ? | ? |
| SPP + marginal speed control | ✓ via T | ✓ | ✓ | ✓ | ✓ (3 N values) | ? (periodic box) | n/a | n/a | n/a | ✗ (overdamped) | ~ | ? | ? |
| Pearce projection | ~ (order varies with φ_a) | ? | ? | n/a (constant speed) | n/a | ? | ✗? (predicts ρ ~ N^(−1/2)) | ✓ (1902.08181 variant) | ? | ? (fast global response) | ? | ? | ✓ |
| Vicsek-topological / Couzin / Flock2 | ~ | ~ | ? | ? | ? | ~ (Flock2 ovoid) | ? | ? | ? | ✗ (Vicsek) / ~ (Flock2 waves) | ? | ~ (Flock2) | ✗ (metric → opaque) |
| Current app | 0.99–1.00 | ✓ 0.33–0.38 | ✓ 0.32–0.36 | ? | ? | ? | ~ (R_FLOCK ∝ N^⅓) | ? | ? | ✗ (first-order) | ? | ~ (alarm hook) | ? |

**Recommendations (what to borrow, expected effect)**
1. **Marginal speed confinement, per bird** (§3): a_sp = (8λ/v₀⁶)·v·(v₀² − |v|²)³, replacing the flock-mean speed hold, with optional clamping. Expected: ξ_sp/L stays ≈ 0.35 from N = 100 to 3000; mean speed flat in N; individual speed spread widens, adding a longitudinal part to |u| (raising |u| rms toward 2 m/s *without* lowering Φ, since Φ uses unit vectors); no effect on shape or turning. Do *not* copy StarDisplay's linear τ = 1 s speed law, which shrinks ξ_sp (Hemelrijk 2015).
2. **ISM spin layer with FPUT alignment** (§2): per-bird spin s ⟂ v, torque from v × Σ_K [(J + 2J₄|Δv|²/v₀²)·(v_j − v_i)]/v₀², damping time χ/η ≫ L/c_s (≈ 3–8 s; the OU τ = 4 s is already on this scale), and n_c J/χ chosen so that a√(n_c J/χ) ≈ 10–20 m/s (20–40 u/s). Expected: linear, unattenuated turn fronts at 10–20 m/s; equal-radius turning (trajectories cross; shape axes rotate relative to velocity); Φ dips during waypoint turns and falcon strikes. Spontaneous C(r) and ξ/L are unchanged (same statics), and overdamped spontaneous fluctuations are kept if J is small and J₄ large. No direct effect on mean Φ.
3. **StarDisplay flight layer** (§1): bank angle from lateral acceleration (w_βin = 10, w_βout = 1 at a 50 ms update), lift ∝ v²/v₀² along the banked up-vector, and vertical roost spring w_RoostV ≈ 0.2 N on an 80 g bird (≈ 2.5 m/s² per metre). This would replace or complement W_LEVEL. Expected: flat flocks with I₁ ⟂ gravity, thickness set by vertical stiffness, altitude loss and speed gain in turns, and more shape variability. It also gives a physical source of driven heading fluctuations from banking turns, which could raise |u| without the global noise stretching the flock.
4. **Separation and cohesion geometry from StarDisplay:** a Gaussian separation with hard core r_h = 0.2 m and σ chosen so g(r_sep) = 0.01; r_sep ≈ 2.5–4 m targets NND ≈ 0.8–1.1 m; separation is omnidirectional while alignment and cohesion use a 2 × 45° rear blind angle; cohesion is boosted for border birds (centrality > 0.35). Expected: NND distribution right-skewed with hard-core cutoff, bearing-angle anisotropy, and better density control. For the *denser* border the StarDisplay correction is not enough; add the edge-inward / interior-outward bias of arXiv:1902.08181.
5. **Φ and |u|:** report Φ from 0.1 s position differences (10 fps), as in the canonical report. Then raise effective noise only together with (3) and (4), so the flock does not stretch (the app's ?noise=1.5 failure mode). Expected end state: |u⊥| ≈ 2–2.5 m/s, Φ(10 fps) ≈ 0.97–0.985, ξ/L ≈ 0.35. Hitting 0.96 exactly needs |u⊥| ≈ 3 m/s at 11.5 m/s, or ≈ 2.8 m/s at 10 m/s.
6. **Opacity meter first, projection steering later** (§4): compute Θ′ from the camera (target 0.3–0.4). Only add δ-steering, amortised, if Θ′ drifts with N.
7. **Escape repertoire from StarEscape** (Zenodo code): neighbours within the field of view, a 20 ms alarmed update vs 50 ms normal, and level turns and dives. Expected: agitation waves, flash expansion and splits under the falcon, matching Storms 2019 patterns.

### Gaps
- None of the expected effects above has been tested in the app. They are predictions from the cited models and must be checked with the app's own ξ/L, Φ(10 fps), |u|, shape and c_s measurements.
