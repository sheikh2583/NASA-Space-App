# FireSense agent entry point

Read [AGENTS.md](AGENTS.md) first. **Strict no-training policy: coding agents must not run training, model-fitting tests, benchmarks, CUDA probes, readiness checks, or setup paths that fit models.** Training commands in the documentation are for humans. This rule supersedes prior training permissions and older task templates.

Read `docs/CLAUDE_HANDOFF.md`, `docs/CLAUDE_REVIEW.md`, `docs/TRAINING.md`, and `docs/TRAINING_RESULTS.md` before changing training logic. The handoff and review supersede the older status/backlog documents under the user's local `codex/` folder.

- Start with `git status --short`; preserve unrelated user edits, including any local `codex/` folder.
- Use the project virtual environment for permitted checks. Inspect their execution paths first; do not run blanket Python tests or integrated workflows that fit learners. Static checks and reviewed non-fitting tests are allowed.
- Keep raw datasets, model outputs, `.env`, dependencies, logs, and share archives outside Git. Never print credentials.
- Keep observed VIIRS, adjusted NOAA-20, and modeled MODIS values distinct. Never describe associated weather as a proven cause.
- SNPP archive exports may have `instrument=SNPP`; satellite identity determines VIIRS classification.
- Retain Punjab/Haryana/Delhi filtering and boundary-edge handling. Data outside retained administrative cells must not enter the weekly panel.
- Changing the selected method requires human-run validation across all holdouts. Agents may inspect existing metrics and prepare commands, but must not generate new fits or overwrite selection outputs. B1 currently wins across both satellite-input configurations; keep it eligible and do not force the GPU candidate to win.
- Use the task's explicit scope for commits/pushes. Do not overwrite local NASA inputs to recreate a demo.
- Hosting is already live on GitHub Pages; successful pushes to main redeploy the static real-data snapshot. Full arbitrary-area queries still require FastAPI.
- The basemap uses OpenStreetMap tiles. Do not restore unauthenticated CARTO URLs or send the NASA FIRMS key to a tile provider or frontend.
- Human-operated training requires CUDA; read `docs/TRAINING.md`, `docs/CUDA_PIPELINE.md`, and `docs/GPU_TRAINING_TIMES.md` without executing their fitting commands. Public CLIs reject CPU training. Preserve device verification and scientific selection in the implementation; agents must not execute those fits, including reference test learners. Do not restore obsolete CPU training menus or onboarding commands.
- Area selection follows Dhoa's inspector pattern: country, local name search, administrative selector, Apply, and OSM boundary clicks. Source boundaries are geoBoundaries, not OSM geocoding. Keep the catalog and saved responses in sync; do not reintroduce manual drawing as the main flow.
