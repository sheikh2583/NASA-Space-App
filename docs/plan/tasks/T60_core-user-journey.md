---
id: "T60"
title: "Verify the challenge's area-calendar-comparison-export journey"
kind: "agent"
owner: "Sattyam"
authors: ["Sattyam","Shammo","Sheikh"]
phase: "P2"
size: "L"
needs: ["T58","T59"]
requires: []
branch: "ws1/T60-core-user-journey"
touches: ["ws2_platform/api/app.py","ws2_platform/api/query.py","ws5_frontend/src/App.tsx","ws5_frontend/src/api.ts","ws5_frontend/src/areas.ts","ws5_frontend/src/components/AreaFilters.tsx","ws5_frontend/src/components/Calendar.tsx","ws5_frontend/src/components/MapView.tsx","ws5_frontend/src/components/AnalysisControls.tsx","ws5_frontend/src/styles.css","ws5_frontend/src/i18n/en.json"]
creates: ["ws2_platform/tests/test_core_journey.py","ws5_frontend/src/coreJourney.test.ts","docs/results/CORE_JOURNEY.md"]
checks: ["CHECK-PLAN","python -m pytest -q ws2_platform/tests/test_core_journey.py","CHECK-WEB"]
---
## Goal
Demonstrate C02-C06 end to end through the supported regional application.

## Steps
1. Read the challenge contract, current API/request/selection/cache and frontend lifecycle code. Preserve catalog ID/polygon-equivalent cell membership.
2. Exercise named selection, supported polygons, no-data/out-of-domain selection, day/week/month, ISO week 53, leap/month boundaries, comparison and CSV.
3. Verify exact source/date/coverage meaning and same-cutoff comparisons. Rapid area/date/view changes and failed/aborted requests must not produce stale mixed-area results.
4. Add focused tiny API and pure frontend regressions for discovered defects; include share-link restoration and export-error behavior.
5. Observe the actual live/local-production browser journey, including loading/error/empty states. Record environment and outcomes; unit tests are not browser evidence.
6. Write CORE_JOURNEY.md with C-ID mapping, reproducible failures/fixes and unresolved support limits.

## Acceptance
- [ ] The complete supported task works and exports matching values/source/record metadata.
- [ ] No stale response wins, missing becomes zero or unsupported geography implies newly acquired data.
- [ ] Critical defects have a disposition; fresh checks are tied to the current revision.

## Stop and ask if
Correctness needs a scientific definition change beyond I13 or an unavailable tool/dependency. Record the specific blocker.

