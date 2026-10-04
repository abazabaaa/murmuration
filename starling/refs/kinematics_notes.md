# Starling kinematics - search log and doubts

Working copies of every text I read (including copyrighted extracts) are in `../../work/`, outside this folder. Nothing there is redistributed.

## What was found, by question

| Q | answer in poses.md | best source | open access |
|---|---|---|---|
| 1 flap: frequency, amplitude, tau, stroke plane | yes, two birds | BG13, ST15, RA01, TO95, DI91 | BG13, ST15 only |
| 2 upstroke flexion | no starling number; passerine proxies | HE06, RH04, HGRS06, TO11 | none |
| 3 glide posture, flap-glide pattern | pattern yes (RA01); posture from jackdaw | RA01, RH01, TO95 | none |
| 4 folded / bound | supported, no numbers | TO95, TO11, RA01 | none |
| 5 turning in flocks | flock bank derived, no individual data | BA08, AT15 | none (arXiv non-exclusive) |
| 6 outlines at graded flexion | top and bottom frames only | BG13, ST15 | yes |
| 7 tail | spread range and use | MR01, RH01 | none |

## Search log (condensed)

1. Starling wind-tunnel kinematics: found Ward 2001 (J Exp Biol 204:3311) and Tobalske 1995 on PubMed. Both paywalled, abstracts only. The real PDF URLs were taken from page metadata, but the content is pay-per-view, so nothing was stored.
2. Rayner et al. 2001 (Am Zool 41:188): full text via a ResearchGate extract. Table 1 (bird #19, 6.2-14.1 m/s) was decoded; see doubt 6.
3. Ben-Gida 2013 and Stalnov 2015 (PLOS ONE, CC BY 4.0): XML, text, PDFs and seven figures downloaded. PDFs re-downloaded this pass from `journals.plos.org/.../file?id=...&type=printable` (13 and 20 pages, valid).
4. Dial, Goslow & Jenkins 1991: abstract found through a PubMed search (PMID 29865507), full text not open. Cineradiography at 9-20 m/s.
5. Passerine proxies: Hedenstrom 2006 (robin) and Spedding 2003 / Hedenstrom 2006 review PDFs from the Lund and USC pages (text read). Rosen 2004 (thrush nightingale kinematics) abstract only. House martin: HGRS06 text only.
6. Jackdaw glide (Rosen & Hedenstrom 2001) from the Lund repository: span ratio, area ratio, tail area, morphology table.
7. Tail: Maybury, Rayner & Couldrick 2001 is on mounted frozen starlings. A first fetch of the Europe PMC XML returned HTTP 500 and the PMC PDF returned an HTML interstitial; the numbers were read through a PDF-parsing scrape of the PMC copy. Table values legible; surrounding text partly garbled by OCR.
8. Flocks: Ballerini 2008 (arXiv 0802.1667), Attanasi 2014 and 2015, Hildenbrandt 2010 model parameters (cruise 10 m/s, 80 g, lift 0.78 N), Flock2 (arXiv 2404.17804), Storms 2019, PMC13448496, PMC11061643. None gives an individual bank angle or a wing posture in a turn.
9. Turning mechanics in other birds: cockatoo (Hedrick & Biewener 2007) and pigeon (Ros 2011) abstracts via PubMed. A PubMed search for starling banked-turn wing kinematics returned nothing.
10. Rose-coloured starling (Engel 2006) abstract: bounding and undulating both used, no trend with speed over 9-14 m/s.
11. Dead ends: a generic web fetch returned unrelated pages (C. elegans, a pigeon homing paper) twice. They held no instructions, I discarded them and found the right URLs from search metadata. A guessed PDF URL gave 404. The Krishnan 2022 review PDF from the publisher gave 403 (the text copy in `work/` came from PMC, CC BY 4.0, and was not needed for numbers).
12. A CC BY 2026 paper (Biomimetics 11:212) on stroke asymmetry from video (PMC13024343) turned out to cover Canada geese and frigatebirds, not starlings. Not used, except that it reports the upstroke projected wing area is about 19 percent below downstroke in those two species.

## Doubts, in order of how much they could move a rig value

1. **Tip-line elevation at top and bottom.** My side-photo geometry gives about +45 deg (38-60) at the top and -55 deg (-46 to -65) at the bottom, with a total near 100 deg. It uses a scale taken from BG13 Fig 2 (60 cm bar, BL = 0.229 m) and an assumed shoulder-to-tip length of 0.18 m (0.176-0.191). The shoulder is hidden under the scapulars, the tip fades into the dark floor at the bottom frame, and the near wing is enlarged by perspective by an unknown few percent. An earlier pass in this task used BL of about 0.20 m and gave smaller values (top +37 to +46 deg, bottom -43 to -50 deg). I replaced it because the Fig 2 bar gives a measured scale, and because the new heights add up to the published 28 cm peak-to-peak. Treat the elevations as low confidence and the tip heights in cm as medium.
2. **Stalnov's flapping-angle range (-55 to +19 deg, 74 deg total, ST15 p11)** matches the bottom but not the top. Its own Fig 3 frames show the wing near vertical at the start of downstroke. The text attributes the range to Kirchhefer et al. (ref 19), which I could not open. I did not use +19 deg.
3. **Fig 3 caption of ST15 is reversed.** The caption says the left images are the start of downstroke. The panel labels and the images show the left panels are the start of upstroke (wing down). BG13 Fig 4 is consistent with the labels.
4. **DI91 reading.** The abstract says the elbow and wrist are "extended to 90 deg or less" at the start of downstroke. I read that as interior angles of 90 deg or less, a folded wing. The humeral "protraction 55 deg" and "retraction to within about 30 deg of the body axis" have no stated reference axis. Both are interpretations. The cineradiography birds flew at 9-20 m/s, not the 12 m/s of BG13. Full text would settle both.
5. **Span ratio R for the upstroke.** 0.50 is a passerine proxy (robin 0.49 at 9 m/s). The starling-specific measurement exists (TO95 reports wingspan at mid-upstroke) but I could not read it. This is the most important missing number for the flexed-upstroke pose.
6. **RA01 Table 1 extraction.** The table text is scrambled: columns and rows of the three blocks interleave. Duty factor, flapping and pause durations, cycle period and frequency are self-consistent (flap s / cycle s reproduces the duty factor to within 0.01 at 8.5 and 12.4 m/s, 0.04 at 10.2 and 0.07 at 14.1 m/s) and are used. The "6" repeated in every column cannot be flaps per burst (1.05 s at 11 Hz is 12 flaps), so I derived flaps per burst as duration x frequency and did not use that column. Other values in the scrambled block (68.2, 41.8, 47.4, 52.6, 54.9 and 0.17, 0.11, 0.09, 0.20) are unlabelled and unused.
7. **TO95 versus RA01.** TO95 says flapping duration and wingbeats per cycle peak at 8 m/s. RA01 shows burst length rising from 12 to 23 beats between 8.5 and 14.1 m/s. Different birds, different protocol (EMG implants shortened the pauses in TO95 per its abstract).
8. **Downstroke fraction from the wake.** Confirmed as a time fraction because lambda_u + lambda_d equals U/f in all four beats. The values (0.43-0.50) are from one bird in four beats. Robin range 0.44-0.49 is in agreement.
9. **Glide span from the jackdaw.** Regression valid 6-11 m/s. The speed mapping (x 0.94) uses wing loading from a morphology table (jackdaw b_max 0.60 m there, but 0.569 m in the Fig 2 caption, measured in flapping flight at 11 m/s). Values above 11 m/s are extrapolated. The hand-sweep upper bound assumes the hand is half the semi-span, which I have not measured on a starling.
10. **Bank angle.** 30 deg comes from a peak centripetal acceleration of 5.7 m/s^2 read from BA08 Fig 4e at 3.2x and 9.6 m/s from Table 1, under a coordinated-turn assumption. It describes the flock path in one event. The tilt of the flock plane in that event is a flock property, not a bird bank angle. AT15 E6 paths are in an inclined plane and were not used.
11. **Single birds.** RA01 is one bird, BG13 and ST15 come from the same tunnel experiments and probably the same bird, so they are not independent, DI91 and TO95 are small samples. No variance is available.
12. **Figure checksums.** One BG13 figure (g004) matched the PLOS download URL by md5 when I re-checked it. The other six were downloaded the same way earlier, and a later re-check was blocked by the server (it returned an identical 50 KB page for all URLs). The images were viewed and are the right figures.
13. **Maybury's tails** were frozen birds set by hand at 4.9 m/s. The 62 deg is the largest spread tested, not the largest a live starling can show.

## Licence triage

| source | licence | stored here |
|---|---|---|
| BG13, ST15 text, PDFs, figures | CC BY 4.0 (PLOS) | yes |
| Storms 2019 (PMC6404399), PMC13448496, PMC11061643, Krishnan 2022 review (PMC9403799) | CC BY 4.0 | no, not needed for numbers |
| RA01, MR01, RH01, HE06, HGRS06, SP03, TO11, TO95, DI91, RH04, EN06, HB07, RO11 | publisher copyright | no, cited only |
| BA08, AT15, Hildenbrandt 2010, Flock2 | arXiv, non-exclusive licence (reference only) | no, cited only |

## What a follow-up would need

- Starling full text of TO95 (mid-upstroke span vs speed, bound percentages) and DI91 (axis conventions): both on JEB and J Morphol, institution access.
- One front-view or dorsal photo set of a gliding or mid-upstroke starling, from the photo agent's folder, to measure the hand sweep and dihedral directly instead of deriving them.
- Kirchhefer et al. 2013 (Phys Fluids 25:111902), the source of the flapping-angle range.
