# MODIS + VIIRS Harmonization (NASA Space Apps 2026)

> Start with docs/GUIDE.md (the end-to-end guide). Read docs/KNOWN_GAPS.md: this kit was written without the official challenge text and without running any project code; several facts are unverified and have H0 checks (docs/H0_VERIFICATION.md).

We build a web app that merges MODIS and VIIRS fire detections into one consistent burning-activity
calendar for any area a user draws: harmonized history with uncertainty bands, flagged unusual
periods (including agricultural burns), associated drivers (never causes) and a current-season outlook.

This starter contains structure, contracts, checklists and prompt packs only. It contains no project
logic; the work starts at H0.

## Start here
Git commands and scripts (clone, branch, save, ship): docs/GIT_WORKFLOW.md. Do its section 0 first.
0. Everyone: open docs/instructions/ and read the file with your name. It tells you what to do, hour by hour, and who to talk to. docs/TALK_TO.md lists every conversation in one table.
1. Sheikh: follow prompts/ws1_sheikh.md, prompt P1.1 (repo setup, 60 minutes).
2. Everyone: read docs/PIPELINE.md (5 minutes), then your folder's README.md.
3. Open your AI tool. For each phase, paste prompts/phases/00_agent_loop.md and your phase prompt from prompts/phases/ (one agent prompt per phase, seven per person). Paste docs/AI_PREAMBLE.md first, then the prompts in your pack, one at a time,
   in order (prompts/ws1_sheikh.md to ws6_samiul.md). Start the next prompt only when the previous one passes its test.
4. When a deliverable passes its test, post a HANDOFF message (docs/HANDOFF_TEMPLATE.md).

## Who owns what
| Slot | Person | Folder | Workstream |
|---|---|---|---|
| 1 | Sheikh | ws1_harmonize/ | harmonization, repo, integration |
| 2 | Sattyam | ws2_platform/, contracts/ | data platform and API |
| 3 | Monazir | ws3_anomaly/ | ingestion, anomalies, drivers |
| 4 | Samin | common/, ws4_outlook/ | shared library, conformal and drift, outlook |
| 5 | Shammo | ws5_frontend/ | web app |
| 6 | Samiul | ws6_validation/, docs/ | QA, validation content, method text, slides, video |

Manual tasks (accounts, downloads, calls, device checks, recording, submitting) are in docs/MANUAL_TASKS.md; a coding agent cannot do these for you.

## How we work
- Stack: docs/TECH_STACK.md. Where things live and run: docs/WHERE_TO_WORK.md.
- No stepping on each other: docs/WORKING_TOGETHER.md and docs/FILE_OWNERSHIP.md (one writer per path).
- How to check a deliverable: docs/VERIFY.md.

## Gates
G0 H3 contracts frozen | G1 H8 gridded data | G2 H24 floor works | G3 H30 core integrated |
H36 feature freeze | H42 code freeze | H46 submit. Full timeline: docs/TIMELINE.md.

## Rules
- Edit only your own folder. Changes to contracts/ and common/ need Sheikh's OK (log them in docs/CONTRACT_CHANGES.md).
- Large files live in the shared drive mirror of data/, never in git. One line per hand-off in data/MANIFEST.md.
- Keys in .env only. Never commit data or secrets.
- Never claim causes. Never hide that a value is modeled.
