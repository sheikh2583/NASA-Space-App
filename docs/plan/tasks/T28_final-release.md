---
id: T28
title: Validate, export and tag v1.0-event after Sheikh's final training
kind: agent
owner: Sheikh
authors: [Sheikh, Shammo]
phase: P3
size: M
needs: [H03]
requires: [real-data]
branch: ws1/T28-final-release
touches: [docs/TRAINING_RESULTS.md, ws5_frontend/public/demo/snapshot.json]
creates: []
checks: [CHECK-PLAN, CHECK-SMOKE, CHECK-QA, CHECK-FILES, CHECK-SNAP]
---
## Goal
Freeze a reproducible, fully measured release by 12 Nov 20:00 Dhaka. Everything shown at the event comes from this
tag.

## Steps
Sheikh has just run the final full training (H03). This card checks it, publishes it and tags it. **Don't retrain.**
1. `git switch main && git pull --ff-only`, then `git status --short` must print nothing (apart from untracked
   `data/`).
2. Run `python scripts/workflow.py validate`, then read `data/processed/validation/qa.json`. All five groups must
   pass. Don't trust the exit code alone.
3. Run `python -m ws2_platform.coverage`: contradictions for verified entries = 0.
4. Run `python scripts/export_hosted_demo.py`, then `python tools/verify_files.py --all`. If T11 is merged, also run
   `python -m ws2_platform.api.static_export --out ws5_frontend/public/demo/static`.
5. In `docs/TRAINING_RESULTS.md`, add a section "Release v1.0-event (<date>)". Mark every number "measured,
   <command>, <date>". Include:
   - the commit;
   - B1 and LightGBM mean held-out CCC on all six holdouts (from `data/interim/sheikh/metrics.csv`), and the selected
     method;
   - weekly and monthly coverage;
   - the season-profile headline numbers, from `python -m ws4_outlook.season_profile --area pb` and `--area bd`;
   - the blind-spot verdict (T20) and the burned-area result (T24), when they exist.
6. If T17 is done, run `python scripts/release_data.py` and the T17 Space redeploy steps, so the hosted API serves the
   same data.
7. Run the checks, mark the card done, `split`, push and open the PR.
8. After Sheikh merges, tag the merge commit: `git switch main && git pull && git tag v1.0-event && git push origin v1.0-event`.
9. Check the deployment: `gh run list --workflow pages.yml --limit 1` is green,
   `https://sheikh2583.github.io/NASA-Space-App/version.json` matches the tag commit, and the site loads both areas.
10. Backup: `python scripts/workflow.py share`. Tell Sheikh to copy `share/firesense-source.zip` to a USB drive.

## Acceptance
- [ ] The tag exists, and the site serves that commit.
- [ ] `TRAINING_RESULTS.md` holds only measured numbers, each with its command and date.
- [ ] The backup zip exists.

## Stop and ask if
- Any QA group fails.
- CCC drops by more than 0.01 against the previous section.
- `version.json` doesn't match.
