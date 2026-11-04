# Claude handoff

Updated 4 November 2026, Asia/Dhaka. The current [README](../README.md), [training guide](TRAINING.md), and source supersede older CPU-era setup/training and prototype backlog instructions. The local `codex/` directory is an unchanged historical proposal folder, not a patch queue to apply automatically.

## Repository and entry points

- Workspace: `X:\Nasa Space Apps Challenge\nasa-modis-viirs`.
- Repository: https://github.com/sheikh2583/NASA-Space-App, branch `main`.
- Live demo: https://sheikh2583.github.io/NASA-Space-App/.
- Windows: `START_HERE.cmd`; Linux/macOS: `bash start.command`.
- Shared workflow: `scripts/workflow.py`; training and the low-level pipeline default to CUDA, GPU 0, eight helper threads.

## Initialization and dependencies

Windows `scripts/setup.ps1` and Linux `scripts/setup.sh` create/check the OS-specific Python 3.11 environment and call the shared `scripts/bootstrap.py`. Default setup installs the complete `requirements-cuda.txt` environment (locked base requirements + XGBoost 3.2.0), checks driver/imports/dependencies, runs an actual CUDA probe, installs npm dependencies, preserves `.env`, and creates input folders. Setup never starts a data pipeline.

`-UiOnly` / `--ui-only` supports mock/UI development without NVIDIA, including macOS. Menu 1 is full CUDA setup, 11 is UI-only setup, 12 verifies CUDA, 4/5 run quick/full CUDA training. The obsolete CPU training menu is removed. Base CPU implementations remain internal for tests and scientific comparison.

Unpinned fallback requires explicit `-AllowCompatible` / `--allow-compatible`. Do not silently bypass installation errors or CUDA failures. Stop the project's Vite/test/preview processes before setup on Windows; native npm file locks can otherwise cause EPERM. Init wrappers bootstrap only when needed rather than reinstalling dependencies on each command. Read [TRAINING.md](TRAINING.md) for all options and runtime prerequisites.

Dependency hardening: `-TrainingOnly` / `--training-only` installs/verifies the full Python/CUDA environment without Node/npm or frontend changes, suitable for a headless GPU server or a running local frontend. Full setup checks ports 5173 and 4173. The actual CUDA probe now tests all four pipeline objectives, reports the compiled CUDA version, and restores an inherited audit-log setting without writing probe events into it. GPU numeric fitting settings and scientific outputs are unchanged by this setup update.

## Current science

Local real inputs contain 4,336,082 detections and produce 778,256 harmonized rows. SNPP identity/confidence normalization and retained administrative-cell filtering are implemented. Land cover and POWER weather are present locally but excluded from Git/ZIP.

The first CUDA trial slightly improved Terra+Aqua CCC, but the candidate's Terra-only spatial performance was poor and the historical anomaly-seam QA failed. That trial was rejected. Selection now averages **both Terra+Aqua and Terra-only holdouts**, keeping B1 eligible. Current selection CCC is B1 0.8855 versus XGBoost CUDA 0.8696; **B1 remains selected**. No scientific gate was weakened.

The corrected downstream resume passed all five QA groups and recorded 399 verified CUDA fits (135 drift, 264 quantile outlook). Weekly/monthly coverage is 0.916/0.937. There are 14,927 anomaly rows, 442 critical periods, and demonstrated forecast skill in 4 of 11 regions. The accepted downstream time of 586 seconds excludes earlier stages and repair; it is not a fresh full-run benchmark.

Read [CUDA_RESULTS.md](CUDA_RESULTS.md) for exact local evidence and failed-trial artifacts. The earlier CPU experiment is archived under `docs/archive/`; it is not the current operating guide. No fresh full training was run for the subsequent setup/UI/documentation work. [GPU_TRAINING_TIMES.md](GPU_TRAINING_TIMES.md) gives labeled planning estimates: 4070 Laptop 18–25 minutes full, 3090 13–22 minutes assuming a comparable host. The 3090 has not been measured. Small GPU fits add overhead; no end-to-end speedup is established.

