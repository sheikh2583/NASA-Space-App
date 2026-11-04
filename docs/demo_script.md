# Demo script (3 minutes) and slide outline

Owner: Samiul. Draft written with an AI assistant; time it aloud and edit. Every number on a slide must come from a
file in data/processed/validation/ (rerun the pipeline before recording so every number matches the latest real-data build).

## Demo path (2:30)
| Time | Screen | Say |
|---|---|---|
| 0:00 | App home, map of South Asia | "Fire managers in Bangladesh and Punjab ask one question: is this burning season normal? Two decades of satellite fire data exist, but split across sensors that can't be compared directly. We joined them into one calendar." |
| 0:20 | Click **Bangladesh demo** | "Draw any area, or pick one. Here is a district-sized area in central Bangladesh." |
| 0:30 | **Current status** card | Audience 1, early warning and responders: "Right now: the level, how this week compares with the same week in past years, and the date the data runs through. This uses NOAA-20 near-real-time data." |
| 0:50 | **Calendar** heatmap | Audience 2, scientists: "Rows are years, columns are weeks. Hatched cells before 2012 are modeled from MODIS; solid cells are observed by VIIRS. Rings mark unusual weeks." Point at the 2012 seam. |
| 1:15 | **Series chart** with band | "Modeled years carry a 90% band, tested on areas we held out. The second line marks where Suomi NPP ended on 2 November 2026." |
| 1:35 | Click **Punjab demo**, then the top **critical period** (October–November) | Audience 3, land managers: "Punjab's paddy-residue season. Periods are ranked and tagged as agricultural when most fires fall in cropland. Selecting one recolours the map: this is where it burned." |
| 2:05 | **Associated conditions** | "Weather patterns that go along with burning. These are associations, not causes, and we say so on screen." |
| 2:15 | **Validation** tab | "Every claim has a validation piece: held-out accuracy, band coverage, drift checks, and forecast skill. Where the forecast shows no skill, we don't show a forecast." |
| 2:30 | Toggle **বাংলা** | "Everything is in Bangla too." |

**Backup path:** if the API is down, the app loads the static fallback automatically; say "this is the saved copy" and continue.

## Slides (8)
1. **The problem**: two decades of fire records, split across MODIS and VIIRS; Suomi NPP ended 2 Nov 2026, so the split now runs across three satellites.
2. **Our approach**: one series in Suomi NPP terms, labeled observed, adjusted or modeled (pipeline diagram from docs/PIPELINE.md).
3. **The app**: map, status card, calendar, critical periods (screenshots from Shammo).
4. **Three audiences, three scenarios**: current status now; historical pattern and the seam; agricultural burn season.
5. **Does it hold up?**: the method chosen and why (held-out CCC), band coverage, drift flags (validation pieces).
6. **Limits**: modeled before 2012, associations not causes, South Asia demo, outlook may show no skill.
7. **What's next**: global coverage, more regions, NOAA-21, burned-area comparison.
8. **Team**, data credits (NASA FIRMS, geoBoundaries, MODIS land cover, CHIRPS, NASA POWER) and AI-use disclosure.
