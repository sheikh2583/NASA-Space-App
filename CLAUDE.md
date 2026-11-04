# FireSense agent entry point

Read `docs/CLAUDE_HANDOFF.md`, `docs/CLAUDE_REVIEW.md`, `docs/TRAINING.md`, and `docs/TRAINING_RESULTS.md` before changing training logic. The handoff and review supersede the older status/backlog documents under the user's local `codex/` folder.

- Start with `git status --short`; preserve unrelated user edits, including any local `codex/` folder.
- Run workflows through the virtual environment: `python scripts/workflow.py smoke`, `prepare`, `train --quick`, or `train`.
- Keep raw datasets, model outputs, `.env`, dependencies, logs, and share archives outside Git. Never print credentials.
- Keep observed VIIRS, adjusted NOAA-20, and modeled MODIS values distinct. Never describe associated weather as a proven cause.
- SNPP archive exports may have `instrument=SNPP`; satellite identity determines VIIRS classification.
- Retain Punjab/Haryana/Delhi filtering and boundary-edge handling. Data outside retained administrative cells must not enter the weekly panel.
- Check metric changes on all holdouts before changing the selected method. B1 currently wins across both satellite-input configurations; keep it eligible and do not force the GPU candidate to win.
- Use the task's explicit scope for commits/pushes. Do not overwrite local NASA inputs to recreate a demo.
- Hosting is already live on GitHub Pages; successful pushes to main redeploy the static real-data snapshot. Full arbitrary-area queries still require FastAPI.
- The basemap uses OpenStreetMap tiles. Do not restore unauthenticated CARTO URLs or send the NASA FIRMS key to a tile provider or frontend.
- CUDA setup/training is the supported workflow; read `docs/TRAINING.md`, `docs/CUDA_PIPELINE.md`, and `docs/GPU_TRAINING_TIMES.md`. Preserve actual device verification and scientific selection. CPU baselines remain internal for regression/scientific comparison; do not restore obsolete CPU training menus or onboarding commands.
- Area selection follows Dhoa's inspector pattern: country, local name search, administrative selector, Apply, and OSM boundary clicks. Source boundaries are geoBoundaries, not OSM geocoding. Keep the catalog and saved responses in sync; do not reintroduce manual drawing as the main flow.
