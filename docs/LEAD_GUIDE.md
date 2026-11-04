# Lead guide (Sheikh): how to run the 48 hours

Master guide: docs/GUIDE.md. Known gaps: docs/KNOWN_GAPS.md.

Your three jobs: build the harmonized series (ws1_harmonize/), set up the repo, keep everyone in step.
Your own step-by-step is docs/instructions/01_sheikh.md; this page is for running the team.

## Gate checklists (5 minutes each; you run them)
Ask: is the artifact delivered, did it pass its test, did the receiver say GOT IT?

| Gate | When | Must exist | Confirmed by |
|---|---|---|---|
| G0 | H3 | openapi.yaml complete, fixtures, mock server answering; repo and hello-world PRs merged; hosting plan chosen | Sattyam, Shammo, Samiul |
| G1 | H8 | detections.parquet (demo regions), grid_daily.parquet, cells.parquet; QA started | Monazir, Sattyam, Samiul |
| G2 | H24 | draw an area, calendar with harmonized v0, flagged periods, on the live API; Samiul's end-to-end run passes | Samiul, Shammo |
| G3 | H30 | harmonized v1, interval_table v1, drift flags live in the API; band, badges, where-map and current-status card in the app | Samin, Sattyam, Shammo |
| Freeze | H36 | drivers, outlook, comparison, validation page, export in the app; no new features after this | Shammo, Samiul |
| Code freeze | H42 | bug fixes only; final build tagged | Samiul |
| Submit | H46 | docs/SUBMISSION_CHECKLIST.md complete | Samiul |

If a gate fails: cut by the agreed order (Bangla polish, forecast alerts, PM2.5, comparison, forecast outlook (the current-status card and the where-map are never cut)), keep the floor intact, never move a gate more than two hours.

## Check-in agenda (10 minutes at H6, H12, H18, H24, H30, H36, H42)
1. Each person, one line: done / next / blocked.
2. You: list blockers with an owner and a time.
3. Check the next hand-offs due (table below). Ask the receiver if the fixture is enough until then.

## Hand-off tracker (update after every HANDOFF; mirror in data/MANIFEST.md)
| Due | From | To | File | Status |
|---|---|---|---|---|
| H3 | Sattyam | Shammo, Samiul | openapi.yaml, fixtures, mock server | |
| H4 / H6 | Monazir | Sattyam, Samiul | detections.parquet (slice / full) | |
| H8 | Sattyam | Sheikh, Samin, Monazir, Samiul | grid_daily, cells | |
| H8 | Monazir | Sattyam | score_series stub | |
| H10 | Samin | Sattyam, Monazir, Sheikh | common series, climatology, intervals | |
| H12 | Samin | Sheikh, Samiul | common splits, metrics | |
| H14 | Sheikh | Sattyam, Monazir, Samin | harmonized v0, interval_table v0 | |
| H16 | Sattyam | Shammo, Samiul | live /aoi/summary, static fallback | |
| H18 | Monazir | Sattyam | anomalies, critical periods v0 | |
| H24 | Sheikh | Samin | predictions_oof.parquet | |
| H26 | Monazir | Samin | weather loaders | |
| H30 | Samin | Sheikh, Sattyam | interval_table v1, drift_flags | |
| H30 | Sheikh | Sattyam | harmonized v1 | |
| H34 | Samin | Sattyam, Shammo | outlook, validation pieces | |
| H34 | Sheikh | Sattyam, Samiul | validation/harmonization.json, method notes | |
| H36 | Monazir | Sattyam, Shammo | drivers | |
| H38 | Samiul | Shammo | method text (Bangla review H42) | |

## When someone is stuck or late
1. Ask what exactly is missing and from whom. Put it in the channel with a time.
2. Tell the receiver to keep working on the fixture or stub.
3. If the delay passes two hours, apply the cut order and tell the team what moved.
4. Offer a pairing: for example Samin takes a defined piece of evaluation; Monazir helps Sattyam with data.

## Watch your own load
H14 to H24 is the heaviest stretch (harmonized v0, CUDA candidate evaluation, the out-of-fold file, and a gate). Hand off any evaluation work you can, and keep check-ins to ten minutes.

## Manual gate checks (things only people can do)
- G0: every teammate has pushed a hello-world PR; accounts exist (GitHub, Earthdata, FIRMS key, hosting); the organizers' answers are shared.
- G1: someone has opened the FIRMS web viewer and compared one day by hand (Samiul).
- G2 and G3: you and Samiul open the live app on a laptop and a phone and walk the demo path by hand.
- Freeze: you announce the cuts in the channel.
- Submit: you submit with your login and open every link in a private window.
Full list per person: docs/MANUAL_TASKS.md.

## Branch protection settings (GitHub, Settings > Branches)
- Require a pull request before merging; no direct pushes to main.
- Require the `guard` status check. Do not require approvals: authors are the only code owners of their folders and cannot approve their own PRs. Review contracts/ and common/ PRs yourself by team rule.
- Turn on "Automatically delete head branches" (protect_main.sh does this).
- Block force pushes and branch deletion on main.
- Tell everyone the rule: pull --rebase before pushing; one folder per pull request (docs/WORKING_TOGETHER.md).
