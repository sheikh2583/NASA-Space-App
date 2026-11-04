# Coverage review: burning-month candidate gaps (card T05)

From `data/interim/coverage_audit/candidate_gaps.csv` (audit run 2026-11-04, commit `2bd2d47`). A candidate is a pass with zero SNPP detections in our cells while a reference satellite saw some. Burning months: Punjab Apr-May and Sep-Nov; Bangladesh Nov-Apr. Candidates are never excluded automatically.

| Date (local) | Region | Pass | Reference | Ref. detections | Verdict |
|---|---|---|---|---:|---|
| 2012-03-25 | BD | D | Aqua | 137 | already in registry (snpp-2012-03-24-outage) |
| 2012-03-26 | BD | D | Aqua | 130 | already in registry (snpp-2012-03-24-outage) |
| 2012-03-28 | BD | D | Aqua | 91 | already in registry (snpp-2012-03-28-outage) |
| 2018-04-29 | BD | D | NOAA20 | 13 | unclear: no MODAPS row for this pass; NOAA20 saw only 13 detections, so a swath gap or a real absence is as likely as an outage |
| 2018-11-08 | BD | D | NOAA20 | 13 | unclear: no MODAPS row for this pass; NOAA20 saw only 13 detections, so a swath gap or a real absence is as likely as an outage |
| 2019-02-02 | BD | N | NOAA20 | 11 | unclear: no MODAPS row for this pass; NOAA20 saw only 11 detections, so a swath gap or a real absence is as likely as an outage |
| 2019-10-31 | PB | D | NOAA20 | 2755 | already in registry (snpp-2019-10-31-outage) |
| 2020-01-08 | BD | D | NOAA20 | 18 | unclear: no MODAPS row for this pass; NOAA20 saw only 18 detections, so a swath gap or a real absence is as likely as an outage |
| 2020-03-20 | BD | N | NOAA20 | 12 | unclear: no MODAPS row for this pass; NOAA20 saw only 12 detections, so a swath gap or a real absence is as likely as an outage |
| 2020-11-18 | BD | D | NOAA20 | 10 | unclear: no MODAPS row for this pass; NOAA20 saw only 10 detections, so a swath gap or a real absence is as likely as an outage |
| 2020-12-04 | BD | D | NOAA20 | 20 | unclear: no MODAPS row for this pass; NOAA20 saw only 20 detections, so a swath gap or a real absence is as likely as an outage |
| 2021-01-11 | BD | D | NOAA20 | 13 | unclear: no MODAPS row for this pass; NOAA20 saw only 13 detections, so a swath gap or a real absence is as likely as an outage |
| 2021-04-15 | PB | N | NOAA20 | 11 | unclear: no MODAPS row for this pass; NOAA20 saw only 11 detections, so a swath gap or a real absence is as likely as an outage |
| 2021-11-16 | BD | D | NOAA20 | 10 | unclear: no MODAPS row for this pass; NOAA20 saw only 10 detections, so a swath gap or a real absence is as likely as an outage |
| 2021-12-23 | BD | D | NOAA20 | 27 | unclear: no MODAPS row for this pass; NOAA20 saw only 27 detections, so a swath gap or a real absence is as likely as an outage |
| 2022-04-16 | BD | N | NOAA20 | 10 | unclear: no MODAPS row for this pass; NOAA20 saw only 10 detections, so a swath gap or a real absence is as likely as an outage |
| 2022-09-29 | PB | D | NOAA20 | 14 | unclear: no MODAPS row for this pass; NOAA20 saw only 14 detections, so a swath gap or a real absence is as likely as an outage |
| 2022-12-26 | BD | D | NOAA20 | 10 | unclear: no MODAPS row for this pass; NOAA20 saw only 10 detections, so a swath gap or a real absence is as likely as an outage |
| 2023-11-02 | PB | D | NOAA20 | 1904 | already in registry (snpp-2023-11-01-cdp) |
| 2023-11-27 | BD | D | NOAA20 | 20 | unclear: no MODAPS row for this pass; NOAA20 saw only 20 detections, so a swath gap or a real absence is as likely as an outage |
| 2023-12-13 | BD | D | NOAA20 | 20 | unclear: no MODAPS row for this pass; NOAA20 saw only 20 detections, so a swath gap or a real absence is as likely as an outage |
| 2023-12-24 | BD | D | NOAA20 | 17 | unclear: no MODAPS row for this pass; NOAA20 saw only 17 detections, so a swath gap or a real absence is as likely as an outage |
| 2024-04-25 | BD | N | NOAA20 | 15 | already in registry (snpp-2024-04-24-anomaly) |
| 2024-05-30 | PB | D | NOAA20 | 202 | already in registry (snpp-2024-05-30-gps) |
| 2024-05-31 | PB | D | NOAA20 | 160 | already in registry (snpp-2024-05-30-gps) |
| 2024-05-31 | PB | N | NOAA20 | 102 | already in registry (snpp-2024-05-30-gps) |
| 2024-09-26 | PB | D | NOAA20 | 15 | already in registry (snpp-2024-09-26-gps) |
| 2024-11-03 | PB | D | NOAA20 | 463 | already in registry (snpp-2024-11-02-gps) |
| 2024-11-04 | PB | D | NOAA20 | 423 | already in registry (snpp-2024-11-02-gps) |
| 2024-11-04 | PB | N | NOAA20 | 18 | already in registry (snpp-2024-11-02-gps) |
| 2024-11-05 | PB | D | NOAA20 | 259 | already in registry (snpp-2024-11-02-gps) |
| 2024-11-05 | PB | N | NOAA20 | 14 | already in registry (snpp-2024-11-02-gps) |
| 2024-11-06 | PB | D | NOAA20 | 259 | already in registry (snpp-2024-11-02-gps) |
| 2025-10-06 | PB | D | NOAA20 | 15 | unclear: no MODAPS row for this pass; NOAA20 saw only 15 detections, so a swath gap or a real absence is as likely as an outage |
| 2025-11-12 | PB | D | NOAA20 | 199 | already in registry (snpp-2025-11-11-l0) |
| 2025-11-12 | PB | N | NOAA20 | 13 | already in registry (snpp-2025-11-11-l0) |
| 2026-03-10 | BD | D | NOAA20 | 145 | already in registry (snpp-2026-03-09-viirs) |
| 2026-03-11 | BD | D | NOAA20 | 43 | already in registry (snpp-2026-03-09-viirs) |
| 2026-03-12 | BD | D | NOAA20 | 140 | already in registry (snpp-2026-03-09-viirs) |
| 2026-04-28 | PB | D | NOAA20 | 352 | already in registry (snpp-2026-04-28-viirs) |
| 2026-04-29 | PB | D | NOAA20 | 1061 | already in registry (snpp-2026-04-28-viirs) |
| 2026-04-30 | PB | D | NOAA20 | 748 | already in registry (snpp-2026-04-28-viirs) |
| 2026-04-30 | PB | N | NOAA20 | 11 | already in registry (snpp-2026-04-28-viirs) |
| 2026-05-01 | PB | N | NOAA20 | 23 | already in registry (snpp-2026-04-28-viirs) |
| 2026-09-20 | PB | N | NOAA20 | 10 | unclear: no MODAPS row for this pass; NOAA20 saw only 10 detections, so a swath gap or a real absence is as likely as an outage |
| 2026-10-13 | PB | D | NOAA20 | 34 | already in registry (snpp-2026-10-12-outage) |

"Unclear" rows have no outage in the MODAPS table, and the reference saw few fires, so they stay as they are.
