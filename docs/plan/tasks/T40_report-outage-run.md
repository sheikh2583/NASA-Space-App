---
id: T40
title: Report the outage-corrected training run and republish
kind: agent
owner: Sheikh
authors: [Sheikh, Shammo, Sattyam]
phase: P1
size: M
needs: [H02]
requires: [real-data]
branch: ws1/T40-report-outage-run
touches: [docs/TRAINING_RESULTS.md, ws5_frontend/public/demo/snapshot.json]
creates: []
checks: [CHECK-PLAN, CHECK-PY, CHECK-QA, CHECK-FILES, CHECK-SNAP]
---
## Goal
Sheikh has run the full training with the outage handling (H02). Measure what changed, check it against the spec's
acceptance criteria, and put the corrected record on the site.

## Steps
1. Run `python scripts/workflow.py validate`, then read `data/processed/validation/qa.json`. All five groups must
   pass.
2. **Compare** with the baseline saved in T06 (`data/interim/baseline_2026-11-04/`), using a short pandas script on
   `metrics.csv` and `method.json`. Make a table, before → after:
   - mean held-out CCC for B1 and LightGBM on all six holdouts;
   - the selected method;
   - weekly and monthly coverage (`validation/intervals.json`);
   - the PB and BD November B1 ratios and the NOAA-20 ratio (`b1_params.pkl` before and after);
   - the number of SNPP+MODIS overlap weeks.
3. **Spec criterion A7.** In the Punjab demo area, show the weekly values for the weeks of 28 Oct and 4 Nov 2024,
   before and after, and the sources. The days 3-6 Nov should now be `adjusted_from_noaa20` (or the week `mixed`).
4. Add the section "Coverage correction (<date>)" to `docs/TRAINING_RESULTS.md`, with the tables from steps 2-3.
   Mark every number "measured, <command>, <date>". Keep the 4 Nov section unchanged.
5. Republish with `python scripts/export_hosted_demo.py`. The pipeline's fixtures stage also rewrote
   `contracts/fixtures/`; keep those changes only if they are the expected new values, otherwise
   `git checkout -- contracts/fixtures`.
6. Run the checks, mark the card done, `split`, push and open the PR. Paste both tables into the PR.

## Acceptance
- [ ] The before → after tables are in `TRAINING_RESULTS.md` and in the PR, all measured.
- [ ] The corrected 2024 Punjab weeks are in the snapshot.

## Stop and ask if
- Any held-out CCC drops by more than 0.01.
- Coverage leaves 0.85-0.97.
- The selected method flips. Report it; don't override.
- A QA group fails.
