# FireSense — MODIS + VIIRS Burning Activity

FireSense combines NASA FIRMS MODIS and VIIRS observations into a consistent fire-activity record for **Bangladesh and Punjab–Haryana–Delhi**. It estimates earlier activity in VIIRS terms, reports uncertainty, flags unusual periods, describes weather associations, and presents results in English and Bangla through React/Vite and FastAPI.

[Render deployment](docs/RENDER.md) · [Legacy snapshot](https://sheikh2583.github.io/NASA-Space-App/) · [Training guide](docs/TRAINING.md) · [GPU time estimates](docs/GPU_TRAINING_TIMES.md) · [Claude handoff](docs/CLAUDE_HANDOFF.md)

**Operator guide — updated 4 November 2026.** Start from the repository root and run each command only after the previous one succeeds. Setup, data acquisition, training, and publication are separate steps.

**Coding agents: strict no training.** Read [AGENTS.md](AGENTS.md) before working here. Training, model-fit probes, readiness checks, default/training-only setup, and tests that fit models are **human-only**. Agents may edit code, run reviewed checks without fitting, and deploy existing validated outputs. The operator commands below do not grant agents permission to train.

[Initialize](#initialize-a-fresh-checkout) · [CUDA setup](#cuda-training-dependencies) · [Data and keys](#prepare-real-training-data) · [Train](#train-and-validate) · [Debug](#debug-and-test) · [Deploy](#deploy-the-demo) · [Project structure](#project-structure-and-contribution)

**Sending work to a teammate?** [Copy the Windows/Linux training handoff](docs/TEAM_TRAINING.md): prerequisite installation, initialization scripts, input copying, logged runs, and deliverable packaging.

## Choose your starting point

| Goal | What you need | Start here |
|---|---|---|
| View the project | A browser | [Live demo](https://sheikh2583.github.io/NASA-Space-App/) |
| Develop or debug the UI/API | Python, Node.js, source code; no NASA account or GPU | [Initialize](#initialize-a-fresh-checkout), then Mock UI |
| Train on real observations | NASA files, boundaries, land cover, weather cache | [Prepare data](#prepare-real-training-data), then [train](#train-and-validate) |
| Set up CUDA training | Supported Windows/Linux NVIDIA environment | [CUDA dependencies](#cuda-training-dependencies) |
| Publish the complete app | GitHub repository and existing Render account | [Deploy frontend + backend together](#deploy-the-demo) |

**Operating modes:** Mock UI uses bundled synthetic contract fixtures. Local trained UI queries processed real data through FastAPI. The combined Render deployment serves the UI and live API together; its first deployment must still be completed in your account. The legacy Pages site serves saved results for 11 administrative regions. A source checkout includes fixtures, named boundaries, and that snapshot; downloaded NASA files and trained models are separate.

The explorer opens on Dhaka's administrative boundary. Select a country, search in English or Bangla, choose a division/state, and click **Apply filters**. A unique name match selects itself; **Reset** returns to Dhaka. The “Viewing” label identifies the area behind the results while you edit filters. You can also click a named boundary or focus its map button and press Enter/Space. Administrative outlines come from geoBoundaries; OSM supplies the basemap. Name search is local and needs no geocoding key. Mock responses remain synthetic fixtures.

The configured record ends on **2 November 2026**. Pre-2012 activity is modeled, weather relationships are associations, and forecasts can have no demonstrated skill. Extending the record requires reviewing sensor windows and configured dates; changing an end-date argument alone is insufficient.

## Initialize a fresh checkout

Install **64-bit Python 3.11** and **Git**. Install **Node.js 22.12+ with npm** for UI development, smoke checks, and frontend builds. A headless training host does not need Node. Choose one setup mode:

| Setup | Windows PowerShell | Linux Bash | Installs / verifies |
|---|---|---|---|
| UI/API development | `scripts\setup.ps1 -UiOnly` | `bash scripts/setup.sh --ui-only` | Locked Python/API dependencies and frontend; no NVIDIA requirement |
| Complete project | `scripts\setup.ps1` | `bash scripts/setup.sh` | CUDA training dependencies, actual GPU fits, and frontend |
| Headless training | `scripts\setup.ps1 -TrainingOnly` | `bash scripts/setup.sh --training-only` | Same Python/CUDA environment and GPU verification; skips Node/npm and frontend changes |

Use the complete PowerShell invocation below if script execution is blocked. macOS supports UI/API development only. Full and training-only modes require an NVIDIA driver and `nvidia-smi`; Windows native dependencies also need the [Microsoft Visual C++ x64 runtime](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist). Linux may need `libgomp1` and `python3.11-venv`; see [platform prerequisites](docs/TRAINING.md#1-install-the-full-training-environment).

Setup creates `.venv`, installs pinned dependencies, and copies example environment files only when absent. Training-only setup creates only the root `.env`. Recreate environments on each OS rather than transferring `.venv` or `node_modules`. Allow at least 5 GiB of free space for training intermediates **plus** downloaded inputs and backups of existing outputs. Internet access is needed for installation, map tiles, and data acquisition. Render serving has a separate minimal environment in `requirements-api.txt` and does not use the training installers.

Clone the repository, or extract the source ZIP and open a terminal in its root. To publish your own copy, fork the repository and clone **your fork's URL** instead.

```sh
git clone https://github.com/sheikh2583/NASA-Space-App.git firesense
cd firesense
```

Paths containing spaces must be quoted when changing directories, for example `cd "X:\Nasa Space Apps Challenge\nasa-modis-viirs"` in PowerShell. The commands below work from any checkout location; no drive letter is hardcoded in the scripts.

### Windows — PowerShell

```powershell
# Initialize UI/API development without needing an NVIDIA GPU.
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup.ps1 -UiOnly

# First successful launch: no datasets, credentials, or GPU needed.
.venv\Scripts\python scripts\workflow.py dev --mock --open
```

### Linux or macOS — Bash

```bash
bash scripts/setup.sh --ui-only
.venv/bin/python scripts/workflow.py dev --mock --open
```

Success means setup prints **SETUP COMPLETE**, then the launcher prints **UI ready**. The UI opens at [localhost:5173](http://localhost:5173), with API documentation at [localhost:8000/docs](http://localhost:8000/docs). Choose a named area; mock responses are synthetic fixtures rather than trained administrative totals. **Ctrl+C** stops both servers. Setup does not download the scientific datasets.

For the commands below, activate the environment once in each new terminal, from the repository root:

| Shell | Activate |
|---|---|
| PowerShell | `.\.venv\Scripts\Activate.ps1` |
| Bash | `source .venv/bin/activate` |

After activation, `python` means the project's interpreter. Activation is optional: replace `python` below with `.venv\Scripts\python` on Windows or `.venv/bin/python` on Linux/macOS. Verify with `python -c "import sys; print(sys.executable)"`; its path must point inside this checkout's `.venv`.

Run the integration check after stopping the development servers:

```sh
python scripts/workflow.py smoke
```

Smoke runs unit/script tests, a fixture API request, frontend tests, translations, and a production build. It also validates real outputs when present; it skips that part in a fresh checkout. Success ends with **SMOKE PASSED**. It does not train or download data. Hardware tests remain skipped unless explicitly enabled. For training-only setup, use the Python-only checks under [Debug and test](#debug-and-test) until frontend dependencies are installed.

### Clickable launchers

Windows: double-click **START_HERE.cmd**. Linux/macOS: `bash start.command`. The menus provide:

| Option | Action | Requirement |
|---|---|---|
| 1 / 12 | Setup complete CUDA environment / Verify an actual GPU fit | NVIDIA Windows/Linux |
| 11 / 7 / 3 | Setup UI development / Mock UI / Smoke | No NASA data or GPU |
| 2 / 4 / 5 | Prepare / Quick training / Full training | Real inputs and working CUDA required |
| 6 / 8 / 9 | Trained UI / Results report / Source ZIP | Training needed for real UI/results |
| 10 | Full CUDA training, tests, and UI build | Real inputs and CUDA |

Menu logs are saved under `results/logs/`. See [the training guide](docs/TRAINING.md) for the complete workflow.

## CUDA training dependencies

Training uses **XGBoost 3.2.0** on NVIDIA Windows/Linux. Install a current NVIDIA driver; Windows also needs the Microsoft Visual C++ x64 runtime. macOS supports UI/API development with `--ui-only`, but cannot train with CUDA. Run the full installer to install the locked scientific environment, XGBoost, frontend dependencies, and verify a real GPU fit:

```powershell
# Windows: safe to rerun after UI-only initialization.
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup.ps1
```

```bash
# NVIDIA Linux
bash scripts/setup.sh
```

Both installers use `scripts/bootstrap.py`, preserve `.env`, create input folders, run `pip check`, and stop on failure. Setup never starts training or changes scientific outputs. Stop Vite before setup to release Windows npm locks. Pinned installation does not silently switch to unpinned packages; see [setup options](docs/TRAINING.md).

For a GPU training server or to leave the running frontend untouched, install **training dependencies only**. This mode needs no Node/npm:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup.ps1 -TrainingOnly
```

```bash
bash scripts/setup.sh --training-only
```

For an existing environment, the complete dependency manifest and standalone probe are:

```sh
python -m pip install -r requirements-cuda.txt
python scripts/workflow.py gpu-check --gpu-id 0 --threads 8
```

The check fits and predicts with all four pipeline objectives (Poisson, Tweedie, binary classification, and quantile regression), then verifies the CUDA device for each. It reports the wheel's CUDA build version and keeps probe fits out of training audit logs. A missing/unusable GPU raises an error; a CUDA request cannot silently switch to CPU.

`workflow.py prepare`, `train`, and `all`, and `scripts/run_pipeline.py` require CUDA with eight helper threads by default. Direct model, drift, outlook, and readiness commands also select CUDA and reject CPU overrides. Scientific baselines and reference implementations remain internal for comparison and CI; data preparation still uses the host CPU.

Harmonization models, drift classifiers, and quantile forecasts use CUDA. File I/O, geospatial operations, baselines, calibration, anomaly statistics, and QA remain on the CPU. B1 can still win model selection. The RTX 4070 Laptop path is verified; RTX 3090 performance has not been measured. Hundreds of small GPU fits currently add overhead, so **an end-to-end speedup has not been established**. Read [CUDA operations](docs/CUDA_PIPELINE.md) and [measured results](docs/CUDA_RESULTS.md) before comparing runtimes.

## Prepare real training data

Create missing directories and populate this layout; all paths are relative to the repository root:

```text
data/
  raw/
    firms/                 FIRMS *.csv or *.csv.gz (extract downloaded ZIPs)
    boundaries/
      BGD_ADM1.geojson      Bangladesh ADM1 boundaries
      IND_ADM1.geojson      India ADM1 boundaries
    landcover/
      MCD12C1*.hdf          Original MCD12C1 land-cover HDF, original filename
    power/                 Resumable NASA POWER JSON tile cache
  interim/monazir/
    weather_BD.parquet     Created by the weather loader
    weather_PB.parquet     Created by the weather loader
```

1. Obtain MODIS Terra/Aqua and VIIRS SNPP/NOAA-20 archives for both areas from [FIRMS country downloads](https://firms.modaps.eosdis.nasa.gov/country/) or [archive requests](https://firms.modaps.eosdis.nasa.gov/download/). Use each product's actual available period; retain original columns. NOAA-21 is optional. India files are clipped to Punjab–Haryana–Delhi by the pipeline. Files containing `synthetic_` in their names are excluded from real-input selection. ZIP files must be extracted before training.
2. Obtain ADM1 GeoJSON files for Bangladesh and India and save them under the exact names above. Country/administrative IDs must be preserved.
3. Download the original MCD12C1 land-cover HDF through Earthdata and keep its filename. The training launcher requires it for reproducibility; the lower-level pipeline has a degraded fallback.
4. Build the weather cache with the command below. NASA POWER needs no API key. Rerunning with the same dates reuses completed raw tiles.

```sh
python -m ws3_anomaly.loaders.weather --start 2000-11-01 --end 2026-11-03
python scripts/workflow.py prepare --backend cuda --gpu-id 0 --threads 8
```

Proceed when readiness prints **READY: 0 blocking check(s)**. Readiness checks imports and file presence; it does not establish full satellite coverage or scientific quality.

Detailed acquisition instructions: [data guide](docs/SHEIKH_GUIDE.md), [data layout](data/README.md), and [training guide](docs/TRAINING.md). Your checkout does not inherit the maintainer's local datasets.

### Environment files and credentials

| File / variable | Purpose |
|---|---|
| Root `.env`: `FIRMS_MAP_KEY` | Backend-only FIRMS API updates; obtain your own [MAP_KEY](https://firms.modaps.eosdis.nasa.gov/api/map_key/). Downloaded archives can be trained without it. |
| Root `.env`: `API_BASE_URL` | API test/script address; normally `http://localhost:8000` |
| `ws5_frontend/.env`: `VITE_API_BASE_URL` | Browser-accessible API URL; locally `http://localhost:8000` |
| `VITE_DATA_MODE` | Data label; launcher sets `synthetic` for Mock UI and `real` for trained UI |
| `VITE_DEMO_MODE` | Empty for live API mode; `snapshot` for static hosting |
| `VITE_FALLBACK_BASE_URL` | Optional static fallback endpoint; leave empty unless separately configured |

Full/UI setup creates both `.env` files from their examples; training-only setup creates the root file. The direct FIRMS downloader reads `FIRMS_MAP_KEY` from its **process environment**; saving it in the root `.env` alone does not load it into that command. Load it privately before API acquisition. Archive training, weather acquisition, mock development, and Pages publication need no FIRMS key.

Vite reads the frontend's environment file and embeds `VITE_*` values at build time. Restart Vite after local configuration changes; rebuild for deployment. Keep the FIRMS key out of frontend variables, Git, screenshots, and handoff ZIPs. The OpenStreetMap basemap requires no FIRMS/CARTO key; follow its [tile usage policy](https://operations.osmfoundation.org/policies/tiles/).

## Train and validate

Run **one pipeline at a time per checkout**: stages share output paths. Stop the trained API while replacing its data, then restart it to clear in-memory caches.

After GPU verification:

```sh
python scripts/workflow.py prepare --backend cuda --gpu-id 0 --threads 8
python scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8 --quick
python scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8
```

Quick training reduces model holdouts; it still rebuilds downstream science and is separate from `smoke`. The full command runs all six holdouts with both Terra+Aqua and Terra-only checks. Run it before reporting final model comparisons. Selection uses held-out agreement; choosing CUDA does not force selection of the learned model. Never bypass a failing scientific gate to obtain a model or deployment.

After training, on either a complete or headless setup:

```sh
python scripts/workflow.py validate
python scripts/workflow.py results
```

With Node and frontend dependencies installed, also run:

```sh
python scripts/workflow.py smoke
python scripts/workflow.py dev --open
```

For a headless host, inspect the reports locally or transfer the validated runtime artifacts to a development/deployment machine. Install the complete setup before running workflows that call npm (`smoke`, `test`, `build`, `dev`, or `all`).

Accept a new full run only when the command exits successfully, prints **Pipeline complete**, and `results/runs/<timestamp>/execution.json` records `status: passed`, `quick: false`, and `start_stage: null`. A quick run or successful downstream resume does not establish completion or elapsed time for a fresh full run. Verify the selected method, real-data provenance, both satellite-input combinations, and scientific checks in the result/validation files before publishing.

Successful QA checks data integrity, API contracts, end-to-end queries, shared libraries, and the historical anomaly seam. Inspect numeric validation results as well as the exit status. Human FIRMS comparisons, Bangla review, and browser/phone checks remain in the [QA checklist](docs/QA_CHECKLIST.md).

| Artifact | Location |
|---|---|
| Selected method, holdout scores, saved learned models | `data/interim/sheikh/` |
| Harmonized record | `data/processed/harmonized.parquet` |
| Anomalies, periods, drivers, outlooks | `data/processed/` |
| Scientific QA and validation | `data/processed/validation/` |
| Readable / machine-readable summary | `results/latest.md` / `results/latest.json` |
| Stage timings, status, hardware, CUDA fit log | `results/runs/<timestamp>/` |
| Pre-run CUDA backup of existing processed/model artifacts | `data/runs/<timestamp>/baseline/` |

CUDA backups can be large. Inputs, models, backups, and run reports stay outside Git. Scientific evidence is in [CUDA results](docs/CUDA_RESULTS.md). Plan **18–25 minutes** for a full RTX 4070 Laptop run or **13–22 minutes** for an RTX 3090 with a similar host and local files. These are planning ranges, not two measured successful full runs; see [assumptions and estimates](docs/GPU_TRAINING_TIMES.md).

### See training progress

The terminal prints stage names (`== model`, `== drift`, and so on), completion times, and harmonization CUDA fit events. This tree-model pipeline has no neural-network epoch counter or single reliable percentage bar. In a second terminal, run:

```sh
nvidia-smi -l 2
```

Press Ctrl+C in that monitoring terminal to stop monitoring. GPU activity is intermittent during file, geospatial, calibration, and statistical work. Inspect `results/runs/<timestamp>/execution.json` for completed stages and `cuda-fits.jsonl` for completed GPU fits. These update at stage/fit boundaries; they are not live per-iteration progress. The menu launchers additionally save console logs in `results/logs/`. For direct-run log capture that preserves failure status, use [training monitoring and recovery](docs/TRAINING.md).

### Resume after a failure

Read the failed stage's output and fix its cause first. Then resume at that stage using the **same backend, quick/full setting, GPU ID, and thread configuration**, for example:

```sh
python scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8 --from intervals
```

Append `--quick` only if the original run was quick. To replace historical reference-model results, restart at `model` or earlier using CUDA. Changed inputs or upstream logic require rebuilding from the earliest affected stage. Downstream resumption rejects a mismatched stored model backend. Avoid the internal `--reuse-metrics` flag unless the panel and fitting configuration are known unchanged.

Stage order:

```text
ingest → grid → sensors → cells → panel → v0 → model → intervals → drift → v1
       → anomalies → outlook → validation → fixtures → fallback → qa → results
```

The lower-level runner additionally supports synthetic input generation when no real inputs exist; the real-training workflow requires readiness and does not use that fallback. See [pipeline details](docs/PIPELINE.md).

## Debug and test

Start with `python scripts/workflow.py smoke`. To isolate a failure:

```sh
# Python-only unit/script checks; no NASA data, Node, or GPU required.
python -m pip check
python -m pytest common ws1_harmonize/tests ws2_platform/tests ws3_anomaly/tests ws4_outlook/tests scripts/tests -q

# Full configured Python suite, including real-output QA: run after training.
python -m pytest -q

# Run one test with its output, or enter pdb on the first failure.
python -m pytest ws1_harmonize/tests/test_harmonize.py -x -vv -s
python -m pytest ws1_harmonize/tests/test_harmonize.py -x --pdb

# Frontend diagnostics, from the frontend directory.
cd ws5_frontend
npm test
npm run check:strings
npm run build
cd ..
```

To debug each server separately, open two terminals in the root with the project Python environment active. For the API:

```sh
python -m uvicorn ws2_platform.api.mock_server:app --host 127.0.0.1 --port 8000 --reload
```

After training, replace `mock_server` with `app` for the real API. In the second terminal, run `npm run dev --prefix ws5_frontend -- --host 127.0.0.1 --strictPort`. For fixture mode set `VITE_DATA_MODE=synthetic` in `ws5_frontend/.env`; leave `VITE_DEMO_MODE` empty. Open browser DevTools → Console/Network to inspect requests. The real API's `/health` loads its data and reports the method version, cell count, and data-through date; `/docs` documents request bodies. Test a demo-area `/aoi/summary` request there as well.

To check the running mock or trained API from any shell:

```sh
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=30).read().decode())"
```

For a useful bug report, include the failing command, first relevant traceback, OS, `python --version`, `python -m pip check`, and (for frontend issues) `node --version` and `npm --version`. For GPU failures, include `nvidia-smi` and `gpu-check` output; for training failures, include the run's `execution.json`. Redact credentials and credential-bearing request URLs before sharing logs.

Enable actual CUDA integration tests only on a configured NVIDIA machine:

```powershell
# PowerShell
$env:FIRESENSE_TEST_CUDA = '1'
python -m pytest ws1_harmonize/tests/test_cuda.py -q
Remove-Item Env:FIRESENSE_TEST_CUDA
```

```bash
# Bash
FIRESENSE_TEST_CUDA=1 python -m pytest ws1_harmonize/tests/test_cuda.py -q
```

| Symptom | Next action |
|---|---|
| Wrong Python / missing module | Check `sys.executable`; use `.venv` Python and rerun setup. Check dependencies with `python -m pip check`. |
| Existing `.venv` belongs to another OS/Python | Rename that environment, rerun the appropriate setup, and reactivate the new environment. Do not transfer virtual environments between computers. |
| Native geospatial/HDF dependency fails to install | Use Python 3.11, keep the error, and follow [training setup](docs/TRAINING.md). Compatible unpinned installation requires an explicit flag. |
| `NOT READY`, missing files, or real API file-not-found | Complete the named downloads/cache; use `dev --mock` until training is ready. |
| CUDA unavailable or CPU fallback rejected | Check the NVIDIA driver, install `requirements-cuda.txt`, and rerun `gpu-check`. Use UI-only setup while training prerequisites are unresolved. |
| `Training requires CUDA` after a direct module command | Remove an old `FIRESENSE_BACKEND=cpu` override from this shell/environment. Use the supported workflow command and repeat GPU verification. |
| npm EPERM/EBUSY | Stop this project's Vite/test/preview processes before setup. Rerun after the lock is released. |
| Port 8000/5173 busy | Stop the earlier project server with Ctrl+C before relaunching. The launcher deliberately refuses occupied ports. |
| UI cannot reach API | Check API terminal/Network errors and `VITE_API_BASE_URL`; clear snapshot mode for live API development and restart Vite. |
| Headless host reports npm missing | Use Python-only checks, `prepare`, `train`, `validate`, and `results`; install complete setup before UI or integrated workflows. |
| Stale results or wrong data mode | Restart API after data changes; restart Vite after environment changes. For hosted mode verify the deployed SHA and reload. |
| QA or historical seam fails | Read `results/latest.md`, validation JSON, and failed-stage output. Repair the data/model and rerun affected stages. |
| Map tiles fail | Check browser networking and tile-service availability/policy. The FIRMS key does not authenticate basemap tiles. |

## Deploy the demo

The primary deployment is now **one Free Render Web Service** for the React frontend and FastAPI backend. Both use the same URL; no separate API address, frontend hosting account, or manual snapshot export is needed for live queries. The previous GitHub Pages site remains a legacy saved snapshot until you create and verify the Render service.

### Render setup

In your existing Render account, create a Web Service linked to this GitHub repository:

| Field | Value |
|---|---|
| Name | `firesense`, or another available name |
| Language | **Docker** |
| Branch | `main` |
| Region | Singapore |
| Root Directory | Leave empty |
| Dockerfile Path | `./Dockerfile` |
| Compute | **Free — $0/month** |
| Docker Command | Leave empty |
| Environment Variables | None required |
| Health Check Path | `/health` |
| Auto-Deploy | On Commit |

The root Dockerfile builds the UI in live mode, downloads the existing validated data pinned in [deployment/runtime.json](deployment/runtime.json), and serves the UI/API with one worker. It verifies the archive checksum and saved real-data QA. No training, CUDA probes, FIRMS key, database, or persistent disk is involved.

Choose **Free** explicitly: Render can preselect a paid instance. After the deployment is Live, use its assigned URL for both the website and API. Alternatively, **New → Blueprint** reads the same settings from [render.yaml](render.yaml).

Full instructions for the current Render form, artifact updates, free-tier limits, and troubleshooting: **[Render deployment guide](docs/RENDER.md)**.

### Verify and update

1. Open `<render-url>/health`: expect `status: ok`, nonzero cells, and the data-through date.
2. Open `<render-url>/version.json`: compare `commit` with your deployed Git SHA.
3. Open `<render-url>/`: select Dhaka, change dates/resolution, inspect cell layers, and export CSV. The saved-snapshot banner should be absent.
4. Open `<render-url>/docs` for API requests. The browser's Network panel should show requests to the same Render host.

A normal push to `main` rebuilds frontend and backend together after Auto-Deploy is enabled. It uses the pinned runtime data and does not acquire new observations or train. The record still ends on **2 November 2026**.

Free services sleep after 15 idle minutes and can take about a minute to wake; the website and API wake together. Free-instance hours are shared across your workspace. Read [Render's free-tier limits](https://render.com/docs/free). Monitor memory and logs; Free capacity has not been load-tested on Render.

### Publish new scientific data

After human-run scientific validation, package the existing outputs:

```sh
python scripts/runtime_bundle.py pack
```

Publish `share/firesense-runtime.zip` under a new GitHub Release version. Update its public URL and printed SHA256 in `deployment/runtime.json`, then commit/push that manifest. The next Docker build retrieves and verifies it. Never overwrite a pinned release asset, commit raw/processed data, or add training commands to deployment.

The serving bundle contains `cells.parquet`, `harmonized.parquet`, `sensor_days.parquet`, `interval_table.json`, `drivers_region.json`, `outlook_region.json`, and five saved validation JSON files. It excludes raw FIRMS observations, trained models, credentials, and run logs.

### Local combined-app verification

On a Docker-capable machine:

```sh
docker build -t firesense .
docker run --rm -p 10000:10000 firesense
```

Open `http://localhost:10000/`, `/health`, and `/docs`. This builds and serves existing artifacts only. The current Windows machine has no Docker engine; local API/UI routing and artifact transport have been verified separately, while the container build still needs verification on Docker or Render.

The older [API-only Dockerfile](ws2_platform/Dockerfile) requires processed files in its local build context; it is not the new Render entrypoint. The GitHub Pages workflow is retained for manual legacy snapshot publication and no longer runs on pushes. Its existing site is not deleted.

## Project structure and contribution

```text
.github/workflows/      Non-fitting Python/frontend CI; manual legacy Pages snapshot
Dockerfile              Combined React build and live API image for Render
render.yaml             Single Free Render service with GitHub auto-deploy
deployment/             Versioned runtime-data URL and SHA256 manifest
common/                 Shared science utilities, CUDA fits, reference test helpers
contracts/              OpenAPI, data schemas, and bundled API fixtures
data/                   Local raw/interim/processed data and CUDA backups
docs/                   Method, acquisition, training, hosting, and handoff guides
results/                Local reports, launcher logs, and execution profiles
scripts/                Setup, workflows, pipeline, export, and source packaging
tools/                  Contract verification and synthetic-data utilities
ws1_harmonize/          MODIS → VIIRS models, baselines, holdouts, selection
ws2_platform/           Grids, cells, boundaries, FastAPI, and API Dockerfile
ws3_anomaly/            FIRMS ingestion, weather, anomalies, periods, drivers
ws4_outlook/            Intervals, drift checks, and seasonal forecasts
ws5_frontend/           React/Vite bilingual geospatial UI and public snapshot
ws6_validation/         Data QA, API contracts, end-to-end flows, scientific gates
START_HERE.cmd          Windows workflow menu
start.command           Linux/macOS workflow menu
requirements-cuda.txt   Complete locked training environment plus CUDA learner
```

Generate a source handoff with `python scripts/workflow.py share`: it writes `share/firesense-source.zip`, including documentation, fixtures, deployment workflow, CUDA requirements, and the public demo snapshot. It excludes raw data, trained models, secrets, dependencies, Git history, and local run logs. Reinitialize an extracted ZIP using the same setup commands above. To train elsewhere, separately transfer the input directories and weather Parquets in [the training transfer guide](docs/TRAINING.md#2-activate-and-prepare-the-inputs); to serve existing results, transfer the processed runtime files listed above.

Before contributing, run `smoke`; after numerical changes, also run quick/full training and scientific QA as appropriate. Inspect generated fixture changes before committing. Record contract changes in [CONTRACT_CHANGES.md](docs/CONTRACT_CHANGES.md), follow [file ownership](docs/FILE_OWNERSHIP.md) and [Git workflow](docs/GIT_WORKFLOW.md), and keep large datasets out of commits.

For continuation, start with [CLAUDE_HANDOFF.md](docs/CLAUDE_HANDOFF.md), [CUDA_PIPELINE.md](docs/CUDA_PIPELINE.md), and [HOSTING.md](docs/HOSTING.md). Older planning documents can describe superseded states; the dated training reports and current source establish what has been verified. Presentation and scientific limitations remain in [KNOWN_GAPS.md](docs/KNOWN_GAPS.md) and the [submission checklist](docs/SUBMISSION_CHECKLIST.md).
