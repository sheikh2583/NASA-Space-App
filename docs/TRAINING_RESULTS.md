# Full real-data training — 4 November 2026

Completed at 12:29 Asia/Dhaka with:

```powershell
.venv\Scripts\python scripts\run_pipeline.py
```

This was a full run without `--quick`. All pipeline stages completed with exit code 0.

## Inputs and corrected preprocessing

- 4,336,082 vegetation/NRT detections from the downloaded FIRMS archives and recent files, through 2 November 2026.
- All 2,098,157 Suomi-NPP detections normalize to VIIRS, with no missing confidence values.
- 2,532 retained administrative grid cells, with zero missing administrative IDs. India boundaries are restricted to Punjab, Haryana, and Delhi.
- The weekly training panel contains 3,196,732 rows across 2,354 active cells and 1,358 weeks.
- Land cover uses the local MCD12C1 HDF; weather uses the completed NASA POWER cache.

## Model selection

Six holdouts were evaluated: spatial blocks, temporal 2019–2021, temporal 2022–2024, temporal 2025–2026, backward 2015–2020 to 2012–2014, and drift era 2015–2020 to 2021 onward. Each also reports a Terra-only input check separately.

| Candidate | Mean held-out Lin's CCC | Selected |
|---|---:|---|
| Per-region/month ratio B1 | 0.9417 | Yes |
| LightGBM | 0.9351 | No |

CCC measures agreement, not classification accuracy. The chosen method is recorded in `data/interim/sheikh/method.json`; B1 parameters and comparison LightGBM models are saved alongside it.

## Outputs and verification

- 3,565,100 out-of-fold predictions: 2,383,920 train, 856,240 calibration, and 324,940 test rows. Both satellite-input combinations are represented.
- 778,256 harmonized rows in `data/processed/harmonized.parquet`.
- Nominal 90% interval coverage: 91.6% weekly and 93.7% monthly on held-out totals.
- 14,927 region-week anomaly rows, 442 critical periods, and weather associations for 11 regions.
- Outlook skill is demonstrated in 4 of 11 regions; other regions retain the no-demonstrated-skill status.
- Data QA: 7 tests passed. API contracts: 17 passed. End-to-end flows: 4 passed. Shared-library QA: 16 passed. The before/after-2012 flag-rate check passed. All five QA groups passed.
- The focused ingestion/platform/harmonization regression suite passed all 16 tests during this run.

Local reports are `results/latest.md` and `results/latest.json`. Detailed metrics are in `data/processed/validation/` and `data/interim/sheikh/metrics.csv`. Downloaded inputs and generated models/results remain outside Git.

## Remaining human checks

Compare representative periods with the FIRMS viewer and review the Bangla text before submission. Pre-2012 values are modeled estimates; weather relationships are associations. Whole unusually strong seasons may be flagged primarily at their edges. This completed training run does not close those scientific and presentation limitations.
