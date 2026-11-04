# Current training results

The active training path uses CUDA. Read [CUDA results](cuda-results.md) for the GPU hardware verification, selection correction, accepted outputs, QA, and timing evidence. Read [training guide](../guides/training.md) to reproduce the supported workflow.

Current selected harmonization: **B1**, with selection CCC 0.8855 versus XGBoost CUDA 0.8696 across Terra+Aqua and Terra-only holdouts. All five scientific QA groups passed. The accepted downstream run recorded 399 verified GPU fits. A resumed downstream time must not be presented as full training time.

[GPU estimates](gpu-training-times.md) distinguish measured RTX 4070 evidence from the unmeasured RTX 3090 projection. The historical experimental comparison remains in [CUDA results](cuda-results.md) and Git history; the obsolete standalone CPU training report/instructions have been removed.

## Coverage correction (2026-11-04)

Full run with the verified outage registry (cards T05, T06; decision 24), by Sheikh on the RTX 4070 Laptop:
`scripts/train.ps1 -SkipQuick -Yes -Pack`, run `results/runs/20261104-211232-599349` (status passed, quick false,
start_stage null), about 23 minutes. QA 5 of 5 groups passed; `pytest -q` 211 passed, 2 skipped; `workflow.py smoke`
passed. Before = the outputs saved before the change (`data/interim/baseline_2026-11-04/` and the pipeline backup
`data/runs/20261104-203552-926195/baseline/`). Every number below: measured, from the named file, 2026-11-04.

**Selection** (`data/interim/sheikh/method.json`): method **B1 before and after**. Selection mean CCC: B1 0.8855 → 0.8900,
XGBoost CUDA 0.8696 → 0.8775. Registry recorded: `64c481c88c867875306b7035aeaa682a9548670f`.

**Holdout agreement** (measured, data/interim/{baseline_2026-11-04 vs sheikh}/metrics.csv, 2026-11-04). Holdout sets shrank because outage weeks leave the fit, so before and after are not
identical samples. ⚠ marks a drop of more than 0.01.

| Holdout | Method | CCC before | CCC after | Change | Weeks before → after |
|---|---|---:|---:|---:|---|
| backward 2015-2020 -> 2012-2014 | B1 | 0.9792 | 0.9789 | -0.0003 | 1,694 → 1,562 |
| backward 2015-2020 -> 2012-2014 | XGBoost CUDA | 0.9842 | 0.9875 | +0.0033 | 1,694 → 1,562 |
| backward 2015-2020 -> 2012-2014 (terra_only inputs) | B1 | 0.8033 | 0.8048 | +0.0015 | 1,694 → 1,562 |
| backward 2015-2020 -> 2012-2014 (terra_only inputs) | XGBoost CUDA | 0.9567 | 0.9697 | +0.0130 | 1,694 → 1,562 |
| drift era 2015-2020 -> 2021+ | B1 | 0.9679 | 0.9699 | +0.0020 | 3,333 → 2,959 |
| drift era 2015-2020 -> 2021+ | XGBoost CUDA | 0.9451 | 0.9544 | +0.0093 | 3,333 → 2,959 |
| drift era 2015-2020 -> 2021+ (terra_only inputs) | B1 | 0.8349 | 0.8403 | +0.0054 | 3,333 → 2,959 |
| drift era 2015-2020 -> 2021+ (terra_only inputs) | XGBoost CUDA | 0.8928 | 0.9267 | +0.0339 | 3,333 → 2,959 |
| spatial blocks | B1 | 0.9010 | 0.9173 | +0.0163 | 2,310 → 2,148 |
| spatial blocks | XGBoost CUDA | 0.9471 | 0.9637 | +0.0166 | 2,310 → 2,148 |
| spatial blocks (terra_only inputs) | B1 | 0.8482 | 0.8336 | -0.0146 ⚠ | 2,310 → 2,148 |
| spatial blocks (terra_only inputs) | XGBoost CUDA | 0.2872 | 0.2928 | +0.0056 | 2,310 → 2,148 |
| temporal 2019-2021 | B1 | 0.9846 | 0.9848 | +0.0002 | 1,716 → 1,672 |
| temporal 2019-2021 | XGBoost CUDA | 0.9863 | 0.9825 | -0.0038 | 1,716 → 1,672 |
| temporal 2019-2021 (terra_only inputs) | B1 | 0.9210 | 0.9246 | +0.0036 | 1,716 → 1,672 |
| temporal 2019-2021 (terra_only inputs) | XGBoost CUDA | 0.9490 | 0.9513 | +0.0023 | 1,716 → 1,672 |
| temporal 2022-2024 | B1 | 0.9631 | 0.9664 | +0.0033 | 1,727 → 1,540 |
| temporal 2022-2024 | XGBoost CUDA | 0.9417 | 0.9490 | +0.0073 | 1,727 → 1,540 |
| temporal 2022-2024 (terra_only inputs) | B1 | 0.7912 | 0.8185 | +0.0273 | 1,727 → 1,540 |
| temporal 2022-2024 (terra_only inputs) | XGBoost CUDA | 0.9105 | 0.9082 | -0.0023 | 1,727 → 1,540 |
| temporal 2025-2026 | B1 | 0.8542 | 0.8562 | +0.0020 | 1,034 → 869 |
| temporal 2025-2026 | XGBoost CUDA | 0.8582 | 0.8541 | -0.0041 | 1,034 → 869 |
| temporal 2025-2026 (terra_only inputs) | B1 | 0.7778 | 0.7849 | +0.0071 | 1,034 → 869 |
| temporal 2025-2026 (terra_only inputs) | XGBoost CUDA | 0.7769 | 0.7901 | +0.0132 | 1,034 → 869 |

**Coverage of the 90% bands** (`data/processed/validation/intervals.json`, all landcovers and seasons): weekly 0.916 → 0.934;
monthly 0.937 → 0.924. Both inside 0.85-0.97.

**Overlap weeks** (`b1_params.pkl`): SNPP+MODIS 770 → 716; SNPP+NOAA-20 448 → 412. These are exactly the 54 and 36 weeks
that `docs/specs/I8_AUDIT_RESULTS.md` predicted at threshold 0.25.

**November ratios** (`b1_params.pkl`, month 11):

| Region | B1 terra_aqua | B1 terra_only | NOAA-20 → SNPP |
|---|---|---|---|
| Punjab | 4.552 → 4.628 | 75.643 → 74.668 | 0.981 → 0.983 |
| Haryana | 4.605 → 4.634 | 62.450 → 60.654 | 0.965 → 0.955 |
| Dhaka | 13.285 → 12.959 | 50.786 → 49.597 | 0.921 → 0.935 |

**Non-operating days** (`data/processed/sensor_days.parquet`, notes starting "outage:"): 105 SNPP sensor-days, the same
as the audit's `would_flip_0.25`; `coverage_days.parquet` has 216 rows.

**Spec criterion A7, Punjab demo area** (API `full_history`, before = pre-correction backup):

| Week | Before | After | After band | Source after |
|---|---:|---:|---|---|
| 28 Oct 2024 | 1,218 (observed) | 1,495 | 1,215-1,776 | mixed, 18.7% filled |
| 4 Nov 2024 | 1,291 (observed) | 1,931 | 1,291-2,572 | mixed, 33.1% filled |

The SNPP outage of 2-6 Nov 2024 had made peak-season weeks look quiet; those days are now filled from NOAA-20 and
labelled, and the week of 4 Nov rises by about half.
