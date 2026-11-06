---
id: "T20"
title: "Overpass blind-spot indicator (are fires moving out of satellite view?)"
kind: "agent"
owner: "Monazir"
authors: ["Monazir","Shammo"]
phase: "P2"
size: "M"
needs: ["T00","T51"]
requires: ["real-data"]
branch: "ws1/T20-blindspot"
touches: ["ws5_frontend/src/components/Pages.tsx","ws5_frontend/src/i18n/en.json","ws5_frontend/src/i18n/bn.json","ws5_frontend/public/demo/areas.json"]
creates: ["ws3_anomaly/blindspot.py","ws3_anomaly/tests/test_blindspot.py"]
checks: ["CHECK-PLAN","python -m pytest -q ws3_anomaly/tests/test_blindspot.py","CHECK-FILES","CHECK-WEB"]
human_checks: ["CHECK-QA"]
---
## Goal
Deferred optional extension. It is outside the default challenge-critical implementation path; no work is executed while this card is cut.

## Steps
1. Reopen only through an explicit scope/capacity decision after science, core user evidence and release gates are stable.
2. Rewrite the historical design against the current live/English architecture and exact output contracts before implementation. No snapshot files or Bangla restoration.
3. For observation-time analysis: acquire independent observation-opportunity/orbit metadata before attributing detected-time changes to orbital drift or unseen burning. Detection-conditioned medians alone do not identify missed fires; exploratory results may be inconclusive.
4. Declare revised file scopes and tests, read all named implementation paths, then use the authorized scientific lane if fitting is needed.
5. No favorable metric, additional feature count or claimed originality is an acceptance condition.

## Acceptance
- [ ] A new reviewed spec/scope and demonstrated user benefit exist before reopening.
- [ ] Scientific meaning, source/freshness, support and limitations are explicit.
- [ ] Default release remains functional when this extension is absent.

## Stop and ask if
The scope decision, required data, authority or dependency is absent. Keep the card cut and the final submission free of undelivered claims.
