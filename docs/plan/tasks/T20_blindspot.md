---
id: T20
title: Overpass blind-spot indicator (are fires moving out of satellite view?)
kind: agent
owner: Monazir
authors: [Monazir, Shammo]
phase: P2
size: M
needs: [T00]
requires: [real-data]
branch: ws1/T20-blindspot
touches: [ws5_frontend/src/components/Pages.tsx, ws5_frontend/src/i18n/en.json, ws5_frontend/src/i18n/bn.json,
          ws5_frontend/public/demo/snapshot.json]
creates: [ws3_anomaly/blindspot.py, ws3_anomaly/tests/test_blindspot.py]
checks: [CHECK-PLAN, CHECK-PY, CHECK-QA, CHECK-FILES, CHECK-WEB, CHECK-SNAP]
---
## Goal
- Punjab's paddy-season detections are falling 58% per decade, measured on the snapshot.
- NASA has reported that burning may have moved later in the **day**, after the afternoon polar passes.

Test with data we already have whether the falling counts could partly be fires out of satellite view, and say
honestly what the data shows. This is our most original scientific point.

## Context
- `data/processed/detections.parquet` has `sat`, `acq_date`, `acq_time` (UTC HHMM), `lat`, `lon` and `daynight`.
- Nominal local overpass times:

  | Satellite | Day pass | Night pass |
  |---|---|---|
  | Terra | about 10:30 | about 22:30 |
  | Aqua | about 13:30 | about 01:30 |
  | Suomi NPP | about 13:30 | about 01:30 |

- Terra's and Aqua's orbits have drifted in recent years, so **measure** each satellite's actual median local
  overpass time per year (UTC + lon/15) rather than assuming the nominal times.
- Season windows and season years come from `ws4_outlook.season_profile` (`SEASON_WINDOWS`, `Season.bounds`).
- Demo region membership: the cell's `country` in `cells.parquet` (`common.grid.cell_id(lat, lon)`).

## Steps
1. **`ws3_anomaly/blindspot.py`,** `blindspot(det, cells, area: str, season: Season) -> dict`. Per season year
   (2003 onward, the Aqua era) it computes:
   - each satellite's median local solar hour for D and N detections;
   - the counts Terra-D, Aqua-D, Terra-N, Aqua-N, SNPP-D and SNPP-N;
   - **R1** = Terra-D / Aqua-D (morning against early afternoon);
   - **R2** = (Terra-N + Aqua-N) / all MODIS;
   - **R3** = SNPP-N / all SNPP (2012 onward).
2. **Trends.** Theil-Sen (`scipy.stats.theilslopes`) of R1, R2 and R3 against year, with 95% intervals. Do the same
   for each satellite's median overpass hour.
3. **Verdict** (coded rules; store the text in `interpretation`):
   - `confounded_by_orbit_drift` if Terra's or Aqua's median day-pass hour moved by 20 minutes or more between the
     first and last 3 years.
   - Otherwise `consistent_with_later_burning` if R1's slope is negative **and** (R2's or R3's slope is positive),
     each with an interval that excludes 0.
   - Otherwise `no_evidence_of_shift` if all three intervals include 0.
   - Otherwise `inconclusive`.

   The text always says "consistent with", never "proves".
4. **Tests** (`test_blindspot.py`), with synthetic detections built in the test:
   - a planted shift of the burning hour from 11:00 to 15:30 over 15 years, with satellites sampling fixed hours,
     gives R1 falling and `consistent_with_later_burning`;
   - the same plus a planted Terra drift of 40 minutes gives `confounded_by_orbit_drift`;
   - no shift gives `no_evidence_of_shift`.
5. **Run.** Add a CLI, `python -m ws3_anomaly.blindspot`. It writes `data/processed/validation/blindspot.json` as a
   validation piece, with `schema_version`, `generated_at`, `producer: "blindspot"`, `metrics` (per area and season:
   the yearly table, the trends and the verdict) and `limitations`. The limitations include "polar orbiters sample
   two moments a day; this is indirect evidence".
6. **UI.** In `Pages.tsx` `ValidationPage`, add a block "Fires out of view?". Use a small Recharts line chart of R1
   and R2 by year for Punjab paddy (lazy-loaded like `SeriesChart`), plus the verdict sentence
   `t("blindspot.verdict_" + verdict)` and the limitations. Add the i18n keys in en and bn.
7. Run `python -m ws3_anomaly.blindspot`, then `python -m ws6_validation.qa` and
   `python scripts/export_hosted_demo.py`. Run the checks, mark the card done, `split`, push and open the PR. Paste
   the verdicts and the overpass-hour table into the PR.

## Acceptance
- [ ] The three synthetic tests pass.
- [ ] `blindspot.json` validates (CHECK-FILES) and shows on the Validation page in the snapshot build.
- [ ] The verdicts are in the PR under Measured, with the overpass-drift numbers.

## Stop and ask if
- The verdict for Punjab paddy is `confounded_by_orbit_drift`. Report it and don't spin it; Samiul adapts the story
  in T23.
