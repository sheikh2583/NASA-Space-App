# Training

**Human-only.** Coding agents must not run anything on this page ([AGENTS.md](../../AGENTS.md)).

Training needs an NVIDIA GPU on Windows or Linux, the [setup](setup.md) in training or everything mode, and the [input data](data.md). Training a teammate's laptop from an input ZIP? Use [teammate training](teammate-training.md) instead.

## The one command

It runs: setup (if `.venv` is missing) → weather cache (if missing) → readiness → **quick run** → pause → **full run** → QA → results summary.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\train.ps1
```

```bash
bash scripts/train.sh
```

It stops at the first failure and tells you which log to read. Every step is logged to `results/logs/<timestamp>-<step>.log`. Rerunning is safe.

| Option | Windows | Linux |
|---|---|---|
| Only the quick run | `-QuickOnly` | `--quick-only` |
| Skip the quick run | `-SkipQuick` | `--skip-quick` |
| Don't pause between quick and full | `-Yes` | `--yes` |
| Resume a failed run at a stage | `-From intervals` | `--from intervals` |
| Also build the deployment ZIP | `-Pack` | `--pack` |
| GPU / helper threads | `-GpuId 0 -Threads 8` | `--gpu-id 0 --threads 8` |
| Python 3.11 for a new `.venv` | `-PythonExecutable PATH` | `--python PATH` |

**Before you start:** plug in the laptop, turn off sleep, close other GPU work, and keep the input files unchanged until the run ends. Run **one pipeline per checkout**, because stages share output paths. Stop the local API while its data is replaced. On Linux, run inside `tmux` so a closed window doesn't kill the run.

## What happens, step by step

The same steps as manual commands (use `.venv\Scripts\python` on Windows):

```bash
.venv/bin/python -m ws3_anomaly.loaders.weather --start 2000-11-01 --end 2026-11-03     # only if weather_*.parquet is missing
.venv/bin/python scripts/workflow.py prepare --gpu-id 0 --threads 8                      # must print READY: 0 blocking check(s)
.venv/bin/python -u scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8 --quick
.venv/bin/python -u scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8
.venv/bin/python scripts/workflow.py validate
.venv/bin/python scripts/workflow.py results
```

- **Readiness** checks imports, every input file, at least 5 GiB free disk, and a real CUDA fit. It doesn't check satellite coverage or scientific quality.
- **Quick run** uses fewer holdouts (spatial and backward) but still rebuilds the whole downstream science. It isn't final evidence.
- **Full run** uses all six holdouts with both Terra+Aqua and Terra-only inputs. Run it before reporting any model comparison.
- Selection uses held-out agreement (CCC). The current method is **B1**, and a successful CUDA fit doesn't force the learned model to win ([training results](../results/training-results.md)). Never bypass a failing scientific gate.

Stage order: `synth (skipped for real inputs) → ingest → grid → cells → sensors → panel → v0 → model → intervals → interval_report → drift → v1 → anomalies → outlook → validation → fixtures → qa → results`.

## How long it takes

| Run | RTX 4070 Laptop 8 GB | RTX 3090 Desktop 24 GB |
|---|---:|---:|
| Quick | 12–20 min | 10–18 min |
| Full | 18–25 min | 13–22 min |

These are planning ranges for the current 4.34-million-detection input with the weather cached. They aren't benchmarks, and the 3090 hasn't been measured; see [GPU time estimates](../results/gpu-training-times.md). Installation, downloads and the first weather build (20–40 min) are extra.

## Watching progress

This is a tree-model pipeline, so there's no epoch counter or percentage bar. The console prints `== <stage>` lines and stage times. You can also watch:

- the GPU, from a second terminal: `nvidia-smi -l 2` (Ctrl+C stops it). Low GPU use during file, geospatial and statistics stages is normal.
- `results/runs/<timestamp>/execution.json`: status, stages done, elapsed times, hardware, backup path.
- `results/runs/<timestamp>/cuda-fits.jsonl`: every verified GPU fit.

Every run first backs up the existing outputs to `data/runs/<timestamp>/baseline/`, so budget disk space for that.

## Accepting a run

Accept a full run only when **all** of these hold:

- The command finished with exit code 0 and printed `Pipeline complete`.
- `execution.json` says `status: passed`, `quick: false` and `start_stage: null`. A resumed run is valid, but its time doesn't count as a full-run benchmark.
- `data/interim/sheikh/method.json` records the selected method and agreement for both Terra+Aqua and Terra-only.
- All five QA groups pass (`data/processed/validation/`, `results/latest.md`), including the historical seam. Read the interval coverage and forecast skill; don't assume them from the exit code.

| Output | Where |
|---|---|
| Selected method, holdout scores, learned models | `data/interim/sheikh/` |
| Harmonized record, anomalies, periods, drivers, outlooks | `data/processed/` |
| Scientific QA and validation | `data/processed/validation/` |
| Summary (human / machine) | `results/latest.md` / `results/latest.json` |
| Stage timings, status, CUDA fit log | `results/runs/<timestamp>/` |

Keep the execution report, CUDA log, console logs, `method.json`, metrics and the summary together with the run's Git commit. Keep the backup until the new results have been reviewed.

## When something fails

Fix the cause, then resume **at the failed stage with the same settings**. The run prints the exact resume command.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\train.ps1 -From intervals
```

```bash
bash scripts/train.sh --from intervals          # add --quick-only if the failed run was quick
```

If inputs or upstream code changed, restart from the earliest affected stage. Avoid the internal `--reuse-metrics` flag. Ctrl+C stops a run without a checkpoint. If the power fails, `execution.json` can still say `running`.

| Failure | What to do |
|---|---|
| Setup / import errors | Rerun setup in training mode and read the **first** error. `pip check` must pass. |
| `nvidia-smi` or the CUDA probe fails | Fix the driver, check the GPU ID, reboot, rerun. CPU training is rejected on purpose. |
| `NOT READY` | Add the exact file readiness names ([data guide](data.md)), then rerun. |
| `Training requires CUDA` | Remove any old `FIRESENSE_BACKEND=cpu` from your shell or environment. |
| Out of GPU memory | Stop other GPU jobs and confirm the GPU ID, then resume. There's no batch-size option. |
| Scientific QA fails | Read `results/latest.md` and the validation JSON, fix the cause, and rebuild from the affected stage. |

For bug reports, see [debugging](debugging.md).

## After a good full run

- Look at it locally: `scripts\start.ps1` / `bash scripts/start.sh` (needs the UI setup).
- Publish it: build the runtime ZIP (`-Pack` / `--pack`, or `python scripts/runtime_bundle.py pack`), then follow [deployment](deployment.md#data-delivery-and-updates).
- Record the measured numbers, with their source and date, in [training results](../results/training-results.md).

Background: [CUDA pipeline](../science/cuda-pipeline.md), [CUDA evidence](../results/cuda-results.md).
