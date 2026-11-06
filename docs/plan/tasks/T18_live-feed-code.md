---
id: "T18"
title: "Live season feed, part 1: redacted NRT fetcher and a cached /live/season endpoint (off without a key)"
kind: "agent"
owner: "Monazir"
authors: ["Monazir","Sattyam","Sheikh","Shammo"]
phase: "P2"
size: "L"
needs: ["T03","T04","T07","T51"]
requires: ["real-data"]
branch: "ws1/T18-live-feed-code"
touches: ["ws3_anomaly/ingest/firms.py","ws3_anomaly/tests/test_ingest.py","scripts/export_area_catalog.py","ws2_platform/api/app.py","contracts/openapi.yaml","docs/project/contract-changes.md","ws5_frontend/src/App.tsx","ws5_frontend/src/components/Panels.tsx","ws5_frontend/src/i18n/en.json","ws5_frontend/src/i18n/bn.json","docs/guides/deployment.md"]
creates: ["ws3_anomaly/ingest/live.py","ws3_anomaly/tests/test_live.py","ws3_anomaly/live_inputs.json","ws2_platform/tests/test_api_live.py","ws5_frontend/src/live.ts","ws5_frontend/src/live.test.ts"]
checks: ["CHECK-PLAN","python -m pytest -q ws3_anomaly/tests/test_ingest.py ws3_anomaly/tests/test_live.py ws2_platform/tests/test_api_live.py ws2_platform/tests/test_tiny_api.py","CHECK-WEB"]
---
## Goal
Deferred optional extension. It is outside the default challenge-critical implementation path; no work is executed while this card is cut.

## Steps
1. Reopen only through an explicit scope/capacity decision after science, core user evidence and release gates are stable.
2. Rewrite the historical design against the current live/English architecture and exact output contracts before implementation. No snapshot files or Bangla restoration.
3. For NRT: freeze pinned/live boundary, late-arrival reconciliation, coverage, cross-year windows, saved adjustment applicability, failure/cache/redaction behavior and actual freshness verification. Never append unknown gaps as zeros or imply validated warning.
4. Declare revised file scopes and tests, read all named implementation paths, then use the authorized scientific lane if fitting is needed.
5. No favorable metric, additional feature count or claimed originality is an acceptance condition.

## Acceptance
- [ ] A new reviewed spec/scope and demonstrated user benefit exist before reopening.
- [ ] Scientific meaning, source/freshness, support and limitations are explicit.
- [ ] Default release remains functional when this extension is absent.

## Stop and ask if
The scope decision, required data, authority or dependency is absent. Keep the card cut and the final submission free of undelivered claims.
