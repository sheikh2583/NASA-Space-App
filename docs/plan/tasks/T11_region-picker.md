---
id: T11
title: Region picker with exact administrative regions (API and snapshot)
kind: agent
owner: Sattyam
authors: [Sattyam, Shammo]
phase: P1
size: M
needs: [T07]
requires: [real-data]
branch: ws1/T11-region-picker
touches: [ws2_platform/api/app.py, ws2_platform/api/query.py, ws2_platform/api/static_export.py,
          contracts/openapi.yaml, docs/project/contract-changes.md, ws5_frontend/src/types.ts, ws5_frontend/src/snapshot.ts,
          ws5_frontend/src/snapshot.test.ts, ws5_frontend/src/App.tsx, ws5_frontend/src/components/MapView.tsx,
          ws5_frontend/src/i18n/en.json, ws5_frontend/src/i18n/bn.json]
creates: [ws2_platform/tests/test_api_regions.py, ws5_frontend/src/components/RegionPicker.tsx,
          ws5_frontend/src/components/RegionPicker.test.tsx, ws5_frontend/public/demo/static]
checks: [CHECK-PLAN, CHECK-PY, CHECK-WEB, CHECK-SNAP]
---
## Goal
The challenge asks for a calendar for a selected area. Let anyone pick any processed administrative region by name,
in the local app and on the hosted site, with totals for **exactly** that region's cells.

## Context
- ADM1 means **Bangladesh divisions** and **Indian states or union territories**. Our India boundaries keep only
  Punjab, Haryana and Delhi (`TARGET_ADMIN_ISOS` in `ws2_platform/cells.py`), and Delhi is a union territory. These
  are not districts.
- `cells.parquet` has `admin1_id`, `admin1_name` and `country` (`BD` or `PB`, the demo code). The 4 Nov run has 11
  regions.
- `ws2_platform/api/static_export.py` already writes the right layout:
  - `index.json`;
  - `regions/<admin1_id>/{summary,critical-periods,outlook,drivers,cells}.json`;
  - `meta/validation.json`.

  But it requests each region by its **bounding box**, which can include a neighbour's cells. This card switches it
  to exact ids.
- `AOIRequest` (`ws2_platform/api/app.py`) requires exactly one of `geometry` or `bbox`. `Store.select(geometry,
  bbox)` is in `query.py`.
- `snapshot.ts` `areaKey()` only knows the two demo areas.

## Steps
1. **Contract.**
   - `AOIRequest` gains optional `region_id` (string); exactly one of `geometry`, `bbox` or `region_id` must be
     given. In OpenAPI, describe it in the schema's `description`; the server validates it.
   - New `GET /meta/regions` returns `{schema_version, data_through, regions: [{region_id, region_name, country, level, n_cells, bbox}]}`,
     where `level` is `division`, `state` or `union_territory`.
   - Append to `docs/project/contract-changes.md`.
2. **API.**
   - `AOIRequest`: add `region_id: Optional[str] = None`, and make `_one_area` count the three fields.
   - `Store.select(geometry=None, bbox=None, region_id=None)`: when `region_id` is given, return
     `self.cells[self.cells["admin1_id"] == region_id]`. If that is empty, raise `AOIError(f"unknown region_id {region_id}")`.
   - Every endpoint calls `s.select(req.geometry, req.bbox, req.region_id)`. `ExportRequest` inherits the field.
   - `/meta/regions`: group `cells` by (`admin1_id`, `admin1_name`, `country`). The level is `division` for `BD`;
     for India it is `union_territory` when the name contains "Delhi", else `state`. The bbox is the cell-centre
     bounds ±0.05.
3. **Tests** in `ws2_platform/tests/test_api_regions.py`, with `tiny_api`. The tiny data has regions `PB-1` and
   `BD-1`, with 4 cells each.
   - `/meta/regions` lists both, with `n_cells == 4` and levels `state` and `division`.
   - `/aoi/summary` with `{"region_id": "PB-1", "start": …, "end": …}` has `aoi.n_cells == 4`.
   - An unknown id returns 422.
   - Giving both `region_id` and `bbox` returns 422.
4. **Static export, now exact.** In `static_export.py`:
   - Request each region with `{"region_id": rid, "start": …, "end": …, "res": "week"}` instead of the bbox.
   - Add `"season"` to the endpoint tuple. Drop `cells` if the size budget below is exceeded.
   - Run `python -m ws2_platform.api.static_export --out ws5_frontend/public/demo/static`. That gives
     `demo/static/index.json`, `demo/static/regions/<admin1_id>/<endpoint>.json` and `demo/static/meta/validation.json`.
   - Measure the total size and record it in the PR; each region folder should be under 600 KB.

5. **Snapshot client** (`snapshot.ts`).
   - `areaKey()` returns `"region:" + request.region_id` when `region_id` is set.
   - `snapshotCall` for a region key fetches `demo/static/regions/<id>/<endpoint>.json` (lazy, cached per URL), and
     fetches the region list from `demo/static/index.json`.
   - Dates are fixed exactly as for the demo areas.
   - Tests in `snapshot.test.ts`: `areaKey({region_id: "X", …}) === "region:X"`, plus a test of a pure helper
     `regionUrl(id, endpoint)`.
6. **UI.**
   - `RegionPicker.tsx` is a labelled `<select>` with `<optgroup>`s: `t("regions.group_bd")` "Bangladesh: divisions"
     and `t("regions.group_in")` "India: states and territories". Options come from `/meta/regions` (API) or
     `regions/index.json` (snapshot), and each option label has its level word.
   - Choosing one sets `area = { region_id }`.
   - `MapView` gets the region's bbox to fit the view; the outline comes from the cells layer.
   - Keep the two demo buttons.
   - `RegionPicker.test.tsx`: renders both groups from a fixed list.
7. Run the checks. In the snapshot build, pick two regions and compare their totals with local API mode (draw
   nothing; use the picker in both). Paste them into the PR.
8. Mark the card done, `split`, push and open the PR.

## Acceptance
- [ ] `test_api_regions.py` passes in CI.
- [ ] Every processed region (11 in the 4 Nov run) is selectable by name in both modes; the labels say division,
  state or union territory.
- [ ] Region totals equal the sum over exactly that region's cells (`n_cells` matches `/meta/regions`).

## Stop and ask if
- The region files total more than 8 MB.
- A region's `n_cells` from the API differs from `cells.parquet`.
