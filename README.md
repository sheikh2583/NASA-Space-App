# FireSense — MODIS + VIIRS Burning Activity

FireSense combines NASA FIRMS MODIS and VIIRS observations into a consistent fire-activity record for **Bangladesh and Punjab–Haryana–Delhi**. It estimates earlier activity in VIIRS terms, reports uncertainty, flags unusual periods, describes weather associations, and presents results in English and Bangla through React/Vite and FastAPI.

[Live demo](https://sheikh2583.github.io/NASA-Space-App/) · [Training guide](docs/TRAINING.md) · [GPU time estimates](docs/GPU_TRAINING_TIMES.md) · [Claude handoff](docs/CLAUDE_HANDOFF.md)

## Choose your starting point

| Goal | What you need | Start here |
|---|---|---|
| View the project | A browser | [Live demo](https://sheikh2583.github.io/NASA-Space-App/) |
| Develop or debug the UI/API | Python, Node.js, source code; no NASA account or GPU | [Initialize](#initialize-a-fresh-checkout), then Mock UI |
| Train on real observations | NASA files, boundaries, land cover, weather cache | [Prepare data](#prepare-real-training-data), then [train](#train-and-validate) |
| Set up CUDA training | Supported Windows/Linux NVIDIA environment | [CUDA dependencies](#cuda-training-dependencies) |
| Publish your own demo | A GitHub repository with Pages available | [Deploy](#deploy-the-demo) |

**Three operating modes:** Mock UI uses bundled synthetic contract fixtures. Local trained UI queries your processed real data through FastAPI. The hosted demo serves committed real-data results for 11 administrative regions and two smaller example areas. A source checkout includes fixtures, named boundaries, and the public snapshot; downloaded NASA files and trained models are separate.

Select a country, filter area names, choose a division/state, and click **Explore area**. You can also select a named boundary on the OpenStreetMap map. No drawing is required. Administrative outlines come from geoBoundaries; OSM supplies the basemap. Filtering names is local and needs no geocoding API key. Mock responses remain example fixtures and do not establish area-specific scientific results.

The configured record ends on **2 November 2026**. Pre-2012 activity is modeled, weather relationships are associations, and forecasts can have no demonstrated skill. Extending the record requires reviewing sensor windows and configured dates; changing an end-date argument alone is insufficient.

## Initialize a fresh checkout

Install **Python 3.11**, **Node.js 22.12+ with npm** (the CI version), and **Git**. Setup installs pinned Python and npm dependencies, creates `.venv`, and copies example environment files only when absent. Allow at least 5 GiB of free space for training intermediates in addition to downloaded inputs and CUDA backups. Internet access is needed for installation, map tiles, and data acquisition.

Clone the repository, or extract the source ZIP and open a terminal in its root. To publish your own copy, fork the repository and clone **your fork's URL** instead.

```sh
git clone https://github.com/sheikh2583/NASA-Space-App.git firesense
cd firesense
```

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

The UI opens at [localhost:5173](http://localhost:5173), with API documentation at [localhost:8000/docs](http://localhost:8000/docs). Choose a demo area to load fixture responses. **Ctrl+C** stops both servers. Setup does not download the scientific datasets.

For the commands below, activate the environment once in each new terminal, from the repository root:

| Shell | Activate |
|---|---|
| PowerShell | `.\.venv\Scripts\Activate.ps1` |
| Bash | `source .venv/bin/activate` |

After activation, `python` means the project's interpreter. If PowerShell blocks activation, use `.venv\Scripts\python` in place of `python`; activation is optional. Verify with `python -c "import sys; print(sys.executable)"`.

Run the integration check after stopping the development servers:

```sh
python scripts/workflow.py smoke
```

Smoke runs unit/script tests, a fixture API request, frontend tests, translations, and a production build. It also validates real outputs when present; it skips that part in a fresh checkout. It does not train or download data. Hardware tests remain skipped unless explicitly enabled.

### Clickable launchers

Windows: double-click **START_HERE.cmd**. Linux/macOS: `bash start.command`. The menus provide:

| Option | Action | Requirement |
|---|---|---|
| 1 / 12 | Setup complete CUDA environment / Verify an actual GPU fit | NVIDIA Windows/Linux |
| 11 / 7 / 3 | Setup UI development / Mock UI / Smoke | No NASA data or GPU |
| 2 / 4 / 5 | Prepare / Quick training / Full training | Real inputs; CUDA by default |
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

For an existing environment, the complete dependency manifest and standalone probe are:

```sh
python -m pip install -r requirements-cuda.txt
python scripts/workflow.py gpu-check --gpu-id 0 --threads 8
```

The check trains and predicts a real model, then verifies its CUDA device. A missing/unusable GPU raises an error; a CUDA request cannot silently switch to CPU. `nvidia-smi` alone is not sufficient verification.

`workflow.py prepare`, `train`, and `all`, and `scripts/run_pipeline.py` default to CUDA with eight CPU helper threads. Scientific baselines and CPU test paths remain internal for comparison and CI. The supported training instructions use CUDA throughout; data preparation still uses the host CPU.

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

Setup creates both `.env` files from their examples. Vite reads the frontend's environment file and embeds `VITE_*` values at build time. Restart Vite after local configuration changes; rebuild for deployment. Keep the FIRMS key out of frontend variables, Git, screenshots, and handoff ZIPs. The OpenStreetMap basemap requires no FIRMS/CARTO key; follow its [tile usage policy](https://operations.osmfoundation.org/policies/tiles/).

## Train and validate

Run **one pipeline at a time per checkout**: stages share output paths. Stop the trained API while replacing its data, then restart it to clear in-memory caches.

After GPU verification:

```sh
python scripts/workflow.py prepare --backend cuda --gpu-id 0 --threads 8
python scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8 --quick
python scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8
```

Quick training reduces model holdouts; it still rebuilds downstream science and is separate from `smoke`. The full command runs all six holdouts with both Terra+Aqua and Terra-only checks. Run it before reporting final model comparisons. Selection uses held-out agreement; choosing CUDA does not force selection of the learned model. Never bypass a failing scientific gate to obtain a model or deployment.

After training:

```sh
python scripts/workflow.py validate
python scripts/workflow.py results
python scripts/workflow.py smoke
python scripts/workflow.py dev --open
```

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

### Resume after a failure

Read the failed stage's output and fix its cause first. Then resume at that stage using the **same backend, quick/full setting, GPU ID, and thread configuration**, for example:

```sh
python scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8 --from intervals
```

Append `--quick` only if the original run was quick. Changing the backend requires restarting at `model` or earlier. Changed inputs or upstream logic require rebuilding from the earliest affected stage. Downstream resumption rejects a mismatched stored model backend. Avoid the internal `--reuse-metrics` flag unless the panel and fitting configuration are known unchanged.

Stage order:

```text
ingest → grid → sensors → cells → panel → v0 → model → intervals → drift → v1
       → anomalies → outlook → validation → fixtures → fallback → qa → results
```

The lower-level runner additionally supports synthetic input generation when no real inputs exist; the real-training workflow requires readiness and does not use that fallback. See [pipeline details](docs/PIPELINE.md).

## Debug and test

Start with `python scripts/workflow.py smoke`. To isolate a failure:

```sh
# CPU-safe unit and script tests; no real training data required.
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
| Native geospatial/HDF dependency fails to install | Use Python 3.11, keep the error, and follow [training setup](docs/TRAINING.md). Compatible unpinned installation requires an explicit flag. |
| `NOT READY`, missing files, or real API file-not-found | Complete the named downloads/cache; use `dev --mock` until training is ready. |
| CUDA unavailable or CPU fallback rejected | Check the NVIDIA driver, install `requirements-cuda.txt`, and rerun `gpu-check`. Use UI-only setup while training prerequisites are unresolved. |
| npm EPERM/EBUSY | Stop this project's Vite/test/preview processes before setup. Rerun after the lock is released. |
| Port 8000/5173 busy | Stop the earlier project server with Ctrl+C before relaunching. The launcher deliberately refuses occupied ports. |
| UI cannot reach API | Check API terminal/Network errors and `VITE_API_BASE_URL`; clear snapshot mode for live API development and restart Vite. |
| Stale results or wrong data mode | Restart API after data changes; restart Vite after environment changes. For hosted mode verify the deployed SHA and reload. |
| QA or historical seam fails | Read `results/latest.md`, validation JSON, and failed-stage output. Repair the data/model and rerun affected stages. |
| Map tiles fail | Check browser networking and tile-service availability/policy. The FIRMS key does not authenticate basemap tiles. |

## Deploy the demo

### GitHub Pages — automatic updates on pushes

The included `.github/workflows/pages.yml` builds and publishes a **static snapshot demo**. It requires no NASA key, Python training environment, GPU, or backend hosting. The saved public snapshot is already in `ws5_frontend/public/demo/snapshot.json`.

1. Fork this repository (or push the source and included workflow to a repository you own). Make sure its default/deployment branch is `main`, or update the workflow trigger.
2. Enable Actions in your fork if GitHub asks. Under **Settings → Pages → Build and deployment → Source**, select **GitHub Actions**.
3. Push a commit to `main`, or open **Actions → Deploy live demo → Run workflow**.
4. Wait for both `build` and `deploy` to succeed. Open the URL in the `github-pages` environment. For a project site it is normally `https://<owner>.github.io/<repository>/`; the relative Vite base supports a repository subpath.
5. Open `<site-url>/version.json` and compare its `commit` with your pushed SHA (`git rev-parse HEAD`). Failed checks prevent that revision from replacing the site.

The workflow runs locked npm installation, frontend tests, translations, type checking/build, and deployment on every push to `main`. It does **not** retrain or fetch NASA data. Pages availability depends on repository visibility and your GitHub plan; see [GitHub's workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

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

Open the preview URL printed by Vite. Other static hosts can publish the same `ws5_frontend/dist/` build. Snapshot mode supports the named administrative and example areas with saved weekly history. Arbitrary API AOIs, alternate date/resolution queries, spatial cell layers, and CSV exports require the live API.

### Publish refreshed scientific results

After completing real-data training, inspect its scientific metrics and run:

```sh
python scripts/workflow.py validate
python scripts/export_hosted_demo.py
```

The exporter refreshes both `ws5_frontend/public/demo/areas.json` and `snapshot.json`, with responses for all 11 administrative regions plus two examples. It refuses validation marked as synthetic. Review provenance and the data-through date, which remains **2026-11-02** explicitly. Preview/test the snapshot build above, then commit both files and push to your deployment branch. A normal code push leaves saved scientific data unchanged. Keep raw inputs, `.env`, models, and large processed files outside Git. [Area-selection notes](docs/AREA_SELECTION.md) explain boundary sources, licenses, and supported coverage.

### Full API hosting

GitHub Pages cannot run FastAPI. Full drawn-area queries need a separate HTTPS API service and a frontend build with `VITE_DEMO_MODE` empty and `VITE_API_BASE_URL` set to that public service. A hosted browser cannot use your laptop's `localhost` URL.

After training and QA, the existing container can be built from the repository root on a Docker-capable machine:

```sh
docker build -f ws2_platform/Dockerfile -t firesense-api .
docker run --rm -p 7860:7860 firesense-api
```

The Dockerfile copies processed runtime files into the image. These are ignored by Git, so a repository-only cloud build will fail unless you supply the artifacts. Validate `http://localhost:7860/health` and a demo-area summary before exposing it. The container path has not been freshly verified by the current Windows setup; platform dependency installation may need adjustment. Provider provisioning, HTTPS, artifact delivery, capacity, and automatic backend deployment are separate work. The current API allows all CORS origins and has no authentication/rate limiting; configure access controls for your hosting context. Read [hosting operations](docs/HOSTING.md) for the current boundaries.

## Project structure and contribution

```text
common/                 Shared science utilities and CPU/CUDA backend
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
```

Generate a source handoff with `python scripts/workflow.py share`: it writes `share/firesense-source.zip`, including documentation, fixtures, deployment workflow, optional CUDA requirements, and the public demo snapshot. It excludes raw data, trained models, secrets, dependencies, Git history, and local run logs. Reinitialize an extracted ZIP using the same setup commands above.

Before contributing, run `smoke`; after numerical changes, also run quick/full training and scientific QA as appropriate. Inspect generated fixture changes before committing. Record contract changes in [CONTRACT_CHANGES.md](docs/CONTRACT_CHANGES.md), follow [file ownership](docs/FILE_OWNERSHIP.md) and [Git workflow](docs/GIT_WORKFLOW.md), and keep large datasets out of commits.

For continuation, start with [CLAUDE_HANDOFF.md](docs/CLAUDE_HANDOFF.md), [CUDA_PIPELINE.md](docs/CUDA_PIPELINE.md), and [HOSTING.md](docs/HOSTING.md). Older planning documents can describe superseded states; the dated training reports and current source establish what has been verified. Presentation and scientific limitations remain in [KNOWN_GAPS.md](docs/KNOWN_GAPS.md) and the [submission checklist](docs/SUBMISSION_CHECKLIST.md).
