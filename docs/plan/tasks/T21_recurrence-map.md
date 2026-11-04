---
id: T21
title: Recurrence map (how often each place burns in a season)
kind: agent
owner: Sattyam
authors: [Sattyam, Shammo, Sheikh]
phase: P2
size: M
needs: [T07]
requires: [real-data]
branch: ws1/T21-recurrence-map
touches: [ws2_platform/api/app.py, contracts/openapi.yaml, docs/CONTRACT_CHANGES.md, scripts/export_hosted_demo.py,
          ws5_frontend/src/types.ts, ws5_frontend/src/components/MapView.tsx, ws5_frontend/src/App.tsx,
          ws5_frontend/src/snapshot.ts, ws5_frontend/src/i18n/en.json, ws5_frontend/src/i18n/bn.json]
creates: [ws2_platform/recurrence.py, ws2_platform/tests/test_recurrence.py, ws5_frontend/public/demo/recurrence_bd.json,
          ws5_frontend/public/demo/recurrence_pb.json]
checks: [CHECK-PLAN, CHECK-PY, CHECK-WEB, CHECK-SNAP]
---
## Goal
Planners need *where* burning returns every year, not only when. Turn the observed seasons into a map of the share of
years each cell burned.

## Definition
For each cell and season, the share of **observed-era complete seasons** in which the cell had at least one detection
inside that season's window.
- Use only `harmonized` rows with `source == "observed_viirs"`. Modeled years are excluded, and the legend says
  "2012-2025, Suomi NPP observed".
- **Denominator:** the season years where SNPP operated on at least 90% of the window's days, according to
  `sensor_days`. This automatically respects the outage handling after T06.
- Also report `mean_detections` per counted season.

## Steps
1. **`ws2_platform/recurrence.py`,** `recurrence(harmonized, cells, sensor_days, cell_ids, season: Season, as_of) -> DataFrame`
   with columns `cell_id`, `lat_c`, `lon_c`, `share`, `n_years` and `mean_detections`.
   - Season windows come from `ws4_outlook.season_profile.Season.bounds`.
   - Only seasons with `end <= as_of` count.
2. **Tests** (`test_recurrence.py`), with `make_tiny_processed`, or direct frames:
   - a cell burning in 7 of 10 observed seasons has `share == 0.7`;
   - a season where SNPP was off for most of its window isn't counted in `n_years`;
   - modeled rows never count.
3. **API.**
   - `POST /aoi/recurrence` takes an AOIRequest plus `season` (a season name; it defaults to the area's last
     window).
   - It returns `{…envelope, season, years: "2012-2025", cells: [{cell_id, lat_c, lon_c, share, n_years, mean_detections}]}`.
   - Add it to OpenAPI and `CONTRACT_CHANGES.md`.
   - Add a tiny-API test.
4. **Snapshot**, in separate lazy files so the first page load stays small.
   - `export_hosted_demo.py` writes `ws5_frontend/public/demo/recurrence_<key>.json` as
     `{<season name>: [cells…]}`, with `share` rounded to 2 and `mean_detections` to 1.
   - `snapshot.ts` serves `/aoi/recurrence` by fetching that file once (cached) and picking `body.season`.
5. **UI.**
   - `MapView` gets a layer toggle (`t("map.layer_week")` / `t("map.layer_recurrence")`). The recurrence layer
     colours cells with a sequential scale from 0% to 100% and a legend "share of years".
   - With more than one season, a season `<select>` appears.
   - Clicking a cell shows `t("map.recurrence_popup", { n, N })`: "Burned in {{n}} of {{N}} seasons (2012-2025)".
6. Republish. Run the checks, mark the card done, `split`, push and open the PR. Include a screenshot of each demo
   area's main season.

## Acceptance
- [ ] Tests pass. The recurrence layer works in both modes with a correct legend.
- [ ] `snapshot.json` doesn't grow; each `recurrence_<key>.json` is under 200 KB; measured sizes in the PR.

## Stop and ask if
- No cell in Punjab paddy has a share of 0.5 or more (that would suggest a data problem).
