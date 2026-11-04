---
id: T05
title: Run the coverage audit and record the outage decision
kind: agent
owner: Sheikh
authors: [Sheikh, Samiul]
phase: P0
size: M
needs: [T32]
requires: [real-data]
branch: ws1/T05-coverage-audit
touches: [docs/science/decisions.md, docs/project/contract-changes.md]
creates: [docs/specs/I8_AUDIT_RESULTS.md, ws6_validation/coverage_review.md]
checks: [CHECK-PLAN, CHECK-PY]
---
## Goal
Measure what the outage registry would change before anything changes, then record the decision with the documented
defaults. Sheikh's merge of this PR is the sign-off. This card writes reports only; `data/processed/` is untouched.

## Context
- The spec is `docs/specs/I8_COVERAGE.md`.
- `python -m ws2_platform.coverage` reads `data/processed/` (detections, cells, grid_daily, sensor_days) and writes
  only to `data/interim/coverage_audit/`.

## Steps
1. Run `python -m ws2_platform.coverage`. Then open `data/interim/coverage_audit/summary.md` and `pass_windows.csv`.
2. In `pass_windows.csv`, every row for SNPP, NOAA20, Terra and Aqua in BD and PB should say `measured`. If any says
   `default`, write down why (too few detections).
3. Read `contradictions.csv`.
   - For `documented` and `table_and_data` entries it should be empty.
   - For each row: compare the event times with the MODAPS table. If the registry is right, the pass window is too
     wide for that day; write that down.
   - Don't edit `common/outages.yaml` in this card. If an entry is wrong, stop and report it, so T32 can be reopened.
4. Read `candidate_gaps.csv`, but only the burning months: PB Apr-May and Sep-Nov, BD Nov-Apr. Create
   `ws6_validation/coverage_review.md` with one line per candidate: date, region, pass, reference satellite and
   count, and a verdict.
   - The verdict is "add to registry (source: …)", "real zero (reason)" or "unclear".
   - Candidates are never excluded automatically.
5. Create `docs/specs/I8_AUDIT_RESULTS.md` with:
   - the run date and the git commit (`git rev-parse --short HEAD`);
   - the summary numbers;
   - the pass-window table;
   - the four `would_flip_*` counts;
   - how many SNPP+MODIS and SNPP+NOAA-20 **overlap weeks** would leave the fit at each threshold. Count weeks in
     `would_flip_*.csv` whose dates fall inside full-overlap weeks: Monday-Sunday weeks where Terra, Aqua and SNPP
     (or SNPP and NOAA-20) all operated for 7 days, as in `ws1_harmonize/model.py`. Write a short script inline,
     using `pandas` only.
   - **one recommended threshold** (the spec suggests 0.25), with one paragraph of reasons.
6. **Record the decision** as a new numbered entry at the end of `docs/science/decisions.md`, titled "Outage handling (I8)":
   - Option A from the spec;
   - the threshold recommended in step 5;
   - filling excluded Suomi NPP days from NOAA-20 from 1 Apr 2018.

   Add one sentence of reasons per choice. Change the I8 row in `docs/project/contract-changes.md` from "proposed" to
   "approved on merge of T05 (<date>)".
7. Run the checks, mark the card done, then `split` (Sheikh: the spec, decisions and contract files; Samiul: the review
   file), push and open the PR. The PR title starts with "T05 (decision)", so Sheikh sees he is signing off.

## Acceptance
- [ ] `I8_AUDIT_RESULTS.md` contains the commit, the counts at all four thresholds, the lost overlap weeks and one
  recommendation, all marked "measured, <date>".
- [ ] Every burning-month candidate has a verdict in `coverage_review.md`.
- [ ] Nothing under `data/` is committed (`git status` shows no data files).

## Stop and ask if
- Contradictions remain for verified entries.
- The audit can't find `detections.parquet`.
