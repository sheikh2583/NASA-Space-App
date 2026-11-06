---
id: "T55"
title: "Implement the registered aggregate-interval repair"
kind: "agent"
owner: "Samin"
authors: ["Samin","Sheikh"]
phase: "P1"
size: "L"
needs: ["T54"]
requires: []
branch: "ws1/T55-interval-remediation"
touches: ["ws4_outlook/conformal.py","ws4_outlook/interval_report.py","ws4_outlook/run.py","common/intervals.py","ws1_harmonize/evaluate.py","ws1_harmonize/features.py","docs/specs/I13_SCIENTIFIC_ACCEPTANCE.md","docs/plan/runs/S01_harmonization.md","docs/project/contract-changes.md"]
creates: ["ws4_outlook/tests/test_interval_repair.py","ws1_harmonize/tests/test_scientific_target_contract.py"]
checks: ["CHECK-PLAN","python -m pytest -q ws4_outlook/tests/test_interval_repair.py ws1_harmonize/tests/test_scientific_target_contract.py"]
---
## Goal
Implement the smallest diagnosis-supported repair while preserving B1, split isolation and honest conditional diagnostics.

## Steps
1. Read T54's actual findings, frozen I13/S01 protocol and all touched source. Implement only the registered candidate mechanism(s); a different hypothesis requires a recorded protocol amendment before evaluation.
2. Ensure deployment strata use available predictors, never future truth-positive labels. Define combination/magnitude/support fallbacks, zero-sensitive behavior and finite-sample quantiles explicitly.
3. Keep count targets consistent through OOF, daily allocation, calendar months and served aggregate lookup. Keep calendar-exact MODIS feature context and full-panel selection; no VIIRS leakage.
4. Add reproducible candidate configuration/versioning so trials do not depend on undocumented manual edits. Preserve a runnable frozen baseline.
5. Add pure fixture tests for combo separation, zero prediction/positive truth, sparse fallback, quantile edge cases, missing days, month boundaries, nonfinite values and disjoint fitting roles. Fitting integration belongs to T56, not these routine checks.
6. Append contract/spec decisions and prepare the exact S01 comparison commands.

## Acceptance
- [ ] Candidate behavior is deterministic/configured and all pure regression contracts pass.
- [ ] At most two registered interval repairs; all-dimensional stop reporting remains intact.
- [ ] No new metric is claimed before T56 numerical evaluation; B1 can still win.

## Stop and ask if
The diagnosis requires an unscoped scientific/output-contract change or a new dependency. A candidate failure is reported, not fixed by tuning on test outcomes.

