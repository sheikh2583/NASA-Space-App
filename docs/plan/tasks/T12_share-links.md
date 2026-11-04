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
checks: [CHECK-PLAN, CHECK-WEB, CHECK-SNAP]
---
## Goal
A planner or journalist can send a link that opens exactly "Punjab, week of 4 Nov 2024, in Bangla". The video and
the judges' first click can land on the right view too.

## Context
- GitHub Pages serves one static file, so state goes in the URL **hash** (`#v=explore&a=pb&p=2024-11-04&l=bn`), not
  the path.
- `App.tsx` holds `view`, `demo`/`area`, `period` and the i18n language.

## Steps
1. **`lib/urlState.ts`.**
   - `export interface UrlState { v?: "explore" | "validation" | "method"; a?: string; p?: string; l?: "en" | "bn"; s?: string }`
     where `a` is `bd`, `pb` or `region:<id>`, and `s` is a story step for T23.
   - `parse(hash: string): UrlState`: ignore unknown keys and invalid values (a wrong date format, unknown view or
     unknown language).
   - `format(state: UrlState): string`: stable key order v, a, p, l, s; omit empty values; returns "" or "#…".
2. **`urlState.test.ts`.** Round-trips every field, ignores unknown keys, rejects `p=2024-13-40` and `l=fr`, and
   `format({})` returns "".
3. **`App.tsx`.**
   - On mount, read `parse(location.hash)` and apply it: view, demo area (`pickDemo`) or region, language, and
     `setPeriod({start: p, end: addDays(p, 6), key: p})` after the summary loads.
   - Whenever these change, call `history.replaceState(null, "", format(state))`.
   - Drawn polygons aren't encoded; when the area is drawn, omit `a`.
4. **Copy link.**
   - In the export card, add a button `t("export.copy_link")`. It calls `navigator.clipboard.writeText(location.href)`;
     when the clipboard is missing, it shows a read-only `<input>` with the URL selected.
   - Show `t("export.copied")` for 2 seconds.
5. Run the checks. In the snapshot build, open `…/#a=pb&l=bn&p=2024-11-04`: Punjab opens in Bangla with that week
   highlighted. Screenshot it for the PR.
6. Mark the card done, `split`, push and open the PR.

## Acceptance
- [ ] `urlState.test.ts` passes.
- [ ] Opening a copied link in a new tab reproduces the view, in both modes.

## Stop and ask if
- Applying the URL on load causes two summary requests.
