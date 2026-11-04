# CUDA training guide

Current workflow: 4 November 2026. Start in the repository root. Training requires NVIDIA Windows/Linux, Python 3.11, Node.js 22.12+, the real inputs below, and a passing CUDA probe. The setup scripts install dependencies only; training is always a separate command. For UI/API development without a GPU, use `-UiOnly` / `--ui-only` and the mock launch in [README](../README.md).

## 1. Install the full training environment

Windows, PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup.ps1
.venv\Scripts\python scripts\workflow.py gpu-check --gpu-id 0 --threads 8
```

NVIDIA Linux, Bash:

```bash
bash scripts/setup.sh
.venv/bin/python scripts/workflow.py gpu-check --gpu-id 0 --threads 8
```

`requirements-cuda.txt` includes the entire pinned `requirements.lock.txt` environment plus XGBoost 3.2.0. Pip installs its declared dependencies, including platform-specific runtime packages. No PyTorch, TensorFlow, CuPy, RAPIDS, or LightGBM GPU compilation is required by this pipeline. The standard XGBoost wheel provides the CUDA learner; do not install `xgboost-cpu`. A separately installed CUDA toolkit is not part of the normal wheel-based setup. The actual fit/predict probe establishes whether the installed wheel and NVIDIA driver work together. See the [official XGBoost installation guide](https://xgboost.readthedocs.io/en/release_3.2.0/install.html).

System prerequisites cannot be supplied by pip:

| Platform | Prerequisite / failure recovery |
|---|---|
| Windows x64 | NVIDIA driver (`nvidia-smi`), 64-bit Python 3.11, Node.js 22.12+, and [Microsoft Visual C++ x64 Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist). Missing runtime DLLs require the redistributable. |
| Linux | NVIDIA driver, Python 3.11 with venv, Node.js 22.12+, modern glibc (2.28+ for the full wheel). On Debian/Ubuntu, missing OpenMP libraries commonly require `libgomp1`; missing venv may require `python3.11-venv`. |
| macOS | UI/API development only; this CUDA training path is unavailable. |

Setup validates Python/Node, checks the NVIDIA driver, installs pinned dependencies with visible pip progress, checks dependency consistency/imports, verifies a GPU fit, preserves existing environment files, and installs locked npm packages. Stop this project's Vite/test/preview processes before reinstalling npm packages on Windows. An occupied port 5173 is detected before installation starts.

An existing `.venv` must belong to the current OS and Python 3.11. Rename an incompatible environment before rerunning setup; do not copy it between Windows and Linux. No automatic system-driver installation or silent unpinned fallback occurs. If a platform cannot install the lockfile, inspect the error first. Explicitly accept compatible base requirements only with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup.ps1 -AllowCompatible
```

```bash
bash scripts/setup.sh --allow-compatible
```

That environment is no longer lockfile-reproducible; record its package versions and rerun all verification. `-NoPipeline` / `--no-pipeline` and `-Cuda` / `--cuda` remain compatibility aliases; setup never trains, and CUDA is the normal setup mode.

## 2. Activate and prepare the inputs

PowerShell: `.\.venv\Scripts\Activate.ps1`. Bash: `source .venv/bin/activate`. If activation is blocked, replace `python` below with `.venv\Scripts\python` (Windows) or `.venv/bin/python` (Linux).

Required local inputs:

| Input | Path |
|---|---|
| MODIS Terra/Aqua + VIIRS SNPP/NOAA-20 archives for both coverage areas | `data/raw/firms/*.csv` or `*.csv.gz`; extract archive ZIPs |
| Bangladesh ADM1 boundary | `data/raw/boundaries/BGD_ADM1.geojson` |
| India ADM1 boundary | `data/raw/boundaries/IND_ADM1.geojson` |
| Original MCD12C1 land cover | `data/raw/landcover/MCD12C1*.hdf` |
| NASA POWER tiles | `data/raw/power/`; weather command creates the regional Parquet caches |

See [data acquisition](SHEIKH_GUIDE.md) for download steps. The training launcher requires land cover even though low-level code permits a degraded fallback. Archive training needs no FIRMS API key. Recent API acquisition uses the private root `.env` key; no key belongs in `VITE_*` variables.

