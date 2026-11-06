---
id: "T58"
title: "Carry scientific support consistently through API, UI and exports"
kind: "agent"
owner: "Shammo"
authors: ["Shammo","Sattyam","Sheikh","Samiul"]
phase: "P1"
size: "M"
needs: ["T56","T57"]
requires: []
branch: "ws1/T58-public-evidence-status"
touches: ["ws2_platform/api/app.py","ws2_platform/api/query.py","contracts/openapi.yaml","ws5_frontend/src/types.ts","ws5_frontend/src/components/Pages.tsx","ws5_frontend/src/components/Panels.tsx","ws5_frontend/src/components/SeasonCard.tsx","ws5_frontend/src/components/SeriesChart.tsx","ws5_frontend/src/i18n/en.json","ws5_frontend/src/styles.css","docs/science/method_en.md","docs/project/contract-changes.md"]
creates: ["ws2_platform/tests/test_scientific_status.py","ws5_frontend/src/components/ScientificStatus.test.tsx"]
checks: ["CHECK-PLAN","python -m pytest -q ws2_platform/tests/test_scientific_status.py","CHECK-WEB"]
---
## Goal
Make uncertainty/provenance limitations understandable at the point of use, not only in a distant report.

## Steps
1. Read I13, T56 dispositions, T57 wire contract, current chart/status/validation/export code and public method text.
2. Expose scoped scientific status, record cutoff, target and source provenance in summary/metadata and CSV. Avoid emitting per-AOI acceptance unless that AOI lies in the evaluated domain.
3. Apply the reviewed policy to unsupported modeled bands and dependent categorical status: qualify or withhold rather than display accepted-looking uncertainty. Missing intervals are not zero-width reliability.
4. Explain observed versus adjusted versus modeled values; differentiate operating-day approximation, record data end, complete-week cutoff and current wall-clock date.
5. Test accepted, limited, severe failure, insufficient support, missing/corrupt metadata and legacy report states with tiny API/static-render fixtures. All UI, Method and Validation wording must agree with the export.
6. Keep English-only live transport and source distinctions beyond color. Update the claim register dispositions indirectly through T56/T28 rather than typing metrics into strings.

## Acceptance
- [ ] Unsupported claims cannot appear as accepted through another view/export.
- [ ] A user can locate data cutoff, source type and scientific limitation without reading source code.
- [ ] Existing API/frontend checks and whole OpenAPI validity remain intact.

## Stop and ask if
A new wire status cannot be represented compatibly or the proposed wording would imply physical fire detection/forecast certainty. Resolve the contract before shipping.

