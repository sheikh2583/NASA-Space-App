# NOTES (ws1_harmonize)

## Decisions and assumptions
- Model works at cell-week level (prompt P1.2 said cell-day): daily cell counts are too sparse. write_harmonized splits weekly
  estimates into days by MODIS daily counts; a week with no MODIS detection books its estimate on the Monday.
- B0/B1 and LightGBM are fitted per satellite combination (terra_only, terra_aqua; decision 19). LightGBM learns Terra-only
  inputs by training every overlap row twice, once with Aqua zeroed.
- Method selection: evaluate.select_method picks B1 or LightGBM by mean Lin's CCC over the holdouts; on synthetic data B1 wins
  (the synthetic generator is a pure ratio). Rerun `python -m ws1_harmonize.run model` on real data: LightGBM may win there.
- Backward holdout is train 2015-2020 -> test 2012-2014, plus a drift-era check (train 2015-2020 -> test 2021+).
- Harmonized table is sparse; days with no operating sensor never appear (common.series turns them into NaN).

## Known issues
- Model step takes about 30 minutes on 2 CPU cores (16 LightGBM fits). `--reuse-metrics` skips the evaluation;
  `--quick` runs only the spatial and backward holdouts.

## AI assistance log (where AI tools helped)
- 2026-11-03: everything in this folder was written with Claude (AI assistant) at Sheikh's direction before the event, on synthetic data, and assigned to this workstream's owner. Review it before relying on it; rerun on real data.
