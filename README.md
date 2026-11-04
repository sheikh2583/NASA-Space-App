# FireSense — MODIS + VIIRS Burning Activity

FireSense turns NASA FIRMS MODIS and VIIRS active-fire observations into a consistent 2000–present record for Bangladesh and Punjab–Haryana–Delhi. It harmonizes satellite eras, quantifies uncertainty, flags unusual periods, describes associated weather conditions, and presents the results in a bilingual web application.

The system uses real FIRMS archives when present and falls back to synthetic development data only when no real files are available. Modeled values and uncertainty are always exposed; associations are not presented as causes.

## Quick start

Requirements: Python 3.11, Node.js LTS, npm, and Git.

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File scripts\init.ps1 -Workflow setup
powershell -ExecutionPolicy Bypass -File scripts\init.ps1 -Workflow train -Quick
powershell -ExecutionPolicy Bypass -File scripts\init.ps1 -Workflow dev
```

### Linux or macOS

```bash
bash scripts/init.sh setup
bash scripts/init.sh train --quick
bash scripts/init.sh dev
```

Open the application at <http://localhost:5173> and API documentation at <http://localhost:8000/docs>.

## Workflows

After setup, the same Python command works on every operating system:

```bash
python scripts/workflow.py train --quick   # real-data smoke training
python scripts/workflow.py train           # full training
python scripts/workflow.py validate        # QA and contract checks
python scripts/workflow.py results         # results/latest.{md,json}
python scripts/workflow.py test            # Python and frontend tests
python scripts/workflow.py build           # production frontend build
python scripts/workflow.py dev             # API + Vite development servers
python scripts/workflow.py dev --mock      # UI against contract fixtures
python scripts/workflow.py all --quick     # train, summarize, test, build
```

Resume a failed stage with `python scripts/workflow.py train --quick --from <stage>`. Stages and artifacts are documented in [docs/PIPELINE.md](docs/PIPELINE.md).

## Project structure

```text
common/                 Shared grids, time splits, intervals, and metrics
contracts/              OpenAPI, JSON/Parquet schemas, and API fixtures
data/                   Local raw/interim/processed data (ignored by Git)
docs/                   Architecture, method, operations, and submission guides
results/                Generated run summaries (latest files ignored by Git)
scripts/                Cross-platform setup, workflows, pipeline, and Git helpers
tools/                  Verification and synthetic-data utilities
ws1_harmonize/          MODIS → VIIRS harmonization and model selection
ws2_platform/           Gridding, land cover, boundaries, FastAPI service
ws3_anomaly/            FIRMS ingestion, anomalies, periods, and drivers
ws4_outlook/            Intervals, drift checks, and seasonal outlook
ws5_frontend/           React/Vite bilingual geospatial application
ws6_validation/         Data, contract, end-to-end, and QA gates
```

## Data setup

Place local inputs under:

```text
data/raw/firms/         FIRMS CSV or compressed CSV files
data/raw/boundaries/    ADM1 GeoJSON files
data/raw/landcover/     MCD12C1 HDF file
data/raw/power/         NASA POWER weather cache
```

Copy `.env.example` to `.env` and set `FIRMS_MAP_KEY` only when recent FIRMS API updates are required. Never commit `.env`, downloaded datasets, processed Parquet files, model outputs, or frontend build artifacts. See [data/README.md](data/README.md) and [docs/SHEIKH_GUIDE.md](docs/SHEIKH_GUIDE.md) for acquisition details.

## Pipeline

```text
FIRMS archives → normalize → daily grid → admin/land-cover cells
              → weekly panel → baseline/model selection → intervals
              → drift correction → harmonized series → anomalies/outlook
              → API fixtures/static fallback → QA → result summary
```

The trained record is written to `data/processed/harmonized.parquet`; validation artifacts go to `data/processed/validation/`; the readable run report is generated at `results/latest.md`.

## Quality gates

The project verifies:

- satellite identity, confidence mapping, temporal coverage, and grid conservation;
- held-out model agreement and leakage-safe splits;
- uncertainty coverage and cross-sensor seam behavior;
- OpenAPI response contracts and complete API flows;
- frontend type checking, unit tests, translations, and production builds.

Run everything with `python scripts/workflow.py all --quick`. Human checks, limitations, and submission tasks are in [docs/QA_CHECKLIST.md](docs/QA_CHECKLIST.md), [docs/KNOWN_GAPS.md](docs/KNOWN_GAPS.md), and [docs/SUBMISSION_CHECKLIST.md](docs/SUBMISSION_CHECKLIST.md).

## Team development

Workstream ownership is documented in [docs/FILE_OWNERSHIP.md](docs/FILE_OWNERSHIP.md). Contract changes must be recorded in [docs/CONTRACT_CHANGES.md](docs/CONTRACT_CHANGES.md). Use [docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md) for branch, review, and release conventions.
