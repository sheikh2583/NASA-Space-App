---
id: T31
title: Truth checks against FIRMS itself (area API, no viewer)
kind: agent
owner: Samiul
authors: [Samiul]
phase: P0
size: S
needs: [T00]
requires: [real-data, secret:FIRMS_MAP_KEY]
branch: ws1/T31-truth-checks
touches: []
creates: [ws6_validation/truth_checks.py, ws6_validation/tests/test_truth_checks.py, ws6_validation/truth_checks.md]
checks: [CHECK-PLAN, "python -m pytest -q ws6_validation/tests/test_truth_checks.py"]
---
## Goal
Our headline numbers must survive a judge opening FIRMS. Compare three surprising numbers with what the FIRMS API
returns for the same box and dates.

## Context
- `ws3_anomaly/ingest/firms.py`:
  - `fetch_window(session, key, source, bbox, first, n_days)` calls the FIRMS area API, at most 10 days per call.
  - Error text can contain the key. **Wrap every call so the key never prints**: catch exceptions and re-raise
    `RuntimeError(str(e).replace(key, "***"))`.
- `common/grid.local_solar_date` and `common/grid.cell_id`; `data/processed/cells.parquet` (Punjab demo cells have
  `country == "PB"`).
- The Punjab demo box is lon 74.6-76.4, lat 29.8-31.2.
- Archive sources: `VIIRS_SNPP_SP` and `VIIRS_NOAA20_SP`. The current season needs `VIIRS_NOAA20_NRT`, because SNPP
  NRT ended on 2 Nov 2026.

## Steps
1. **`ws6_validation/truth_checks.py`:**
   - `firms_count(key, source, bbox, start, end)` sums the detections from `fetch_window` over windows of at most 10
     days.
   - `our_count(area_cells, start, end, sat)` sums `grid_daily.n_det` for that satellite over cells in the box and
     local solar dates in range.
   - `main()` runs the checks and writes `ws6_validation/truth_checks.md`. It reads the key from the environment or
     `.env` and never prints it.

   | Check | What | Expectation |
   |---|---|---|
   | a | SNPP, 15 Sep-1 Nov 2026, against our 455 | |
   | b | SNPP and NOAA-20 by day, 2-8 Nov 2024 | SNPP close to 0 on 3-6 Nov, NOAA-20 not |
   | c | SNPP season totals, 15 Sep-31 Dec of 2016 and of 2024 | Against `seasons[1].years` in `contracts/fixtures/punjab_season_profile.json` |

2. **Tests** (`test_truth_checks.py`), with no network: a fake fetch returns fixed frames. Check that windowing
   covers the range exactly, that the key never appears in raised errors, and that the report table is written.
3. Run `python -m ws6_validation.truth_checks` on the laptop.
4. Expect small differences:
   - we use local solar days and keep only our cells and vegetation-type fires;
   - the FIRMS box count includes everything in the box.

   For each difference over 10%, write one sentence of explanation in the report.
5. Run the checks, mark the card done, `split`, push and open the PR. Paste the table into the PR.

## Acceptance
- [ ] `truth_checks.md` has all three checks, with FIRMS value, our value, difference and verdict.
- [ ] No key appears anywhere: search the report for the first 6 characters of the key; there must be no match.

## Stop and ask if
- Check a differs by more than a factor of 2. That would point to a data gap in 2026.
