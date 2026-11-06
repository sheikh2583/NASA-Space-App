# FireSense agent entry point

Read [AGENTS.md](AGENTS.md) first. **Policy updated 6 November 2026: Sheikh explicitly authorizes agent-operated training, fitting, calibration, readiness probes, fitting tests and integrated validation.** This replaces the earlier no-training policy and H03 training freeze. Preserve baselines and use attributable scientific runs; see [authorization](docs/project/training-authorization.md).

Work plan: run `python scripts/plan.py next` and follow `docs/plan/README.md` section 3 (the loop), with scientific execution governed by `AGENTS.md`.

Read `docs/agents/claude-handoff.md`, `docs/agents/claude-review.md`, `docs/guides/training.md`, and `docs/results/training-results.md` before changing training logic. The handoff and review supersede the older status/backlog documents under the user's local `codex/` folder.

- Start with `git status --short`; preserve unrelated user edits, including any local `codex/` folder.
- Use the project virtual environment. Inspect execution paths first; keep routine checks non-fitting and run fitting tests, full suites and scientific stages in the documented scientific-run workflow.
- Keep raw datasets, model outputs, `.env`, dependencies, logs, and share archives outside Git. Never print credentials.
- Keep observed VIIRS, adjusted NOAA-20, and modeled MODIS values distinct. Never describe associated weather as a proven cause.
- SNPP archive exports may have `instrument=SNPP`; satellite identity determines VIIRS classification.
- Retain Punjab/Haryana/Delhi filtering and boundary-edge handling. Data outside retained administrative cells must not enter the weekly panel.
- Changing the selected method requires validation across all holdouts. Agents may generate new fits and selection outputs after preserving the baseline. Historical results favor B1 across both satellite-input configurations; keep it eligible and do not force the GPU candidate to win.
- Use the task's explicit scope for commits/pushes. Do not overwrite local NASA inputs to recreate a demo.
- Primary hosting is a single Render Docker service serving the UI and live FastAPI from one origin; read `docs/guides/deployment.md`. Deployment configuration is prepared, but do not claim it is live without checking the assigned Render URL. Root `Dockerfile` downloads pinned existing runtime artifacts without training. GitHub Pages, snapshot mode and the static fallback are retired. There is no CI test workflow; `pr-guard.yml` checks path ownership only, and Render's Docker build runs the frontend tests.
- The basemap uses OpenStreetMap tiles. Do not restore unauthenticated CARTO URLs or send the NASA FIRMS key to a tile provider or frontend.
- Training requires CUDA; read `docs/guides/training.md`, `docs/science/cuda-pipeline.md`, and `docs/results/gpu-training-times.md` before execution. Public CLIs reject CPU training. Preserve device verification and scientific selection, including for agent-operated runs. Do not restore obsolete CPU training menus or onboarding commands.
- Area selection follows Dhoa's inspector pattern: country, local name search, administrative selector, Apply, and OSM boundary clicks. Source boundaries are geoBoundaries, not OSM geocoding. Keep the catalog and saved responses in sync; do not reintroduce manual drawing as the main flow.
