# Phase prompts: Samin (Team Member 4). Detailed sub-prompts: prompts/ws4_samin.md

## PHASE 1: Kickoff (H0-3)
```
GOAL: Know what each consumer needs from common/, then start series.py.
STEPS:
1. Ask Sattyam which columns he needs from weekly_series; ask Monazir which climatology functions he needs; ask Sheikh to agree the split labels (block_id % 5: 0 calib, 1 test).
2. Run P4.1 (series.py) on a tiny synthetic harmonized table.
DELIVER: series.py draft with tests.
DONE WHEN: totals equal a direct sum on the synthetic table.
IF BLOCKED: ask Sheikh for a fixture of harmonized.parquet.
MANUAL (you do these yourself; the agent cannot):
- Check Python deps install cleanly on your laptop; agree the split labels with Sheikh in conversation
```

## PHASE 2: Data (H3-8)
```
GOAL: series, climatology and intervals handed over by H10.
STEPS:
1. Finish P4.1. Run P4.2 (climatology) and P4.3 (intervals) with tests.
2. Print the HANDOFF to Sattyam, Monazir, Sheikh at H10 at the latest.
3. Start P4.4 (splits and metrics).
DELIVER: common/series.py, climatology.py, intervals.py.
DONE WHEN: all tests pass; fallbacks in intervals work.
IF BLOCKED: hand over series and intervals first; climatology next.
MANUAL (you do these yourself; the agent cannot):
- Ask Sattyam and Monazir what they need from common/ before you write it
```

## PHASE 3: Floor (H8-24)
```
GOAL: splits and metrics at H12; outlook floor; conformal groundwork.
INPUTS: harmonized v0 (Sheikh, H14).
STEPS:
1. Finish P4.4; print the HANDOFF to Sheikh and Samiul at H12.
2. Run P4.7 (outlook floor, including current_status) once harmonized v0 arrives.
3. Prepare conformal.py on fixtures; agree the out-of-fold columns and timing with Sheikh.
DELIVER: splits.py, metrics.py; outlook floor.
DONE WHEN: determinism and no-leakage tests pass; outlook uses only data up to as_of.
IF BLOCKED: simplify the outlook to a season-to-date percentile only.
MANUAL (you do these yourself; the agent cannot):
- Agree the exact columns and timing of the out-of-fold file with Sheikh
```

## PHASE 4: Core (H24-30)
```
GOAL: interval_table v1 and drift flags at H30.
INPUTS: predictions_oof.parquet (Sheikh, H24); weather loaders (Monazir, H26).
STEPS:
1. Run P4.5 (conformal, AOI-sampling, coverage table).
2. Run P4.6 (drift checks and drift_flags.parquet).
3. Print the HANDOFF to Sheikh and Sattyam at H30; confirm the API loads interval_table v1.
DELIVER: conformal.py, drift.py, interval_table.json v1, drift_flags.parquet.
DONE WHEN: JSON and parquet validate; coverage within about 3 points of 90 percent or the gap is reported.
IF BLOCKED: ship empirical-quantile intervals.
MANUAL (you do these yourself; the agent cannot):
- Look at the coverage table and decide with Sheikh whether to ship conformal intervals or the empirical-quantile fallback
```

## PHASE 5: Scale-up (H30-36)
```
GOAL: outlook, skill and validation pieces at H34.
STEPS:
1. Run P4.8: forecast, leave-one-season-out skill, status field; alerts only if time allows.
2. Agree the wording of no_demonstrated_skill with Shammo.
3. Run P4.9: validation pieces; stretch MCD64A1 comparison.
4. Print the HANDOFF to Sattyam and Shammo.
DELIVER: outlook.py, outlook_region.json, validation pieces.
DONE WHEN: no leakage; schemas validate.
IF BLOCKED: cut alerts, then the forecast; keep season-to-date.
MANUAL (you do these yourself; the agent cannot):
- Agree the wording of no_demonstrated_skill with Shammo
```

## PHASE 6: Polish (H36-42)
```
GOAL: trustworthy numbers.
STEPS:
1. Re-check coverage on the final harmonized v1.
2. Fix your items on Samiul's bug lists.
DELIVER: final coverage table.
DONE WHEN: validation pieces match the final data.
MANUAL (you do these yourself; the agent cannot):
- If you do the burned-area comparison, download the MCD64A1 files from NASA Earthdata with your login
```

## PHASE 7: Ship (H42-48)
```
GOAL: spot-check the deployed app.
STEPS:
1. Check that bands, drift icons and outlook status in the app match your files.
2. Stay on call until submission.
DELIVER: confirmation message to Sheikh.
MANUAL (you do these yourself; the agent cannot):
- Open the deployed app and check that the bands, drift icons and outlook status match your files
```
