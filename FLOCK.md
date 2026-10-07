# Large-flock geometry: the page against wild starling flocks

Work in progress (2026-10-07). Benchmarks come from `~/prj/murmuration-refs/flock/` (notes with page references):
Ballerini et al. 2008 (PNAS; Animal Behaviour, arXiv preprints), Cavagna et al. 2010, 2013, 2022, Attanasi et al.
2014, 2015, Young et al. 2013, Hemelrijk & Hildenbrandt 2011, Hemelrijk et al. 2015, Goodenough et al. 2017.
`murmuration-flock.js` measures the page headless (`node murmuration-flock.js 80 "seed=1&calm&n=5000"`), and prints
each statistic beside the same statistic on featureless uniform ellipsoids of the flock's own size and shape (the
edge/centre spacing reads 1.13-1.29 on a uniform cloud, about 3.1 on a Gaussian one; γ(n) reads 1/3 ± 0.3 per
snapshot). It reports a flock as fragmented, and drops the shape rows, when Φ < 0.8 or the largest group holds under
90 % of the birds.

## The default page (seed 1, calm, 60 s after 20 s)

| | 400 | 1,600 | 5,000 | wild flocks |
|---|---|---|---|---|
| polarization Φ | 0.993 | 0.991 | 0.985 | 0.96 ± 0.03; 0.975 ± 0.023 |
| aspect ratios I2/I1, I3/I1 | 1.4, 2.2 | 1.3, 1.7 | 1.3, 1.7 | 2.8 ± 0.4, 5.6 ± 1.0, the same at every N |
| thickness in neighbour spacings | 8.7 | 13.9 | 20.9 | 5.7-13 (N 448-2,631), ∝ N^⅓ |
| nearest-neighbour distance, m | 1.44 | 1.37 | 1.23 | 0.68-1.51, mean 1.05, independent of N |
| edge / centre spacing (uniform null) | 1.09 (1.29) | 1.16 (1.17) | 1.33 (1.12) | 0.65-0.82: a denser edge |
| neighbour anisotropy γ(1) | 0.41 ± 0.04 | 0.42 ± 0.04 | 0.24 ± 0.04 | ≈0.85 (1/3 if isotropic) |
| bird speed SD / mean | 0.06 | 0.07 | 0.09 | ≈0.13-0.2 |
| displacement in the flock frame at 1 s, m² | 1.22 | 1.86 | 4.40 | ≈1.9 |
| neighbours kept after 3.5 s (Q10) | 0.60 | 0.55 | 0.48 | ≈0.5 |

Correlation length ξ/L is 0.35 at 5,000 (`murmuration-check.js`), as in Cavagna 2010. The default flock is a squashed
ball that gets rounder and denser as it grows, densest in the core: the pull of every bird toward the flock's centre
(`W_GLOBAL`, a fixed spring) builds that. Neighbours show no anisotropy.

## A candidate from local rules: `?local` (experimental)

`?local` sets a bundle of experimental options (each can still be overridden in the URL):

| option | default page | `?local` | why |
|---|---|---|---|
| `balanced` | the 7 nearest birds | the nearest bird in each octant (up to 8) | groups of mutual nearest neighbours cannot close off (Camperi et al. 2012, Interface Focus 2:715, on starling data) |
| `geom=2&gh=0.1&gv=0&gx=0` | centre pull 0.12/s² in all directions | 0.012/s², horizontal only | the flock is held together locally; a weak pull only bounds its horizontal extent |
| `rj` | rejoin beyond 23 m at 5,000 | off (`rj=100`) | |
| `kappa` | 1 | 2: cohesion twice as strong vertically | flattens the flock by a local, scale-free rule |
| `rs` | separation within 2.5 m | 1.5 m | so separation is not a gas pressure on every neighbour |
| `noise`, `tau` | 9 units/s², memory 4 s | 22.5 units/s², memory 0.25 s | long-memory noise drives slow whole-flock deformations; fast noise moves birds among their neighbours |
| `tlag` | turn reaches the back 2.4 s after the front | all birds turn together | the delayed turn shears large flocks; wild turns cross the flock in 0.3-1.3 s |
| `backstop` | per-bird push back into a box around the view | off | it otherwise caps the length of the 5,000-bird flock |

