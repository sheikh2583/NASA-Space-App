# Phase prompts: Samiul (Team Member 6). Detailed sub-prompts: prompts/ws6_samiul.md

## PHASE 1: Kickoff (H0-3)
```
GOAL: QA checklist and test scaffolds ready by H4.
STEPS:
1. Ask Sheikh what the checklist must cover; ask Sattyam when the mock URL lands.
2. Run P6.1: test scaffolds in ws6_validation/tests/ and a README on how to run them.
3. Print the HANDOFF to everyone.
DELIVER: docs/QA_CHECKLIST.md; test scaffolds.
DONE WHEN: the contract test runs against the mock once it exists.
IF BLOCKED: write the checklist first; scaffolds next.
MANUAL (you do these yourself; the agent cannot):
- Join the channel; get the QA and submission checklists from the repo; confirm your tools run
```

## PHASE 2: Data (H3-8)
```
GOAL: Contract tests passing; data QA report at H10.
INPUTS: detections (Monazir, H6); grid_daily and cells (Sattyam, H8).
STEPS:
1. Run P6.2: contract tests on the mock.
2. Run P6.3: data QA checks and the manual check against the FIRMS web viewer.
3. Print the HANDOFF of the data QA report to Sattyam and Monazir at H10.
4. Collect the en.json key list from Shammo at H8.
DELIVER: data QA report.
DONE WHEN: every failed check lists the offending rows or files.
IF BLOCKED: report the checks you could run and what is waiting.
MANUAL (you do these yourself; the agent cannot):
- Open the FIRMS web viewer, pick one day and one small area, count the detections by hand and compare with our number
```

## PHASE 3: Floor (H8-24)
```
GOAL: End-to-end runs; draft story; floor gate at H24.
STEPS:
1. Draft the slide outline and demo script (P6.7); confirm the story with Sheikh (observed vs modeled, limits).
2. Run P6.4 when the live API is up (H16); send the bug list to Shammo and Sattyam.
3. At H24 run the full end-to-end check and give Sheikh the G2 result.
DELIVER: bug list; end-to-end report; draft outline and script.
DONE WHEN: every bug has an owner and a reproduction step.
IF BLOCKED: test against the static fallback.
MANUAL (you do these yourself; the agent cannot):
- Use the app by hand on a phone and a laptop for the full demo path; take screenshots of every bug
```

## PHASE 4: Core (H24-30)
```
GOAL: End-to-end run at H30.
STEPS:
1. Run P6.4 again; add checks for intervals from v1 and drift icons.
2. Start collecting validation pieces.
DELIVER: H30 report and bug list.
DONE WHEN: the report is in the channel by H30.
MANUAL (you do these yourself; the agent cannot):
- Repeat the hand test with intervals and drift icons visible; add new bugs with screenshots
```

## PHASE 5: Scale-up (H30-36)
```
GOAL: qa.json and validation content by H34; end-to-end run at H36.
STEPS:
1. Ask Sheikh for method notes and Samin for validation pieces by H34.
2. Run P6.5: write qa.json and the three-line summary; print the HANDOFF to Sattyam and Shammo.
3. Run P6.4 at H36.
DELIVER: qa.json; summary; H36 report.
DONE WHEN: every number in the summary appears in a piece.
IF BLOCKED: write the QA piece now; add the rest as pieces arrive.
MANUAL (you do these yourself; the agent cannot):
- Ask a fluent Bangla speaker to be ready for the review at H42; collect the numbers for slides from the validation files
```

## PHASE 6: Polish (H36-42)
```
GOAL: Method text at H38; slides at H40; Bangla review at H42.
STEPS:
1. Run P6.6: method text under 250 words; send to Shammo at H38.
2. Find a fluent teammate to review the Bangla text; mark every line needing a check.
3. Finish the slides (H40); run P6.4 at H42.
DELIVER: method text; reviewed Bangla; slides.
DONE WHEN: every number on a slide traces to a file or a validation piece.
IF BLOCKED: publish the English text first.
MANUAL (you do these yourself; the agent cannot):
- Sit with the Bangla reviewer and go through every line; rehearse the demo aloud and time it
```

## PHASE 7: Ship (H42-48)
```
GOAL: Video at H44; checklist complete at H46.
STEPS:
1. Record the video using the rehearsed demo path; keep the fallback as backup.
2. Run P6.8: docs/SUBMISSION_CHECKLIST.md against the organizers' current rules.
3. Hand Sheikh the completed checklist for the submission at H46.
4. Stretch only if ahead: P6.9 PM2.5, reviewed by Monazir.
DELIVER: video; completed checklist.
DONE WHEN: nothing is unchecked at H46.
MANUAL (you do these yourself; the agent cannot):
- Record the video with a screen recorder and a microphone, watch it end to end, upload it; fill in the submission forms with Sheikh
```
