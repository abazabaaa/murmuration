# Field and roost ecology of starling murmurations: life cycle, drivers and quantitative targets for an evening sequence

Scope: European starling (*Sturnus vulgaris*) winter roosts, mainly Europe; North American data are flagged **[NA]**. Grey literature and citizen science are flagged **[grey]** / **[citizen science]**. Every reference was checked against a DOI landing page, a PMC/PubMed record or an institutional page during this session (2026-10-05). Where only an abstract or a short extract could be read, this is said. Several journal sites (ScienceDirect, Springer, Wiley) blocked direct fetching; their abstracts were read through a scraping service, so for those papers only the abstract (not the full text) was verified. Each finding ends with **Sim:**, a one-line implication for `murmuration.html` (currently 20–3000 birds, default 400, ground camera, flock 37–100 m away, 46° vertical FOV, no roost, time of day, weather or merging).

---

## 1. Timing: start and end relative to sunset, duration, season, light level

### Takeaway
The roost assembles over about 30–45 min that straddle sunset. In a Scottish winter roost, the first flock arrived about 50 min before sunset in October and about 15 min before in December–January. The last birds were in about 11 min before sunset in October and about 13–18 min after sunset in midwinter. Arrival time tracks day length closely (r = 0.82). Display duration is a few minutes to more than an hour, with a mean of about 26 min in the UK. It is shortest around the winter solstice and longest early and late in the season. Murmuration size peaks in early February. No published lux threshold for roost entry was found. Light level clearly matters, though: overcast or misty evenings bring roosting 14–28 min earlier than predicted.

