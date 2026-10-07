# Murmuration

A starling flock in a single HTML page, with the observables of Cavagna et al.,
"Scale-free correlations in starling flocks", PNAS 107:11865 (2010) measured live.

Open `murmuration.html` in a browser (keep `murmuration-sky.jpg` next to it), or run
`./bootstrap.sh` to serve this checkout on 127.0.0.1 and print its URL (`--open`, `--status`, `--stop`).
By default it shows what a camera on the ground would: 5,000 birds at life size, a 1/60 s exposure, sensor grain
and a camera that pans to follow the flock (`?classic` for the earlier look: 400 birds drawn twice life size on clean
frames, fixed camera). Move the pointer to lure the flock, click to loose a falcon, press **C** for the
correlation panel and **I** for the view from above (see *Where was the falcon?* below).

| URL option | effect |
|---|---|
| `?n=800` | number of birds (20–10000, default 5000, 400 under `?classic`; above 1,000 an exact grid search finds the neighbours) |
| `?classic` | the earlier defaults: 400 birds, twice life size, no motion blur or grain, fixed camera (the flight is the same) |
| `?seed=1` | fixed random seed |
| `?noise=1.5` | scale the behavioural noise |
| `?calm` | no spontaneous falcon attacks |
| `?stats` | open the correlation panel |
| `?painted` | painted sky instead of the photograph |
| `?warm=20` | simulate 20 s before the first frame |
| `?inset` | open the views from above and from the side |
| `?roll=15` | SD in degrees of each bird's smoothly wandering roll (default 15, set by the wave stripes in real footage; 0 for wings-level birds) |
| `?trail` | leave fading ghosts behind moving birds (the old default; `?trail=.3` for longer ones) |
| `?halt` | start paused; press **.** to step one 1/60 s frame (with `?warm=T`, frame-exact captures) |
| `?batch=40` | birds per drawing path (default 40; 0 draws each depth bin as one path, the old and much slower way) |
| `?life=0` | draw birds and falcon twice life size, larger still in small windows (by default they are life size) |
| `?shutter=8` | exposure in ms for the motion blur (default 1/60 s; birds are averaged over several instants); `?shutter=0` for none |
| `?grain=2` | camera noise over the frame, so the photographed sky flickers like filmed sky (default 1; `?grain=0` for none) |
| `?follow=0` | fixed camera (by default it pans left and right to follow the flock, as a person filming would; the flight is unchanged, but flocks over 3,000 birds then roam the full width) |

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
- **The flock:** each stoop is slow, medium or fast (9/82/9 %, Storms et al. 2019).
  Whether a flash expansion follows depends on the stoop's direction and speed as in
  Storms' Fig. 6; slow stoops never cause one. Starlings in the falcon's path dodge at
  3.4 g, in every phase of the hunt, including the climb back out through the flock.
  In some hunts, orientation waves spread by each bird copying its nearest neighbours'
  roll, during the stoop and also while the falcon waits beside the flock beforehand.

`murmuration-falcon.js` measures hunts headless. Pooled over 32 seeds × 300 s, 400
birds (388 strikes, 131 hunts), against the measured values:

| observable | page | measured |
|---|---|---|
| strikes per hunt | 2.8 | ~3 |
| strikes within 5 s of the last | 25 % | 31 % |
| attacks from above / side / below | 53 / 38 / 10 % | 69/21/10 % and 30/57/13 % (two tallies of the Rome footage) |
| peak speed of stoops from above | 34.0 m/s | 31–39 m/s |
| guided (PN) final approach | 60 m, 2.8 s | 47–114 m, median 4.9 s |
| flash expansion | 26 % of strikes (22 % expand >20 % in 3 s) | 34 % within 5 s (Fig. 6); 25 % as the next event (Fig. 3) |
| flash expansion by direction above / side / below | 40 / 10 / 18 % | 42 / 11 / 22 % |
| flash expansion by speed slow / medium / fast | 0 / 27 / 44 % | 0 / 36 / 47 % |
| split after a flash expansion | 45 % | 22 % |
| attacks with a wave in the 5 s before | 30 % | 28 % |
| wave speed | 14.1 m/s (3.6–26) | 13 m/s (3.7–25) |
| hunts with waves | 41 % | 36–42 % |
| hunts with a catch (pass within 0.2 m) | 47 % | 23–24 % |

Storms et al. 2019 counts are in `falcon/refs/hunting_notes.md` §3.5. The flash table
reproduces Fig. 6 cell by cell (per-class shares above are within sampling noise of it).
The page's overall share stays below 34 % because it attacks from the side more often than
Storms saw; with Storms' 69/21/10 mix the same table gives 34 %. The falcon waits and starts its stoops at least 37 m in front of the observer, so it
never lines up over the observer's head. Two gaps remain open:
the flock splits after too many flash expansions, and the catch rate is high.

**Catch rate.** The page never draws a catch. Its catch rate matches simulated attacks
better than field hunts: Mills et al. reach 26–31 % per attack, and the page catches
on 20 % of strikes. Field success is lower than either.

