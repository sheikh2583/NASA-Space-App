---
id: T48
title: Use runtime metadata consistently for record-end dates
kind: agent
owner: Shammo
authors: ["Shammo", "Sheikh"]
phase: P1
size: M
needs: ["T00"]
requires: []
branch: ws1/T48-record-end
touches: ["ws5_frontend/src/config.ts", "ws5_frontend/src/App.tsx", "ws5_frontend/src/api.ts", "ws5_frontend/src/types.ts", "ws5_frontend/src/components/AnalysisControls.tsx", "ws5_frontend/src/i18n/en.json", "ws5_frontend/src/i18n/bn.json", "scripts/export_area_catalog.py", "README.md", "docs/guides/deployment.md"]
creates: ["ws5_frontend/src/lib/recordEnd.ts", "ws5_frontend/src/lib/recordEnd.test.ts"]
checks: ["CHECK-PLAN", "python -m pytest -q ws2_platform/tests/test_season_record_end.py", "CHECK-WEB"]
human_checks: [CHECK-QA]
---
## Goal
Make date controls, status and snapshot request metadata agree with the actual served record.

## Context
ws2_platform/api/app.py health(); ws5_frontend/src/config.ts; ws5_frontend/src/App.tsx; ws5_frontend/src/snapshot.ts; scripts/export_hosted_demo.py; deployment/runtime.json.

## Steps
Live mode reads validated ISO data_through from /health; snapshot mode uses snapshot.data_through. Keep RECORD_END only as a documented fallback and display stale/fallback state accurately. Handle asynchronous metadata without overwriting explicit user ranges; clamp only against actual available bounds. Exporter derives record end from the local API health metadata and cross-checks response dates, never from a hardcoded day. Parameterize hosting date strings. Tests cover differing live/static dates, missing/invalid metadata and preserved explicit ranges. Preserve correct 2 Nov SNPP cutoff wording and the partial week starting 2 Nov. English UI only; preserve legacy translation keys where compatibility requires them.

## Acceptance
Default range, date picker maximum, exported request end and served data_through agree; no FIRMS credential reaches the frontend.

## Stop and ask if
The deployed metadata disagrees with the actual served artifacts; report the mismatch instead of masking it.