Measured with the corrected tool, calm, 60 s after 20 s, with no screen backstop (seeds in brackets):

| | 400 (1, 2) | 1,600 (1, 2) | 5,000 (1, 2, 3) | default page, 400 / 5,000 | wild flocks |
|---|---|---|---|---|---|
| one flock | yes | yes | yes | yes | |
| polarization Φ | 0.995-0.996 | 0.981-0.992 | 0.988-0.994 | 0.993 / 0.985 | 0.96 ± 0.03 |
| I2/I1, I3/I1 | 2.2-2.3, 3.1-3.2 | 2.4-2.7, 3.6-4.7 | 2.2-2.6, 3.4-6.0 | 1.4, 2.2 / 1.3, 1.7 | 2.8 ± 0.4, 5.6 ± 1.0, flat in N |
| thickness / spacing | 6.4-6.5 | 9.7-10.3 | 14.2-15.4 | 8.7 / 20.9 | 5.7-13 (N 448-2,631), ∝ N^⅓ |
| nearest-neighbour r1, m | 0.86 | 0.87-0.88 | 0.87-0.88 | 1.44 / 1.23 | 0.68-1.51, independent of N |
| edge / centre (uniform null) | 1.17-1.18 (1.32) | 1.09-1.12 (1.18-1.20) | 1.07-1.10 (1.14-1.15) | 1.09 (1.29) / 1.33 (1.12) | 0.65-0.82 |
| γ(1) | 0.48 | | 0.41 | 0.41 / 0.24 | ≈0.85 |
| CM-frame MSD at 1 s, m² | 0.78-0.83 | 1.15-3.39 | 1.34-2.53 | 1.55-1.82 / 3.05-4.70 | ≈1.9, no N trend |
| mutual MSD at 1 s, m² | 0.21-0.22 | 0.21-0.24 | 0.23-0.24 | 0.06 / 0.07-0.09 | ≈0.42 |
| Q10 after 3.5 s | 0.42 | 0.37-0.38 | 0.36 | 0.60 / 0.48 | ≈0.5 |
| bird speed SD / mean | 0.07 | 0.07-0.10 | 0.08-0.09 | 0.06 / 0.09 | ≈0.13-0.2 |
| ξ/L (`murmuration-check.js`, 40 s, seed 1) | 0.29 | 0.28 (800: 0.29) | | 0.35 / — | 0.35 |

Right: one flock at every size with no spring or container; density independent of N; the flattened shape with
I2/I1 near the field value at every N; thickness growing as N^⅓; internal motion at the field value in large flocks;
neighbour-distance fluctuations three times the default's. Still wrong: the edge is no denser than a uniform cloud;
no neighbour anisotropy; polarization and the 400-bird flock's stillness are too high; neighbour distances fluctuate
half as much as in wild flocks; ξ/L is lower than the default's; I3/I1 varies from seed to seed and is low at 400.
Several values are fits rather than mechanisms: the noise memory and strength, κ = 2, the 1.5 m separation range, and
the weak horizontal pull (with none the 5,000-bird flock stretches to 140 m). The octants are fixed to the world axes,
and rebuilding the octant neighbours every 0.1 s costs O(N²): about 3 ms per step at 5,000 birds headless.

Other checks of `?local`:

- **Hunts** (`murmuration-falcon.js 300 "seed=1&n=400&local&classic"`, against the same without `local`): no flock
  split after a flash expansion (default 50 %, Storms 2019 22 %), fewer flash expansions (18 % of strikes, default
  36 %, field 25-34 %), 2.5 strikes per hunt. At 5,000 birds with hunts (150 s, seed 1) it stays one flock (Φ 0.948)
  but spreads: internal motion 9.7 m², 20 % of birds outside the backstop box.
