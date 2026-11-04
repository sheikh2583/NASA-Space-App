# CUDA training guide

**Human-operated guide. Coding agents must not execute training or fitting checks.** [AGENTS.md](../AGENTS.md) prohibits model fits, including CUDA probes, readiness checks, default/training-only setup, and tests that fit learners. Agents may prepare commands and inspect existing outputs; a human runs the fitting workflows below.

Current workflow: 4 November 2026. Start in the repository root. Training requires NVIDIA Windows/Linux, Python 3.11, the real inputs below, and a passing CUDA probe. The complete project setup also requires Node.js 22.12+; training-only setup does not. Setup installs dependencies only; training is always separate. For UI/API development without a GPU, use `-UiOnly` / `--ui-only` and the mock launch in [README](../README.md).

For a complete teammate handoff with prerequisite installation, Windows/Linux initialization, input-copy commands, logged quick/full runs, and return-archive commands, use **[TEAM_TRAINING.md](TEAM_TRAINING.md)**. Linux supports an explicit interpreter via `--python "$(uv python find --system 3.11)"`; Windows supports `-PythonExecutable 'C:\full\path\to\python.exe'` when creating `.venv`. Linux training checks x86_64, glibc 2.28+, and OpenMP before installing packages. A fresh native Linux installation still requires human verification.

## Start here: run on your training machine

Use the same procedure on the RTX 4070 Laptop 8 GB or RTX 3090 Desktop 24 GB. GPU 0 means the first CUDA-visible GPU **on that machine**. These examples use the project interpreter directly, so virtual-environment activation is optional. Run one block at a time and resolve any failure before continuing. The commands below use the required downloaded files; setup does not obtain those files for you.

### Windows — either GPU

Open PowerShell and enter the repository. This is the current workspace path; change it on another computer:

```powershell
Set-Location "X:\Nasa Space Apps Challenge\nasa-modis-viirs"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup.ps1 -TrainingOnly
if ($LASTEXITCODE -ne 0) { throw 'Setup failed. Resolve the error before continuing.' }
.venv\Scripts\python scripts\workflow.py prepare --gpu-id 0 --threads 8
if ($LASTEXITCODE -ne 0) { throw 'Training inputs or CUDA are not ready.' }
```

When readiness prints `READY: 0 blocking check(s)`, run quick training:

```powershell
.venv\Scripts\python -u scripts\workflow.py train --backend cuda --gpu-id 0 --threads 8 --quick
if ($LASTEXITCODE -ne 0) { throw 'Quick training failed. Inspect its failed stage and QA.' }
```

Inspect `results/latest.md` and confirm QA passes. Then run the final full comparison:

```powershell
.venv\Scripts\python -u scripts\workflow.py train --backend cuda --gpu-id 0 --threads 8
if ($LASTEXITCODE -ne 0) { throw 'Full training failed; do not publish this run.' }
.venv\Scripts\python scripts\workflow.py results
```

### NVIDIA Linux — either GPU

Clone/extract the source and enter its root. Replace the example path with your checkout. Transfer the required input files first using the layout below. Create a fresh Linux `.venv`; a Windows `.venv` cannot be reused.

```bash
cd "/path/to/nasa-modis-viirs"
bash scripts/setup.sh --training-only
```

Run readiness, then quick training only when readiness succeeds:

```bash
.venv/bin/python scripts/workflow.py prepare --gpu-id 0 --threads 8
```

```bash
.venv/bin/python -u scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8 --quick
```

After quick training and QA pass, run full training and refresh the report:

```bash
.venv/bin/python -u scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8
```

```bash
.venv/bin/python scripts/workflow.py results
```

Each command must finish with exit status 0. A successful training run prints `Pipeline complete`; its `execution.json` records `status: passed`. A full run must also show `quick: false` and `start_stage: null` to establish a newly completed whole pipeline. A successful resume is useful validation, but its elapsed time excludes earlier stages.

### Time budget

| Run | RTX 4070 Laptop 8 GB | RTX 3090 Desktop 24 GB |
|---|---:|---:|
| Quick training | 12–20 minutes | 10–18 minutes |
| Full pipeline | 18–25 minutes | 13–22 minutes |

These are planning ranges for the current 4.34-million-detection input, cached weather, local SSD, and a comparable host CPU. Installation and data downloads are additional. The 4070 model stage measured 274 seconds; the first full trial failed QA and required repair. The 3090 has not been benchmarked. Use [GPU timing evidence](GPU_TRAINING_TIMES.md) for the assumptions; do not present either range as a guaranteed successful-run benchmark.

The pipeline trains tree models and evaluates held-out agreement. It is not an epoch-based neural-network training loop. `--quick` reduces holdouts; `--threads` controls host helpers. The selected scientific method may still be B1 after the CUDA candidate has been trained.

Before starting, stop other runs in this checkout, keep the input files unchanged, and reserve space for both new outputs and a copy of the previous outputs. Readiness requires at least 5 GiB free; large existing artifacts/backups can require more. On the laptop, connect power and use adequate cooling. Stop the trained API while replacing its data and restart it after validation.

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

