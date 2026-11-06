---
id: "T52"
title: "Add an explicit scientific validation lane with preserved baselines"
kind: "agent"
owner: "Sheikh"
authors: ["Sheikh"]
phase: "P1"
size: "M"
needs: ["T51"]
requires: []
branch: "ws1/T52-scientific-check-lane"
touches: ["scripts/plan.py","scripts/run_pipeline.py","scripts/workflow.py","scripts/tests/test_plan.py","scripts/tests/test_plan_checks.py","docs/plan/README.md","docs/plan/AGENT_PROMPT.md","docs/project/training-authorization.md","docs/guides/training.md"]
creates: ["scripts/tests/test_scientific_lane.py"]
checks: ["CHECK-PLAN","python -m pytest -q scripts/tests/test_scientific_lane.py scripts/tests/test_plan.py scripts/tests/test_plan_checks.py"]
---
## Goal
Make the newly authorized scientific workflow executable without allowing ordinary checks to start surprise fits.

## Context
Read AGENTS.md, the authorization record, S01/S02 run specs, scripts/plan.py and every touched runner/test.

## Steps
1. Add a documented --scientific selector to plan.py checks/show. Keep ordinary --run behavior non-fitting. The scientific selector uses the legacy human_checks command list and scientific_spec path; it does not rerun ordinary checks implicitly.
2. Validate that scientific cards name an existing run spec and declared commands. Replace misleading human-only messages with lane semantics; keep backward compatibility and all ordinary refusal assertions.
3. Require explicit scientific execution, attributable run ID/source patch/input hashes, one writer per output tree and verified backups before shared outputs can be replaced. Reuse run_pipeline.py's execution/backups rather than inventing a second training stack.
4. Review setup/readiness/probe placement, failure/resume reporting and disk checks. A probe that fits is logged as fitting. Never silently fall back to synthetic inputs for a real-data run.
5. Test default denial, explicit scientific selection, malformed/missing specs, command failures, unavailable backup/lock and source/config recording using fake subprocesses and temporary paths. Tests must not actually train.
6. Update instructions with exact supported CLI and recovery behavior.

## Acceptance
- [ ] Ordinary lane still rejects fitting/blanket suites; explicit scientific lane runs only declared commands.
- [ ] Mocked tests prove no command starts after a failed preservation/precondition check.
- [ ] No existing scientific or guard assertion is weakened; no real fit occurs in these unit tests.
- [ ] Training permission is not another interactive approval prompt.

## Stop and ask if
A required external service/dependency is unavailable, or baseline preservation cannot be guaranteed within the declared paths. Fix in-scope runner defects; do not bypass the ordinary guard.

