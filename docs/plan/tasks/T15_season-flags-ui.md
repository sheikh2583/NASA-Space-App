---
id: "T15"
title: "Season flags in the season response and on the calendar"
kind: "agent"
owner: "Monazir"
authors: ["Monazir","Sattyam","Sheikh","Shammo"]
phase: "P2"
size: "S"
needs: ["T14","T08","T58"]
requires: ["real-data"]
branch: "ws1/T15-season-flags-ui"
touches: ["ws2_platform/api/app.py","ws2_platform/tests/test_api_season.py","contracts/json_schemas/season_profile.schema.json","ws5_frontend/src/types.ts","ws5_frontend/src/components/Calendar.tsx","ws5_frontend/src/components/SeasonCard.tsx","ws5_frontend/src/i18n/en.json","docs/project/contract-changes.md"]
creates: []
checks: ["CHECK-PLAN","python -m pytest -q ws2_platform/tests/test_api_season.py ws2_platform/tests/test_tiny_api.py ws3_anomaly/tests/test_season_flags.py","CHECK-WEB","CHECK-FILES"]
human_checks: ["CHECK-PY"]
scientific_spec: "docs/plan/runs/S03_release-validation.md"
---
## Goal
Expose the approved descriptive season flags consistently in the live API/calendar (C03/C05).

## Steps
1. Read T14's actual I1 decision, I13/T58 support states and touched API/schema/UI/tests.
2. Attach flags through the existing season endpoint; preserve response envelope/version compatibility. Include basis/reference count, cutoff, provenance, support and sensitivity semantics.
3. Add tiny-API/schema tests for valid, partial, missing, adjusted and unsupported cases; do not require every complete season to have a supported verdict.
4. Render high/low markers with text alternatives and a current-season sentence. Cross-year season markers use the season-ending year. Unsupported/sensitivity-unstable states cannot look like confident alerts.
5. Add focused component checks, run the declared checks and observe the live/local-production view. Record actual flagged seasons by artifact revision; do not export snapshots or restore Bangla delivery.
6. Append contract changes and hand over through the normal Git flow.

## Acceptance
- [ ] API/schema/UI agree with the approved flag contract and actual support.
- [ ] Markers are comprehensible without color and never described as forecasts.
- [ ] All existing relevant regressions pass; actual findings remain sourced.

## Stop and ask if
Integration requires an unapproved interpretation or incompatible response change.
