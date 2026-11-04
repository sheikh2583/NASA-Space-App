# Contributing

## Ground rules

- **One writer per path.** [File ownership](docs/project/file-ownership.md) names the only person who edits each folder or file. Everyone reads everything. To change someone else's file, ask the owner. A pull-request check (`scripts/git/guard.py`) and local hooks enforce this.
- **Append-only logs:** `data/MANIFEST.md` and [`docs/project/contract-changes.md`](docs/project/contract-changes.md). Add your line at the bottom; never edit earlier lines.
- **Contracts** (`contracts/`): a field may be added; never rename or remove one. Sheikh approves and logs every change in the contract log first.
- **Never commit** data, models, `.env` files, keys, logs, `share/` ZIPs or notebook outputs. `.gitignore` already covers them, so `git add .` is safe.
- **Python packages** are added only through Sheikh (`requirements*.txt`). Web packages go in `ws5_frontend/package.json`.
- **Science wording:** keep observed VIIRS, adjusted NOAA-20 and modeled MODIS distinct; weather is an association, never a cause; detections aren't burned area.

## Coding agents

Read [AGENTS.md](AGENTS.md) first. Agents never run training, model-fitting tests, CUDA probes, readiness checks, or training setup. Those are human-only. The work plan is in [docs/plan/](docs/plan/README.md).

## Everyday git

The maintainer works directly on `main`:

```bash
git pull --ff-only
git add .
git commit -m "What changed"
git push
```

Teammates use the branch and pull-request helpers in `scripts/git/` (`start.sh`, `save.sh`, `ship.sh`, `sync.sh`), which run in Git Bash on Windows. See the [git workflow](docs/guides/git-workflow.md). Branches use your prefix (`ws1/`…`ws6/`). Never force-push `main`.

## Before you push

| Changed | Run |
|---|---|
| Anything | `python -m compileall -q common scripts ws1_harmonize ws2_platform ws3_anomaly ws4_outlook` and `python scripts/plan.py check` |
| Python code | The tests next to your change, e.g. `python -m pytest ws2_platform/tests/test_coverage.py -q` |
| Frontend | `npm test`, `npm run check:strings` and `npm run build` in `ws5_frontend/` |
| Science or numbers (human) | Quick and full training plus QA ([training](docs/guides/training.md)); record the measured numbers in [training results](docs/results/training-results.md) |

More commands and troubleshooting: [debugging](docs/guides/debugging.md).
