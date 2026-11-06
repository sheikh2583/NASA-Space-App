---
id: "T22"
title: "Evidence-bearing planner brief in English"
kind: "agent"
owner: "Shammo"
authors: ["Shammo"]
phase: "P2"
size: "M"
needs: ["T08","T58","T60"]
requires: []
branch: "ws1/T22-planner-brief"
touches: ["ws5_frontend/src/App.tsx","ws5_frontend/src/types.ts","ws5_frontend/src/components/SeasonCard.tsx","ws5_frontend/src/styles.css","ws5_frontend/src/i18n/en.json"]
creates: ["ws5_frontend/src/components/Brief.tsx","ws5_frontend/src/components/Brief.test.tsx","ws5_frontend/src/lib/miniMap.ts","ws5_frontend/src/lib/miniMap.test.ts"]
checks: ["CHECK-PLAN","CHECK-WEB"]
---
## Goal
Give a monitoring/planning user a one-page export that remains understandable outside the app (C06).

## Steps
1. Read the challenge contract, claim register, T58 support/provenance contract and current view/share/season code.
2. Add a brief view/button using current selected runtime data: area/season, central window, same-cutoff status, source/record dates, supported comparison, method/runtime identity and share link.
3. Include an existing selected-period spatial view with its exact meaning. Recurrence may be added only when T21 is actually delivered; it is not a prerequisite for this useful brief.
4. Add a concise limitations box: detections versus burned area, observed/adjusted/modeled, availability, uncertainty disposition and absence of demonstrated operational warning.
5. Use tile-free inline graphics and English print CSS. Test longest names, unavailable products, low support, stale metadata, missing uncertainty and no-data state with src/test fixtures/renderHtml.
6. Observe print preview and export A4 output for both main regions. It must fit one readable page without clipping or hidden caveats; save generated evidence outside Git.

## Acceptance
- [ ] One readable page from actual selected data, with date/source/scientific status.
- [ ] Brief and API/chart values agree; unavailable values are not invented.
- [ ] No snapshot or Bangla dependency; printing needs no map network request.

## Stop and ask if
A critical field lacks provenance/support or readable layout requires hiding caveats. Narrow the content rather than conceal limitations.
