---
id: T28
title: Validate, export and tag v1.0-event after Sheikh's final training
kind: agent
owner: Sheikh
authors: [Sheikh, Shammo]
phase: P3
size: M
needs: [H03, T16]
requires: [real-data, gh-auth]
branch: ws1/T28-final-release
touches: [docs/results/training-results.md, ws5_frontend/public/demo/areas.json, deployment/runtime.json]
creates: []
checks: ["CHECK-PLAN", "CHECK-TESTS", "CHECK-FILES", "CHECK-WEB"]
---
## Goal
Freeze a reproducible, fully measured release by 12 Nov 20:00 Dhaka. Everything shown at the event comes from this
tag.

## Steps
Sheikh has just run the final full training (`scripts/train.ps1 -Pack`: QA, results and the runtime ZIP included),
plus pytest and smoke (H03). This card reports,
publishes and tags it. **Don't train, validate or rerun any pipeline stage.**
1. `git switch main && git pull --ff-only`, then `git status --short` must print nothing (apart from untracked
   `data/`).
2. Read `data/processed/validation/qa.json`, from Sheikh's validate in H03. All five groups must pass. Don't trust an
   exit code alone.
3. Run `python -m ws2_platform.coverage`: contradictions for verified entries = 0.
4. Run `python tools/verify_files.py --all`, then `python scripts/export_hosted_demo.py` (the legacy snapshot) and
   `python scripts/export_area_catalog.py`, if the cells changed.
5. In `docs/results/training-results.md`, add a section "Release v1.0-event (<date>)". Mark every number "measured,
   <command>, <date>". Include:
   - the commit;
   - the selection metrics for B1 and the learned candidate on every holdout (from `data/interim/sheikh/metrics.csv`,
     named as the file does), and the selected method;
   - weekly and monthly coverage;
   - the season-profile headline numbers, from `python -m ws4_outlook.season_profile --area pb` and `--area bd`;
   - the blind-spot verdict (T20) and the burned-area result (T24), when they exist.
6. Publish the data to Render: `python scripts/release_runtime.py --data-through <date>` (dry run), then with
   `--publish` (T16). This rewrites `deployment/runtime.json`.
7. Run the checks, mark the card done, and hand over for commit. Sheikh commits and pushes; Render rebuilds.
8. After the push, tag that commit: `git tag v1.0-event <commit> && git push origin v1.0-event`. Do this only when
   Sheikh says the commit is final.
9. Check the deployment: `python scripts/check_render.py --commit <tagged commit>` passes (T17), and the site loads
   Dhaka and Punjab.
10. Backup: `python scripts/workflow.py share`. Tell Sheikh to copy `share/firesense-source.zip` and
    `share/firesense-runtime.zip` to a USB drive.

## Acceptance
- [ ] The tag exists, and Render serves that commit with the released data.
- [ ] `docs/results/training-results.md` holds only measured numbers, each with its command and date.
- [ ] The backup zip exists.

## Stop and ask if
- Any QA group fails.
- CCC drops by more than 0.01 against the previous section.
- `check_render.py` fails after one rebuild.
