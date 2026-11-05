---
id: T50
title: Repair partial-month, calendar and snapshot regressions
kind: agent
owner: Sattyam
authors: [Sattyam, Shammo, Sheikh]
phase: P1
size: M
needs: [T48]
requires: []
branch: ws1/T50-product-regressions
touches: [ws2_platform/api/app.py, ws5_frontend/src/lib/format.ts, ws5_frontend/src/lib/format.test.ts, ws5_frontend/src/components/Calendar.tsx, ws5_frontend/src/components/Calendar.test.tsx, ws5_frontend/src/snapshot.ts, ws5_frontend/src/snapshot.test.ts, ws5_frontend/src/areas.test.ts, ws5_frontend/src/i18n/en.json]
creates: [ws2_platform/tests/test_partial_month.py, docs/results/PRODUCT_REGRESSIONS_2026-11-05.md]
checks: [CHECK-PLAN, "python -m pytest -q ws2_platform/tests/test_partial_month.py", CHECK-WEB, CHECK-SNAP]
human_checks: []
---
## Goal
Fix five reproduced product defects without recalibration or unsupported scientific claims.
## Context
Read all touched files, ws2_platform/tests/conftest.py, ws2_platform/tests/tiny_data.py,
ws2_platform/tests/test_api_complete.py and the saved snapshot request metadata.
## Steps
1. Compute month coverage from intersection with requested start/end and actual data end.
2. Give display ISO week 53 its own column; keep the existing folded climatology helper.
3. Clear failed snapshot download promises so a later retry can fetch again.
4. Make uncertainty help describe a nominal target and conditional undercoverage.
5. Derive snapshot test requests from exported request metadata; preserve rejection assertions.
6. Add direct regression tests, run live/static builds, commit by owner and record deployment status.
## Acceptance
15-31 December is 17 days/incomplete; full months remain complete; display weeks 52 and 53
have different coordinates; failed snapshot download retries succeed; fresh exported metadata
passes tests without date constants. Scientific undercoverage and pending forecast validation remain explicit.
## Stop and ask if
Fixing any reproduction requires modifying scientific artifacts or weakening a test.
