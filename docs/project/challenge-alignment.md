# Alignment with the MODIS/VIIRS challenge

Reviewed 6 November 2026 against source `e97d49f`. The instrument is **VIIRS**. The official title is [Harmonization of MODIS and VIIRS Hot Spots](https://www.spaceappschallenge.org/2026/challenges/modis-and-viirs-hot-spots/).

The indexed official summary was available; the full page returned HTTP 502 during this review. A [local organizer mirror](https://hackathlone.com/challenges/modis-and-viirs-hot-spots) corroborated the brief. This is an assessment of the verified summary, not a certification against an unseen resource sheet or submission rules.

The task centers on comparable hotspot history, a geographic burning-activity calendar and exploration of patterns and unusual periods for monitoring audiences. FireSense addresses that core through a regional reference-sensor reconstruction.

| Capability | Delivered implementation | Qualification |
|---|---|---|
| Harmonize instrument records | Separate MODIS configurations, B1 ratios, NOAA-20 adjustment and source provenance | Holdout performance and uncertainty must retain their revision/target context |
| Calendar and historical exploration | Weekly calendar, time series, comparison and CSV | Modeled/adjusted counts are not additional observed fires |
| Area and spatial exploration | Named divisions/states, boundary clicks and cell map | Loaded geography is regional; arbitrary polygons do not download new data |
| Unusual conditions and periods | Weekly anomaly scoring and ranked periods | Whole-season anomaly work remains planned |
| Agricultural context | Cropland share and qualified seasonal fallback | Not a verified classifier of fire causes |
| Monitoring use | Seasonal/current status and record-end labels | Historical planning support; not demonstrated operational early warning |
| Web delivery | React and live FastAPI on Render | Snapshot/static fallback retired |

Global motivation in the brief does not by itself establish a mandatory globally populated demo. State the regional scope explicitly. Likewise, forecasting is not treated as a verified mandatory requirement; disabled alerts are preferable to unsupported prediction claims.

The principal gap is **validity evidence**, not a missing model family: saved conditional interval coverage fails, and recent scientific repairs lack refreshed numerical validation. A focused user demo and observed user feedback would also strengthen the hackathon submission.

For the evidence ledger, provisional judging rubric and honest rating, read the [dated assessment](review-2026-11-06.md). Planned slides, story mode, broader coverage or scientific checks earn no delivery credit until completed. Older plan figures remain historical planning context, not current validation.
