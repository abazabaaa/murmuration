# Bird colours from the photographed sky

The page's backdrop, `murmuration-sky.jpg`, is the CC0 Poly Haven HDRI "Scythian Tombs 2" reprojected for the page camera. This
directory measures what a starling should look like against it. The steps are: recover how the JPEG was made from the HDR, light the
measured starling model with the same sky in Cycles, and measure haze from the treelines. The page's bird colours over the photo
(`PHOTO_COL` in `murmuration.html`) come from `page_colours.json`.

Downloads are not in the repository. Get them from https://api.polyhaven.com/files/scythian_tombs_2: the 8k and 4k `.hdr` files
and the tone-mapped JPG. OpenStreetMap data for the bbox `33.545,50.775,33.62,50.82` comes from the main API's `map.json` call.

```bash
cd sky
uv run python register.py  HDR8K ../murmuration-sky.jpg --tonemapped PH_JPG   # -> registration.json
uv run python fit_curve.py HDR8K ../murmuration-sky.jpg --tonemapped PH_JPG   # -> tone_curve.json
uv run python bake.py      HDR8K                                              # -> sky_light.json
uv run python fit_haze.py  HDR8K OSM_MAP_JSON                                 # -> haze.json, haze_samples.npz
# Cycles renders of the starling (one Blender at a time: two at once crash writing Metal's shader cache)
blender --background --factory-startup --python ../starling/blender/run_headless.py -- JOB.json   # -> renders.json
uv run python fit_birds.py    renders.json                                    # -> bird_light.json
uv run python page_colours.py renders.json                                    # -> page_colours.json
```

`JOB.json` runs `bird_build.py`, `bird_render.py`, `bird_measure.py` and `starling_look.py` from `starling/blender/`, then
`apply_look(OBJS); exec(open('sky/bl_birds.py').read())`. Its globals are the starling build's plus `HDR` (the 4k), `REG`,
`SKY_DIR`, `OUT`, `N=120`, `SEED=11` and `SPP=64`.

## Results

| step | result |
|---|---|
| registration | yaw 14.24°, pitch 14.27°, roll 0.0°. NCC of log luminance 0.961 against the page JPEG at 960×400. In Blender the world is turned 270° − yaw (checked: NCC 0.9999 against `common.reproject`). |
| source of the JPEG | A global tone curve of the HDR, not Poly Haven's tone-mapped JPG. The isotonic curve per channel is off by 0.7–1.1 codes in-sample and 2.2–3.4 held out (fitted on the left half, tested on the right). sRGB with a fitted exposure is off by 9–10. Mapping through Poly Haven's JPG is off by 3–13. The curve is nearly neutral, with code 16 at radiance 0.1 and 115 at 1. |
| dark end | Only 0.3 % of fitted pixels are below radiance 0.05, and the darkest is 0.02. Below that the curve is a power law (exponent 1.15–1.29) fitted to the lowest decade. |
| sun | 8.54° up, 22° right of the frame centre; normal irradiance (3.15, 2.13, 0.86). pvlib puts the sun there at 14:05:50 UTC on 2022-10-09, azimuth 248.9°, so the page looks toward 226.7° (SW). |
| irradiance | On an upward-facing surface (3.5, 3.9, 4.5); on a downward-facing one (0.27, 0.26, 0.10). The undersides seen from the ground get almost no light. |
| starling, Cycles | 120 random places in the frame, headings, banks and poses, each rendered at albedo 0.03 / 0.05 / 0.10 and in the model's own plumage. The mean radiance is 0.07, mostly the plumage's specular reflection of the sky, so albedo barely matters: code 8 at 0.03 and 12 at 0.10. The model's plumage acts like albedo 0.07. |
| sun glints | 6 % of renders are much brighter (radiance up to 1.2): grazing reflections off a wing panel, mostly within 80° of the sun. A rule built from the body's up vector cannot predict them. They are left out and not drawn. |
| per-bird rule | A rule from irradiance on the visible wing and on the side facing the camera does not beat the mean (cross-validated 0.052 against a spread of 0.057). Variation between birds depends on wing-panel angles. The page uses the mean. |
| haze | The treelines give only a bound. The dark wood 139 m away (OSM; at 1.4× it is the wood on the left of the frame) has its darkest foliage at 2.45 % of its sky in blue, so airlight there is at most that: β ≤ 1.8×10⁻⁴ /m, visibility ≥ 22 km. Farther mapped woods are hidden by the rolling ground, so no value comes from them. The page uses half the bound (V ≈ 44 km). |
| page colours | Codes (12,12,12) at 43 m to (14,14,14) at 95 m. With no haze: 10.7. At the bound: 13.6–17.0. The old fills were purple, (9,7,18) to (39,27,52), with the far ones 23 % transparent; that is more than ten times the haze the treeline allows. |

## Not done

- Glints: these need the page's own wing-panel normals per pose.
- A whole-frame check, comparing a Cycles render of an exported frame with a page screenshot bird by bird (step f of the plan).
- The falcon, which is paler below than a starling, keeps its old fill.