For a headless GPU server, or when the local frontend should keep running, use `scripts\setup.ps1 -TrainingOnly` on Windows or `bash scripts/setup.sh --training-only` on Linux. This installs the same complete Python/CUDA dependencies and verifies all four pipeline objectives, but skips Node/npm, frontend environment files, and frontend changes. UI build/test workflows require the complete setup later. `-UiOnly` and `-TrainingOnly` are mutually exclusive.

`requirements-cuda.txt` includes the entire pinned `requirements.lock.txt` environment plus XGBoost 3.2.0. Pip installs its declared dependencies, including platform-specific runtime packages. No PyTorch, TensorFlow, CuPy, RAPIDS, or LightGBM GPU compilation is required by this pipeline. The standard XGBoost wheel provides the CUDA learner; do not install `xgboost-cpu`. A separately installed CUDA toolkit is not part of the normal wheel-based setup. The actual fit/predict probe establishes whether the installed wheel and NVIDIA driver work together. See the [official XGBoost installation guide](https://xgboost.readthedocs.io/en/release_3.2.0/install.html).

System prerequisites cannot be supplied by pip:

| Platform | Prerequisite / failure recovery |
|---|---|
| Windows x64 | NVIDIA driver (`nvidia-smi`), 64-bit Python 3.11, and [Microsoft Visual C++ x64 Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist). Node.js 22.12+ is needed for frontend setup only. |
| Linux | NVIDIA driver, Python 3.11 with venv, modern glibc (2.28+ for the full wheel). Node.js 22.12+ is needed for frontend setup only. On Debian/Ubuntu, missing OpenMP libraries commonly require `libgomp1`; missing venv may require `python3.11-venv`. |
| macOS | UI/API development only; this CUDA training path is unavailable. |

Setup validates Python/Node as applicable, checks the NVIDIA driver, installs pinned dependencies with visible pip progress, checks dependency consistency/imports, verifies GPU training/prediction, and preserves existing environment files. Full setup also installs locked npm packages and checks development/preview ports 5173 and 4173 before changing packages. Stop this project's Vite/test/preview processes before full setup on Windows, or use training-only setup.

The CUDA probe checks `count:poisson`, `reg:tweedie`, `binary:logistic`, and `reg:quantileerror`, which cover harmonization, drift, and outlook fitting. Each tiny fit verifies the selected device and finite predictions. The result includes `cuda_build_version` and `verified_objectives`. Probe fits never append to a configured pipeline audit log; the prior log setting is restored even if verification fails.

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

When moving to the 3090 machine, transfer `data/raw/firms/`, `data/raw/boundaries/`, `data/raw/landcover/`, and both regional weather Parquets under `data/interim/monazir/`. Raw POWER JSON tiles are useful for rebuilding/resuming weather acquisition, but existing valid regional Parquets satisfy readiness. Preserve directory names. Downloaded ZIPs must be extracted into CSV/CSV.GZ inputs before training. Recreate dependencies on the destination; keep `.venv`, `node_modules`, and private `.env` files out of the transfer bundle. Archive training does not require copying an API key.

See [data acquisition](SHEIKH_GUIDE.md) for download steps. The training launcher requires land cover even though low-level code permits a degraded fallback. Archive training needs no FIRMS API key. Recent API acquisition uses the private root `.env` key; no key belongs in `VITE_*` variables.

```sh
python -m ws3_anomaly.loaders.weather --start 2000-11-01 --end 2026-11-03
python scripts/workflow.py prepare --gpu-id 0 --threads 8
```

Wait for both `data/interim/monazir/weather_BD.parquet` and `weather_PB.parquet`. The cache resumes completed raw tiles when dates are unchanged. Readiness must print **READY: 0 blocking check(s)**. It checks presence/imports, free disk, and an actual CUDA probe; inspect coverage separately. Dates and satellite windows are configured for the November 2026 record.

## 3. Smoke, quick training, full training

Choose the checks for the setup you installed:

| Installed setup | Before training | After training |
|---|---|---|
| Complete project setup, including Node/npm | `python scripts/workflow.py smoke` | `validate`, `results`, then `smoke` and the UI |
| Training-only setup, no Node/npm | Python-only tests below, then `prepare` | `validate` and `results`; install frontend dependencies separately before UI checks |

The commands in the rest of this guide use activated-environment `python`. Use the explicit Windows/Linux interpreter paths from the fast path if activation is unavailable.

Training-only software checks:

```sh
python -m pip check
python -m pytest common ws1_harmonize/tests ws2_platform/tests ws3_anomaly/tests ws4_outlook/tests scripts/tests -q
```

Hardware integration tests are opt-in; the readiness probe always tests actual CUDA. The Python-only command uses tiny test data and needs neither NASA inputs nor Node. It intentionally excludes the real-output QA suite until training has produced its artifacts.

With complete project setup, the integrated smoke check and training commands are:

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

For a terminal run, save the live console output as well as the automatic execution report. These logging examples start a **full** run; use them instead of launching another full command in parallel.

PowerShell:

```powershell
New-Item -ItemType Directory -Force results\logs | Out-Null
$trainingLog = "results\logs\train-full-$(Get-Date -Format yyyyMMdd-HHmmss).log"
.venv\Scripts\python -u scripts\workflow.py train --backend cuda --gpu-id 0 --threads 8 2>&1 | Tee-Object -FilePath $trainingLog
if ($LASTEXITCODE -ne 0) { throw "Training failed. Inspect $trainingLog" }
```

Bash:

```bash
set -o pipefail
mkdir -p results/logs
training_log="results/logs/train-full-$(date +%Y%m%d-%H%M%S).log"
.venv/bin/python -u scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8 2>&1 | tee "$training_log"
```

The Bash pipeline's exit status now reflects a failed training command rather than just a successful `tee`. Leave the terminal/process running. Ctrl+C interrupts the current run; it does not create a paused training checkpoint. After an interruption, inspect partial outputs and rerun from the interrupted stage. If power/process termination prevented a final status update, `execution.json` can still say `running`; that does not prove a process is active.

GPU activity is intermittent because CSV/Parquet/geospatial/calibration/anomaly work uses the host CPU and many fits are small. Low utilization during those stages is expected. `--threads` sets model-library/helper workers, not GPU cores. The two GPUs on separate computers do not pool VRAM.

If a stage fails, repair its cause and resume at that stage with the original quick/full setting:

```sh
python scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8 --from intervals
```

Include `--quick` only for an originally quick run. If inputs or upstream code changed, restart from the earliest affected stage. Switching a numeric backend requires restarting at `model` or earlier. Avoid the internal `--reuse-metrics` flag: it is only valid when the panel and fit settings are known unchanged. Do not weaken QA to bypass a failure.

| Failure | Resolve before resuming |
|---|---|
| Missing imports / pip conflicts | Rerun the training-only installer in the project's Python 3.11 environment; read the first installation/import error. |
| GPU probe fails | Check the NVIDIA driver and selected GPU ID; install the full CUDA requirements. Every objective must verify the requested CUDA device. |
| Missing input/cache | Complete the exact file named by readiness, then run readiness again. |
| Out of GPU memory | Stop other GPU workloads you control, confirm the intended device, and rerun the failed stage. A repeated failure needs a measured model/data change and fresh evaluation; there is no launcher batch-size option. |
| Scientific QA fails | Inspect validation JSON and the failed scientific check, fix its cause, and rebuild the affected upstream/downstream stages. |
| Missing Node/npm in `smoke`/`dev` | Use Python-only checks on the training host, or install the complete project environment before frontend workflows. |

## 5. Review and publish

On either a training-only or complete installation:

```sh
python scripts/workflow.py validate
python scripts/workflow.py results
```

For UI review, first install the complete project setup if the machine was initialized with training-only mode. Then:

```sh
python scripts/workflow.py smoke
python scripts/workflow.py dev --open
```

Read `results/latest.md`, `data/processed/validation/`, and `data/interim/sheikh/method.json`. Check held-out agreement, interval coverage, the historical seam, and forecast skill. Current accepted science selects **B1**; GPU harmonization candidates were still trained and evaluated. See [measured CUDA results](CUDA_RESULTS.md).

Accept a final run only after checking:

- The execution report is `passed`, with the intended GPU/device, four verified probe objectives, and the expected full-run stages. Do not mistake setup/probe success for completed training.
- `method.json` records the selected method and both Terra+Aqua and Terra-only holdout agreement. CCC is an agreement metric, not classification accuracy.
- All five QA groups pass, including the historical seam. Interval coverage and forecast skill are inspected rather than assumed from a zero exit code.
- Final outputs exist under `data/processed/`; learned comparison artifacts are under `data/interim/sheikh/`. CUDA models use `xgb_count.ubj`, `xgb_frp.ubj`, and `xgb_metadata.json`; `b1_params.pkl` supplies the baseline if selected.
- Keep the execution report, CUDA fit log, console log, selected-method record, metrics table, and results summary with the run's Git revision. Preserve the pre-run backup until the new science has been reviewed.

To package existing validated results for the combined Render deployment after review:

```sh
python scripts/runtime_bundle.py pack
```

Upload `share/firesense-runtime.zip` under a new GitHub Release version, update its URL and printed SHA256 in `deployment/runtime.json`, and push the manifest. Render rebuilds the frontend/API with those existing results; it never trains. The record remains fixed at 2026-11-02. `export_hosted_demo.py` is only needed when refreshing the optional legacy snapshot. See [Render deployment](RENDER.md) and [the teammate deliverables checklist](TEAM_TRAINING.md#acceptance-and-deliverables).

Run real CUDA integration tests with `FIRESENSE_TEST_CUDA=1` as shown in the README. Manual FIRMS comparisons, fluent Bangla review, and phone/browser checks remain separate submission checks. Timing ranges for both requested GPUs are in [GPU_TRAINING_TIMES.md](GPU_TRAINING_TIMES.md).
