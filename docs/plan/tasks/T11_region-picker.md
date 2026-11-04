---
id: T11
title: "Retired: region picker (done on main by the named-area explorer)"
kind: agent
owner: Sattyam
authors: [Sattyam]
phase: P1
size: S
needs: [T07]
requires: []
branch: ws1/T11-region-picker
touches: [docs/plan/STATUS.md]
creates: []
checks: [CHECK-PLAN]
---
## Goal
Retired on 4 Nov 2026; its status is `cut`. Nothing to do.

## Context
The goal was any Bangladesh division or Punjab/Haryana/Delhi state, chosen by name, with exact boundaries. Commits
`04adbc4` and `0c9241d` delivered it:
- `scripts/export_area_catalog.py` writes `ws5_frontend/public/demo/areas.json` from geoBoundaries ADM1, keeping
  regions that have grid cells;
- `ws5_frontend/src/areas.ts` and `components/AreaFilters.tsx` provide country, local name search (English and
  Bangla), an administrative selector and Apply;
- the live API serves any selected geometry.

`CLAUDE.md` says to keep this pattern and not to reintroduce manual drawing as the main flow. Cards that used to
mention "the region picker" now mean these area filters.

## Steps
1. None. If `plan.py next` ever offers this card, run `python scripts/plan.py set T11 cut`.

## Acceptance
- [ ] Status is `cut`.

## Stop and ask if
- Never.
