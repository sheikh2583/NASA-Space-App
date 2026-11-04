# FireSense — MODIS + VIIRS Burning Activity

FireSense combines NASA FIRMS MODIS and VIIRS observations into a consistent fire-activity record for **Bangladesh and Punjab–Haryana–Delhi**. It estimates earlier activity in VIIRS terms, reports uncertainty, flags unusual periods, describes weather associations, and presents results in English and Bangla through React/Vite and FastAPI.

[Live demo](https://sheikh2583.github.io/NASA-Space-App/) · [Training guide](docs/TRAINING.md) · [GPU time estimates](docs/GPU_TRAINING_TIMES.md) · [Claude handoff](docs/CLAUDE_HANDOFF.md)

**Operator guide — updated 4 November 2026.** Start from the repository root and run each command only after the previous one succeeds. Setup, data acquisition, training, and publication are separate steps.

**Coding agents: strict no training.** Read [AGENTS.md](AGENTS.md) before working here. Training, model-fit probes, readiness checks, default/training-only setup, and tests that fit models are **human-only**. Agents may edit code, run reviewed checks without fitting, and deploy existing validated outputs. The operator commands below do not grant agents permission to train.

[Initialize](#initialize-a-fresh-checkout) · [CUDA setup](#cuda-training-dependencies) · [Data and keys](#prepare-real-training-data) · [Train](#train-and-validate) · [Debug](#debug-and-test) · [Deploy](#deploy-the-demo) · [Project structure](#project-structure-and-contribution)

## Choose your starting point

| Goal | What you need | Start here |
|---|---|---|
| View the project | A browser | [Live demo](https://sheikh2583.github.io/NASA-Space-App/) |
| Develop or debug the UI/API | Python, Node.js, source code; no NASA account or GPU | [Initialize](#initialize-a-fresh-checkout), then Mock UI |
| Train on real observations | NASA files, boundaries, land cover, weather cache | [Prepare data](#prepare-real-training-data), then [train](#train-and-validate) |
| Set up CUDA training | Supported Windows/Linux NVIDIA environment | [CUDA dependencies](#cuda-training-dependencies) |
| Publish your own demo | A GitHub repository with Pages available | [Deploy](#deploy-the-demo) |

**Three operating modes:** Mock UI uses bundled synthetic contract fixtures. Local trained UI queries your processed real data through FastAPI. The hosted explorer serves committed real-data results for 11 administrative regions. A source checkout includes fixtures, named boundaries, and the public snapshot; downloaded NASA files and trained models are separate.

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

Setup creates `.venv`, installs pinned dependencies, and copies example environment files only when absent. Training-only setup creates only the root `.env`. Recreate environments on each OS rather than transferring `.venv` or `node_modules`. Allow at least 5 GiB of free space for training intermediates **plus** downloaded inputs and backups of existing outputs. Internet access is needed for installation, map tiles, and data acquisition.

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

Choose a deployment mode before building:

| Target | What is served | Required artifacts | What updates on push |
|---|---|---|---|
| Included GitHub Pages workflow | Static named-area explorer | Committed `areas.json` and `snapshot.json` | Frontend code and committed snapshot; no retraining |
| Another static host | The same snapshot build | `ws5_frontend/dist/` built in snapshot mode | Depends on that host's configuration |
| Full API plus frontend | Queries against processed runtime data | Separate API service, processed artifacts, public API URL, frontend build | Backend automation must be provisioned separately |

### GitHub Pages — automatic updates on pushes

The included `.github/workflows/pages.yml` builds and publishes a **static snapshot demo**. It requires no NASA key, Python training environment, GPU, or backend hosting. The saved public snapshot is already in `ws5_frontend/public/demo/snapshot.json`.

1. Fork this repository (or push the source and included workflow to a repository you own). Make sure its default/deployment branch is `main`, or update the workflow trigger.
2. Enable Actions in your fork if GitHub asks. Under **Settings → Pages → Build and deployment → Source**, select **GitHub Actions**.
3. Push a commit to `main`, or open **Actions → Deploy live demo → Run workflow**.
4. Wait for both `build` and `deploy` to succeed. Open the URL in the `github-pages` environment. For a project site it is normally `https://<owner>.github.io/<repository>/`; the relative Vite base supports a repository subpath.
5. Open `<site-url>/version.json` and compare its `commit` with your pushed SHA (`git rev-parse HEAD`). Failed checks prevent that revision from replacing the site.

The workflow runs locked npm installation, frontend tests, translations, type checking/build, and deployment on every push to `main`. It does **not** retrain or fetch NASA data. Pages availability depends on repository visibility and your GitHub plan; see [GitHub's workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

The separate `ci` workflow checks Python contracts/tests and the frontend. Pages depends on its own frontend checks, not on the separate Python job. Check both workflow results before treating a pushed change as verified. If Pages fails, open its failed job log, fix the reported test/build/permission/environment issue, and push the fix or rerun the workflow. Verify `version.json` again after deployment.

`scripts/github_pages.py` is a maintainer helper hardcoded to `sheikh2583/NASA-Space-App`; use repository Settings/Actions for your own fork. Do not run its `--enable` action expecting it to configure another repository.

### Preview the hosted build locally

With dependencies installed, from the repository root:

```powershell
# PowerShell
cd ws5_frontend
$env:VITE_DEMO_MODE = 'snapshot'
$env:VITE_DATA_MODE = 'real'
npm test
npm run check:strings
npm run build
npm run preview -- --host 127.0.0.1
# After Ctrl+C, clear shell overrides before returning to API development.
Remove-Item Env:VITE_DEMO_MODE, Env:VITE_DATA_MODE -ErrorAction SilentlyContinue
cd ..
```

```bash
# Bash
cd ws5_frontend
npm test
npm run check:strings
VITE_DEMO_MODE=snapshot VITE_DATA_MODE=real npm run build
npm run preview -- --host 127.0.0.1
# After Ctrl+C:
cd ..
```

Open the preview URL printed by Vite. Other static hosts can publish the same `ws5_frontend/dist/` build. Snapshot mode exposes the 11 named administrative regions with saved weekly history, including comparison between regions. Arbitrary API AOIs, alternate date/resolution queries, spatial cell layers, and CSV exports require the live API.

### Publish refreshed scientific results

After completing real-data training, inspect its scientific metrics and run:

```sh
python scripts/workflow.py validate
python scripts/export_hosted_demo.py
```

The exporter refreshes both `ws5_frontend/public/demo/areas.json` and `snapshot.json`, with responses for all 11 administrative regions plus two examples. It refuses validation marked as synthetic. Review provenance and the data-through date, which remains **2026-11-02** explicitly. Preview/test the snapshot build above, then commit both files and push to your deployment branch:

```sh
git diff --stat -- ws5_frontend/public/demo
git add ws5_frontend/public/demo/areas.json ws5_frontend/public/demo/snapshot.json
git commit -m "Refresh validated public demo results"
git push origin main
```

Use your deployment branch instead of `main` if you changed the workflow trigger. A normal code push leaves saved scientific data unchanged. Keep raw inputs, `.env`, models, and large processed files outside Git. [Area-selection notes](docs/AREA_SELECTION.md) explain boundary sources, licenses, and supported coverage.

### Full API hosting

GitHub Pages cannot run FastAPI. Arbitrary geometry/date queries need a separate HTTPS API service. For that frontend build, set `VITE_DEMO_MODE` empty, `VITE_DATA_MODE=real`, and `VITE_API_BASE_URL` to the public service in `ws5_frontend/.env`, then run `npm run build --prefix ws5_frontend` and publish `ws5_frontend/dist/`. The included Pages workflow explicitly forces snapshot mode; change its build environment if adapting it for a live API. A hosted browser cannot use your laptop's `localhost` URL.

After training and QA, the existing container can be built from the repository root on a Docker-capable machine:

```sh
docker build -f ws2_platform/Dockerfile -t firesense-api .
docker run --rm -p 7860:7860 firesense-api
```

The Dockerfile expects these paths under `data/processed/`: `cells.parquet`, `harmonized.parquet`, `sensor_days.parquet`, `interval_table.json`, `drivers_region.json`, `outlook_region.json`, and `validation/`. They are ignored by Git, so a repository-only cloud build will fail unless you supply the artifacts. The serving container uses processed outputs; it does not train models.

Validate `http://localhost:7860/health` and a demo-area summary through `http://localhost:7860/docs` before exposing it. Restart the API after replacing runtime data. The container path has not been freshly verified by the current Windows setup; platform dependency installation may need adjustment. Provider provisioning, HTTPS, artifact delivery, capacity, and automatic backend deployment are separate work. The current API allows all CORS origins and has no authentication/rate limiting; configure access controls for your hosting context. Read [hosting operations](docs/HOSTING.md) for the current boundaries.

## Project structure and contribution

```text
.github/workflows/      Python/frontend CI and push-to-main Pages deployment
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
