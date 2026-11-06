---
id: "T24"
title: "Corroborating burned-area and timing check with MCD64A1"
kind: "agent"
owner: "Samin"
authors: ["Samin","Samiul","Shammo","Sheikh"]
phase: "P2"
size: "M"
needs: ["T33","T53","T58"]
requires: ["real-data","earthdata-files"]
branch: "ws1/T24-burned-area-check"
touches: ["ws5_frontend/src/components/Pages.tsx","ws5_frontend/src/i18n/en.json","docs/science/method_en.md","scripts/runtime_bundle.py","docs/project/claim-register.md"]
creates: ["ws6_validation/mcd64.py","ws6_validation/tests/test_mcd64.py","docs/results/BURNED_AREA_CORROBORATION.md"]
checks: ["CHECK-PLAN","python -m pytest -q ws6_validation/tests/test_mcd64.py","CHECK-FILES","CHECK-WEB"]
human_checks: ["CHECK-QA"]
scientific_spec: "docs/plan/runs/S03_release-validation.md"
---
## Goal
Compare seasonal variation/timing against a corroborating product with shared-input and small-burn limitations (Q03).

## Steps
1. Read T33 inventory, NASA product/user guide and algorithm paper, I13, season_profile.py and current validation/packaging contracts.
2. Predeclare included years/areas and metrics before inspecting agreement. Verify collection-specific QA, fill/water/unmapped flags, geotransform/pixel area, burn-date uncertainty and cross-year windows from metadata.
3. Implement correctly geolocated eligible-pixel/season aggregation and compare ranks/variation and p50 timing. Counts and km2 remain different quantities; no conversion to validated absolute fires/area.
4. Test known coordinate/tile round trips against independently checked metadata, pixel centers, valid zeros versus unmapped, cross-year dates, QA exclusion, repeated granules and known synthetic timing.
5. Produce a validation piece and sourced Markdown with all included/missing years, denominators, disagreements and limitations. No minimum positive correlation is required.
6. Show actual results on Method/Validation and include the optional evidence in new compatible runtimes. MCD64A1 uses MODIS active-fire inputs; never label it independent ground truth.
7. If required products are unavailable, record an explicit missing/deferred disposition; any cut is visible in the final assessment.

## Acceptance
- [ ] Reproducible sample and reported results, including weak agreement/missingness.
- [ ] Evidence respects QA/geometry and cannot validate pre-2012 SNPP truth or absolute detection completeness.
- [ ] Runtime/UI wording and attribution match the actual corroboration.

## Stop and ask if
Metadata/coordinates cannot be verified or a new dependency is needed. Zero valid burned pixels may be a valid result; investigate without forcing a positive result.
