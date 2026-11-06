---
id: "T13"
title: "Interval report by stratum (measurement only)"
kind: "agent"
owner: "Samin"
authors: ["Samin","Shammo"]
phase: "P1"
size: "M"
needs: ["T00"]
requires: ["real-data"]
branch: "ws1/T13-interval-report"
touches: ["ws4_outlook/conformal.py","ws4_outlook/run.py","ws5_frontend/src/components/Pages.tsx","ws5_frontend/src/i18n/en.json","ws5_frontend/src/i18n/bn.json","ws5_frontend/public/demo/areas.json"]
creates: ["ws4_outlook/interval_report.py","ws4_outlook/tests/test_interval_report.py"]
checks: ["CHECK-PLAN","python -m pytest -q ws4_outlook/tests/test_interval_report.py","CHECK-FILES","CHECK-WEB"]
human_checks: ["CHECK-QA"]
scientific_spec: "docs/plan/runs/S03_release-validation.md"
---
## Goal
Retain complete conditional interval measurement and close the reporting evidence independently of remediation.

## Context
The reporting implementation exists and saved failures remain visible. T46 corrected unique contributing area counts and all-dimensional stops; T54-T56 own diagnosis/repair/new evaluation. The old snapshot/Terra-only-era instructions are superseded.

## Steps
1. Read I13, current interval_report.py/run.py and the saved target/provenance.
2. Verify all requested dimensions, positive-activity/zero-prediction diagnostics, unique versus drawn cells and stop rows are retained.
3. Do not refit/widen bands in this reporting card. Scientific recomputation follows the registered T54-T56 workflow; agent execution is now authorized by AGENTS.md.
4. Record report production separately from scientific acceptance. Evidence is served through the live API/runtime, never a regenerated snapshot.
5. Hand over the exact sourced measurement and remaining failures for status closeout; do not claim a failure disappeared because a report exists.

## Acceptance
- [ ] Complete truthful reporting and immutable source/table identity.
- [ ] Reporting completion does not imply scientific acceptance.
- [ ] Fresh measurements are distinguished from historical reports.

## Stop and ask if
Report identity/target is incompatible or a required dimension is silently omitted. Preserve failure visibility.