### Cited Findings
- **Arrival window vs sunset (Brodie 1980, central Scotland, 44 dry winter days):** R₁ is the arrival of the first flock (5–6 birds that stay and form the nucleus) and R₂ the arrival of the last roosting birds, both in minutes (+ before, − after sunset). Table I gives mean ± SD by period: Oct R₁ 50.2 ± 11.1, R₂ 10.7 ± 3.6 (day length D = 608 min); Oct/Nov 41.6 / 0.8 (D 534); Nov 24.2 / −7.6 (D 489); Nov/Dec 17.6 / −13.8 (D 444); Dec 19.3 / −12.8 (D 420); Dec/Jan 14.5 / −18.4 (D 432); Jan 22.0 / −15.3 (D 475); Feb 33.0 / −14.0 (D 522). — [Brodie J (1980) Estimation of winter roosting times of the Starling. *Bird Study* 27:116–120 (in "Short Notes"), doi:10.1080/00063658009476667](https://doi.org/10.1080/00063658009476667) (text read via the [ResearchGate copy of the Short Notes PDF](https://www.researchgate.net/profile/Chris-Feare/publication/261644433_Short_Notes/links/55e076c008aede0b572e3048/Short-Notes.pdf))
  - Sim: script `t_first = sunset − (0.19·D − 67.6) min` and `t_last ≈ sunset + 13…18 min` in midwinter. In October, `t_last ≈ sunset − 11 min`.
- **Regression of first arrival on day length:** the extracted text prints "R₁ = 67.56 + 0.19D" (r = 0.82, t₄₂ = 9.16, P < 0.001). The intercept must be **−67.56**: with D = 608 this gives 48 min, matching the October mean of 50.2, and with D = 432 it gives 14.5, matching December/January. The sign was probably lost in the PDF/OCR extraction. — [Brodie 1980](https://doi.org/10.1080/00063658009476667)
  - Sim: use `R1 = 0.19·D − 67.56` (minutes before sunset, D in minutes). It reproduces Table I to within a few minutes.
- **Assembly period length (derived from Brodie's Table I, R₁ − R₂):** Oct 39.5 min; Oct/Nov 40.8; Nov 31.8; Nov/Dec 31.4; Dec 32.1; Dec/Jan 32.9; Jan 37.3; Feb 47.0. — computed from [Brodie 1980](https://doi.org/10.1080/00063658009476667)
  - Sim: the total scripted evening, from first flock to last bird down, should run about 31–47 min of simulated time (shortest around the solstice).
- **Display duration (UK citizen science) [citizen science]:** 1,066 confirmed murmurations (≥500 birds, seen to roost). Mean duration 26 min ± 44 s (SEM). Duration was measured "from the start of observation until the display ended", so it is observer-truncated. Duration is U-shaped across the season: longer at the start and end, shortest around the winter solstice. It fits a quadratic in day of season (R² = 0.267) and is positively related to weekly mean day length (R² = 0.384). Murmurations last longer further north, but the effect is tiny (r² = 0.021). — [Goodenough AE et al. (2017) *PLoS ONE* 12:e0179277, doi:10.1371/journal.pone.0179277 (PMC5476259)](https://doi.org/10.1371/journal.pone.0179277)
  - Sim: default display phase about 26 min, scaled by day length. Use about 20 min near the solstice and 30 min or more in October or March.
- **Season of size:** mean murmuration size rises from October to a peak in early February, then falls until the season ends in March (quadratic, R² = 0.127). The survey ran 1 Oct–end of March. — [Goodenough 2017](https://doi.org/10.1371/journal.pone.0179277)
  - Sim: a `month` selector that scales N. Smallest in October, largest in early February.
- **Season of displays at year-round roosts (London):** "mass evolutions occur only from mid-July to late March" (Cramp et al. 1957, quoted by Brodie 1976). Brodie also notes that on many evenings starlings "quickly enter the roost on arrival, or give only a brief flying display". — [Brodie J (1976) The flight behaviour of Starlings at a winter roost. *British Birds* 69:51–60 (opening paragraph read on the publisher page)](https://britishbirds.co.uk/journal/article/flight-behaviour-starlings-winter-roost)
  - Sim: include a "no display" outcome, with birds flying straight in, as a valid evening.
- **Season, radar:** UK radar "ring angel" activity at Bushy Hill, Essex (1958–61) peaks in late summer. It declines through autumn and winter "due to the coalescence of flocks to form larger roost communities" and stops completely in the breeding season. — [Eastwood E, Isted GA, Rider GC (1962) Radar ring angels and the roosting behaviour of starlings. *Proc. R. Soc. B* 156:242–267, doi:10.1098/rspb.1962.0042](https://doi.org/10.1098/rspb.1962.0042)
  - Sim: roosts get fewer and larger as winter goes on. Late-season scenes should have one big roost, not several small ones.
- **Season, Denmark (Sort Sol) [grey, Danish Nature Agency]:** spring passage February to mid-April; autumn passage from August, which "can last all the way to December". — [Naturstyrelsen, "Sort sol"](https://naturstyrelsen.dk/aktiviteter-i-naturen/safari/sort-sol)
  - Sim: a "Sort Sol" preset should be a migration-season scene (Sep–Oct or Mar–Apr), not a midwinter one.
- **Light, not clock time, drives departure for the roost (likely [NA]; location not given in the abstract):** observations 27 Aug–7 Oct 1966. "Initial departure towards the roost was closely correlated with light intensity". The correlation weakens nearer the roost. Arrival at the roost "is not simply a function of the light-time stimulus", because it also depends on flight distance and on interactions en route. No lux values in the abstract. — [Davis GJ, Lussenhop JF (1970) Roosting of starlings: a function of light and time. *Anim. Behav.* 18:362–365, doi:10.1016/S0003-3472(70)80049-5](https://doi.org/10.1016/S0003-3472(70)80049-5)
  - Sim: drive arrivals from a sky-luminance variable rather than a clock, so that cloud cover shifts the timeline.
- **Cloud and light, radar:** morning dispersals from widely separated roosts happen at about the same time, around sunrise. There is a significant correlation between time of first flight and local light intensity "as affected by varying amounts of cloud". Starlings "fly out earlier and return later, relative to the sun… in winter than in summer". — [Eastwood et al. 1962](https://doi.org/10.1098/rspb.1962.0042)
  - Sim: winter scenes should put the last arrivals later relative to sunset than autumn scenes do (consistent with Brodie's R₂ going from +11 to −18 min).
- **Poor visibility advances roosting (Table II of Brodie 1980):** observed minus predicted roosting time (R₁ − R_E, minutes earlier than predicted) was +28 ("light rain, overcast"), +23 ("misty, overcast"), +16 ("clear to heavy rain cloud") and +14 ("thin mist"). Clear, dry days ranged from −8 to +10. "Roosting occurs earlier than expected on days when visibility is poor… Starlings will also roost early when heavy rain threatens or falls shortly before 'normal' roosting time." — [Brodie 1980](https://doi.org/10.1080/00063658009476667)
  - Sim: `overcast` shifts the whole sequence about 15–25 min earlier relative to sunset.
- **Twilight illuminance scale (for converting times to light):** on a clear evening, horizontal illuminance falls from about 410–585 lx at sunset to about 2–3.5 lx at the end of civil twilight (Sun at −6°). 3.4 lx is the conventional dark limit of civil twilight. This was read only as a search-result summary of the glossary page and is not verified in full. — [AMS Glossary of Meteorology, "civil twilight"](https://glossary.ametsoc.org/wiki/civil-twilight/)
  - Sim: make the sky brightness a function of solar elevation and tie the roost-entry trigger to it.

### Inferences
- Combining Brodie's R₂ with the twilight scale: in midwinter, last birds enter 13–18 min after sunset, roughly the first third to half of civil twilight at 56°N. Roost entry therefore probably finishes at illuminances of a few tens of lux on a clear evening, and higher on overcast evenings when roosting comes early. This is an inference, not a measurement.
- Goodenough's SEM of 44 s implies an SD of about 17–24 min for duration (n ≈ 553–1,066). The duration distribution is therefore wide and probably right-skewed (from a few minutes up to an hour or more). A lognormal with a median of about 20 min and a mean of about 26 min is a reasonable scripting choice. This SD is my back-calculation, not a published figure.
- Display (murmuration) duration of about 26 min is shorter than the assembly window of about 31–47 min. The display covers only part of the arrival period, plausibly from when enough birds are present to when the last flocks drop in.

### Gaps
- No peer-reviewed lux threshold for roost *entry* was found. Davis & Lussenhop (1970) and Jumber (1956, *Auk* 73:411–426) may contain foot-candle values, but only the 1970 abstract was accessible.
- No published distribution (histogram) of murmuration start time relative to sunset across many roosts. Brodie gives one Scottish roost; Goodenough recorded clock time but did not report it relative to sunset.
- Carere et al. 2009 and Zoratto et al. 2010 (Rome) record times relative to sunset in their full texts, which could not be read.

---

## 2. Size: murmuration sizes, sub-flock arrival, directions, rates and merging

### Takeaway
Murmurations range from a few hundred birds to about a million. The UK mean is about 30,000 (max 750,000), and Rome roosts held about 20,000 and 60,000. The size distribution is extremely right-skewed. Roosts are built from many incoming flocks. Small flocks funnel into larger ones along flight lines, and the first flock of 5–6 birds acts as a nucleus. Where predation is higher, incoming flocks are more compact and larger. At the roost the display is not one flock: several flocks continually split and merge. Rates of sub-flock arrival are not published. The best available proxy is radar timing of *morning* departure waves (modal interval 3 min, log-normal).

### Cited Findings
- **UK sizes [citizen science]:** mean 30,082 ± 6,699 SEM birds, maximum 750,000. Threshold for a "true murmuration": ≥500 birds, chosen from the Rome minima of 448 and 428 birds needed to produce a definite murmuration pattern. Size is barely correlated with duration (R² ≈ 0.017). UK and non-UK sizes do not differ (t = 0.604, p = 0.546). — [Goodenough 2017](https://doi.org/10.1371/journal.pone.0179277)
  - Sim: N should be a scene parameter spanning 500 to 10⁵ or more (rendered with impostors or LOD). The current 20–3000 range covers only single sub-flocks.
- **Rome roost sizes:** Termini (city centre) held up to 20,000 starlings with 2 peregrines; EUR (south Rome) held about 60,000 with 5 peregrines. The roosts are about 10 km apart. — [Storms RF, Carere C, Zoratto F, Hemelrijk CK (2019) *Behav. Ecol. Sociobiol.* 73:10, doi:10.1007/s00265-018-2609-0 (PMC6404399)](https://doi.org/10.1007/s00265-018-2609-0)
  - Sim: "Rome" preset at 2×10⁴–6×10⁴ birds in total, displayed as several flocks of 10²–10⁴.
- **Two classes of flock at the Rome roost:** (a) "very high above the roost (>200 m), typically very large (tens of thousands of birds) with a columnar-like shape", performing the most striking changes. (b) Lower flocks (<100 m) right over the roost, "usually smaller in size, ranging from a few hundred to several thousand birds… often very compact, with sharp-bordered edges", which "performed a random walk above the roost". Reconstructed flocks were 448–2,631 birds. — [Ballerini M et al. (2008) *Anim. Behav.* 76:201–215, doi:10.1016/j.anbehav.2008.02.004 (arXiv:0802.1667, full text read)](https://doi.org/10.1016/j.anbehav.2008.02.004)
  - Sim: the app's 400–3000-bird flock corresponds to class (b). Add an optional distant, high, columnar "beacon" mass as a background layer.
- **Single roost size by radar:** an estimate of 500,000 starlings for one large roost (February 1961), from radar signal amplitude. Feeding density about 1 starling per acre (max about 3 per acre). — [Eastwood et al. 1962](https://doi.org/10.1098/rspb.1962.0042)
- **Denmark [grey, government agency]:** Sort Sol "can sometimes contain up to 1 million birds". When the roosting flock exceeds 500,000, it splits "because there becomes too much internal unrest". — [Naturstyrelsen](https://naturstyrelsen.dk/aktiviteter-i-naturen/safari/sort-sol)
  - Sim: cap a single cohesive mass at about 5×10⁵ birds and split above that.
- **Incoming flocks and predation (Rome, 53 observation days):** 12 flocking shapes identified among incoming flocks not under direct attack. "Significantly higher frequencies of compact and large flocks" at the high-predation roost; "small flocks and singletons were more frequent at the roost with low predation pressure". Similar patterns appeared at both roosts when other flocks were performing anti-predator behaviour, even far away. This suggests social information passes between flocks. — [Carere C, Montanino S, Moreschini F, Zoratto F, Chiarotti F, Santucci D, Alleva E (2009) *Anim. Behav.* 77:101–107, doi:10.1016/j.anbehav.2008.08.034 (abstract only)](https://doi.org/10.1016/j.anbehav.2008.08.034)
  - Sim: a `predationPressure` knob that sets arriving sub-flock sizes (high → fewer, larger, compact flocks; low → many small flocks and singletons).
- **Funnelling along flight lines:** Davis & Lussenhop "showed that small flocks 'funnelled' into progressively larger ones along flight-lines to the roost", and concluded that social stimulation from aerial displays helped create larger roosts. This is Goodenough et al.'s summary of the 1970 paper. — [Goodenough 2017](https://doi.org/10.1371/journal.pone.0179277) citing [Davis & Lussenhop 1970](https://doi.org/10.1016/S0003-3472(70)80049-5)
  - Sim: spawn sub-flocks at the horizon along 1–3 flight lines; flocks merge en route, so arrivals get larger as the evening goes on.
- **Nucleus:** roost formation begins with "the first flock of five or six Starlings which subsequently remained to form the nucleus of the roosting mass which followed". — [Brodie 1980](https://doi.org/10.1080/00063658009476667)
  - Sim: start the evening with one small (5–10 bird) flock circling over the roost; later sub-flocks join it.
- **Directionality:** "a 360° dispersal may sometimes be followed by an evening assembly from one direction only". In calm weather the morning dispersal forms concentric rings. — [Eastwood et al. 1962](https://doi.org/10.1098/rspb.1962.0042)
  - Sim: arrivals should come from a narrow azimuth sector (one or a few flight lines), not uniformly around the horizon.
- **Wave timing proxy:** successive morning departure waves have a log-normal inter-wave interval with mode 3 min (larger in summer than winter). Each successive wave flies about 1 knot slower. — [Eastwood et al. 1962](https://doi.org/10.1098/rspb.1962.0042)
  - Sim: as a first guess, draw evening sub-flock inter-arrival times from a log-normal with mode about 3 min (shorter in winter), tightening as sunset approaches.
- **Splitting and merging during display:** displays at roosts consist of "multiple flocks which are continually changing shape and density, while splitting and merging". In the StarDisplay model this needed a roost-area attraction (a cylinder sized to the Termini flight area) plus banking turns. — [Hildenbrandt H, Carere C, Hemelrijk CK (2010) *Behav. Ecol.* 21:1349–1359, doi:10.1093/beheco/arq149 (arXiv:0908.2677, full text read)](https://doi.org/10.1093/beheco/arq149)
  - Sim: add a horizontal roost-cylinder force and a vertical "preferred height above roost" force (StarDisplay's w_roostH, w_roostV) so that merges and splits emerge.
- **Split/merge sequencing under attack:** "Merges happened after splits, followed by flock dilution". 78.3% of flash expansions did not lead to a split. Dilution took 15.0 ± 2.4 s after an attack. Splits were more likely at EUR (higher hunting pressure, larger flocks). — [Storms et al. 2019](https://doi.org/10.1007/s00265-018-2609-0)
  - Sim: target split → re-merge → dilution over about 15 s after a falcon pass.
- **Catchment [NA within a review; numbers via Goodenough]:** individuals regularly travel ≥8 km between roost and feeding grounds, exceptionally up to 50 km in favourable weather, and switch roosts. — [Goodenough 2017](https://doi.org/10.1371/journal.pone.0179277) (citing older sources)
  - Sim: incoming flocks should cross the scene from beyond the horizon at cruising speed (about 17–21 m/s; see section 3), not appear near the roost.

### Inferences
- For a sample of about 1,000 records, an SEM of 6,699 implies an SD on the order of 2×10⁵ birds, several times the mean. The size distribution is therefore heavy-tailed, roughly log-normal: most murmurations are a few thousand birds, with rare enormous ones. Median ≪ mean. This is a back-calculation.
- The app's N ≤ 3000 matches individual Rome flocks (448–2631), not whole murmurations. A realistic evening needs multiple flocks: several app-scale flocks in the foreground plus a far, large aggregate.

### Gaps
- No published arrival rate (flocks per minute) or sub-flock size distribution for evening assembly at European roosts was found in accessible text. Carere 2009 contains incoming-flock counts by shape, but only the abstract was readable.
- No quantitative merge rate (merges per minute) at roosts.
- Brodie 1976 (British Birds) has a detailed description of flight behaviour at a Scottish roost, but only the first paragraph is open access.

---

## 3. Weather: temperature, wind, cloud and rain effects on duration, size, height and shape

### Takeaway
Rain and poor visibility shorten or cancel displays: birds roost early and fly straight in low. Overcast advances roosting by about 15–28 min. Temperature has only a weak effect: colder evenings give slightly longer displays (Goodenough), and warmer days shift arrival by about 2.5 min per °C (Brodie). Temperature does not predict size. Wind has a contested effect. Older sources say aerial evolutions are "at their best when high winds make it difficult for flocks to alight". Others report that on very windy or wet evenings birds fly straight in at 1–2 m. Radar shows departures in wind becoming downwind arcs at lower altitude. Modern weather radar has not been used to quantify European starling roosts in any paper found.

### Cited Findings
- **Rain:** Brodie excluded rainy days because "rainfall has a marked effect upon Starling roosting behaviour". Birds "roost early when heavy rain threatens or falls shortly before 'normal' roosting time" (light rain + overcast: 28 min earlier than predicted). — [Brodie 1980](https://doi.org/10.1080/00063658009476667)
  - Sim: `rain` → advance by about 20–30 min, display duration toward 0–5 min, and birds descend straight in.
- **Wind and rain, low direct entry vs better displays (conflicting):** Brodie (1976) summarises Spencer (1966): aerial evolutions "are at their best when high winds make it difficult for flocks to alight", and when starlings react to a kestrel or similar predator. He also summarises Bickerton & Chapple (1961): "on very windy or wet evenings Starlings flew straight into their roost, often without rising more than a metre or two above ground". — [Brodie 1976](https://britishbirds.co.uk/journal/article/flight-behaviour-starlings-winter-roost)
  - Sim: model moderate wind as increasing turbulence and turning, and strong wind plus rain as skipping the display with a low-level direct approach. Flag this as contested.
- **Wind and altitude (radar):** calm-weather dispersals form concentric circles at a mean altitude of 150 ft (≈ 46 m). "In the presence of wind there is a tendency for the dispersal to be in the form of arcs moving downwind", partly because birds fly lower upwind and drop below the radar. — [Eastwood et al. 1962](https://doi.org/10.1098/rspb.1962.0042)
  - Sim: in wind, arriving flocks heading upwind fly lower (tens of metres) and drift; the display centre should shift downwind of the roost.
- **Flight speed by season:** mean airspeed of starlings leaving the roost was 37 knots (≈ 19 m/s): 40 kn (≈ 20.6 m/s) in winter, 32 kn (≈ 16.5 m/s) in summer. — [Eastwood et al. 1962](https://doi.org/10.1098/rspb.1962.0042)
  - Sim: transit (arrival) flocks at about 17–21 m/s, faster than in-display flocks (Rome display flocks: centre-of-mass 6.9–15.2 m/s, [Ballerini 2008](https://doi.org/10.1016/j.anbehav.2008.02.004)).
- **Temperature and duration/size [citizen science]:** temperature was a significant *negative* predictor of duration (colder → longer). On its own it explained R² = 0.144, weaker than day length (R² = 0.384). Temperature did not predict size, nor how the murmuration ended (ANOVA p = 0.174). — [Goodenough 2017](https://doi.org/10.1371/journal.pone.0179277)
  - Sim: a small duration multiplier, about +10% per 5 °C colder; no temperature effect on N.
- **Temperature and roosting time:** the residual of roosting time against mean temperature over the preceding 24 h: R₁ − R_E = −12.29 + 2.46T (r = 0.37), "only 2½ minutes alteration in roosting time for each centigrade degree". — [Brodie 1980](https://doi.org/10.1080/00063658009476667)
  - Sim: the sign implies warmer days bring first arrivals slightly earlier relative to sunset (R positive = before sunset). Apply about 2.5 min per °C as a minor shift.
- **Shape and weather disturbance (model):** the StarDisplay authors attribute the gap between their model and real flock volume, thickness and altitude variability to the lack of disturbances: "threat of predators… other species (such as gulls), the wind, rain and change in lighting conditions". — [Hildenbrandt et al. 2010](https://doi.org/10.1093/beheco/arq149)
  - Sim: wind gusts as a slowly varying force field are a cheap way to add realistic shape variability.
- **Field conditions for 3-D data:** STARFLAG photographs were taken only when wind speed "never exceeded 12 m s⁻¹". — [Ballerini 2008](https://doi.org/10.1016/j.anbehav.2008.02.004)
  - Sim: the published kinematic targets (density, aspect ratio) apply to winds below 12 m/s.
- **Modern radar:** an open European weather-radar biological dataset covers 141 radars in 18 countries (2008–2023) as vertical profiles. It is not a roost dataset. — [Biological data derived from European weather radars, *Sci. Data* (2025), doi:10.1038/s41597-025-04641-5 (PMC11871220)](https://doi.org/10.1038/s41597-025-04641-5). **[NA]:** machine-learning roost-ring detection on US NEXRAD (mostly swallows and martins) — [Perez et al. (2024) *Remote Sens. Ecol. Conserv.* doi:10.1002/rse2.388](https://doi.org/10.1002/rse2.388); [arXiv:2004.12819](https://arxiv.org/abs/2004.12819).

### Inferences
- Weather mostly modulates *whether* and *how long* there is a display, and *when* birds arrive. It changes size much less, because size is set by the roost population that evening.
- The wind conflict can be reconciled as dose-dependent: moderate wind may prolong airborne milling (hard to alight), while gale plus rain suppresses the display. This reconciliation is my own and is untested.

### Gaps
- No quantitative study found of the effect of wind speed, cloud cover or rain on murmuration duration, height or shape, from Goodenough or any 2018–2026 study.
- No Danish peer-reviewed Sort Sol study was found in accessible form; Danish values above are from a government agency page.
- No European weather-radar study of evening starling roost assembly was found. Eastwood 1962 remains the main radar source and concerns mostly morning dispersal.
- No Rome weather analysis (Carere/Cavagna/Hemelrijk/Storms) was found.

---

## 4. Altitude and spatial extent: height, horizontal size, distance from the roost

### Takeaway
Display flocks over the roost fly at roughly 20–100 m. The Rome reconstructions were taken at about 100 m range from a 30 m-high terrace, and the low class was below 100 m. Large "beacon" masses fly above 200 m. Individual display flocks are thin horizontal sheets 5–19 m thick and about 20–145 m long. Volumes are about 900–33,500 m³ (STARFLAG) or 500–17,000 m³ (StarDisplay). Displays stay "more-or-less static with respect to a focal point on the ground", the roost, within a confined area whose radius is not published in accessible text. Transit flocks arriving or leaving fly at about 46 m (150 ft) in calm air and lower into the wind. In bad weather, birds approach at 1–2 m above ground.

### Cited Findings
- **Height classes:** "very high above the roost (>200 m)… columnar-like shape" versus lower flocks "(<100 m), right over the roost". — [Ballerini 2008](https://doi.org/10.1016/j.anbehav.2008.02.004)
  - Sim: put the main flock at 30–100 m above ground, plus an optional far layer at 200 m or more.
- **Flock dimensions (10 Rome events, N = 448–2631):** thickness I₁ = 5.3–19.0 m. I₃ = I₁·(I₃/I₁) runs from about 21 m (event 32-06: 5.33 × 4.02) to about 143 m (event 16-05: 17.14 × 8.36). Volumes 930–33,487 m³. Flocks "slide parallel to the ground" (|I₁·G| = 0.93). — [Ballerini 2008](https://doi.org/10.1016/j.anbehav.2008.02.004) (I₃ values computed from its Table 1)
  - Sim: at N = 400–3000, the flock's long axis should be about 20–145 m. At the app's 37–100 m viewing distance, a 100 m flock overfills a 46° frame (see section 8).
- **Model flock volume:** 500–17,000 m³ in StarDisplay. — [Hildenbrandt et al. 2010](https://doi.org/10.1093/beheco/arq149)
- **Roost tether:** displays remain "more-or-less static with respect to a focal point on the ground (generally the roosting site)". — [Goodenough 2017](https://doi.org/10.1371/journal.pone.0179277). StarDisplay confines birds to "a cylindrical area of approximately the size of the flight area above the roosting site at Termini". It also uses vertical attraction to a "preferred height above the roost", which produces both the flat flock and the turns at the cylinder edge. — [Hildenbrandt et al. 2010](https://doi.org/10.1093/beheco/arq149)
  - Sim: add a roost at a fixed ground point within about 100–300 m of the camera; birds turn back at the cylinder edge, which drives turning without waypoints.
- **Transit altitude:** calm morning dispersal at a mean of 150 ft (≈ 46 m); lower upwind. — [Eastwood et al. 1962](https://doi.org/10.1098/rspb.1962.0042)
- **Bad-weather approach:** "often without rising more than a metre or two above ground". — [Brodie 1976](https://britishbirds.co.uk/journal/article/flight-behaviour-starlings-winter-roost)
- **Robot-falcon field data (Netherlands, 2019, agricultural sites, not roosts):** under pursuit, flocks of about 20–2000 birds often went "columnar", elongated in altitude. Pursuits lasted 20 s–2 min (mean about 1 min). — [Papadopoulou M et al. (2026) A mechanistic understanding of collective escape in starling flocks. *Commun. Biol.* doi:10.1038/s42003-026-10173-4 (PMC13448496, full text read)](https://doi.org/10.1038/s42003-026-10173-4)
  - Sim: under falcon attack, allow a vertical "column" mode as well as the flat sheet.

### Inferences
- With the camera on the ground and flocks 30–100 m up and 37–100 m away horizontally, elevation angles of 20–70° are typical. The flock should often be seen fairly steeply from below, which is why observers misjudge its thinness (Ballerini 2008 notes this projection effect).

### Gaps
- No published radius of the display area above a roost. StarDisplay's R_Roost value (its Table 1) was not in the accessible text.
- No distribution of display height over the course of an evening (for example, whether flocks descend progressively as light fades).

---

## 5. Roost descent: how the murmuration ends

### Takeaway
Displays end in one of two ways. Either the whole mass descends to roost, or the aggregation breaks up and birds leave (67.1% of observers saw the end). Mass descent is significantly more likely when birds of prey are present (χ² = 33.6, P < 0.001). The last birds are in by about 13–18 min after sunset in midwinter. Descents are widely described as funnel- or vortex-like "pouring" into reeds or trees, but no peer-reviewed measurement of descent rate or duration was found. Inside the roost, position is hierarchical: adult males sit centrally and first-year females peripherally. That gives a mechanistic reason for jostling and delayed entry.

### Cited Findings
- **End types and predators [citizen science]:** "The frequency of birds descending after murmurating was substantially and significantly higher, and the frequency of the murmuration dispersing and the birds flying away was lower, when a bird of prey was present" (χ² = 33.600, d.f. = 2, P < 0.001). The end was seen in 67.1% of reports. Temperature had no effect on the end type. — [Goodenough 2017](https://doi.org/10.1371/journal.pone.0179277)
  - Sim: an end-state roll. P(descend) is higher when the falcon is enabled; otherwise there is some chance the mass drifts off-screen.
- **Last arrival timing:** R₂ = −12.8 to −18.4 min (after sunset) in Dec–Feb; +10.7 in October. — [Brodie 1980](https://doi.org/10.1080/00063658009476667)
  - Sim: finish the descent by sunset + 15 ± 8 min in winter.
- **Fast direct entry:** on many evenings starlings "quickly enter the roost on arrival, or give only a brief flying display". — [Brodie 1976](https://britishbirds.co.uk/journal/article/flight-behaviour-starlings-winter-roost)
- **Descent morphology [grey]:** "funnel down into the reeds in one last whoosh of wings"; "dropping down like stones". — [The Wildlife Trusts, "Starling murmurations"](https://www.wildlifetrusts.org/where_to_see_starling_murmurations); [Lancashire Wildlife Trust blog](https://www.lancswt.org.uk/blog/starling-murmuration-facts). These are descriptive only and give no rates.
  - Sim: descent as a sink at the roost point. Birds within a funnel radius switch to a steep dive (pitch −30 to −60°), so the stream thins into a vortex. Waves of sub-flocks peel off in sequence.
- **Waves of departure (morning analogue):** birds leave in successive waves with a modal interval of 3 min. Roost "chatter" intensity cycles in step with the waves. — [Eastwood et al. 1962](https://doi.org/10.1098/rspb.1962.0042)
  - Sim: by symmetry, script the evening descent as 2–5 waves rather than one block. The wave interval is unmeasured; keep it tunable, at tens of seconds to minutes.
- **Roost hierarchy:** "proportionately more adult males occurred in the centre compared with the periphery, and proportionately more first-year females occurred on the periphery". "Birds in the centre were heavier than peripheral ones irrespective of differences in body-size"; the centre is the preferred location. — [Summers RW, Westlake GE, Feare CJ (1987) *Ibis* 129:96–102, doi:10.1111/j.1474-919X.1987.tb03164.x (abstract)](https://doi.org/10.1111/j.1474-919X.1987.tb03164.x)
- **Murmuration as negotiation over roost position (2025 review/hypothesis):** murmurations are "closely linked to reedbed roosting". Subdominant juveniles, especially females, are relegated to the periphery and "suffer a disproportionately high mortality". Murmurations are proposed as "prolonged and energy-consuming negotiations about relative roosting positions". This is a hypothesis with no new data. — [Mouy H (2025) *Behav. Ecol. Sociobiol.* 79:127, doi:10.1007/s00265-025-03668-3 (abstract)](https://doi.org/10.1007/s00265-025-03668-3)
  - Sim (optional): give birds a "dominance" scalar; dominants descend first and to the roost centre, others later and to the edges.

### Inferences
- A plausible scripted descent is 1–5 min long for the bulk of a display flock, inferred from grey descriptions and the R₂ spread (SD 3–12 min across nights), but this is unmeasured. The descent is probably fastest when a predator is present (Goodenough's end-type result).

### Gaps
- **No measured descent rate** (birds/s entering the roost), funnel geometry, dive angle or descent duration was found in peer-reviewed literature. This is the largest gap for scripting the ending; high-frame-rate video at a reed roost would be needed.
- No study measured whether descent proceeds in discrete waves in the evening (only the morning-departure analogue exists).

---

## 6. Functional hypotheses and evidence

### Takeaway
Anti-predator benefit ("safer together": dilution, detection, confusion) has the most quantitative support. Predator presence and activity explain about 30–40% of the variance in murmuration size and about 12–26% of duration, and predators raise the probability of en-masse descent. Peregrines at Rome roosts succeed in 23.1% of 328 hunts and catch at least one starling every evening. Most hunts target flocks, but singletons are caught more often. "Warmer together" (thermal/roost advertising) has only weak support: temperature does not predict size and only weakly predicts duration. The beacon/advertising and information-centre ideas are largely untested for starlings. A 2025 review proposes competition for central roost positions.

### Cited Findings
- **Predators and size [citizen science]:** birds of prey were present at 29.6% of murmurations, most commonly sparrowhawk, then buzzard, marsh harrier, hen harrier and peregrine. Corvids were reported at 15.8% and gulls at 17.6%. Size models: presence only (harrier, buzzard, peregrine, owl, sparrowhawk) adj. R² = 0.304–0.349. Activity (harrier and peregrine flying or engaging; buzzard engaging) adj. R² = 0.385–0.401. Only "flying" and "engaging" ever entered the models; perched predators did not. — [Goodenough 2017](https://doi.org/10.1371/journal.pone.0179277)
  - Sim: the falcon's presence and attack rate should raise both N (attraction to big roosts) and display duration. Perched predators have no effect.
- **Predators and duration:** presence + temperature(−) adj. R² 0.110–0.122. Activity models (sparrowhawk and harrier engaging or flying, peregrine engaging, buzzard and kite flying) adj. R² up to 0.256. — [Goodenough 2017](https://doi.org/10.1371/journal.pone.0179277)
  - Sim: each active predator pass extends the scripted display by a few minutes.
- **Causality caveat:** "the murmuration-predator relationship could… be as much (potentially more) driven by murmurations attracting predators… than by predators causing starlings to murmurate". — [Goodenough 2017](https://doi.org/10.1371/journal.pone.0179277)
- **Peregrine hunting at Rome roosts:** 328 hunting sequences, overall success 23.1%. Success was higher when sequences lasted <1.5 min, had <3 attacks and no other falcons were hunting. It was higher on singletons than on flocks, but most hunts targeted flocks. Nine hunting strategies were identified; the "surprise attack" was the most frequent and most successful. Constant predation pressure did not change roost use, and falcons "captured at least one prey item every evening". — [Zoratto F, Carere C, Chiarotti F, Santucci D, Alleva E (2010) *J. Avian Biol.* 41:427–433, doi:10.1111/j.1600-048X.2010.04974.x (abstract)](https://doi.org/10.1111/j.1600-048X.2010.04974.x)
  - Sim: falcon script of 1–3 attacks per sequence, sequences under about 1.5 min, several sequences per evening, mostly from above (121/175 attacks from above; [Storms 2019](https://doi.org/10.1007/s00265-018-2609-0)).
- **Predation and flocking shape:** larger, compact incoming flocks at the high-predation roost; predation success was higher at the low-predation roost. — [Carere et al. 2009](https://doi.org/10.1016/j.anbehav.2008.08.034)
- **Confusion effect:** human "predators" attacking simulated 3-D starling flocks; cited as experimental support for confusion. Title and DOI verified; numbers not read. — [Hogan BG, Hildenbrandt H, Scott-Samuel NE, Cuthill IC, Hemelrijk CK (2017) *R. Soc. Open Sci.* 4:160564, doi:10.1098/rsos.160564](https://doi.org/10.1098/rsos.160564)
- **Warmer together (thermal) and roost advertising:** temperature did not predict size and only weakly predicted duration (R² 0.144 vs day length 0.384). The authors conclude murmurations are "primarily an anti-predator adaptation rather than being undertaken to attract larger numbers of individuals to increase roost warmth". — [Goodenough 2017](https://doi.org/10.1371/journal.pone.0179277). Roost microclimate study (no abstract available): [Yom-Tov Y, Imber A, Otterman J (1977) *Ibis* 119:366–368, doi:10.1111/j.1474-919X.1977.tb08258.x](https://doi.org/10.1111/j.1474-919X.1977.tb08258.x); huddling in roosting starlings: [Peach WJ, Gibson TSH, Fowler JA (1987) *Bird Study* 34:37–38, doi:10.1080/00063658709476933](https://doi.org/10.1080/00063658709476933) (numbers not read).
- **Beacon/advertising:** the high, columnar flocks of tens of thousands "may act as beacon to signal the location of the roost to conspecifics (Feare 1984)". This is a suggestion, not a test. — [Ballerini 2008](https://doi.org/10.1016/j.anbehav.2008.02.004)
  - Sim: an optional high distant mass visible early in the evening, before the foreground flocks arrive.
- **Information centre:** the original hypothesis is [Ward P, Zahavi A (1973) *Ibis* 115:517–534, doi:10.1111/j.1474-919X.1973.tb01990.x](https://doi.org/10.1111/j.1474-919X.1973.tb01990.x). **[NA]** radiotelemetry of communally roosting starlings: [Morrison DW, Caccamise DF (1985) Ephemeral roosts and stable patches? *Auk* 102:793–804](https://doi.org/10.2307/4087008) (DOI taken from the reference list of Mouy 2025; content not read). No starling-specific numbers were obtained.
- **Roost-position competition:** see section 5 ([Summers 1987](https://doi.org/10.1111/j.1474-919X.1987.tb03164.x); [Mouy 2025](https://doi.org/10.1007/s00265-025-03668-3)).
- **Social information between flocks:** flocks at both Rome roosts flocked more compactly when *other* flocks were showing anti-predator behaviour, even far away and with no predator at the focal roost. — [Carere 2009](https://doi.org/10.1016/j.anbehav.2008.08.034)
  - Sim: a falcon attack on one flock should briefly compact other visible flocks too.

### Inferences
- For a scripted evening, predators are the only driver with quantitative effect sizes. Making the falcon an evening-level variable that affects N, duration and end type is well supported. The thermal and advertising variables should at most be minor modifiers.

### Gaps
- Morrison & Caccamise 1985: its DOI (10.2307/4087008) was inferred from JSTOR's pattern and the Mouy reference list did not give it. **Treat this DOI as unverified.**
- No numbers were obtained for the information-centre test or the thermal benefit (roost-minus-ambient temperature).

---

## 7. Acoustic environment (optional realism)

### Takeaway
The display sound is dominated by wingbeats: "murmuration" is named for the sound of many wingbeats. Calls (chatter) rise once birds are in the roost. Radar-era work showed roost chatter intensity cycling in step with waves of departing birds. No peer-reviewed acoustic measurement (spectrum, dB SPL) of a murmuration was found.

### Cited Findings
- Murmurations are "so-called because of the sound produced by multiple wingbeats". — [Goodenough 2017](https://doi.org/10.1371/journal.pone.0179277)
- "Cyclic variation in the intensity of starling chatter, as recorded at the roost, is correlated with the periodic eruptions of the waves of birds which produce the rings upon the radar." — [Eastwood et al. 1962](https://doi.org/10.1098/rspb.1962.0042)
  - Sim: tie roost-chatter loudness to the number of birds already down, with a bump just before each departure or descent wave.
- **[grey, low-quality web source]:** during the display "calling actually drops… the dominant sound becomes the rush of tens of thousands of wingbeats, a low rustling roar". After landing there is "a deafening chorus of chattering, whistling, and clicking" that continues after dark. — [The Faunalist, "Starling sounds"](https://thefaunalist.com/birds/starling-sounds/)
  - Sim: use band-limited noise for the "whoosh", with gain proportional to the number of birds within about 50 m of the camera and modulated by flock turning rate. Fade in roost chatter as birds descend.
- Wingbeat frequency of about 10 Hz (wing-flap peak at about 68 rad/s) from 3-D tracking. — Cavagna et al. 2025, arXiv:2505.19665, as summarised in `/home/user/murmuration/research/criticality-canonical-references.md`.
  - Sim: amplitude-modulate individual nearby wing sounds at about 10 Hz; a mass of birds gives a broadband roar.

### Gaps
- No measured sound pressure level, spectrum or distance attenuation of murmuration wing noise in the peer-reviewed literature.

---

## 8. Observer and camera geometry (check of the app's setup)

### Takeaway
The best-documented scientific field setup (STARFLAG, Rome) used cameras 30 m above ground (a rooftop), flocks at an average of 100 m and up to 250 m, and 35 mm lenses on an APS-H body. That gives a field of view of about 45° × 30°, so the vertical FOV is narrower than the app's 46°. Ground-level video of roosts in Rome (Storms) used a fixed HD camera "in front of the roost". The app's ground camera at 37–100 m with a 46° vertical FOV is plausible for a close observer. With N ≥ 1,000, though, real flocks (long axis up to about 140 m) would overflow the frame at the near end of that range.

### Cited Findings
- **STARFLAG geometry:** apparatus "30 m above ground level"; "average distance of birds from the cameras was 100 m"; flocks had to be "smaller than 250 m" away for reconstruction; event 16-05 (2,630 birds) was "at approximately 240 m". Canon EOS-1D Mark II (3504 × 2336 px) with 35 mm lenses, 1/1000–1/250 s, 10 fps bursts of up to 8 s, stereo baseline 25 m, camera "tilt-up between 35% and 40%" (units as printed; probably degrees). — [Ballerini 2008](https://doi.org/10.1016/j.anbehav.2008.02.004) (arXiv full text)
  - Sim: a "STARFLAG" camera preset: eye 30 m up, look-up 35–40°, flock at 100 m.
- **Rome roost video:** high-definition video (JVC JY-HD10, 30 fps) from a fixed location in front of the roost by two operators. Recording ran "90 min before dusk… until nightfall", giving 16 h of footage over 110 sessions. — [Storms 2019](https://doi.org/10.1007/s00265-018-2609-0)
  - Sim: a full-evening timeline of about 90 min is the scientific observation window; compress it with a time-scale control.
- **Robot-falcon study:** ground camera plus a camera on the RobotFalcon. The ground camera "has to move" to follow the flock. — [Papadopoulou 2026](https://doi.org/10.1038/s42003-026-10173-4)
- **Viewing illusion:** ground observers "project the flock onto our tilted plane of vision, thus losing perception of its orientation and relatively thin aspect". — [Ballerini 2008](https://doi.org/10.1016/j.anbehav.2008.02.004)

### Inferences
- **FOV computation (mine, not sourced):** the EOS-1D Mark II sensor is about 28.7 × 19.1 mm (APS-H), a manufacturer value not verified here. With a 35 mm lens, horizontal FOV = 2·atan(14.35/35) ≈ 44.6° and vertical FOV = 2·atan(9.55/35) ≈ 30.5°. In landscape orientation, STARFLAG's vertical FOV was therefore about 30°. The app's 46° vertical (about 42° horizontal limit in the code) is wider vertically and similar horizontally.
- **Frame coverage:** a 46° vertical FOV spans 2·d·tan 23° = 0.85d, which is 31 m at d = 37 m and 85 m at d = 100 m. Rome flocks of 450–2,600 birds have long axes of about 21–143 m and thickness 5–19 m (section 4). At d = 37 m, any flock above about 1,000 birds would overflow the frame. A d of 100–250 m better matches both the scientific footage and N ≥ 1,000.
- For whole-murmuration scenes (10⁴–10⁵ birds, hundreds of metres across), a realistic observer distance is several hundred metres. That is beyond the app's current range and implies impostor rendering for distant birds.

### Gaps
- No systematic data on typical public or broadcast murmuration video (distance, focal length). That would need an image-metadata survey (for example, EXIF from the Goodenough photo submissions, which were not published).
