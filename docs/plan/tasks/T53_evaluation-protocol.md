---
id: "T53"
title: "Audit and freeze targets, splits and scientific acceptance"
kind: "agent"
owner: "Sheikh"
authors: ["Sheikh"]
phase: "P1"
size: "S"
needs: ["T51","T52"]
requires: []
branch: "ws1/T53-evaluation-protocol"
touches: ["docs/specs/I13_SCIENTIFIC_ACCEPTANCE.md","docs/plan/runs/S01_harmonization.md","docs/plan/runs/S02_outlook.md","docs/project/contract-changes.md"]
creates: ["docs/results/EVALUATION_PROTOCOL.md"]
checks: ["CHECK-PLAN"]
---
## Goal
Freeze an executable, leakage-aware evaluation protocol before choosing a calibration repair or quoting new scores.

## Context
Read I13, S01/S02, common/splits.py, ws1_harmonize/evaluate.py, features.py, panel.py, write_harmonized.py, ws4_outlook/conformal.py, interval_report.py, outlook.py and current saved metrics.

## Steps
1. Inventory actual holdouts, split/block/year support, source combinations, overlapping OOF rows and previously inspected scores. Document fit/calibration/selection/evaluation roles by actual identifiers.
2. Specify calendar-month daily allocation, source-availability requirements, named-AOI applicability and coherent out-of-sample aggregation. Never pool partial spatial holdouts into purported full-area truth.
3. Freeze primary groups, support rules, sampling seeds, dependence-aware uncertainty method, metric tolerances and candidate budget in EVALUATION_PROTOCOL.md and the run appendices. The existing n>=500/coverage<0.80 stop remains unchanged.
4. Record whether fresh uninspected confirmation is possible; otherwise explicitly classify results as development validation.
5. Specify baseline comparison, maximum two diagnosis-led interval candidates and stop/resume/resource criteria. Candidate mechanisms are selected after T54; protocol roles/tolerances are frozen first.
6. Record scientific/contract decisions. Evidence of incomplete support is a valid finding, not a reason to lower the gate.

## Acceptance
- [ ] Run appendix contains actual values or explicit blockers rather than invented support/device counts.
- [ ] Targets and all required holdouts/input combinations are named; test reuse is disclosed.
- [ ] A reviewer can tell what will fit, what calibrates, what selects and what evaluates.

## Stop and ask if
The existing artifact provenance cannot establish split/target compatibility. Preserve uncertainty and specify reconstruction needed; do not relabel inspected data as untouched confirmation.

