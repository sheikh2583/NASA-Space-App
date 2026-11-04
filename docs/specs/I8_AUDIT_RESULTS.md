# I8 audit results: what the outage registry would change

**Measured, 2026-11-04**, by `python -m ws2_platform.coverage` (read-only) at commit `2bd2d47`, on the registry checked against NASA's MODAPS table in card T32. Nothing in `data/processed/` was changed.

## Summary

- registry_events: 80
- registry_unchecked: 0
- affected_region_days: 216
- contradictions: 1
- candidate_gaps: 77
- candidate_gaps_not_in_registry: 34
- would_flip_sensor_days: {'0': 112, '0.25': 105, '0.5': 98, '1': 90}
- pass_windows_measured: 20

## Pass windows (local solar time, all measured)

| Satellite | Region | Pass | From | To | Detections used |
|---|---|---|---|---|---:|
| Aqua | BD | D | 12:37 | 15:10 | 93,004 |
| Aqua | BD | N | 01:10 | 03:27 | 935 |
| Aqua | PB | D | 12:33 | 15:12 | 351,623 |
| Aqua | PB | N | 01:15 | 04:06 | 915 |
| NOAA20 | BD | D | 12:13 | 14:09 | 109,446 |
| NOAA20 | BD | N | 00:42 | 02:37 | 11,052 |
| NOAA20 | PB | D | 12:01 | 14:05 | 656,112 |
| NOAA20 | PB | N | 00:42 | 02:47 | 19,872 |
| NOAA21 | BD | D | 12:14 | 14:10 | 45,082 |
| NOAA21 | BD | N | 00:43 | 02:36 | 4,796 |
| NOAA21 | PB | D | 12:01 | 14:05 | 159,016 |
| NOAA21 | PB | N | 00:44 | 02:49 | 8,311 |
| SNPP | BD | D | 12:10 | 14:10 | 206,779 |
| SNPP | BD | N | 00:43 | 02:38 | 20,278 |
| SNPP | PB | D | 12:02 | 14:07 | 1,270,094 |
| SNPP | PB | N | 00:43 | 02:50 | 31,057 |
| Terra | BD | D | 09:17 | 11:33 | 8,541 |
| Terra | BD | N | 20:27 | 22:58 | 3,839 |
| Terra | PB | D | 09:18 | 11:35 | 96,466 |
| Terra | PB | N | 20:15 | 22:52 | 3,894 |

Every SNPP, NOAA-20, Terra and Aqua window in BD and PB is `measured`; none fell back to a default.

## What each threshold would change (measured, 2026-11-04)

A sensor-day becomes non-operating when an outage covers at least this share of any pass window. Overlap weeks are Monday-Sunday weeks in which every satellite of the pair operated all 7 days (as in `ws1_harmonize/model.py`); a week is lost when one of its days would flip.

| Threshold | Sensor-days that flip | SNPP+MODIS overlap weeks lost (of 770) | SNPP+NOAA-20 overlap weeks lost (of 448) |
|---|---:|---:|---:|
| any overlap | 112 | 60 (7.8%) | 37 (8.3%) |
| 0.25 | 105 | 54 (7.0%) | 36 (8.0%) |
| 0.5 | 98 | 47 (6.1%) | 32 (7.1%) |
| 1.0 | 90 | 41 (5.3%) | 29 (6.5%) |

## Contradictions

One row: SNPP, Punjab, night pass of 5 Aug 2026 (local), inside `snpp-2026-08-03-viirs`, with 1 detection in our cells. The registry entry matches the MODAPS table exactly (3 Aug 02:00 to 6 Aug 16:30 UTC). The table calls this a "VIIRS Anomaly Impact" period, i.e. degraded data rather than a total loss: FIRMS still published 5 low-FRP nominal-confidence SNPP detections on 4-5 Aug (UTC). So the registry is right and the pass is not empty on that day; excluding it removes one real detection, which is the safe side.

## Burning-month candidate gaps

46 candidates in the burning months (Punjab Apr-May and Sep-Nov, Bangladesh Nov-Apr): 27 are already in the registry and 19 are unclear (no MODAPS row; NOAA-20 saw only 10-27 detections). None is added automatically. Details: `ws6_validation/coverage_review.md`.

## Recommendation: threshold 0.25

Use **0.25** (measured, 2026-11-04). It flips 105 sensor-days: it drops days on which at least a quarter of a pass window was lost, which would visibly undercount, but ignores single 6-minute granule blips. Compared with excluding any overlap, it keeps 6 more SNPP+MODIS training weeks; compared with 1.0 it removes 15 more partly-dark days. The fit loses 54 of 770 SNPP+MODIS overlap weeks (7.0%) and 36 of 448 SNPP+NOAA-20 weeks (8.0%), a small share; the differences between thresholds are modest, so the choice is not fragile. The default in the spec stands.