```sh
python -m ws3_anomaly.loaders.weather --start 2000-11-01 --end 2026-11-03
python scripts/workflow.py prepare --gpu-id 0 --threads 8
```

Wait for both `data/interim/monazir/weather_BD.parquet` and `weather_PB.parquet`. The cache resumes completed raw tiles when dates are unchanged. Readiness must print **READY: 0 blocking check(s)**. It checks presence/imports, free disk, and an actual CUDA probe; inspect coverage separately. Dates and satellite windows are configured for the November 2026 record.

## 3. Smoke, quick training, full training

```sh
# Unit/script tests, fixture API, optional existing-output QA, frontend checks/build.
python scripts/workflow.py smoke

# Reduced holdouts; still runs the downstream science pipeline.
python scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8 --quick

# Final comparison: six holdouts and both satellite-input configurations.
python scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8
```

Quick training is not final evidence. It evaluates spatial and backward holdouts; full training adds three temporal folds and the drift-era fold. B1 and the GPU candidate are evaluated on both Terra+Aqua and Terra-only inputs. The selected method drives out-of-fold predictions, intervals, reconstruction, and anomalies. A successful CUDA fit does not justify forcing the learned model to win.

Keep one run active per checkout. Every CUDA pipeline run backs up existing processed/harmonization outputs under `data/runs/<timestamp>/baseline/` before writing. Budget disk space for those copies. Stop/restart the real API around replacement of its scientific files.

The menus are equivalent: **1 setup**, **12 GPU verification**, **2 readiness**, **3 smoke**, **4 quick CUDA**, **5 full CUDA**, **6 trained UI**, **7 mock UI**, **8 results**, **9 source ZIP**, **10 full train + tests/build**, **11 UI-only setup**. The old CPU training action has been removed.

## 4. Monitor and recover

The console prints `== <stage>` and stage completion times. Inspect:

- `results/logs/`: transcript/log from clickable launchers.
- `results/runs/<timestamp>/execution.json`: running/passed/failed status, requested stages, elapsed times, hardware, and backup path.
- `cuda-fits.jsonl` beside that report: every verified fit's objective, rows, device, and wall time.
- `nvidia-smi -l 2` in another terminal: utilization/memory; Ctrl+C exits monitoring.

GPU activity is intermittent because CSV/Parquet/geospatial/calibration/anomaly work uses the host CPU and many fits are small. Low utilization during those stages is expected. `--threads` sets model-library/helper workers, not GPU cores. The two GPUs on separate computers do not pool VRAM.

If a stage fails, repair its cause and resume at that stage with the original quick/full setting:

```sh
python scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8 --from intervals
```

Include `--quick` only for an originally quick run. If inputs or upstream code changed, restart from the earliest affected stage. Switching a numeric backend requires restarting at `model` or earlier. Avoid the internal `--reuse-metrics` flag: it is only valid when the panel and fit settings are known unchanged. Do not weaken QA to bypass a failure.

## 5. Review and publish

```sh
python scripts/workflow.py validate
python scripts/workflow.py results
python scripts/workflow.py smoke
python scripts/workflow.py dev --open
```

Read `results/latest.md`, `data/processed/validation/`, and `data/interim/sheikh/method.json`. Check held-out agreement, interval coverage, the historical seam, and forecast skill. Current accepted science selects **B1**; GPU harmonization candidates were still trained and evaluated. See [measured CUDA results](CUDA_RESULTS.md).

To publish the named-area demo after review:

```sh
python scripts/export_hosted_demo.py
```

This exports supported administrative boundaries and saved responses for each named area. Review the public JSON, test/preview in snapshot mode, commit those artifacts, and push to the deployment branch. The export date remains fixed at 2026-11-02. [README deployment](../README.md#deploy-the-demo) and [hosting operations](HOSTING.md) cover GitHub Pages, revision checks, and full API hosting limits.

Run real CUDA integration tests with `FIRESENSE_TEST_CUDA=1` as shown in the README. Manual FIRMS comparisons, fluent Bangla review, and phone/browser checks remain separate submission checks. Timing ranges for both requested GPUs are in [GPU_TRAINING_TIMES.md](GPU_TRAINING_TIMES.md).
