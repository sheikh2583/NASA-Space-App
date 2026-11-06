---
id: "T59"
title: "Revalidate corrected outlook and enforce honest alert disposition"
kind: "agent"
owner: "Samin"
authors: ["Samin","Sheikh"]
phase: "P1"
size: "M"
needs: ["T56","T57","T44","T45"]
requires: ["real-data"]
branch: "ws1/T59-outlook-revalidation"
touches: ["ws4_outlook/outlook.py","ws4_outlook/alerts.py","ws4_outlook/run.py","contracts/json_schemas/outlook_region.schema.json","docs/plan/runs/S02_outlook.md","docs/results/training-results.md"]
creates: ["ws4_outlook/tests/test_outlook_release_contract.py","docs/results/OUTLOOK_REVALIDATION.md"]
checks: ["CHECK-PLAN","python -m pytest -q ws4_outlook/tests/test_outlook_release_contract.py"]
human_checks: ["python -m ws4_outlook.run outlook","CHECK-QA"]
scientific_spec: "docs/plan/runs/S02_outlook.md"
---
## Goal
Measure the corrected forward evaluation while keeping historical status useful and unsupported alerts disabled.

## Steps
1. Read S02, existing fold/target/alert code and compatible S01 outputs. Reuse a sufficient attributable outlook run instead of fitting again needlessly.
2. Freeze training-only climatology/persistence baselines, horizons, embargo, region eligibility, uncertainty and multiplicity handling before evaluation.
3. Add pure tests for forward boundaries, target censoring, partial/missing weeks and alert prerequisites/transitions.
4. Execute declared S02 scientific commands only when new computation is necessary. Report all required eligible region/horizon results, baseline skill and uncertainty.
5. Keep alerts off where skill is not demonstrated or genuine forward bounds are missing. Current-status percentile is not a forecast lower bound.
6. Record source/artifact identity and update sourced results. No demonstrated skill is an acceptable honest outcome.

## Acceptance
- [ ] Every required region/horizon has a result or explicit eligibility reason; no cherry-picked positive skill.
- [ ] No leakage regressions; no unsupported forecast alert.
- [ ] Historical status/season context remains available with coverage limits.

## Stop and ask if
Evidence cannot establish feature/target availability at issue time. Retain alerts off and report the incompatibility.

