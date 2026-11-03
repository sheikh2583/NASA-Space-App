# Phase prompts: Sheikh (Team Member 1). Detailed sub-prompts: prompts/ws1_sheikh.md

## PHASE 1: Kickoff (H0-3)
```
GOAL: Repo live, everyone able to push, contracts frozen at G0 (H3).
INPUTS: starter zip; docs/DECISIONS.md; docs/LEAD_GUIDE.md.
STEPS:
1. Run P1.1: create the repo, replace CODEOWNERS handles, invite all six, create channel and shared drive.
2. Confirm each teammate's hello-world pull request is merged.
3. Tell Sattyam the skeleton contracts/openapi.yaml is ready; ask for completion with fixtures by H3.
4. Run the 15-minute kickoff round: confirm the six slots, read out DECISIONS.md, confirm venue hours.
5. At H3 run the G0 checklist in docs/LEAD_GUIDE.md.
DELIVER: live repo; G0 called.
DONE WHEN: six PRs merged; mock server answers; fixtures exist.
DO NOT: spend more than 60 minutes on repo setup.
IF BLOCKED: hand the remainder of setup to Samin and start the kickoff round.
MANUAL (you do these yourself; the agent cannot):
- Create the GitHub repo from your own account, invite all six, and set branch protection in the repo settings
- Create the team channel and the shared drive folder, and set sharing so all six can edit
- Ask the organizers (in person or by message): venue hours, submission deadline, whether the starter structure may be brought, AI-use disclosure, licence rules, hardware rules; tell the team the answers
- Check that each teammate has git, Python 3.11 and Node LTS installed and can push; help them if not
- Run the 15-minute kickoff round (confirm the six slots, read out docs/DECISIONS.md)
```

## PHASE 2: Data (H3-8)
```
GOAL: First harmonization code running on the Bangladesh slice; G1 called at H8.
INPUTS: detections slice (Monazir, H4); grid_daily or fixture (Sattyam, H6-8); common/ drafts (Samin).
STEPS:
1. Ask Monazir at H4 whether the slice has arrived; ask Sattyam at H6 whether grid_daily is on track.
2. Run P1.2 (panel builder) and test it on synthetic data.
3. Run P1.3 (baselines B0 and B1) and test it on synthetic data.
4. Run P1.10 (verification tool and CI) and tell everyone to use tools/verify_files.py before each hand-off.
5. Run the H6 check-in; list blockers with owners.
6. At H8 run the G1 checklist.
DELIVER: panel.py and baselines.py with passing tests; G1 called.
DONE WHEN: both tests pass; grid_daily and cells exist.
DO NOT: wait for the full data before writing code; use the fixture.
IF BLOCKED: ask Sattyam for a 2-year Bangladesh grid_daily to work on.
MANUAL (you do these yourself; the agent cannot):
- Run the H6 check-in with everyone (done / next / blocked)
- Open the first detections slice yourself and look at a few rows
```

## PHASE 3: Floor (H8-24)
```
GOAL: harmonized v0 at H14; LightGBM prototype; out-of-fold file at H24; G2 called at H24.
INPUTS: grid_daily, cells; common/splits and metrics (Samin, H12).
STEPS:
1. Agree split labels with Samin (block_id % 5: 0 calib, 1 test) before H12.
2. Run P1.4. Validate both files against the contracts. Post the HANDOFF to Sattyam, Monazir, Samin by H14.
3. Run P1.5 (features and LightGBM) with the forbidden-feature and leakage tests.
4. Run P1.6 (three holdouts and predictions_oof.parquet). Post the HANDOFF to Samin by H24.
5. Run check-ins at H12, H18, H24; run the G2 checklist with Samiul's end-to-end report.
DELIVER: harmonized v0 + interval_table v0 (H14); predictions_oof.parquet (H24).
DONE WHEN: all contract checks pass; leakage test passes; G2 passes.
DO NOT: use VIIRS-derived features or the year; sum cell-level lo/hi.
IF BLOCKED: ship B1 only for v0; tell Samin the out-of-fold file will come from B1 if LightGBM slips.
MANUAL (you do these yourself; the agent cannot):
- Run the check-ins at H12, H18 and H24
- At G2 open the live app yourself on a laptop and a phone and try the demo path by hand
```

## PHASE 4: Core (H24-30)
```
GOAL: harmonized v1 integrated and live; G3 called at H30.
INPUTS: drift_flags.parquet and interval_table.json v1 (Samin, H30).
STEPS:
1. Ask Samin at H26 whether conformal and drift are on track.
2. Finish LightGBM; rerun P1.6 if features changed.
3. Run P1.7: assemble v1 with the value rule, merge drift flags, run the seam check.
4. Post the HANDOFF to Sattyam. Confirm with Sattyam that the API serves v1.
5. Run the G3 checklist.
DELIVER: harmonized.parquet v1.
DONE WHEN: contract checks and seam check pass; the app shows bands from interval_table v1.
IF BLOCKED: serve v0 with interval_table v0 and say so in the limitations.
MANUAL (you do these yourself; the agent cannot):
- At G3 open the live app and look at the bands, badges and drift icons yourself
- Talk to Samin and Sattyam about what slips if H30 is missed; decide the cut
```

## PHASE 5: Scale-up (H30-36)
```
GOAL: validation JSON and method notes delivered; feature freeze called at H36.
INPUTS: metrics tables; Samin's validation pieces.
STEPS:
1. Run P1.8: validation/harmonization.json and docs/method_notes_sheikh.md. Post the HANDOFF to Sattyam and Samiul by H34.
2. Walk the demo path yourself on the live app (Bangladesh, then Punjab).
3. Collect bug reports from Samiul and assign owners.
4. At H36 run the freeze checklist: nothing new merges except bug fixes.
DELIVER: validation JSON, method notes; freeze called.
DONE WHEN: JSON validates; every number appears in a table.
IF BLOCKED: write the limitations first; add metrics as they finish.
MANUAL (you do these yourself; the agent cannot):
- Walk the whole demo path by hand (Bangladesh, then Punjab) and note anything confusing
- Call the feature freeze at H36 in the channel and tell everyone what is cut
```

## PHASE 6: Polish (H36-42)
```
GOAL: Stable build; code freeze called at H42.
STEPS:
1. Accept only bug-fix pull requests; merge in dependency order (data, API, app).
2. Update data/MANIFEST.md and docs/CONTRACT_CHANGES.md; check that CHANGES match the contracts.
3. Review Samiul's H36 and H42 bug lists; assign every item an owner and a time.
4. Tag the build; call the code freeze at H42.
DELIVER: tagged build; frozen repo.
DONE WHEN: Samiul's H42 run has no severity-1 bugs.
IF BLOCKED: revert the offending change and tell its owner.
MANUAL (you do these yourself; the agent cannot):
- Merge pull requests in the GitHub web page in dependency order (data, API, app) and tag the final build
- Go through the bug lists with the owners and set times
```

## PHASE 7: Ship (H42-48)
```
GOAL: Submitted at H46 with a buffer.
STEPS:
1. Check the final deploy with Samiul's end-to-end script (live API and static fallback).
2. Go through docs/SUBMISSION_CHECKLIST.md with Samiul.
3. Submit at H46. Save a copy of the submission text and links in docs/.
DELIVER: submission.
DONE WHEN: confirmation received; links open for someone outside the team.
IF BLOCKED: ship with the static fallback URL and the repo link; fix the rest after.
MANUAL (you do these yourself; the agent cannot):
- Submit on the official Space Apps site from your login; check the right challenge is selected
- Open every submitted link in a private browser window to confirm it works for outsiders
```
