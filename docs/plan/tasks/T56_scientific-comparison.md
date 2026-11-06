---
id: "T56"
title: "Execute the controlled scientific comparison and record dispositions"
kind: "agent"
owner: "Sheikh"
authors: ["Sheikh","Samin"]
phase: "P1"
size: "L"
needs: ["T55","T57"]
requires: ["real-data"]
branch: "ws1/T56-scientific-comparison"
touches: ["docs/plan/runs/S01_harmonization.md","docs/results/training-results.md","docs/project/claim-register.md"]
creates: ["docs/results/SCIENTIFIC_REMEDIATION.md"]
checks: ["CHECK-PLAN","CHECK-FILES"]
human_checks: ["python scripts/workflow.py prepare --gpu-id 0 --threads 8","python scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8 --quick","python scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8","CHECK-QA","CHECK-PY"]
scientific_spec: "docs/plan/runs/S01_harmonization.md"
---
## Goal
Produce fresh numerical evidence from the registered repaired procedure, not just code/test claims.

## Steps
1. Read AGENTS.md, I13, S01, the frozen protocol, T54 diagnosis, T55 configuration and T57 gate. Confirm the actual source patch/inputs/resources and preservation record.
2. Execute S01 through T52's explicit scientific lane. Readiness/probes, quick/full fits and integrated QA are authorized; routine checks stay non-fitting. Preserve baseline and each candidate in ignored run dossiers.
3. Report all actual holdouts and both MODIS input combinations, point agreement/bias/error, calendar-month target, conditional positive/zero activity coverage, width/score and support/dependence uncertainty.
4. Compare identical eligible samples, record all attempted/rejected candidates and distinguish selection/development results from genuine confirmation. B1 remains eligible.
5. Reconcile generated provenance/hashes/QA with actual run identity. Report engineering status and scientific disposition separately.
6. Write SCIENTIFIC_REMEDIATION.md and update training-results/claim register with sources. If no repair passes, retain limitations and the baseline/rejected outputs; do not manufacture acceptance.
7. Record measured compute cost and a justified next action. Do not repeat an unchanged failed fit.

## Acceptance
- [ ] Full attributable comparison, all required groups/holdouts, preserved baseline and exact artifacts exist.
- [ ] Actual pass/fail/limited dispositions are reported, including unsuccessful candidates.
- [ ] Quick/resumed runs and historical scores are not mislabeled as fresh full confirmation.
- [ ] No runtime publication or unsupported forecast enabling is hidden in this card.

## Stop and ask if
A precondition fails, baseline protection is unavailable, or resources/authentication prevent the declared run. Expected scientific failure is reported as evidence; it is not suppressed.

