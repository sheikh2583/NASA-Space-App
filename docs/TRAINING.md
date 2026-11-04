# Clickable workflows and training guide

CUDA update: training and readiness workflows now default to the NVIDIA CUDA backend. Choose menu 11 to install optional GPU dependencies, 12 to verify an actual GPU fit, 4/5 for quick/full CUDA training, or 13 for CPU training. Use `--backend cpu` for CPU-only machines. Read [CUDA_PIPELINE.md](CUDA_PIPELINE.md) for exact stage placement, backups, and execution logs.

On Windows, double-click **START_HERE.cmd** at the project root. The menu keeps the window open after success or failure. Choose Setup once on a new machine; all other choices use `.venv` without reinstalling packages.

On Linux/macOS run `bash start.command`. macOS can also launch it from Finder after `chmod +x start.command`. Linux double-click behavior depends on the file manager; the terminal command always works. Windows requires Python 3.11 and Node.js/npm; a source ZIP does not require Git.

| Menu | Workflow | Expected behavior |
|---|---|---|
| 1 | Setup | Create `.venv`, install Python and npm packages, copy example environment files only when absent |
| 2 | Prepare | Check imports, input files, weather caches, and disk space; return a nonzero exit code if missing |
| 3 | Smoke | Unit tests, fixture API, real-output QA when present, translations, frontend tests, production UI build |
| 4 | Quick training | Require real inputs, then run the pipeline with reduced model holdouts |
| 5 | Full training | Require real inputs, run all holdouts and every downstream stage |
| 6 | Trained UI | Start API and UI, open browser when ready; Ctrl+C stops both |
| 7 | Mock UI | Same UI using bundled contract fixtures; no NASA downloads needed; synthetic badge |
| 8 | Results | Refresh `results/latest.md` and `results/latest.json` from local validation files |
| 9 | Share | Generate `share/firesense-source.zip` without secrets, datasets, dependencies, or Git history |
| 10 | All | Full training, Python/frontend tests, and production build |

For automation, use `START_HERE.cmd -Action smoke` (Windows), `bash start.command smoke` (Linux/macOS), or the environment's Python with `scripts/workflow.py smoke`. Valid actions are shown in `scripts/workflow.py --help`. Menu logs are saved under `results/logs/`; keep a single training run active per checkout because outputs use fixed paths.

## Prepare real inputs

Download FIRMS CSV/CSV.GZ archives for Bangladesh and Punjab–Haryana–Delhi and save them under `data/raw/firms/`. Include MODIS Terra/Aqua and VIIRS SNPP/NOAA-20; NOAA-21 is optional. Retain `satellite`, `instrument`, `confidence`, coordinates, date/time, FRP, and source-type columns. The pipeline selects real files and ignores filenames containing `synthetic_`.

Put `BGD_ADM1.geojson` and `IND_ADM1.geojson` under `data/raw/boundaries/`. Put the original `MCD12C1*.hdf` under `data/raw/landcover/`. This launch workflow requires land cover for reproducible training, although the lower-level pipeline supports a degraded fallback.

Complete NASA POWER weather acquisition using the environment's Python:

```bash
python -m ws3_anomaly.loaders.weather --start 2000-11-01 --end 2026-11-03
```

This should produce `data/interim/monazir/weather_BD.parquet` and `weather_PB.parquet`. Raw tiles in `data/raw/power/` are resumable. A FIRMS MAP_KEY is needed only for API updates, not for training downloaded archives. Store it in `.env`; never paste it into a handoff or frontend configuration.

Readiness checks confirm presence and imports, not scientific completeness. Inspect the actual satellite/date coverage and run data QA after ingestion. The current configured record ends in November 2026; extending it requires reviewing satellite windows, dates, and frontend settings.

## Run sequence

1. Setup on a new machine.
2. Prepare and resolve any FAIL lines.
3. Smoke to verify software and, when available, existing outputs.
4. Quick training when changing data or model logic.
5. Full training for the final model comparison.
6. Smoke again, then open the trained UI and inspect Bangladesh, Punjab, Validation, and Method views.

The original CPU full run on the current i7-14650HX took about 12 minutes, with 6 minutes 39 seconds in the model stage. This is an observation from one run, not a runtime guarantee. The installed LightGBM build remains CPU-only; the new CUDA path uses XGBoost with its own holdout evaluation. GPU hardware alone does not accelerate the legacy CPU path.

## Outputs and resume

Main artifacts: `data/processed/harmonized.parquet`, `data/processed/predictions_oof.parquet`, `data/processed/validation/`, and model parameters under `data/interim/sheikh/`. Read [TRAINING_RESULTS.md](TRAINING_RESULTS.md) for the completed full-run baseline.

After a failure, resolve the error and run:

```bash
python scripts/workflow.py train --from model
```

Use `--quick` only when you intend reduced holdouts. Training launchers check real inputs first; the lower-level `scripts/run_pipeline.py` still supports synthetic development data when real inputs are absent. Smoke tests never launch that fallback pipeline.

If ports 8000 or 5173 are busy, stop the previous project instance before launching another. Setup and test errors return nonzero exit codes. Avoid closing the console with the window X while servers are running; Ctrl+C allows cleanup.

## Minimal ZIP and handoff

The ZIP is a source handoff, not a trained-data bundle. Extract it to a normal writable folder, run Setup, then Mock UI to render the application immediately. Obtain the NASA datasets separately before Prepare/Train. See `CLAUDE.md` and [CLAUDE_HANDOFF.md](CLAUDE_HANDOFF.md) for continuation instructions.
