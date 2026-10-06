# Murmuration

A starling flock rendered on Canvas, with the observables of Cavagna et al.,
"Scale-free correlations in starling flocks", PNAS 107:11865 (2010) measured live.

Open `murmuration.html` in a browser with `murmuration-sky.jpg` and `motion/` alongside it.
Move the pointer to lure the flock, click to loose a falcon, press **C** for the
correlation panel.

| URL option | effect |
|---|---|
| `?n=800` | number of birds (20–3000, default 400) |
| `?seed=1` | fixed random seed |
| `?noise=1.5` | scale the behavioural noise |
| `?calm` | no spontaneous falcon attacks |
| `?stats` | open the correlation panel |
| `?painted` | painted sky instead of the photograph |
| `?warm=20` | simulate 20 s before the first frame |
| `?motion=legacy` | compare the earlier 2D outlines |

The default renderer uses the Blender-baked XYZ bird surfaces. Starlings have
individual flap/glide/bound schedules; falcon shapes follow position, stoop,
climb and leave events. Open `motion-lab.html` from the page's motion link to
inspect either bird from four views. These animation changes preserve the
merged hunting/escape controller. Gaits currently affect drawing rather than
lift, thrust or glide deceleration; physical coupling is a later milestone.

## What it reproduces

The panel plots the correlation function of the velocity fluctuations, C(r), for
orientation and for speed, and marks the correlation length ξ where each crosses
zero. In the paper ξ grows in proportion to the flock size L (ξ ≈ 0.35 L). Here,
in undisturbed flight with 100 to 1600 birds (L = 17–39 m), ξ/L = 0.33–0.38 for
orientation and 0.32–0.36 for speed, and C(r) keeps one shape in r/L.

Two things in the model produce that: nothing restores a single bird's heading or
speed to a preferred value (steering, levelling and the speed hold act on flock
means), and the behavioural noise is persistent while alignment is stiff. The
fluctuations are smaller than in real flocks: about 1.1–1.5 m/s rms against
roughly 2 m/s, with polarization 0.99 against 0.96.

## The falcon

The peregrine hunts as described in `falcon/refs/hunting_notes.md`:
- **The hunt:** 1–4 strikes per hunt. Before each strike the falcon takes up a
  position above, beside or below the flock.
- **The dive:** it tips over toward the nearest starling and steers the last stretch
  by proportional navigation (gain 2.6, Brighton et al. 2017). Mills et al. (2018)
  supply its 50 ms sensing delay and line-of-sight error. Turns are capped at 2.5 g.
- **After the pass:** a zoom climb. About a third of strikes follow within 5 s.
- **The flock:** flash expansions follow about a quarter of strikes. Starlings in the
  falcon's path dodge with an estimated 3.4 g lateral acceleration. This is a
  model parameter, not a measured starling limit; Mills' modeled load factor
  3.4 is a different quantity. In some hunts, orientation waves spread by each bird
  copying its nearest neighbours' roll.

`murmuration-falcon.js` measures hunts headless. The earlier 16-seed × 300 s,
400-bird benchmark (179 strikes, 62 hunts) is retained below as historical output.
Simulation proxies and observed field classifications are not identical:

| observable | page | measured |
|---|---|---|
| strikes per hunt | 2.8 | ~3 |
| strikes within 5 s of the last | 22 % | 31 % |
| attacks from above / side / below | 54 / 34 / 12 % | 69/21/10 % and 30/57/13 % (two tallies of the Rome footage) |
| peak speed of stoops from above | 34.6 m/s | 31–39 m/s |
| guided (PN) final approach | 75 m, 3.2 s | 47–114 m, median 4.9 s |
| flash expansion (>20 % in 3 s) | 22 % | 25 % |
| flock split after a strike | 21 % | 22 % |
| wave speed | 16 m/s (3.6–24) | 13 m/s (3.7–25) |
| hunts with waves | 29 % | 36–42 % |
| hunts with geometric contact (pass within 0.2 m) | 48 % | 23–24 % observed capture |

**Contact and capture.** The page never draws a catch. Passing within 0.2 m is
a geometric contact proxy, not an observed capture. The historical benchmark
reports contact on 21 % of strikes. Comparisons with Mills' simulated attacks
or field capture rates need matching definitions and experimental context.

**Estimated parameters.** These are not measured: the dodge timing and width,
the waiting position, and the bound share of starling pauses. Their values and
reasons are in the comments in `murmuration.html`.

## Checking it

Run the actual page headlessly, including its animation-frame callbacks and
drawing calls, with no browser or package dependencies:

```sh
node sim/run.js --seconds 30 --query 'seed=1&n=100&calm&painted'
node sim/run.js --seconds 60 --query 'seed=7&n=100&falcon&painted' --format csv
node sim/check.js
node sim/differential.js --seconds 40
node motion/check.js
```

The runner records virtual time, seed/query, Node version, page/script hashes,
trajectory digest and full hunt events. `--inputs FILE` replays timestamped
pointer/key events. The differential checker compares each frame with merged
revision `a5dedcc`, including positions, velocities, falcon behavior and hunt
history. See [sim/README.md](sim/README.md) for input format, optional native
Canvas PNGs, and the distinction between simulation, drawing and browser tests.

```
node murmuration-check.js murmuration.html 40 "seed=1&calm&n=800"
```

runs the page headless and measures the same observables with an independent
implementation.

```
node murmuration-falcon.js 300 "seed=1&n=400"
```

measures hunts against the field data above (`--json` per run, `--merge a.json b.json …`
pools runs).

Check that both embedded bird tables match the latest model exports:

```
node murmuration-assets.js
```

After rebuilding either model's outline, run `node murmuration-assets.js --write`
to refresh the comparison renderer. The starling rebuild does this automatically.
The default XYZ renderer consumes `motion/motion-data.js`; see
[motion/README.md](motion/README.md) for rebuilding and evidence limits. Blender
scenes are authoring assets and are not loaded by the browser.

The headless checker reports distances and speeds in world units. The panel uses
0.5 metres per world unit. Headless checks exercise simulation and drawing code
with canvas stubs; check the page in a browser to validate appearance and controls.

Nothing published may contain a home-directory path or a personal name:

```
git config core.hooksPath .githooks
```

turns on the pre-commit and pre-push hooks, which run `node murmuration-privacy.js`.
It searches text, compressed `.blend` files and PNG metadata, and refuses any
`/Users/<name>` or `/home/<name>` path, the login name, and the names listed one per
line in `.private-words` (git-ignored). `--history` checks every commit.

## Layout

- `murmuration.html`, `murmuration-sky.jpg`: the page. `murmuration-check.js`,
  `murmuration-falcon.js`, `murmuration-assets.js`: headless checks.
- `sim/`: reusable actual-page simulator, regression checks and input replay.
- `motion/`, `motion-lab.html`: baked XYZ models, gait/pose controller and viewer.
- `docs/REALISM_IMPLEMENTATION_PLAN.md`: research-based stages beyond this milestone.
- `blender/`: an earlier rigged falcon; the page no longer uses it.
- `starling/`: the measured starling model the page's starling outline comes from.
- `falcon/`: a peregrine model with measured proportions, its build scripts,
  renders and validation. See `falcon/README.md`.

## Licence

Code and models are MIT licensed (see `LICENSE`). Third-party material and the
references the models were measured from are listed in `CREDITS.md`.
