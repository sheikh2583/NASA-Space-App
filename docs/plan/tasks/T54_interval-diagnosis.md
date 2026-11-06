---
id: "T54"
title: "Diagnose conditional interval failures and deployment support"
kind: "agent"
owner: "Samin"
authors: ["Samin","Sheikh"]
phase: "P1"
size: "L"
needs: ["T53"]
requires: ["real-data"]
branch: "ws1/T54-interval-diagnosis"
touches: ["ws4_outlook/conformal.py","ws4_outlook/interval_report.py","docs/specs/I13_SCIENTIFIC_ACCEPTANCE.md","docs/plan/runs/S01_harmonization.md"]
creates: ["ws4_outlook/diagnostics.py","ws4_outlook/tests/test_interval_diagnosis.py","docs/results/INTERVAL_DIAGNOSIS.md"]
checks: ["CHECK-PLAN","python -m pytest -q ws4_outlook/tests/test_interval_diagnosis.py"]
---
## Goal
Explain the saved failures and target mismatch using existing predictions before modifying calibration.

## Steps
1. Read I13/S01, the T53 protocol, source aggregation/calibration code and inspected input/OOF schemas. Preserve/hash existing table and reports.
2. Implement a standalone read-only diagnostic using saved OOF/grid/sensor/cell inputs. Write a separate ignored run report and concise sourced Markdown summary.
3. Report resolution/combo, positive/zero truth, positive truth at zero prediction, predicted/truth magnitude, under/over misses, width, interval score, unique/drawn cells, sparse support and geographic/time coverage.
4. Record unique blocks/periods and rectangle overlap; preserve IDs needed for justified dependence-aware uncertainty. Do not treat draws as independent physical observations.
5. Verify weekly-to-daily truth and calendar-month alignment. Audit whole named AOIs versus <=400-cell holdout-block sampling; explicitly report unsupported shapes/mixtures.
6. Test month/year/leap boundaries, missing weeks, duplicate contributing IDs, combination filtering and immutable table hash with handcrafted fixtures. Run the non-fitting diagnostic on the frozen baseline after review.
7. Rank causal hypotheses about implementation/calibration failures by actual evidence, then register at most two candidate mechanisms in S01. This is not causal attribution of fire activity.

## Acceptance
- [ ] Diagnostic covers all registered primary groups and records denominators/support and target identity.
- [ ] Baseline calibration bytes remain unchanged; no new fit is hidden in the diagnostic.
- [ ] Each severe failure has an explanation/hypothesis, counterexample or explicit unresolved status.

## Stop and ask if
Saved OOF/daily truth disagree or are incompatible with the named target. Diagnose and report before fitting a repair; never quietly drop disagreeing rows.