- **Framing** (seeds 1-3, 5,000 birds, the 16:9 crop of a 1200×793 window, 20-24 s): at worst 5-15 % of birds out of
  frame, against 9-25 % for the default.
- **Speed.** Most steps are faster than the default (13 against 29 ms at 5,000 birds, headless), but every sixth step
  rebuilds the octant neighbours of all pairs and takes about 116 ms: a visible stutter at 5,000 birds. It is 14-17 ms
  at 1,600 and 32-41 ms at 2,500. View `?local` at `n=1600` until the rebuild uses the spatial grid or is spread
  over frames.

How this was found: GPT-6-Astra (`codex exec`, xhigh) reviewed the code, this file and the papers, ran 74 headless
experiments, and proposed the octant neighbours. I reproduced its runs, found that the screen backstop was holding
its 5,000-bird flock (6 % of birds), and added fast noise, κ and the weak horizontal pull to the reproduced version.

## Correction (2026-10-07): two internal-motion measures were wrong

An outside review (GPT-6-Astra via `codex exec`) found, and I confirmed in the paper's PDF, that
`murmuration-flock.js` did not measure what Cavagna et al. 2013 measured:

- **Centre-of-mass MSD** (their Eq 2.3) removes only the flock's translation. The tool also removed its rotation, which
  can only lower the value. Fixed; the rotation-removed value is still printed as a diagnostic.
- **Mutual MSD** (their Eq 2.5) is the squared change in the *distance* to the bird's nearest neighbour at t0,
  [|s_ij(t0+t)| − |s_ij(t0)|]². The tool used the change in the neighbour *vector*. Fixed.

Corrected values for the default page (seed 1 / seed 2, calm, 60 s after 20 s):

| | 400 | 5,000 | wild flocks |
|---|---|---|---|
| centre-of-mass MSD at 1 s, m² | 1.82 / 1.55 | 4.70 / 3.05 | ≈1.9, no N trend (N 239-1,246) |
| exponent | 1.88 / 1.97 | 2.06 / 2.07 | 1.73 ± 0.07 |
| mutual MSD at 1 s, m² | 0.06 / 0.06 | 0.09 / 0.07 | ≈0.42 |
| mutual exponent | 1.95 / 1.98 | 2.10 / 2.04 | 1.58 ± 0.2 |

So the page's birds keep almost fixed distances to their neighbours, about 5-7× too still in the field's
measure, while the 5,000-bird flock as a whole deforms 2× too much. The MSD column in the tables above and below
used the old, rotation-removed definition: compare its values only with each other.

## Experiments behind `?geom` (the default is bit-identical without them)

Parameters, all experimental: `geom=1` scales the centre pull by (400/N)^gx (`gx`, default 2/3); `geom=2` also makes it
`gv` times stiffer vertically and `gh` times horizontally; `geom=3` adds local cohesion (1 + `edge`·c) times stronger
for edge birds; `geom=4` replaces the spring with a fixed pull `gf` on edge birds only; `rj` sets the rejoin radius in
units of R_FLOCK; `tlag` scales the delay of a turn from the front of the flock to the back (0: all birds turn
together); `pturn=1` replays one flock-level push to each bird after its delay; `rs` and `coh` override the separation
radius (5 units = 2.5 m) and the local cohesion weight (6). Seed 1, calm, 60 s measured after 20 s.

