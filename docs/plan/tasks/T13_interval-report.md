---
id: T13
title: Interval report by stratum (measurement only)
kind: agent
owner: Samin
authors: [Samin, Shammo]
phase: P1
size: M
needs: [T00]
requires: [real-data]
branch: ws1/T13-interval-report
touches: [ws4_outlook/conformal.py, ws4_outlook/run.py, ws5_frontend/src/components/Pages.tsx,
          ws5_frontend/src/i18n/en.json, ws5_frontend/src/i18n/bn.json, ws5_frontend/public/demo/areas.json]
creates: [ws4_outlook/interval_report.py, ws4_outlook/tests/test_interval_report.py]
checks: ["CHECK-PLAN", "python -m pytest -q ws4_outlook/tests/test_interval_report.py", "CHECK-FILES", "CHECK-WEB"]
human_checks: [CHECK-QA]
---
## Goal
Overall band coverage is 91.6% weekly and 93.7% monthly for nominal 90%. A statistics-minded judge will ask where
the bands fail. Measure coverage and interval score by area size, magnitude, season and satellite combination. This
card changes no band.

## Context
- `ws4_outlook/conformal.py`:
  - `_aggregate_samples(oof, cells, split, n, res, rng)` draws random rectangles of cells and random weeks or months
    from `predictions_oof.parquet` rows of one split (`train`, `calib` or `test`).
  - **It keeps only `sat_combo == "terra_aqua"`.**
  - `apply_interval_many` applies the table.
- `common.metrics.coverage(y, lo, hi)` and `common.metrics.interval_score(y, lo, hi, alpha)` exist.
- `ws4_outlook/run.py` `piece(producer, metrics, limitations)` writes `data/processed/validation/<producer>.json`.
  `/meta/validation` keys pieces by `producer`, and the snapshot copies them.

## Steps
1. In `conformal.py`, give `_aggregate_samples` two keywords:
   - `sat_combo="terra_aqua"`, used in the row filter;
   - `max_side=10`, used as `rng.integers(1, max_side + 1, 2)` instead of `rng.integers(1, 11, 2)`.

   Also add a column `n_cells = h * w` (the rectangle drawn) to the returned frame. With the defaults, the generator
   must be consumed exactly as before, so `build_table`'s output is byte-identical. Rectangles stay inside one
   holdout block (2 × 2 degrees, so at most 20 × 20 = 400 cells).
2. **New `ws4_outlook/interval_report.py`**, `report(oof, cells, table, n=4000, seed=7) -> dict`:
   - For `res` in (week, month) and `sat_combo` in (terra_aqua, terra_only), draw test-split samples, apply the
     table, and compute per stratum: `n`, `coverage`, `interval_score` (alpha 0.1), the median relative width
     `(hi - lo) / max(y, 1)`, and, for `y == 0` rows, `zero_covered` (the share whose band includes 0).
   - Use `max_side=20` for the report so that large areas are sampled.
   - Strata:
     - area size: `n_cells` 1-10, 11-50, 51-100, 101-400;
     - magnitude: `y == 0`, then the quartiles of `y > 0`;
     - season: q1-q4, from `common.series.season_label`;
     - satellite combination.
   - Return `{"rows": [...], "nominal": 0.9}`.
   - `terra_only` rows may be few (Nov 2000-Jul 2002). Report n honestly; a stratum with `n < 30` gets
     `"note": "too few samples"`.
3. Add `step_interval_report()` to `run.py`, registered as `"interval_report"`. It writes
   `piece("intervals_by_stratum", report(...), [limitations])`. The limitations say: test blocks only; terra_only
   from a short period; width is a diagnostic, not a target.
4. **Tests** (`test_interval_report.py`), on synthetic OOF data built in the test, using the column names from
   `contracts/parquet_schemas.json` `predictions_oof` plus `cells`. When truth is drawn from the band's own
   distribution, overall coverage is 0.85-0.95 at n ≥ 2000; the interval score is finite; every requested stratum
   appears.
5. **Sheikh runs (human-only; `ws4_outlook.run` is a pipeline stage module):**
   `python -m ws4_outlook.run interval_report`, then `python scripts/workflow.py validate`. Either do it at his next
   training run (H02 or H03), or ask him now. Don't run them yourself. Until the piece exists, the UI shows nothing
   for it.
6. **UI** (`Pages.tsx` `ValidationPage`). Add a table "Where the bands hold" from `pieces.intervals_by_stratum`,
   with columns stratum, n, coverage and interval score. Rows with coverage under 0.85 get the class `warn`. Add
   i18n keys `validation.by_stratum` and `validation.by_stratum_note`.
7. Once the piece exists, republish the legacy snapshot with `python scripts/export_hosted_demo.py`. Run the checks,
   mark the card done, and hand over for commit. Paste the five weakest strata into the hand-over, or "pending
   Sheikh's run".

## Acceptance
T46 supersedes the old area-count and Terra-only descriptions: n_cells is unique contributing
OOF cells, drawn_n_cells preserves h*w, and Terra-only OOF rows are overlap-era holdouts,
not observed truth for the pre-2012 record. Stop detection applies to every dimension.

- [ ] `build_table` output is unchanged: `interval_table.json` hash before = after, pasted into the PR.
- [ ] The new piece validates (CHECK-FILES) and appears on the Validation page in the snapshot build.
- [ ] Measured results are in the PR, with the command and date.

## Stop and ask if
- Coverage in a large stratum (n ≥ 500) is below 0.80. Report it; don't change the bands.
