# Starling (Sturnus vulgaris) ventral flight photos: collection notes

Collected 2026-10-03. Files are in this folder; `manifest.json` has the 12 kept photos, `rejected.json` has 38 reject entries (some are group entries), `contact_sheet.jpg` shows the kept set, `candidates/` holds everything downloaded for inspection, `extras_not_ventral/` holds one lateral folded-wing frame.

## Result in one paragraph

Strict criteria (ventral, bilateral, body axis in the image plane, whole bird sharp, plain sky, wingspan at least 500 px) are met by 6 glide frames and 2 raised-wing downstroke frames. Four further flap-phase frames are kept at quality 2 only as pose-phase references (banked, head-on or oblique); do not use them for symmetric outline fitting. No mid/bottom-of-downstroke or true upstroke frame with a symmetric ventral view was found, and no ventral folded-wing frame.

| Class | Usable (q3 and above) | Low-confidence (q2) |
|---|---|---|
| glide / full spread | 6 (01 q5, 02-05 q4, 06 q3) | 0 |
| downstroke | 2 (08 q4 wings-up, 07 q3 wings-up head-on) | 2 (09 banked, 10 head-on roll) |
| upstroke | 0 | 2 (11 banked climbing, 12 oblique profile) |
| folded | 0 | 0 (one lateral example in extras_not_ventral/) |

## Search queries and sources

**Wikimedia Commons**
- Category listing: `Category:Sturnus vulgaris in flight` (24 files).
- Recursive crawl of `Category:Sturnus vulgaris` to depth 3 (41 categories, 1,553 files; skipped eggs, nests, art, audio, dead, museum, anatomy, flocks).
- 25 full-text searches in the File namespace, including: Sturnus vulgaris flight; Sturnus vulgaris in flight underside; starling flying from below; starling wings spread flight; European starling flying; common starling flying; Etourneau sansonnet en vol; Star im Flug Sturnus; Spreeuw in vlucht; Estornino pinto en vuelo; starling in flight blue sky; Sturnus vulgaris takeoff; starling landing wings; Sturnus vulgaris ventral; starling flapping; starling hovering; Stare fliegend; Gewone spreeuw vliegend; Estorninho-malhado em voo; Sturnus vulgaris volo; starling wing upstroke.
- About 2,240 titles from search plus the crawl; filtered by licence, at least 900 px, starling text or category, no illustration categories (818 + 830 files), then thumbnails were screened by eye in contact sheets, plus an automatic plain-sky pre-filter (63 survivors).

