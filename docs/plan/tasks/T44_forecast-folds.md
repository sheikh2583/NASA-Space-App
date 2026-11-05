---
id: T44
title: Eliminate forecast feature and target leakage
kind: agent
owner: Samin
authors: ["Samin", "Sheikh", "Samiul"]
phase: P1
size: M
needs: ["T00"]
requires: []
branch: ws1/T44-forecast-folds
touches: ["ws4_outlook/outlook.py", "docs/science/decisions.md", "docs/project/contract-changes.md", "docs/science/method_en.md", "docs/results/training-results.md"]
creates: ["docs/specs/I10_FORECAST_VALIDATION.md", "ws4_outlook/tests/test_forecast_fold_data.py"]
checks: ["CHECK-PLAN", "python -m pytest -q ws4_outlook/tests/test_forecast_fold_data.py"]
human_checks: [CHECK-QA]
---
## Goal
Construct forecast features and references within each validation fold and qualify historical skill claims.

## Context
ws4_outlook/outlook.py; common/climatology.py; ws4_outlook/tests/test_outlook.py; ws4_outlook/run.py; docs/results/training-results.md.

## Steps
Write a spec and decision first. Define forecast issue times, seasons and target support for weeks +2..+4. Compute climatology/reference statistics from training-fold observations only and reuse them on evaluation rows. Exclude training examples whose target support touches held-out outcomes; handle gaps by calendar dates rather than row shifts. Define whether deployment claims require forward-only rather than leave-one-season-out validation. Preserve permissible issue-time history and document it. Add pure data-construction tests: held-out-value perturbations cannot alter training features/reference statistics, and targets cannot cross forbidden boundaries. Do not call evaluate_forecast() or fit models in tests. Mark saved forecast skill as historical/leakage-affected pending human recomputation; do not invent replacement scores.

## Acceptance
Fold data isolation and target embargo tests pass; forecast claims explicitly qualified. Existing artifacts remain unchanged. Human-only: corrected forecast fitting and QA, separately approved and launched by Sheikh.

## Stop and ask if
Implementing the selected validation design requires changing model selection or scientific artifacts without the spec/decision.

