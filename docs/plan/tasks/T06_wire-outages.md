---
id: T06
title: Wire verified outages into sensor_days and fill from NOAA-20 (code and tests)
kind: agent
owner: Sheikh
authors: [Sheikh, Sattyam, Samin]
phase: P1
size: L
needs: [T05]
requires: [real-data]
branch: ws1/T06-wire-outages
touches: [ws2_platform/sensors.py, ws2_platform/tests/test_platform.py, common/series.py, common/tests/test_common.py,
          ws1_harmonize/run.py, ws1_harmonize/tests/test_harmonize.py, contracts/parquet_schemas.json,
          docs/project/contract-changes.md]
creates: [ws2_platform/tests/test_sensors_outages.py]
checks: [CHECK-PLAN, CHECK-PY, CHECK-SMOKE]
---
## Goal
Take verified outage days out of the record and the training ratios, and fill them from NOAA-20 where it exists. This
is the most important validity fix (`docs/specs/I8_COVERAGE.md`, sections 4-5, as decided in T05).
- **This card writes and tests the code only.** Sheikh runs the full training (H02).
- The agent then reports the results (T40).

## Context
- `ws2_platform/sensors.py` `sensor_days(grid, end=None)`:
  - marks each satellite operating from its first to its last data day;
  - applies `common.regions.OUTAGES`.
  - **Keep `common.regions.OUTAGES`**: `tools/synth_firms.py` uses it.
- `ws2_platform/coverage.py` already has `load_registry`, `pass_windows`, `affected_passes`, `day_table` and
  `excluded`.
- `common/series.py` `day_sources()` returns:
  - `observed_viirs` on SNPP days;
  - `adjusted_from_noaa20` only on or after `SNPP_CUTOFF`;
  - otherwise `modeled_from_modis`.
- `ws1_harmonize/write_harmonized.py` `assemble()` maps every day through `day_sources`. Changing `day_sources`
  therefore makes outage days use `n20 * n20_ratio` automatically.
- Pipeline stage names (`scripts/run_pipeline.py`): ingest, grid, sensors, cells, panel, v0, model, intervals, drift,
  v1, anomalies, outlook, validation, fixtures, fallback, qa.

## Steps
1. **Baseline for later comparison.** Copy `data/processed/validation/`, `data/interim/sheikh/metrics.csv`,
   `data/interim/sheikh/method.json` and `data/interim/sheikh/b1_params.pkl` to `data/interim/baseline_2026-11-04/`. This stays outside git; T40 compares
   against it.
2. **Contract.**
   - In `contracts/parquet_schemas.json`, add `coverage_days` with columns `sat` (string), `region` (string),
     `date` (date32), `overlap_D` (float32), `overlap_N` (float32), `event_ids` (string) and `verification`
     (string), and key (`sat`, `region`, `date`).
   - Append to `docs/project/contract-changes.md`: "approved (T05 decision): coverage_days added; sensor_days meaning extended;
     adjusted_from_noaa20 may appear before 2 Nov 2026".
3. **`ws2_platform/sensors.py`:**
   - New signature: `sensor_days(grid, end=None, coverage_days=None, threshold=0.25)`.
   - When `coverage_days` is given, for each (date, sat) where `coverage.excluded(rows_for_that_day, threshold)` is
     true in any region: `operating=False` and `note=f"outage: {event_ids} ({verification})"`.
   - Use only rows whose `verification` contains no `transcribed` and no `rejected`.
   - `main()` gains `--registry` (default `common/outages.yaml`), `--threshold` (default: the value in the T05 decision) and
     `--coverage-out` (default `data/processed/coverage_days.parquet`).
   - It reads `detections.parquet` and `cells.parquet`, and builds pass windows, `affected_passes` and `day_table`.
     It writes `coverage_days.parquet` with `tools.verify_files.write_parquet_contract` and passes the table to
     `sensor_days`.
4. **`common/series.py` `day_sources`:**
   - On a day with no SNPP operation, before `SNPP_CUTOFF`, where NOAA20 is operating, return `ADJUSTED`.
   - Everything else stays as it is.
5. **Tests:**
   - New `ws2_platform/tests/test_sensors_outages.py`:
     - an outage day becomes non-operating with the event id in `note`;
     - a `transcribed` row changes nothing;
     - a 0.1 overlap is kept at threshold 0.25 and excluded at threshold 0.
   - `common/tests/test_common.py`: 4 Nov 2024 gives `adjusted_from_noaa20` when SNPP is off and NOAA20 on; a 2015
     outage day gives `modeled_from_modis`.
   - `ws1_harmonize/tests/test_harmonize.py`: in a tiny assemble case, SNPP is off for a day and NOAA20 has 10
     detections. The result has `value_count == 10 * ratio` and `source == "adjusted_from_noaa20"`.
   - The existing `test_sensor_days_marks_snpp_cutoff_and_outages` must still pass unchanged.
6. **Version** (`ws1_harmonize/run.py`).
   - In `step_v1`, change `version = "v1-" + choice["method"]` to `version = "v1-" + choice["method"] + "-cov1"`.
   - In `step_model`, right after `choice = evaluate.select_method(table)`, add
     `choice["outage_registry"] = registry_hash()`. `registry_hash()` runs
     `git rev-parse HEAD:common/outages.yaml` with `subprocess.run(..., capture_output=True, text=True)` and returns
     the stripped output, or `"unknown"` when git fails.
7. Run the checks, mark the card done, `split`, push and open the PR. In the PR, tell Sheikh: "After merging, run
   card H02 (full training)."

## Acceptance
- [ ] All new tests pass in CI, without data, and the existing sensor-days test is unchanged.
- [ ] Running `python -m ws2_platform.sensors` on the laptop writes `coverage_days.parquet` and prints how many
  (date, sat) rows became non-operating. Paste that into the PR; it should match the chosen threshold's count in
  `docs/specs/I8_AUDIT_RESULTS.md`.
- [ ] No full training run in this card.

## Stop and ask if
- The non-operating count differs from the audit's count by more than 5%.