## Named-area explorer

The old drawing-first UX and Leaflet Draw dependency are removed. Inspired by Dhoa's inspector, the UI provides country → English/Bangla name search → division/state → Apply, plus Reset and direct boundary selection. Dhaka's actual administrative outline loads initially. Rectangular/example AOIs are excluded from the primary picker; all 11 regions are also available for comparison. A unique search match becomes the draft selection, “Viewing” identifies the actual applied results, and Reset restores Dhaka. Failed catalogs offer Retry instead of substituting a sample area. Map boundaries support Enter/Space; dates/calendar changes preserve the geographic viewport.

`scripts/export_area_catalog.py` exports original geoBoundaries ADM1 geometry only for loaded regions. There are eight Bangladesh divisions, Punjab/Haryana/Delhi, and two smaller examples. OSM supplies key-free map tiles; geoBoundaries supplies the administrative outlines. Name filtering is entirely local, with no Nominatim/API key. Polygon and MultiPolygon requests are now explicitly documented in the API contract. Refer to [AREA_SELECTION.md](AREA_SELECTION.md) for sources, licenses, boundary vintage, and cell-edge semantics.

`scripts/export_hosted_demo.py` now exports the catalog and all 13 sets of real API responses. The public snapshot was deliberately refreshed from the accepted current local science after QA. The geometry catalog and snapshot total about 8.7 MB uncompressed; these are intentional public artifacts. Exact-area/date matching prevents misleading substitution of another region's results. Synthetic validation is refused. Local mock responses remain fixture examples and are labeled synthetic.

Request-generation checks prevent stale summary/secondary responses from replacing the latest selection; cell-layer responses also use cleanup guards. For interface changes, keep keyboard selectors, Bangla, a no-results state, and supported-area limits clear.

## Hosting and sharing

`.github/workflows/pages.yml` tests/translates/builds and deploys successful pushes to `main`. `version.json` identifies the deployed SHA. A push does not acquire data or retrain. Static hosting supports named saved areas with fixed weekly dates; arbitrary API requests, cell products, and CSV export require FastAPI.

Full API hosting is not provisioned. `ws2_platform/Dockerfile` requires local processed runtime artifacts that are absent from a Git-only cloud build. Provider/artifact/HTTPS/capacity work is separate. The key-free OSM basemap fix remains in place; do not restore unauthenticated CARTO URLs or expose FIRMS_MAP_KEY in the frontend.

Generate `share/firesense-source.zip` with `python scripts/workflow.py share`. It contains source, current docs, fixtures, optional-platform requirements, named boundaries, and the public snapshot, and excludes raw data, trained models, dependencies, credentials, run logs, and `codex/`.

## Verification and remaining work

The Windows CUDA dependency installer was executed successfully on the RTX 4070 Laptop, including `pip check`, scientific imports, real GPU fit/prediction, and clean npm install. Both shell families were syntax-checked; a fresh native Linux installation and RTX 3090 execution remain unverified.

The current selector passed ten frontend tests, translations, type checking, and production snapshot build. Every named area's saved response was checked against its own geometry and selected-cell count. Browser checks covered real Dhaka startup, Bangla name search with pending/applied labels, Apply/Reset, Haryana selection, keyboard map selection, comparison between administrative regions, mobile width without overflow, and desktop rendering with no console errors. Earlier integration runs passed all five real-output QA groups and 55 unit/script tests with two hardware tests skipped. Dependency hardening separately passed 29 common/script tests and two actual CUDA integration tests. No scientific retraining was needed for the selector update.

Keep one pipeline per checkout; output paths remain shared. Inputs/date completeness, representative FIRMS viewer comparison, fluent Bangla review, full backend hosting, and presentation/submission checks remain follow-up work. Read [CLAUDE_REVIEW.md](CLAUDE_REVIEW.md) before changing scientific assumptions; user authorization in this chat takes precedence over historical scope statements.
