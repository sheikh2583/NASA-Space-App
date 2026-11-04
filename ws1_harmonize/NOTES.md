# NOTES (ws1_harmonize)

## Decisions and assumptions
- Model works at cell-week level (prompt P1.2 said cell-day): daily cell counts are too sparse. write_harmonized splits weekly
  estimates into days by MODIS daily counts; a week with no MODIS detection books its estimate on the Monday.
- B0/B1 and the CUDA XGBoost candidate are fitted per satellite combination (terra_only, terra_aqua; decision 19). The learned model handles Terra-only
  inputs by training every overlap row twice, once with Aqua zeroed.
- Method selection averages held-out Lin's CCC across both Terra+Aqua and Terra-only configurations. B1 remains selected on current real data; CUDA fitting does not force the candidate to win. Public `model` commands require CUDA, including direct module execution.
- Backward holdout is train 2015-2020 -> test 2012-2014, plus a drift-era check (train 2015-2020 -> test 2021+).
- Harmonized table is sparse; days with no operating sensor never appear (common.series turns them into NaN).

## Known issues
- Use [GPU estimates](../docs/results/gpu-training-times.md) for measured evidence and planning ranges. `--quick` runs spatial/backward holdouts; full runs add temporal/drift-era checks. Internal metric reuse is valid only with unchanged input and fitting settings.

## AI assistance log (where AI tools helped)
- 2026-11-03: everything in this folder was written with Claude (AI assistant) at Sheikh's direction before the event, on synthetic data, and assigned to this workstream's owner. Review it before relying on it; rerun on real data.
