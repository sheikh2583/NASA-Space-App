# Claude handoff

## Project and state

FireSense is a React/Vite + FastAPI application backed by Python MODIS/VIIRS harmonization, anomaly detection, and seasonal outlook workflows. Source folders remain divided into six workstreams; `common/` and `contracts/` define shared behavior.

The full real-data run on 4 November 2026 passed all five QA groups. It processed 4,336,082 detections into 778,256 harmonized rows, using 2,354 active cells. All 2,098,157 SNPP rows normalize to VIIRS with valid confidence. Retained cells have no missing administrative IDs.

B1 mean held-out CCC: 0.9417; LightGBM: 0.9351. Nominal 90% bands covered 91.6% weekly and 93.7% monthly held-out totals. The complete metrics are in local `data/processed/validation/` and the dated summary is `docs/TRAINING_RESULTS.md`.

## Entry points

- Windows: double-click `START_HERE.cmd`.
- Linux/macOS: `bash start.command`.
- Scripts: `scripts/workflow.py` dispatches Prepare, Smoke, Train, Validate, Results, Test, Build, Dev, Share, and All.
- `scripts/prepare_training.py` checks local real inputs without printing secrets.
- `scripts/smoke.py` tests unit modules, fixture API, existing real outputs, translations, and UI build without retraining.
- `scripts/share_zip.py` produces an allowlisted source ZIP; test that `.env`, raw data, models, dependencies, and generated output never enter it.

The source ZIP has contract fixtures but no NASA data or virtual environment. Setup + Mock UI must work independently of real inputs. Training requires separate NASA downloads and a successful readiness check.

## Known constraints

- The installed LightGBM 4.7.0 is CPU-only. GPU probe failed with “GPU Tree Learner was not enabled in this build.”
- Current model code caps training at two CPU threads. RTX 4070 Laptop is detected locally; RTX 3090 was discussed but not benchmarked or accessed.
- Full run observed: about 12 minutes total, model stage 399 seconds. Do not claim estimated GPU times as measured results.
- Fixed output paths mean concurrent pipeline runs in one checkout are unsafe.
- Pipeline fixture generation modifies tracked examples; inspect those changes and preserve the intended fixture baseline unless the task explicitly calls for updating it.
- Manual FIRMS viewer comparison, fluent Bangla review, and device checks remain presentation/science tasks.
- Current satellite windows, UI record dates, and documentation assume the November 2026 snapshot.

## Verification and next work

Use `smoke` for routine integration checks, `train --quick` for a changed ingestion/model path, and full `train` before reporting final comparisons. Inspect QA JSON as well as exit status. UI launch checks server startup, and browser rendering should be checked on both demo areas and at phone width after interface changes.

Potential follow-up work, only if requested: configurable CPU threads, cached feature construction, measured OpenCL/CUDA experiments, improved run provenance, automatic date discovery, stronger input completeness validation, and production hosting. Preserve leakage-safe spatial/time holdouts and rerun method selection after any numeric backend change.
