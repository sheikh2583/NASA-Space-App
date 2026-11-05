# FireSense: MODIS + VIIRS burning-activity calendar

FireSense combines NASA FIRMS **MODIS** and **VIIRS** fire detections into one consistent weekly fire-activity record for **Bangladesh** and **Punjab–Haryana–Delhi**. Earlier MODIS-era activity is expressed in Suomi NPP VIIRS terms, with uncertainty bands, unusual-period flags, weather associations and an outlook. The English web app runs on React + Vite with a FastAPI backend.

- The release record end is data_through in deployment/runtime.json; the UI reads the actual served end from runtime metadata. Values before 2012 are modeled, weather links are associations (not causes), and historical forecast-skill scores need corrected validation.
- Current numbers, with their sources: [training results](docs/results/training-results.md).
- Hosting: one Render service for the UI and API ([deployment](docs/guides/deployment.md)). [Open FireSense](https://nasa-space-app-e6vz.onrender.com).

> **Coding agents:** read [AGENTS.md](AGENTS.md) first. Training, model fits, CUDA probes and training setup are **human-only**.

## Quickstart

You need Git, 64-bit **Python 3.11**, and **Node 22.12+** for the UI. Training also needs an **NVIDIA GPU** on Windows or Linux. Full prerequisites: [setup](docs/guides/setup.md).

```bash
git clone https://github.com/sheikh2583/NASA-Space-App.git firesense
cd firesense
```

| Goal | Windows (PowerShell) | Linux (Bash) |
|---|---|---|
| 1. Install for UI work (no GPU) | `scripts\setup.ps1 -UiOnly` | `bash scripts/setup.sh --ui-only` |
| 2. See the app with sample data | `scripts\start.ps1 -Mock` | `bash scripts/start.sh --mock` |
| 3. Install for training (human) | `scripts\setup.ps1 -TrainingOnly` | `bash scripts/setup.sh --training-only` |
| 4. Train end to end (human) | `scripts\train.ps1` | `bash scripts/train.sh` |
| 5. See the app with your trained data | `scripts\start.ps1` | `bash scripts/start.sh` |
| Train on a teammate's laptop (human) | `scripts\teammate_train.ps1 -Name you` | `bash scripts/teammate_train.sh --name you` |

On Windows, run a script as `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup.ps1 -UiOnly` (and so on); this works even when script execution is blocked. Training needs the [input data](docs/guides/data.md) first. `train` installs what's missing, builds the weather cache, checks readiness, then runs the quick and full runs, QA and the summary, with logs in `results/logs/`. Details: [training](docs/guides/training.md).

The app opens at <http://127.0.0.1:5173>, and the API docs are at <http://127.0.0.1:8000/docs>.

## Project layout

```text
common/             shared science utilities, CUDA compute helpers, regions and outage registry
contracts/          OpenAPI spec, data schemas, API fixtures
ws1_harmonize/      MODIS → VIIRS harmonization: features, baselines, models, holdouts, selection
ws2_platform/       grid, cells, sensor days, coverage audit, FastAPI app
ws3_anomaly/        FIRMS ingestion, weather loader, anomalies, critical periods, drivers
ws4_outlook/        intervals, drift checks, season profile, outlook
ws5_frontend/       React / Vite English map UI
ws6_validation/     data QA, API contracts, end-to-end checks, scientific gates
scripts/            setup / train / start / teammate_train (.ps1 + .sh), workflow.py, pipeline, packaging, plan tool
  git/              branch / PR helpers and the ownership guard
  tests/            script tests
tools/              contract verification, synthetic data
docs/               guides, science, results, plan and project docs (index: docs/README.md)
data/               local inputs and outputs (not in Git; see data/README.md)
results/            local run summaries and logs (not in Git)
deployment/         pinned runtime-data URL + SHA256 for the Render image
Dockerfile          Render image: builds the UI, serves UI + API, never trains
render.yaml         Render blueprint
```

## Common commands

All workflows go through `scripts/workflow.py` (use `.venv\Scripts\python` on Windows):

```bash
.venv/bin/python scripts/workflow.py dev --mock --open   # mock UI + API
.venv/bin/python scripts/workflow.py results             # rebuild results/latest.md from saved outputs
.venv/bin/python scripts/workflow.py share               # source-only ZIP in share/ (no data, keys or .venv)
.venv/bin/python scripts/plan.py next                    # next card in the work plan
```

`prepare`, `train`, `gpu-check`, `smoke`, `test` and `all` are human-only, because they fit models.

## Documentation

Everything is indexed in **[docs/README.md](docs/README.md)**. Most-used pages: [setup](docs/guides/setup.md) · [data](docs/guides/data.md) · [training](docs/guides/training.md) · [teammate training](docs/guides/teammate-training.md) · [deployment](docs/guides/deployment.md) · [debugging](docs/guides/debugging.md) · [contributing](CONTRIBUTING.md).

## Credits

NASA FIRMS (MODIS C6.1, VIIRS 375 m) · geoBoundaries ADM1 · MODIS MCD12C1 (LP DAAC) · NASA POWER · OpenStreetMap basemap. Full list with links: [references](docs/REFERENCES.md).

## Licence

Apache-2.0, see [LICENSE](LICENSE). Data products remain under their providers' terms (see [docs/REFERENCES.md](docs/REFERENCES.md)).
