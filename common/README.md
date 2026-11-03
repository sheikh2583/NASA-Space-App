# common/ (owner: Samin; changes need Sheikh's OK)
Shared Python used by everyone. Nobody re-implements these. Files to create:

- series.py        weekly_series(harmonized, cells, region_ids=None, bbox=None, res='week')
                   -> week_start, value, lo, hi, modeled_share      (due H10)
- climatology.py   same-week quantiles (+/-2 week window), season helpers (Oct 1 to Sep 30)   (due H10)
- intervals.py     apply_interval(value, res, stratum, table) -> lo, hi                         (due H10)
- splits.py        2x2 degree spatial blocks (one-cell buffer), yearly folds, backward holdout,
                   calibration blocks; default labels block_id % 5 == 0 calib, == 1 test       (due H12)
- metrics.py       relative bias, RMSE on log1p, Spearman, Lin's CCC, coverage, interval score  (due H12)

Every function gets a docstring and a pytest test on tiny synthetic input.
