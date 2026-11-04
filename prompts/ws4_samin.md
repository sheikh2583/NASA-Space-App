# Prompt pack: Samin (Team Member 4), shared library, uncertainty and outlook
Folders: common/ and ws4_outlook/

## P4.1 series.py (H0-6)  HANDOFF
Prompt: "Write common/series.py: weekly_series(harmonized, cells, region_ids=None, bbox=None, res='week') aggregating cell values to AOI-week (Monday weeks) or month, returning week_start, value, lo, hi, modeled_share (fraction of the value from modeled rows). lo/hi come from common.intervals.apply_interval when a table is given, otherwise NaN. Docstrings and pytest tests on a tiny synthetic harmonized table."
Output: series.py + tests. HANDOFF: to Sattyam, Monazir, Sheikh (H10 at the latest).
Test: totals equal a direct sum; modeled_share is 0 on SNPP operating days; weeks are Monday-based on the local solar date.

## P4.2 climatology.py (H4-8)  HANDOFF
Prompt: "Write common/climatology.py: same_week_quantiles(weekly_df, q, window=2) over years with a +/-2 week window (ISO week 53 folded into 52; weeks with no operating sensor excluded); season helpers (season = Oct 1 to Sep 30, season_of(date), day_of_season); cumulative_by_season(weekly_df). Tests on a synthetic multi-year series."
Output: climatology.py + tests. HANDOFF: to Monazir, Sheikh.
Test: quantiles match a hand-computed example.

## P4.3 intervals.py (H6-10)  HANDOFF
Inputs: contracts/json_schemas/interval_table.schema.json.
Prompt: "Write common/intervals.py: apply_interval(value, res, stratum, table) -> (lo, hi): choose the most specific matching stratum, then the magnitude bin by value; lo = value x lo_mult, hi = value x hi_mult + hi_add. Fall back to stratum 'all' then to the widest entry. Tests including missing strata."
Output: intervals.py + tests. HANDOFF: to Sattyam, Monazir.
Test: lo <= value <= hi for sane tables; fallbacks work.

## P4.4 splits.py and metrics.py (H8-12)  HANDOFF
Prompt: "Write common/splits.py: 2x2 degree spatial blocks with a one-cell buffer, block_id derived deterministically from the block corner; labels block_id % 5 == 0 -> calib, == 1 -> test, else train; yearly temporal folds; backward holdout (train 2015-2020, test 2012-2014) and a drift-era fold (train 2015-2020, test 2021 onward). Write common/metrics.py: signed relative bias, RMSE on log1p, Spearman, Lin's CCC, empirical coverage, interval (Winkler) score. Tests: the same call returns the same labels; no calib or test row appears in a training set."
Output: splits.py, metrics.py + tests. HANDOFF: to Sheikh, Samiul.
Test: determinism and no-leakage tests pass.

## P4.5 Conformal intervals (H24-28)
Inputs: predictions_oof.parquet (Sheikh, H24).
Prompt: "Inspect current ws4_outlook/conformal.py before modifying it. Preserve calibration-only interval fitting, AOI aggregation semantics, held-out coverage, and interval contracts. A learned residual-scale model is a proposed experiment, not the current implementation; if justified, use common/compute.py with verified CUDA and separately compare held-out coverage and interval scores. Do not sum indicative cell intervals or impose arbitrary width targets. Use docs/TRAINING.md for execution."
Output: conformal.py, interval_table.json v1, coverage table.
Test: JSON validates; coverage within about 3 points of 90 percent, or the gap is reported plainly.

## P4.6 Drift (H26-30)  HANDOFF
Prompt: "Write ws4_outlook/drift.py: rolling region-year ratio of observed VIIRS to predicted; CUSUM on standardized scores; a classifier two-sample test between overlap-era and pre-2012 MODIS features giving an applicability flag. Write drift_flags.parquet (region_id, year, drift_flag, reason)."
Output: drift.py, drift_flags.parquet. HANDOFF (with interval_table v1): to Sheikh, Sattyam by H30.
Test: schema validates; a planted ratio shift is flagged.

## P4.7 Outlook floor (H12-24)
Inputs: harmonized v0 (H14).
Prompt: "Write ws4_outlook/outlook.py: outlook(weekly_df, bbox, as_of) returning season_to_date_percentile against previous seasons and expected_range q10/q50/q90 of cumulative activity at that week, using common.climatology. Use only data up to as_of. Status no_demonstrated_skill until the forecast is evaluated. Also return current_status {week_percentile, level none/watch/high, data_through, message}: the percentile of the latest complete week against same-week climatology (watch at the 80th percentile, high at the 90th), the date the data run through (from the NOAA-20 near-real-time feed), and a one-line plain-language message. current_status is core and is never cut."
Output: outlook.py (floor level) + tests.
Test: as_of never uses later data; schema validates.

## P4.8 Forecast, skill and alerts (H24-34)  HANDOFF
Inputs: weather anomalies (Monazir, H26).
Prompt: "Maintain CUDA XGBoost quantile fitting in outlook.py via common/compute.py with verified device placement. Evaluate leave-one-season-out, excluding the held-out season from training and climatology; report skill against climatology and persistence, bootstrap CIs, and pinball loss. Preserve no_demonstrated_skill when the CI fails to establish improvement, current-season context, alert gating, and outlook_region.json contracts. Check current feature availability at as_of before adding predictors; use docs/TRAINING.md for execution."
Output: outlook.py, alerts.py, outlook_region.json. HANDOFF: to Sattyam, Shammo.
Test: no leakage test; schema validates; status reflects the CI.

## P4.9 Validation pieces (H32-34; stretch H36)  HANDOFF
Prompt: "Write validation/intervals.json (coverage by land cover and season, mean width, interval score), validation/drift.json, validation/outlook_skill.json per contracts/json_schemas/validation_piece.schema.json, each with a plain-language limitations list. Stretch: validation/mcd64a1.json comparing monthly burned area (MCD64A1) with MODIS-only, VIIRS-only and harmonized series over the overlap period (Spearman and rank agreement of peak months)."
Output: validation pieces. HANDOFF: to Sattyam.
Test: schemas validate; every number traces to a computed table.