**Not modelled.** Blackening, the flock darkening before and around attacks (the
commonest response in Storms et al. 2019). A mild alarm in birds near a falcon that is
not stooping was tried; the optical density measured headless did not rise before
attacks, so it was left out.

**Estimated parameters.** These are not measured: the dodge timing and width,
the waiting position, the stoop-speed factors of the three speed classes, how often
waves start before an attack (fitted to the 28 %) and their halving for slow and fast
stoops, and the bound share of starling pauses. Two more are fitted indirectly: the
roll of a bird in a wave (63°) and the spread of each bird's roll (15°) were never
measured on birds, so they are set together so that the page's wave stripes, measured
the same way, match the Rome hunting video of Storms et al. 2019. Their values and
reasons are in the comments in `murmuration.html`.

### Where was the falcon?

The page is one perspective view, so a falcon that overlaps the flock on screen may be
tens of metres in front of or behind it. Press **I** (or open with `?inset`) for the same
moment from above and from the side, with the line of sight through the falcon, birds
coloured by state (red dodging, yellow alarmed, blue rolling in a wave) and the falcon's
last 3 s coloured by phase. A ring marks the falcon: red within 2 m of a bird, amber
within 6 m. **P** pauses, **.** steps one frame.

`murmuration-falcon.js` sorts every on-screen overlap by what really happened. Over the
32 runs above (684 episodes), 14 % were depth illusions (median 19 m from the nearest
bird), 3 % passed within 6 m with no bird reacting, and the rest passed through birds
that dodged, fled or expanded. Before the falcon was dodged in every phase, 36 % passed
with no reaction, almost all of them the climb back out through the flock after a stoop.

```
node murmuration-falcon.js 300 "seed=1&n=400&classic" --flythrough --view=1728x820
```

lists each episode with a URL that replays it; the run depends on the window size, so
pass your browser's (`innerWidth`×`innerHeight`). The counts above are for the classic view (fixed camera, birds
twice life size); at life size fewer passes overlap on screen. For a 3D replay in Blender:

```
node murmuration-falcon.js 80 "seed=1&n=400&classic" --export=75.5:80
blender --background --factory-startup --python replay/replay_build.py -- "replay/out/replay_seed=1_n=400_classic_75.5-80.json" --at=77.6
```

writes a `.blend` to scrub and orbit, and stills from the page's camera, from above,
from the side and from an orbit, with shadows on a 10 m grid (`--anim` adds an orbit
video). The script checks that its page camera reproduces the page's projection.

## Checking it

```
node murmuration-check.js murmuration.html 40 "seed=1&calm&n=800"
```

(Its default query is `seed=1&n=400`; the page's own default of 5,000 birds is slow to analyse headless.)

runs the page headless and measures the same observables with an independent
implementation.

```
node murmuration-falcon.js 300 "seed=1&n=400&classic"
```

measures hunts against the field data above (the flight does not depend on the view; `classic` keeps the on-screen
overlap counts in the fixed, twice-life-size view they were measured in) (`--json` per run, `--merge a.json b.json …`
pools runs; `--flythrough`, `--view` and `--export` as in *Where was the falcon?*).

```
node murmuration-flock.js 80 "seed=1&calm&n=5000"
```

measures a large flock's shape, density, edge, neighbour anisotropy and internal motion against field data on wild
starling flocks, beside the same statistics on featureless clouds of the same size and shape. `FLOCK.md` has the
results and the experimental `?geom` options tried so far (none of them changes the default page).

Check that both embedded bird tables match the latest model exports:

```
node murmuration-assets.js
```

After rebuilding either model's outline, run `node murmuration-assets.js --write`
to refresh the page. The starling rebuild does this automatically. The page uses
the starling's 15-point `flap_mid`, `upstroke`, `glide` and `bound` shapes and the
peregrine's four dive keys; the Blender scenes are build assets and are not loaded by the browser.

The headless checker reports distances and speeds in world units. The panel uses
0.5 metres per world unit. Headless checks exercise simulation and drawing code
with canvas stubs; check the page in a browser to validate appearance and controls.

## Layout

- `murmuration.html`, `murmuration-sky.jpg`: the page. `murmuration-check.js`,
  `murmuration-falcon.js`, `murmuration-flock.js`, `murmuration-assets.js`: headless checks. `FLOCK.md`: large-flock geometry. `bootstrap.sh`, `murmuration-serve.js`: local server.
- `replay/replay_build.py`: Blender replay of an exported stretch of a run (output in `replay/out/`, not tracked).
- `sky/`: bird colours over the photographed sky, measured from the HDRI, Cycles renders of the starling model and the treelines' haze (`sky/README.md`).
- `blender/`: an earlier rigged falcon; the page no longer uses it.
- `starling/`: the measured starling model the page's starling outline comes from.
- `falcon/`: a peregrine model with measured proportions, its build scripts,
  renders and validation. See `falcon/README.md`.

## Licence

Code and models are MIT licensed (see `LICENSE`). Third-party material and the
references the models were measured from are listed in `CREDITS.md`.