**Flickr** (no API key: parsed the public search page's embedded JSON; licence filter 4, 5, 9, 10 = CC BY 2.0, CC BY-SA 2.0, CC0, Public Domain Mark)
- Four sweeps, 100+ distinct queries, sorted by relevance, interestingness, date posted and date taken, up to 12 pages each. Examples: starling in flight; starling flying; starling flight underside; starling from below flying; starling wings spread; starling wings raised; starling wings down flight; starling underwing; starling hover feeder flight; starling takeoff sky; starling landing wings; sturnus vulgaris flight; starling blue sky flying; plus French, German, Dutch, Spanish terms.
- About 1,030 unique thumbnails screened. Then every photo by the two productive photographers (Alex M Shepherd, 137390807@N03, about 130 starling photos; Jon Brinn, 126816719@N03) was enumerated with a user-scoped search.
- Originals fetched from the photo page's `o` size where the licence allows downloading (all CC0/PDM/CC BY ones used).

**iNaturalist** (API, taxon 14850, licences cc0/cc-by/cc-by-sa, 17 flight-related search terms): 547 photos, 469 at least 1000 px screened as thumbnails. All phone snapshots; nothing usable.

## How species was checked

Each kept photo was inspected on the ORIGINAL file at 3x to 10x magnification (zoom lens crops of head, tail and both wingtips; the magnification is written in each manifest `species_check`). Cues used: pointed bill (yellow in breeding adults, dark in non-breeding and juveniles), glossy black or spangled plumage with buff/white spots and buff-edged undertail coverts, plain brown juveniles with pale throat, triangular pointed wings, short square-ended tail of about a dozen feathers. Other sturnids were rejected on sight: Asian glossy starlings (red eye), chestnut-tailed starling, pied/Asian starlings, mynas. None of the kept adults shows spotless-starling features: all show spotted undertail coverts or spangling, whereas S. unicolor adults are uniform black. Caveat: the two juveniles (02, 05) are plain brown and cannot be told from a juvenile spotless starling by plumage at this resolution; that is ruled out only by range (the photographer's captions name Angus, Scotland localities such as Montrose and East Haven), which is a location argument and not a visual one.

Doubt: photo 08 is a backlit silhouette, so colour cues are absent and the photographer's page does not name the species (the frame was found through a photographer-scoped "starling" search). Identification there rests on spangling, bill and tail shape and the starlings fighting in the same frame. I rate it probable, not certain.

## How symmetry was estimated

1. Segmented each bird against the sky: Lab-space colour distance from a fitted second-order background plane, threshold, closing, hole fill; checked by drawing the outline on the photo. Background residuals (99th percentile of Lab distance outside the mask) were low on the clear-sky photos (1.7 to 6.6); the two highest are 07 (10.5, because foliage at the bottom of the frame was picked up) and 08 (8.0, soft cloud texture).
2. Placed a bill-tip and tail-centre point by hand on a gridded crop to define the body axis.
3. Measured the perpendicular distance of the silhouette's convex-hull extremes on each side of that axis (half-spans) and quoted the percentage difference, plus the tip-to-tip Feret distance.
Caveats: the half-span numbers are only meaningful when the body axis lies in the image plane. For head-on frames (07, 10) and banked frames (09, 11, 12) the axis is foreshortened or the near wing is foreshortened, so the percentages are given but flagged unreliable in the notes. Axis placement error is about 3 percent.

## Things the lead should know

- Eight of the 12 files are by one photographer (Alex M Shepherd, CC0, mostly garden shots; his captions mention Angus, Scotland localities, location not verified): likely a handful of birds repeated, so plumage and wing-shape diversity is narrower than the count suggests.
- Photo 05 has a second bird in the lower half of the frame (not touching): crop to bbox x 922-1934, y 155-920 first.
- Photo 07 has foliage along the bottom 30 percent of the frame (well clear of the bird). Photo 08 is a crop from a frame with two other birds; the original is in `candidates/jb_20948174994.jpg`.
- Photos 06 and 09 carry food in the bill and hanging legs (and 12 an insect in the bill): the outline includes them.
- Photos 04, 07 and 11 are processed (sharpening halos, noise, painterly edges in 11); fine wingtip outlines there are less trustworthy.
- Flickr "Public Domain Mark" (photo 08) is an assertion by the uploader, not a CC grant; CC BY / CC BY-SA photos (04, 07, 11) require the credit line in the manifest, and CC BY-SA requires sharing derivatives under the same terms. The licence shown was read from the file page or the Flickr photo page on 2026-10-03.
- Wingspan in the image is above 900 px for all kept photos (tip-to-tip Feret 907 to 4276 px).
- Commons category files by Bengt Nyman (NZ8 1936-1939) and Charles J. Sharp composites were rejected deliberately (flat recoloured backgrounds, composites, painterly texture).

## What I could not find

- A symmetric ventral frame at the bottom of the downstroke (wings lowered, tips below the body) or at mid-downstroke.
- A symmetric ventral upstroke with the hand swept back.
- A ventral folded-wing frame. The only folded example is a clean lateral frame (`extras_not_ventral/X1_folded_lateral_q4_shepherd-2025-09-07.jpg`, CC0, Alex M Shepherd, Flickr 54786700935, 4337x2837): do not feed it to a ventral pipeline.
- Possible next sources not searched: Flickr users outside the licence filter (all-rights-reserved is excluded by instruction), Pexels/Pixabay (own licences, not on the allowed list), video stills.
