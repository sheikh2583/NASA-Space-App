---
id: "T25"
title: "Fire intensity (FRP) view, labelled uncalibrated"
kind: "agent"
owner: "Sattyam"
authors: ["Sattyam","Shammo","Sheikh"]
phase: "P2"
size: "S"
needs: ["T07","T51"]
requires: ["real-data"]
branch: "ws1/T25-frp-view"
touches: ["ws2_platform/api/app.py","contracts/openapi.yaml","docs/project/contract-changes.md","scripts/export_area_catalog.py","ws5_frontend/src/types.ts","ws5_frontend/src/api.ts","ws5_frontend/src/App.tsx","ws5_frontend/src/components/AnalysisControls.tsx","ws5_frontend/src/components/SeriesChart.tsx","ws5_frontend/src/i18n/en.json","ws5_frontend/src/i18n/bn.json"]
creates: ["ws2_platform/tests/test_api_frp.py","ws5_frontend/public/demo/frp_bd.json","ws5_frontend/public/demo/frp_pb.json"]
checks: ["CHECK-PLAN","python -m pytest -q ws2_platform/tests/test_api_frp.py ws2_platform/tests/test_tiny_api.py","CHECK-WEB"]
human_checks: ["CHECK-PY"]
---
## Goal
Deferred optional extension. It is outside the default challenge-critical implementation path; no work is executed while this card is cut.

## Steps
1. Reopen only through an explicit scope/capacity decision after science, core user evidence and release gates are stable.
2. Rewrite the historical design against the current live/English architecture and exact output contracts before implementation. No snapshot files or Bangla restoration.
3. For FRP: keep sampled MW distinct from energy/continuous intensity, never apply count bands as calibrated FRP uncertainty, and resolve NOAA-20 count-ratio limitations.
4. Declare revised file scopes and tests, read all named implementation paths, then use the authorized scientific lane if fitting is needed.
5. No favorable metric, additional feature count or claimed originality is an acceptance condition.

## Acceptance
- [ ] A new reviewed spec/scope and demonstrated user benefit exist before reopening.
- [ ] Scientific meaning, source/freshness, support and limitations are explicit.
- [ ] Default release remains functional when this extension is absent.

## Stop and ask if
The scope decision, required data, authority or dependency is absent. Keep the card cut and the final submission free of undelivered claims.