| setting | N | one flock? | Φ | I2/I1, I3/I1 | thickness / spacing | r1, m | edge (null) | flock-frame MSD 1 s, m² |
|---|---|---|---|---|---|---|---|---|
| default | 5,000 | yes | 0.985 | 1.3, 1.7 | 20.9 | 1.23 | 1.33 (1.12) | 4.40 |
| default + `tlag=0` | 5,000 | yes | 0.988 | 1.3, 1.5 | 21.3 | 1.23 | 1.34 (1.14) | **2.09** |
| default + `pturn=1` | 5,000 | yes | 0.952 | 1.3, 1.7 | 21.8 | 1.23 | 1.34 (1.14) | 5.47 |
| `geom=1` (gx 2/3) | 5,000 | yes, 30 % past the rejoin radius | 0.972 | 1.3, 2.0 | 23.1 | 1.43 | 1.06 (1.14) | 4.97 |
| `geom=2&gh=1&gv=4` | 400 | yes | 0.990 | 2.6, 3.9 | 5.9 | 1.42 | 1.08 (1.32) | 2.05 |
| `geom=2&gh=1&gv=4` | 5,000 | no (41 %) | 0.74 | | | 1.40 | | 46 |
| `geom=2&gh=1&gv=4&gx=0.333&tlag=0` | 400 | yes | 0.993 | **2.6, 3.7** | 6.1 | 1.41 | 1.08 (1.32) | 2.02 |
| same, seeds 1 / 2 / 3 | 1,600 | **borderline (84 / 89 / 93 %)** | 0.91-0.95 | 2.4, 3.4 (seed 3) | 10.5 | 1.35-1.37 | 1.12 (1.18) | 8.6-13.6 |
| same, seeds 1 / 2 | 5,000 | yes (97 / 98 %) | 0.972-0.979 | 2.1, 3.1 | 15.1-15.2 | 1.28 | 1.24 (1.15) | 5.1-5.5 |
| same, `tlag=0.5` | 5,000 | yes (96 %) | 0.930 | 1.9, 3.8 | 15.3 | 1.29 | 1.20 (1.16) | 13.3 |
| same, `geom=3` (edge cohesion) | 5,000 | no (88 %) | 0.894 | | | 1.18 | | 17.4 |
| `geom=2&gh=1&gv=4&gx=0&tlag=0` (default horizontal, vertical ×4) | 5,000 | yes | 0.995 | 2.1, 2.5 | 14.8 | **1.09** | **1.51** (1.15) | 1.69 |
| `geom=2&gh=0.5&gv=4&gx=0&tlag=0` | 400 | **no (41 %)** | 0.921 | | | 1.44 | | 12.5 |
| same, seeds 1 / 2 | 1,600 | borderline (88 / 90 %) | 0.936-0.944 | | | 1.34 | | 11.6-12.2 |
| same, seeds 1 / 2 | 5,000 | yes (99 %) | 0.966 / 0.899 | **2.6, 4.6 / 2.7, 5.4** | 11.7-12.1 | 1.20 | 1.29-1.32 (1.15) | 6.5 / 17.0 |
| same + `ge=3` (spring 1 + 3c for edge birds) | 5,000 | yes (99 %) | 0.980 | 3.0, 4.5 | 11.4 | 1.13 | 1.30 (1.15) | 5.24 |
| default + `tlag=0` | 400 / 1,600 | yes | 0.995 / 0.997 | 1.5, 2.4 / 1.3, 1.6 | 8.5 / 14.5 | 1.46 / 1.36 | 1.03 (1.31) / 1.17 (1.15) | 1.36 / 0.94 |
| default + `tlag=0.4` (≤ 1 s delay) | 5,000 | yes | 0.993 | 1.2, 1.4 | 22.0 | 1.21 | 1.36 (1.14) | 1.34 |
| default + `tlag=0` + `ge=2` / `ge=5` | 400 | yes | 0.998 | 1.7, 2.3 / 1.5, 1.9 | 7.8 / 8.4 | 1.43 / 1.40 | 1.07 / 1.06 (1.33) | 0.90 / 0.63 |
| default + `tlag=0` + `kappa=2` (vertical gain on local cohesion) | 400 / 1,600 / 5,000 | yes | 0.997 / 0.996 / 0.992 | **2.8, 4.0** / 2.2, 2.7 / 1.7, 2.0 | 5.8 / 10.3 / 17.4 | 1.32 / 1.26 / 1.15 | 1.06 (1.32) / 1.13 (1.17) / 1.30 (1.14) | 1.01 / 1.32 / 2.07 |
| default + `tlag=0` + `kappa=3` | 400 / 5,000 | yes | 0.997 / 0.994 | 5.2, 6.6 / 2.4, 2.9 | 3.8 / 14.2 | 1.17 / 1.05 | 1.06 (1.34) / 1.25 (1.15) | 0.89 / 1.82 |
| `geom=4` (edge-only pull, `gf` 3 or 6) | 400-5,000 | no (21-42 %) | 0.62-0.91 | | | 1.41-1.47 | | 18-65 |
| `geom=4&gh=1&gv=1&tlag=0&gf=24&c0=.35` | 400 / 1,600 / 5,000 | yes / yes / 92 % | 0.997 / 0.991 / 0.939 | 1.4, 2.2 / 1.4, 2.2 / 1.7, 2.4 | 8.3 / 13.5 / 21.0 | **1.37 / 1.35 / 1.31** | 1.03 (1.32) / 1.07 (1.16) / **1.13 (1.15)** | 0.96 / 2.19 / 10.0 |
| `geom=4&gh=1&gv=1&tlag=0&gf=12&c0=.2` | 400 / 1,600 / 5,000 | yes / yes / 95 % | 0.997 / 0.996 / 0.969 | 1.6, 2.4 / 1.4, 2.0 / 1.4, 2.1 | 7.9 / 13.8 / 20.3 | 1.39 / 1.35 / 1.30 | 1.08 (1.32) / 1.11 (1.15) / 1.19 (1.15) | 0.97 / 1.14 / 7.27 |
| same as `gf=24`, `gv=3` | 400 / 5,000 | yes / 97 % | 0.997 / 0.901 | 2.3, 3.3 / 1.8, 4.0 | 6.1 / 17.9 | 1.31 / 1.26 | 1.04 (1.32) / 1.15 (1.16) | 0.81 / 17.4 |
| no global force, `rs` 2.5-5, `coh` 6-12 | 400 | no (6-17 %) | 0.84-0.92 | | | 0.75-1.47 | | 21-33 |
| full spring, vertical ×4, `rs` 3-3.5 or `coh` 12 | 400 | no (14-56 %) | 0.81-0.94 | | | 0.84-1.20 | | 13-36 |

