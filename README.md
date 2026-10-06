# Murmuration

A starling flock in a single HTML page, with the observables of Cavagna et al.,
"Scale-free correlations in starling flocks", PNAS 107:11865 (2010) measured live.

Open `murmuration.html` in a browser (keep `murmuration-sky.jpg` next to it).
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

## Checking it

```
node murmuration-check.js murmuration.html 40 "seed=1&calm&n=800"
```

runs the page headless and measures the same observables with an independent
implementation.

Check that both embedded bird tables match the latest model exports:

```
node murmuration-assets.js
```

After rebuilding either model's outline, run `node murmuration-assets.js --write`
to refresh the page. The starling rebuild does this automatically. The page uses
the starling's 15-point `flap_mid` and `upstroke` shapes and the peregrine's four
dive keys; the Blender scenes are build assets and are not loaded by the browser.

The headless checker reports distances and speeds in world units. The panel uses
0.5 metres per world unit. Headless checks exercise simulation and drawing code
with canvas stubs; check the page in a browser to validate appearance and controls.

## Layout

- `murmuration.html`, `murmuration-check.js`, `murmuration-sky.jpg`: the page.
- `blender/`: an earlier rigged falcon; the page no longer uses it.
- `starling/`: the measured starling model the page's starling outline comes from.
- `falcon/`: a peregrine model with measured proportions, its build scripts,
  renders and validation. See `falcon/README.md`.

## Licence

Code and models are MIT licensed (see `LICENSE`). Third-party material and the
references the models were measured from are listed in `CREDITS.md`.
