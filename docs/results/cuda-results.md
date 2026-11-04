# CUDA verification — 4 November 2026

The native Windows CUDA path was exercised on real project data using an **RTX 4070 Laptop GPU, 8,188 MiB**, NVIDIA driver 592.82, XGBoost 3.2.0, `cuda:0`, and eight CPU helper threads. Harmonization count/FRP models, historical drift classifiers, and median quantile forecasts all completed actual GPU fits. Each fit checks the booster configuration and rejects CPU fallback.

See [CUDA operations](../science/cuda-pipeline.md) for setup, commands, device selection, and recovery. The RTX 3090 was not available for measurement. This implementation uses one selected local GPU; it does not distribute work across computers.

## Scientific correction and accepted outputs

The first full CUDA trial used the old Terra+Aqua-only selection score. XGBoost slightly exceeded B1 there (0.9438 versus 0.9417), but its Terra-only spatial CCC was about 0.287 versus B1's 0.848. The historical anomaly-seam QA then failed. That trial exited unsuccessfully; its outputs were rejected and the gate was preserved.

Selection now averages the six holdouts for **both Terra+Aqua and Terra-only input configurations**, since both are used in the reconstructed history. This change applies to either compute backend; ties favor B1.

| Candidate | Terra+Aqua mean CCC | Both configurations, selection mean CCC | Selected |
|---|---:|---:|---|
| B1 regional/monthly ratio | 0.9417 | 0.8855 | Yes |
| XGBoost CUDA | 0.9438 | 0.8696 | No |

The existing full six-holdout CUDA table was reused with unchanged panel and fitting configuration to repair selection. Out-of-fold B1 predictions and the final GPU comparison models were rebuilt, then all downstream stages were rerun from `intervals`. This was a **resumed validation run**, not a newly timed full pipeline after the repair.

Accepted outputs contain 778,256 harmonized rows and 14,927 anomaly rows, with 442 critical periods across 11 regions. Nominal 90% interval coverage is 91.6% weekly and 93.7% monthly. The before/after-2012 flag rates are 0.0312 and 0.0419, passing the unchanged seam gate. Forecast skill is demonstrated in 4 of 11 regions. B1 remains the deployed local harmonization method; CUDA execution does not establish that the GPU candidate is scientifically superior.

## Measured runtime

| Execution | Wall time | Interpretation |
|---|---:|---|
| Earlier CPU baseline | About 12 min 7 s | Historical complete run; LightGBM candidate, B1 selected |
| First CUDA trial | About 19 min 6 s across recorded stages | Full trial failed scientific QA; not an accepted benchmark |
| Corrected CUDA downstream run | 9 min 46 s | Starts at intervals; excludes ingestion, model selection, and repair |

The first CUDA model stage took 274 s, compared with the earlier CPU model stage's 399 s. Different learners, helper-thread counts, and machine load prevent attributing that difference solely to CUDA. The corrected CUDA outlook stage took 265 s; the earlier CPU outlook stage took about 19 s. Hundreds of tiny GPU fits incur substantial overhead. **No end-to-end CUDA speedup has been demonstrated.**

The accepted downstream execution recorded 399 verified CUDA fits: 135 drift classifiers and 264 quantile forecasts. Their combined measured fit wall time was 262.435 s, including matrix construction, transfers, and fitting; this is not a GPU-kernel profiler measurement. Harmonization fits are recorded in the initial trial and selection-repair logs separately.

Local evidence, relative to the repository root:

- Initial trial and original CPU backup: `results/runs/20261104-125554-037115/` and `data/runs/20261104-125554-037115/baseline/`.
- Rejected scientific artifacts: `data/runs/20261104-125554-037115/failed-cuda-trial/`.
- Selection-repair fit log: `results/runs/selection-repair-20261104/cuda-fits.jsonl`.
- Accepted downstream execution: `results/runs/20261104-131609-921795/execution.json` and its `cuda-fits.jsonl`.
- Current accepted science: `data/processed/validation/`, `data/interim/sheikh/method.json`, and `results/latest.md`.

The accepted execution report predates the final report-only placement fix: its `cuda_stages`/`cpu_stages` arrays list the whole pipeline. Its `start_stage`, actual `stages`, fit counts, and timings describe the resumed run correctly. Future reports list only the stages actually requested.

## Verification and handoff

- Full Python suite with real CUDA tests enabled: **77 passed**; one existing Starlette/httpx deprecation warning.
- Separate script/packaging/resume tests: **4 passed**.
- All five real-output QA groups passed (47 individual checks including the seam gate).
- Frontend: all six tests, translation checks, and snapshot production build passed.
- Optional dependency installation passed `pip check`. Windows PowerShell and Linux shell launcher syntax were checked; a fresh Linux environment was not executed.

The original CUDA implementation preserved the earlier public snapshot. The subsequent named-area UI update deliberately refreshed it from these accepted local outputs after QA and review, adding responses for all 11 administrative regions and the two examples. Future updates still require explicit export/review in [hosting](../guides/deployment.md). Raw data, trained models, run logs, and backups remain local and are excluded from the source ZIP.

The next performance work should batch or avoid repeated tiny forecast fits and profile CPU feature/anomaly operations. A larger GPU alone does not resolve launch overhead. Any optimization must repeat held-out evaluation and all scientific gates; do not force selection of the GPU candidate.
