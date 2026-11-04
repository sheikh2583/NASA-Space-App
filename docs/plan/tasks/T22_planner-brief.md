---
id: T22
title: Planner brief (one printable page, en/bn)
kind: agent
owner: Shammo
authors: [Shammo]
phase: P2
size: M
needs: [T08, T21]
requires: []
branch: ws1/T22-planner-brief
touches: [ws5_frontend/src/App.tsx, ws5_frontend/src/components/SeasonCard.tsx, ws5_frontend/src/styles.css,
          ws5_frontend/src/i18n/en.json, ws5_frontend/src/i18n/bn.json]
creates: [ws5_frontend/src/components/Brief.tsx, ws5_frontend/src/components/Brief.test.tsx,
          ws5_frontend/src/lib/miniMap.ts, ws5_frontend/src/lib/miniMap.test.ts]
checks: [CHECK-PLAN, CHECK-WEB, CHECK-SNAP]
---
## Goal
Influence comes from use. A division or state officer, an NGO or a journalist needs one page they can print or
forward: when burning usually happens, how this season is going, and where.

## Steps
1. **Opening the brief.** A "Planner brief" button on `SeasonCard` (`t("brief.open")`) sets `view` to `"brief"` for
   the current area and season. If T12 is merged, the URL hash gets `v=brief`.
2. **`lib/miniMap.ts`.** `cellsToSvgRects(cells, width, height)` maps cells (`lat_c`, `lon_c`, `share`) to
   `{x, y, w, h, fill}` within a box, keeping the aspect ratio (cos(latitude) correction). No map tiles, so it
   always prints. Test that the corners map to the box edges and that a 0.1° cell has positive size.
3. **`components/Brief.tsx`.** Print layout on A4 portrait, with this CSS in `styles.css`:
   `@media print { @page { size: A4; margin: 12mm } .topbar, .banner, .mapcol, nav { display: none } }`.
   It contains:
   - **Title:** `t("brief.title", { area, season })`, plus the "Data through" date and the generated date.
   - **Box "When":** the typical window sentence from the season card, and a 52-week strip (SVG) with the band and the
     peak tick.
   - **Box "This season":** the season-to-date sentence and the current status level from T03.
   - **Box "Where":** an inline SVG mini-map of the recurrence cells (T21, for the same season), the legend "share of
     years, 2012-2025, observed", and a north arrow.
   - **Box "Trend":** timing and amount trend sentences, only when the verdict isn't "no clear shift".
   - **Box "Read with care":** four caveats as i18n keys (`brief.caveat_1`…`brief.caveat_4`), from the T10 text:
     detections are not area; overpass times; pre-2012 modeled; not an alert service.
   - **Footer:** the method version, the share link, and "Data: NASA FIRMS (MODIS, VIIRS)".
   - A "Print or save as PDF" button calls `window.print()`, and is hidden in print.
4. **`Brief.test.tsx`.** Render from `public/demo/snapshot.json` (`areas.pb`) and `public/demo/recurrence_pb.json`
   (T21). Check that:
   - the five box headings are present in en;
   - the Bangla render has no English box headings;
   - the SVG has at least one `<rect`.
5. Run the checks. In the snapshot build, open the brief for Punjab paddy, then use Chrome's print preview in English
   and in Bangla. Each must fit on **one** page; attach the two PDFs or screenshots to the PR.
6. Mark the card done, `split`, push and open the PR.

## Acceptance
- [ ] Tests pass. The brief prints on one A4 page per language for each demo area's main season.
- [ ] No map tiles or external images are needed to print.

## Stop and ask if
- Bangla text overflows the page even at 10 pt.
