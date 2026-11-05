---
id: T12
title: Shareable links (view, area, period, language in the URL)
kind: agent
owner: Shammo
authors: [Shammo]
phase: P1
size: S
needs: [T00]
requires: []
branch: ws1/T12-share-links
touches: [ws5_frontend/src/App.tsx, ws5_frontend/src/i18n/en.json, ws5_frontend/src/i18n/bn.json]
creates: [ws5_frontend/src/lib/urlState.ts, ws5_frontend/src/lib/urlState.test.ts]
checks: ["CHECK-PLAN", "CHECK-WEB"]
---
## Goal
A planner or journalist can send a link that opens exactly "Punjab, week of 4 Nov 2024, in Bangla". The video and
the judges' first click can land on the right view too.

## Context
- State goes in the URL **hash** (`#v=explore&a=<area id>&p=2024-11-04&l=bn`). That is still the simplest choice:
  - Render serves the built app through FastAPI `StaticFiles(html=True)` (`ws2_platform/api/frontend.py`), which has
    no fallback for unknown paths, so path-based routes would 404;
  - a hash never reaches the server, never reloads the page, and also works on the legacy Pages snapshot.
- `App.tsx` holds `view`, `selectedId` (an id from `ws5_frontend/public/demo/areas.json`; `pickArea(option)` applies
  it), `period` and the i18n language. The default area is Dhaka (`defaultArea` in `areas.ts`).

## Steps
1. **`lib/urlState.ts`.**
   - `export interface UrlState { v?: "explore" | "validation" | "method"; a?: string; p?: string; l?: "en" | "bn"; s?: string }`
     where `a` is an area id from the catalog, and `s` is a story step for T23.
   - `parse(hash: string): UrlState`: ignore unknown keys and invalid values (a wrong date format, unknown view or
     unknown language).
   - `format(state: UrlState): string`: stable key order v, a, p, l, s; omit empty values; returns "" or "#…".
2. **`urlState.test.ts`.** Round-trips every field, ignores unknown keys, rejects `p=2024-13-40` and `l=fr`, and
   `format({})` returns "".
3. **`App.tsx`.**
   - On mount, read `parse(location.hash)` and apply it:
     - the view;
     - the area: once the catalog has loaded, find the option with that id and call `pickArea`; an unknown id keeps
       the default;
     - the language;
     - `setPeriod({start: p, end: addDays(p, 6), key: p})` after the summary loads.
   - Whenever these change, call `history.replaceState(null, "", format(state))`.
   - Only catalog areas are encoded. With no selected area, omit `a`.
4. **Copy link.**
   - In the export card, add a button `t("export.copy_link")`. It calls `navigator.clipboard.writeText(location.href)`;
     when the clipboard is missing, it shows a read-only `<input>` with the URL selected.
   - Show `t("export.copied")` for 2 seconds.
5. Run the checks. In a local live build (`python scripts/workflow.py dev`, or the Render URL after commit), open
   `…/#a=<Punjab's id>&l=bn&p=2024-11-04`. Punjab must open in Bangla with that week highlighted. Screenshot it for
   the hand-over.
6. Mark the card done and hand over for commit.

## Acceptance
- [ ] `urlState.test.ts` passes.
- [ ] Opening a copied link in a new tab reproduces the view, on Render (live) and in the snapshot build.

## Stop and ask if
- Applying the URL on load causes two summary requests.