What the runs say:

- **Turns.** The page delays each bird's turn by up to 2.4 s from the front of the flock to the back, and ends it for
  all birds at once. That shears a large flock on every turn. Turning all birds together halves the default 5,000-bird
  flock's internal motion to the field value (2.09 against 1.9 m²). Wild flocks fit this better: turns start at a
  lateral tip and cross the flock in 0.3-1.3 s (N 154-595), and birds turn on equal-radius paths, so the flock keeps
  its orientation over the ground while its heading turns (Attanasi et al. 2015, J R Soc Interface; notes_empirical.md).
  Replaying one push to each bird after its delay (`pturn`) is worse: during a turn two birds whose delays differ by Δ
  differ in velocity by the push integrated over Δ, up to 8 units/s² × 2.4 s.
- **Shape.** A pull toward the centre that is stiffer vertically gives the wild shape, thickness and internal motion at
  400 birds. The vertical/horizontal stiffness ratio sets the aspect ratio, but at 5,000 the same rules give 2.1, 2.5-3.1.
- **Density against cohesion.** With a spring, the strength that holds the flock together also compresses its core.
  With the default horizontal strength and vertical ×4 the 5,000-bird flock holds (Φ 0.995, internal motion 1.7 m²),
  but the vertical stiffening packs it (r1 1.09 m) and makes it densest in the middle. Weakened as (400/N)^⅓, a fit
  rather than a derivation, density varies less (r1 1.41 → 1.28 m for 12.5× the birds), but at 1,600 birds the flock
  is on the edge of splitting (largest group 84-93 % over three seeds). (400/N)^⅔, which would hold density constant,
  fragments at 5,000. Half the default horizontal strength with vertical ×4 gives the wild shape at 5,000 (2.6-2.7,
  4.6-5.4) at the default density, but splits at 400 birds and is floppy at 5,000 (internal motion 6.5-17 m²).
