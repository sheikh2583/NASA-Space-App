---
id: "T21"
title: "Observed hotspot recurrence by eligible season"
kind: "agent"
owner: "Sattyam"
authors: ["Sattyam","Shammo","Sheikh"]
phase: "P2"
size: "M"
needs: ["T07","T53","T58"]
requires: ["real-data"]
branch: "ws1/T21-recurrence-map"
touches: ["ws2_platform/api/app.py","ws2_platform/api/query.py","contracts/openapi.yaml","docs/project/contract-changes.md","ws5_frontend/src/types.ts","ws5_frontend/src/components/MapView.tsx","ws5_frontend/src/App.tsx","ws5_frontend/src/api.ts","ws5_frontend/src/i18n/en.json"]
creates: ["ws2_platform/recurrence.py","ws2_platform/tests/test_recurrence.py"]
checks: ["CHECK-PLAN","python -m pytest -q ws2_platform/tests/test_recurrence.py ws2_platform/tests/test_tiny_api.py","CHECK-WEB"]
human_checks: ["CHECK-PY"]
scientific_spec: "docs/plan/runs/S03_release-validation.md"
---
## Goal
Show where detected activity recurs across eligible observed seasons without claiming a probability of fire (C02/C03).

## Steps
1. Read I1/I13, common/series.py, sensor-day conventions, current cell selection and map/API contracts.
2. Compute per-cell share of eligible complete seasons with at least one observed-SNPP detection; exclude adjusted/modeled rows. Eligible seasons require at least 90% SNPP operating days in the season window, subject to the operating-versus-perfect-observation caveat.
3. Include eligible zero-detection cells; zero eligible seasons is unsupported, not zero recurrence. Derive actual eligible years/n_years and mean_detections; never hardcode 2012-2025.
4. Add /aoi/recurrence and contract/types using the same cell membership as other AOI endpoints. Cache only bounded results with the current artifact revision.
5. Add a sequential map layer/season selector and legend: share of eligible seasons with detected hotspots. Popup uses numerator/denominator and actual years; never says proven burned in N years.
6. Test 7/10, outages, quiet cells, no eligible years, cross-year windows, adjusted/model exclusion and catalog/polygon equivalence. Observe both primary demo regions in the live UI.

## Acceptance
- [ ] Numerators, eligible denominators, years and source are visible and tested.
- [ ] No snapshot files or offline transport introduced.
- [ ] Sparse support/missing coverage cannot masquerade as no fire.

## Stop and ask if
Observation eligibility cannot be reconstructed from saved metadata. Report limited support; a low recurrence result alone is not evidence of a code defect.
