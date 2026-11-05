---
id: T40
title: Report the outage-corrected training run and publish it to Render
kind: agent
owner: Sheikh
authors: [Sheikh, Shammo]
phase: P1
size: M
needs: [H02, T16]
requires: [real-data, gh-auth]
branch: ws1/T40-report-outage-run
touches: [docs/results/training-results.md, ws5_frontend/public/demo/areas.json, deployment/runtime.json]
creates: []
checks: ["CHECK-PLAN", "CHECK-TESTS", "CHECK-FILES", "CHECK-WEB"]
---
## Goal
Sheikh has run the full training with the outage handling (`scripts/train.ps1 -Pack`, which includes QA, results
and the runtime ZIP), plus pytest and smoke (H02). Measure what
changed, check it against the spec's acceptance criteria, and put the corrected record on the Render service.
**Don't train, validate or rerun any pipeline stage.** Only read saved outputs.

## Steps
1. Read `data/processed/validation/qa.json` and `results/latest.md`, written by Sheikh's run in H02. All five groups must
   pass. Don't rerun validate: it is human-only.
2. **Compare** with the baseline saved in T06 (`data/interim/baseline_2026-11-04/`), using a short read-only pandas
   script on `metrics.csv` and `method.json`. Make a before → after table:
   - the selection metrics for B1 and the learned candidate, on every holdout in `metrics.csv` (name them as the file
     does);
   - the selected method;
   - weekly and monthly coverage (`validation/intervals.json`);
   - the PB and BD November B1 ratios and the NOAA-20 ratio (`b1_params.pkl`, before and after);
   - the number of SNPP+MODIS overlap weeks;
   - how many (date, sat) rows `coverage_days.parquet` made non-operating, against the count in
     `docs/specs/I8_AUDIT_RESULTS.md`.
3. **Spec criterion A7.** For the Punjab area, show the weekly values for the weeks of 28 Oct and 4 Nov 2024, before
   and after, with their sources. The days 3-6 Nov should now be `adjusted_from_noaa20` (or the week `mixed`).
4. Add a section "Coverage correction (<date>)" to `docs/results/training-results.md`, with the tables from steps 2-3. Mark
   every number "measured, <file or command>, <date>". Keep the existing text unchanged.
5. **Publish.**
   - `python tools/verify_files.py --all` must pass.
   - Run `python scripts/release_runtime.py --data-through <data_through from /health or the processed data>`
     (dry run), then again with `--publish` (T16). This rewrites `deployment/runtime.json`.
   - Refresh the legacy snapshot too: `python scripts/export_hosted_demo.py`.
   - The pipeline's fixtures stage may have rewritten `contracts/fixtures/`. Keep those changes only if they are the
     expected new values; otherwise `git checkout -- contracts/fixtures`.
6. Run the checks, mark the card done, and hand over for commit. After Sheikh pushes and Render rebuilds, run
   `python scripts/check_render.py`, if T17 is done, and paste the result.

## Acceptance
- [ ] The before → after tables are in `docs/results/training-results.md` and in the hand-over, all measured.
- [ ] The corrected 2024 Punjab weeks are served by Render (`check_render.py` passes on the new `data_through` and
  commit).

## Stop and ask if
- Any selection metric drops by more than 0.01.
- Coverage leaves 0.85-0.97.
- The selected method flips. Report it; don't override.
- A QA group failed in H02.