- **Local vertical cohesion (κ)** holds the flock at every size with field-like internal motion, and flattens it, but
  less as N grows (κ = 2: 2.8, 4.0 at 400; 1.7, 2.0 at 5,000): the spring sets the large-scale shape.
- **Edge.** The 5,000-bird edge stays sparser than the centre (edge/centre 1.25-1.36 against a uniform-cloud 1.15)
  in every setting that holds; edge weighting on the spring (`ge`) does not change it. At 400 birds the edge is
  already denser than that null (1.03-1.11 against 1.31-1.34).
- **Why local rules don't rescue it.** The separation radius (2.5 m) is about twice the neighbour spacing, so every
  bird is pushed by most of its seven neighbours. The flock is a compressed gas held in by the spring: denser as it
  grows, densest in the core, with the edge pushed outward. Shortening the separation range or strengthening cohesion
  toward the seven nearest neighbours splits the flock into small groups (the largest held 6-56 % of 400 birds), with
  or without the spring. Pulling only edge birds toward the centre (`geom=4`) does not hold the flock either.

- **A strong pull on edge birds only** (`geom=4`, `gf` 12-24, about the outward push separation puts on an edge
  bird) holds the flock with no spring. Density is then almost independent of N (r1 1.37 → 1.31 m over 12.5× the
  birds) and the sparse edge is gone (uniform at 5,000), but the 5,000-bird flock is floppy: internal motion 7-10 m²
  at 1 s and Φ 0.94-0.97. In the field internal motion does not depend on N (D = 3.5-4.1 × 10⁻², N 239-1,246; Cavagna
  2013 Table 1); here it is 1.0 m² at 400 and 7-10 at 5,000. A surface force leaves a large flock's slow, long
  deformations unchecked; a body force (the spring) checks them but compresses the core.
- **Outline (projection) cohesion** (Pearce et al. 2014) moves each bird toward the average direction of the
  light-dark boundaries in its view. At the page's density and life-size birds the flock is mostly transparent
  (optical depth ≈ 0.004 per metre, about 0.3 along the 5,000-bird flock's length), so each other bird's silhouette
  contributes boundary on all sides of it, weighted by its angular size, 1/d. The pull is then toward a 1/d-weighted
  centre with a strength that grows as r/R: a spring whose stiffness falls as 1/R ∝ N^-⅓, the `gx=0.333` row above.
  When opaque it acts on edge birds only, the `geom=4` rows. Both limits are measured above; neither holds 5,000 birds
  as still as wild ones. [derived here, not run]
  **Wrong, per the outside review:** with clustered birds, silhouettes that overlap within a cluster cancel
  boundary even at low overall opacity. In its two-lobed test configuration the centre of mass sits at the
  observer, so both centre-directed forms give zero, yet the outline response is not zero. The equivalence holds
  only for a smooth, uniform flock. Separately, the `geom=4` edge threshold c0 = 0.35 is below 1/√7 ≈ 0.38, the RMS
  imbalance of seven isotropic directions. The review counted 15-16 % of interior birds in 400-bird snapshots above
  it, so `geom=4` was not a surface-only force, and its rows do not show that surface confinement must be floppy.

Correlation length with `tlag=0` (`murmuration-check.js`, 40 s, seed 1, calm): ξ/L 0.321 / 0.313 / 0.334 at
400 / 800 / 1,600 birds, against 0.351 / 0.350 / 0.333 for the default.

Open: a global cohesion that holds a large flock without compressing it (wild starlings see the whole flock; Pearce et
al. 2014 model this as a response to the flock's projected outline); the 5,000-bird aspect ratio; the edge; neighbour
anisotropy; birds' speed spread.
