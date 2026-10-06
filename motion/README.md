# Reference-informed bird motion

The browser consumes `motion-data.js` and `motion.js`; Blender is the offline authoring/evaluation tool. The meshes retain forward, lateral and vertical motion. Each model has 316 material-point vertices, 440 near triangles and 48 distant triangles. All projected triangles wind consistently so folded/overlapping wings remain filled from every view.

`motion-lab.html` exposes species, clip, view, phase, playback speed and bank. The flock defaults to this geometry. `?motion=legacy` selects the earlier outline renderer for comparison.

## Evidence and modeling choices

`reference-targets.json` keeps sources and their scope with the generated data. Starling tip-height endpoints were fitted to existing side-view landmarks and the published 28 cm stroke excursion at 12 m/s in one continuously flapping bird. This does not validate anatomical joint limits.

Individual starling gait timing uses Rayner et al. (2001), Table 1, printed p. 197: one wind-tunnel bird's mean flap/glide durations at four airspeeds. Bout duration is frozen on entry instead of moving with each frame's speed. Table values are observations; interpolation between speeds, clamping beyond the table, ±15% bout variation, separate per-bird random streams, bounding probability and alarm response are simulation choices. The table's reported mean duty factors are retained as evidence, not asserted to equal ratios of mean durations. Tobalske (1995) establishes glides, partial bounds and bounds, with more bounds at higher speeds; partial bounds are not yet separately implemented, and the paper does not supply the implemented bound probability.

Independent wingbeat phases are a default, not a measured law of wild murmurations. Starling flock turning studies measure coordinated trajectories, not synchronized wingbeats. The 2024 small-group study explicitly could not measure pairwise wingbeat phase. Direct phase evidence in shorebirds and ibises differs by species and formation, so neither is imposed on this flock.

The starling models' upstroke path, glide dihedral, folded geometry, and transition interpolation retain estimates from existing photographic fits. Falcon poses retain existing approximate hand droop and `scale_x` folding controls; feather overlap is not physically solved. The controller follows explicit position/stoop/climb/leave events, with speed and normalized steering demand as visual cues. High steering demand can open the wings early within a stoop; it is not a measured load factor. Dive/recovery timing and thresholds are estimated. The flight forces and behavioral random stream are unchanged: these motions visualize the current flight state and do not calculate wing-generated lift, thrust or glide deceleration. Thus the Rayner observation of approximately ±1 m/s within-cycle airspeed variation is not reproduced dynamically.

The external reference library is `~/prj/murmuration-refs/starling/intermittent-flight/`; its manifest records actual downloaded PDFs, hashes, printed pages, licenses and inaccessible sources. Public readability is not treated as an open reuse license. PDF content is not redistributed in this code repository.

## Rebuild

Run in the connected Blender MCP (substitute the absolute checkout path):

```python
path = '/path/to/murmuration/motion/bake_motion.py'
exec(compile(open(path).read(), path, 'exec'), {'__file__': path, '__name__': '__main__'})
```

The script creates `Bird Motion Lab` with both species, replaces only `MotionStarling`/`MotionFalcon` objects, and writes `birds-motion.blend` plus the JSON/JS exports. Original species `.blend` and pose specifications are preserved. Blender actions include a cyclic 12 Hz starling stroke and a four-second estimated falcon dive demonstration; the live browser controller chooses its own gait timing. Space plays the scene animation. File → Open `motion/birds-motion.blend` loads the saved generated scene in a later session.

CLI export can use Blender `--background --factory-startup --python motion/bake_motion.py` (not exercised in this implementation run). All generated files must be rebuilt together. Inputs are SHA-256 recorded in the exports.

## Checks and limits

```sh
node motion/check.js
node murmuration-assets.js
node murmuration-check.js murmuration.html 40 'seed=1&calm&n=400'
```

`node sim/differential.js --seconds 40` compares the actual page's frame callbacks against merged `0d3078f`, including every bird's positions/velocities, baseline falcon fields and complete hunt events. The earlier comparison to `425fe07` in `OBSERVATIONS.md` is historical and does not verify this newer hunt integration.

Bake-time 96 withheld phases bound XYZ atlas interpolation error against evaluated Blender meshes; recorded maxima were 1.54 mm starling flap, 1.50 mm falcon flap, 1.57 mm tuck and 2.09 mm pullout. These quantify interpolation of this rig, not accuracy against living birds. Earlier independent saved-file Blender readback matched all 37 starling action knots within 1.60 micrometres and seven falcon demonstration shape knots within 0.273 mm; those historical measurements are retained with their chain in `OBSERVATIONS.md`. Current integration checks and native Canvas raster evidence are recorded in [FIRST_MILESTONE.md](../docs/FIRST_MILESTONE.md). Browser layout and input delivery remain unobserved; offline rasterization does not substitute for them.
