---
id: T49
title: Verify and publish the reviewed correctness repairs
kind: agent
owner: Sheikh
authors: ["Sheikh", "Shammo", "Samiul", "Samin", "Sattyam"]
phase: P1
size: M
needs: ["T42", "T43", "T44", "T45", "T46", "T47", "T48"]
requires: []
branch: ws1/T49-repair-release
touches: ["deployment/runtime.json", "ws5_frontend/public/demo/areas.json", "docs/results/training-results.md", "docs/guides/deployment.md", "ws4_outlook/run.py", "ws5_frontend/src/i18n/en.json", "docs/science/method_en.md", "ws2_platform/api/app.py", "contracts/openapi.yaml", "contracts/json_schemas/season_profile.schema.json", "docs/project/contract-changes.md", "scripts/export_area_catalog.py"]
creates: ["docs/results/CORRECTNESS_REPAIR_2026-11-05.md", "ws2_platform/tests/test_season_record_end.py"]
checks: ["CHECK-PLAN", "CHECK-FILES", "python -m pytest -q ws2_platform/tests/test_season_record_end.py"]
human_checks: [CHECK-QA]
---
## Goal
Close the repair package with honest evidence, a compatible runtime and verified deployment.

## Context
docs/plan/REPAIR_PLAN_2026-11-05.md; docs/guides/deployment.md; scripts/export_hosted_demo.py; scripts/release_runtime.py; scripts/check_render.py; each repair card.

## Steps
Record which code/tests passed and which saved outputs remain historical. Human-only: Sheikh explicitly runs necessary non-fitting pipeline recomputations and workflow validation; forecast fitting remains human-only and is not assumed authorized by this card. If forecast revalidation is deferred, keep affected forecast skill/alerts explicitly unvalidated/off and do not present historical numbers as validation. Agent may run approved read-only diagnostics and snapshot/release tooling after path review. Update only a NEW pinned runtime release; never replace assets. Verify the detailed report and dates in the resulting /meta/validation and /health responses with check_render.py, reading secrets in code without printing values. Never claim live deployment from a push alone.

## Acceptance
Report includes all eight findings, measured stop rows and remediation dispositions; detailed diagnostics reach the live service; date metadata agrees. Any deferred forecast validation is explicit. No experimental recalibration is introduced.

## Stop and ask if
QA fails, a release needs overwritten assets, required authority/authentication is absent, or any fitting command would be agent-executed.

