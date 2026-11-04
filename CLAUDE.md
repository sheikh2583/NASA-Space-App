# FireSense agent entry point

Read `docs/CLAUDE_HANDOFF.md`, `docs/TRAINING.md`, and `docs/TRAINING_RESULTS.md` before changing training logic.

- Start with `git status --short`; preserve unrelated user edits, including any local `codex/` folder.
- Run workflows through the virtual environment: `python scripts/workflow.py smoke`, `prepare`, `train --quick`, or `train`.
- Keep raw datasets, model outputs, `.env`, dependencies, logs, and share archives outside Git. Never print credentials.
- Keep observed VIIRS, adjusted NOAA-20, and modeled MODIS values distinct. Never describe associated weather as a proven cause.
- SNPP archive exports may have `instrument=SNPP`; satellite identity determines VIIRS classification.
- Retain Punjab/Haryana/Delhi filtering and boundary-edge handling. Data outside retained administrative cells must not enter the weekly panel.
- Check metric changes on all holdouts before changing the selected method. B1 currently wins; GPU implementation is not authorized merely by the presence of a GPU.
- Use the task's explicit scope for commits/pushes. Do not overwrite local NASA inputs to recreate a demo.
