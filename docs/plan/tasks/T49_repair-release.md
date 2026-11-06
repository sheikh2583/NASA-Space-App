---
id: "T49"
title: "Verify and publish the reviewed correctness repairs"
kind: "agent"
owner: "Sheikh"
authors: ["Sheikh","Shammo","Samiul","Samin","Sattyam"]
phase: "P1"
size: "M"
needs: ["T42","T43","T44","T45","T46","T47","T48"]
requires: []
branch: "ws1/T49-repair-release"
touches: ["deployment/runtime.json","ws5_frontend/public/demo/areas.json","docs/results/training-results.md","docs/guides/deployment.md","ws4_outlook/run.py","ws5_frontend/src/i18n/en.json","docs/science/method_en.md","ws2_platform/api/app.py","contracts/openapi.yaml","contracts/json_schemas/season_profile.schema.json","docs/project/contract-changes.md","scripts/export_area_catalog.py"]
creates: ["docs/results/CORRECTNESS_REPAIR_2026-11-05.md","ws2_platform/tests/test_season_record_end.py"]
checks: ["CHECK-PLAN","CHECK-FILES","python -m pytest -q ws2_platform/tests/test_season_record_end.py"]
human_checks: ["CHECK-QA"]
scientific_spec: "docs/plan/runs/S03_release-validation.md"
---
## Goal
Close the historical correctness-repair evidence without conflating it with newly authorized scientific remediation.

## Steps
1. Read the dated repair review, current 6 November assessment and training authorization.
2. Reconcile fixed-code/test observations, saved-output provenance and dated live revision/report evidence. Earlier stale-deployment notes are historical; do not infer the host cause.
3. New training/calibration belongs to T52-T59's scientific-run specs. This historical closeout does not silently repeat or relabel those experiments.
4. Preserve compatibility and publish only new immutable assets through T28. Record each deferred/failed scientific claim.
5. Hand over remaining closeout evidence through the normal Git flow. No snapshot export or retired transport.

## Acceptance
Historical repairs, tests and deployment observations have attributable dispositions; current scientific acceptance is not inferred from older QA.

## Stop and ask if
Evidence conflicts or a release needs overwritten assets/unknown authority. Report the exact conflict.

