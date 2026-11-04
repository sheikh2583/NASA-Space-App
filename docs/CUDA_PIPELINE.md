# CUDA training pipeline

Measured hardware, selection correction, validation, and runtime limitations are recorded in [CUDA results](CUDA_RESULTS.md).

The supported Windows/Linux training path uses XGBoost 3.2.0 with `device=cuda:<id>`, histogram trees, quantized training matrices (`max_bin=63`), and verified device placement. Legacy LightGBM baselines remain internal for comparison/tests. This is a separately evaluated learned candidate, not a claim that the algorithms give identical results.

Official backend references: [XGBoost GPU support](https://xgboost.readthedocs.io/en/release_3.2.0/gpu/index.html) and [LightGBM installation](https://lightgbm.readthedocs.io/en/stable/Installation-Guide.html#build-cuda-version). LightGBM's CUDA backend does not support native Windows; changing its `device` parameter cannot fix the installed CPU-only library.

## What runs where

| Work | CUDA mode |
|---|---|
| Harmonization Poisson count fitting | XGBoost CUDA |
| Harmonization Tweedie FRP fitting | XGBoost CUDA |
| Learned-model prediction | XGBoost device set to selected CUDA device; DMatrix prediction |
| Historical applicability drift classifiers, three folds | XGBoost CUDA |
| Seasonal median quantile forecast fitting | XGBoost CUDA |
| B0/B1 baselines and method selection | CPU; B1 can still win |
| CSV/HDF/Parquet I/O, geospatial boundaries, weekly feature construction | CPU |
| Calibration sampling, anomaly statistics, weather bootstrap, API/UI export, QA | CPU |

GPU acceleration does not turn file/network access or Shapely operations into CUDA work. Small classifier/forecast fits can have more GPU overhead than CPU compute; measured end-to-end runtime is the performance criterion, not GPU utilization alone.

## Setup and click-to-run

Use the full Windows/Linux installer in [TRAINING.md](TRAINING.md), or install the complete manifest in an existing project environment:

```powershell
.venv\Scripts\python -m pip install -r requirements-cuda.txt
.venv\Scripts\python scripts\workflow.py gpu-check
```

Alternatively double-click `START_HERE.cmd`: option 1 installs the complete CUDA environment; option 12 verifies it; options 4 and 5 run quick/full CUDA training. Option 11 initializes UI development without requiring NVIDIA. Linux menu names match; macOS supports UI development only. The old CPU training action is removed.

The probe fits/predicts tiny models for all four pipeline objectives and checks every booster configuration for the requested CUDA device. Its result includes the compiled CUDA version and verified objectives. GPU detection or a successful import alone does not pass. A request that becomes CPU raises an error. Probe fits are excluded from pipeline audit logs, including direct probes run in a shell with an existing log setting. No automatic dependency installation occurs during training.

For Python/CUDA dependencies without frontend installation or a Node/npm requirement, use `scripts\setup.ps1 -TrainingOnly` or `bash scripts/setup.sh --training-only`. Full setup also checks Vite's standard development/preview ports before npm installation to avoid Windows native-module locks.

## Commands

```powershell
# Default training workflow now selects CUDA; all holdouts remain enabled unless --quick is given.
.venv\Scripts\python scripts\workflow.py prepare --backend cuda
.venv\Scripts\python scripts\workflow.py train --backend cuda --threads 8
.venv\Scripts\python scripts\workflow.py train --backend cuda --quick --threads 8

# Select another locally installed GPU by its nvidia-smi index.
.venv\Scripts\python scripts\workflow.py train --backend cuda --gpu-id 1 --threads 8

```

Both the lower-level `scripts/run_pipeline.py` and workflow training/prepare default to CUDA with eight CPU helper threads. `--threads` controls host-side/library workers; it does not select a number of GPU cores.

Public workflow and pipeline commands accept only CUDA. Direct model, drift, outlook, and readiness entrypoints also select CUDA, default to eight helper threads, and reject an inherited `FIRESENSE_BACKEND=cpu`. Set `FIRESENSE_GPU_ID` and `FIRESENSE_THREADS` consistently when resuming. Internal reference functions remain available to regression tests; they are not a supported training workflow. Do not mix historical method-selection records with CUDA-generated downstream results.

## Models, provenance, and recovery

Before a CUDA run changes pipeline outputs, it copies the previous processed outputs and harmonization artifacts under `data/runs/<timestamp>/baseline/`. This is a local recoverable backup, not a Git artifact. Avoid simultaneous runs because working output paths are still shared.

Run execution reports are saved under `results/runs/<timestamp>/execution.json`. They include backend/device/library/hardware details, quick/full mode, stage timings and exit codes, backup path, and the number and total duration of verified CUDA fits. `cuda-fits.jsonl` records purpose, objective, row/feature counts, rounds, device, and measured duration for every actual model fit. Counts omit the preflight probe.

Fit durations include host matrix construction and transfers; they are wall times, not isolated GPU-kernel times. The internal `--reuse-metrics` model-stage flag checks backend and holdout count but does not fingerprint the input panel or fitting parameters. Use it only when both are known unchanged; normal training always recomputes evaluation.

The learned candidate is named `XGBoost CUDA`, with method ID `xgb`. GPU models are saved as `xgb_count.ubj`, `xgb_frp.ubj`, and `xgb_metadata.json` under `data/interim/sheikh/`; CPU LightGBM text models retain their existing filenames. B1 remains eligible and is chosen if its held-out agreement is better. Conformal intervals, drift, anomaly products, and outlook validation are rebuilt after model selection.

Selection now includes **both Terra-only and Terra+Aqua holdouts**. The first CUDA trial slightly improved Terra+Aqua mean CCC but performed poorly on the Terra-only spatial holdout and failed the existing historical anomaly-seam gate. The gate was not weakened. `mean_ccc` retains the Terra+Aqua comparison for historical compatibility; `selection_mean_ccc` includes both configurations and determines the chosen method. B1 can therefore be selected while every learned candidate, drift classifier, and forecast is still trained on CUDA.

The public snapshot is not automatically replaced by training. After reviewing new metrics, explicitly export and commit it using the hosting procedure. The current named-area export contains all 11 administrative regions and two examples; the earlier two-example snapshot was refreshed from accepted local outputs during the area-filter update.

## Verification

Normal CPU CI skips hardware-specific tests. On an NVIDIA machine:

```powershell
$env:FIRESENSE_TEST_CUDA = '1'
.venv\Scripts\python -m pytest common/tests ws1_harmonize/tests ws4_outlook/tests -q
```

These include actual CUDA Poisson/Tweedie/classification/quantile fitting, model round-trip persistence, forbidden-target-column behavior, and rejection of CPU fallback. Full-pipeline QA additionally checks data contracts and API flows. Inspect execution reports and numeric holdouts; successful CUDA execution alone does not establish scientific superiority.

Only the RTX 4070 Laptop 8 GB is available on the current machine. RTX 3090 24 GB support uses the same single-device path but is not a measured benchmark. The two GPUs on separate computers do not pool memory. Distributed/multi-GPU execution is not implemented by this change.
