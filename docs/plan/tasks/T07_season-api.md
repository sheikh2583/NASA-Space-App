---
id: T07
title: Season profile in the API, mock server, fixtures and snapshot
kind: agent
owner: Sattyam
authors: [Sattyam, Sheikh, Shammo]
phase: P1
size: M
needs: [T00]
requires: [real-data]
branch: ws1/T07-season-api
touches: [ws2_platform/api/app.py, ws2_platform/api/mock_server.py, ws2_platform/api/make_fixtures.py,
          contracts/openapi.yaml, docs/project/contract-changes.md, scripts/export_hosted_demo.py, tools/verify_files.py,
          ws5_frontend/src/snapshot.test.ts, ws5_frontend/public/demo/snapshot.json]
creates: [ws2_platform/tests/test_api_season.py, contracts/fixtures/punjab_season.json,
          contracts/fixtures/bangladesh_season.json]
checks: [CHECK-PLAN, CHECK-PY, CHECK-WEB, CHECK-SNAP, CHECK-FILES]
---
## Goal
Serve the season profile ("when does burning usually happen here, and how is this season going?") in every mode:
local API, mock API and the hosted snapshot. The library is done and tested (`ws4_outlook/season_profile.py`; spec
`docs/specs/I1_SEASON_PROFILE.md`).

## Context
- `Store.full_history(sel)` returns the weekly series used by summary and outlook: `week_start`, `value`, `lo`,
  `hi`, `modeled_share`, `source`.
- `Store.region_of(sel)` returns `{region_id, region_name, country}`, and `country` is the demo code `PB` or `BD`.
  `season_profile.SEASON_WINDOWS` keys are `pb` and `bd`.
- `ws5_frontend/src/snapshot.ts` `selectSnapshot` already returns `area[path.replace("/aoi/", "")]`. So once the
  snapshot has `areas.<key>.season`, `/aoi/season` works in snapshot mode with no client change.
- `ws2_platform/api/mock_server.py` serves `contracts/fixtures/{punjab|bangladesh}_{kind}.json` for each kind in a
  tuple.
- `ws2_platform/api/make_fixtures.py` writes those fixtures from the real API.
- The draft schema is `contracts/json_schemas/season_profile.schema.json`.

## Steps
1. **Contract** (`contracts/openapi.yaml`).
   - Add `POST /aoi/season`. The request body is `AOIRequest`. The 200 response is `SeasonProfileResponse`:
     `allOf: [Envelope, {type: object, required: [area, as_of, data_through, definition, seasons], properties: {area: {type: string, nullable: true}, as_of: {type: string, format: date}, data_through: {type: string, nullable: true}, definition: {type: string}, seasons: {type: array, items: {type: object}}}}]`.
   - The full shape of `seasons` stays in the JSON Schema file; reference it in a `description`.
   - Append a line to `docs/project/contract-changes.md`.
2. **Endpoint** (`ws2_platform/api/app.py`). Add next to `aoi_outlook`:
   ```python
   from ws4_outlook import season_profile as season_mod

   @app.post("/aoi/season")
   def aoi_season(req: AOIRequest):
       def run():
           s = store()
           sel = s.select(req.geometry, req.bbox)
           reg = s.region_of(sel)
           area = reg["country"].lower() if reg else None
           as_of = s.data_end + pd.Timedelta(days=1)
           if sel.empty or area not in season_mod.SEASON_WINDOWS:
               prof = {"schema_version": season_mod.SCHEMA_VERSION, "area": area, "as_of": as_of.date().isoformat(),
                       "data_through": s.data_end.date().isoformat(), "units": "", "definition": season_mod.DEFINITION,
                       "seasons": []}
               notes = ["No season windows are configured for this area."]
           else:
               prof = season_mod.season_profile(s.full_history(sel), as_of=as_of, area=area)
               notes = [season_mod.DEFINITION]
           return {**prof, **envelope("season", notes), "profile_version": prof["schema_version"]}
       return _cached(_key("season", req), run)
   ```
   The envelope goes last, so `schema_version` (0.2.0), `units` ("SNPP-equivalent detections per season"),
   `day_convention` and `notes` follow the API convention, and the profile's own version is kept as
   `profile_version`.

3. **Tests** in `ws2_platform/tests/test_api_season.py`, using `tiny_api` and `tiny_request`:
   - "pb" returns two seasons, `wheat_residue` and `paddy_residue`. The paddy `typical.p50.median_md` is "11-01",
     "11-02" or "11-03" (the tiny data peaks on 2 Nov), and wheat is "05-08" to "05-10".
   - "bd" returns one season, `dry_season`, with p50 in March.
   - The response validates against `SeasonProfileResponse` (OpenAPI) and against `season_profile.schema.json`
     (jsonschema, on the profile part).
   - Changing the request's `start` and `end` doesn't change the response.
   - A bbox with no cells, `[0, 0, 0.5, 0.5]`, returns `seasons == []` and a note.
4. **Mock and fixtures.**
   - Add `"season"` to the kinds tuple in `mock_server.py`, and `"season"` to the endpoint loop in
     `make_fixtures.py`.
   - On the laptop, run `python -m ws2_platform.api.make_fixtures`. Keep only the two new `*_season.json` files:
     `git checkout -- contracts/fixtures/*.json` for every other changed fixture, unless the change is intended.
5. **Snapshot.**
   - In `scripts/export_hosted_demo.py`, add `"season"` to `for endpoint in ("summary", "critical-periods", "drivers", "outlook")`.
   - Run `python scripts/export_hosted_demo.py`.
   - Check the size: `python -c "import os;print(os.path.getsize('ws5_frontend/public/demo/snapshot.json'))"` must
     stay under 1,000,000.
6. **Snapshot test.** In `snapshot.test.ts`, add: `selectSnapshot(snapshot, "/aoi/season", DEMOS.pb)` returns 2
   seasons, and for `DEMOS.bd` 1 season.
7. **verify_files.** Make `tools/verify_files.py --all` also validate each `areas.*.season` in
   `ws5_frontend/public/demo/snapshot.json` against the schema, when that file exists. Print `PASS snapshot season <key>`.
8. Run the checks, mark the card done, then `split` (Sattyam, Sheikh, Shammo), push and open the PR. Paste both demo
   areas' paddy and dry-season typical windows from the snapshot into the PR.

## Acceptance
- [ ] `test_api_season.py` passes in CI, using tiny data.
- [ ] The snapshot has `season` for `bd` and `pb`, and `verify_files --all` validates both.
- [ ] The mock serves `/aoi/season`: `curl -X POST localhost:8001/aoi/season -d @contracts/fixtures/punjab_request.json -H "Content-Type: application/json"`
  returns two seasons.
- [ ] `snapshot.json` is under 1 MB.

## Stop and ask if
- Snapshot Punjab paddy `typical.p50.median_md` isn't in late October or early November.
- The snapshot grows past 1 MB.
