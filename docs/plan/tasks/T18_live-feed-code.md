---
id: T18
title: "Live season feed, part 1: redacted NRT fetcher and a cached /live/season endpoint (off without a key)"
kind: agent
owner: Monazir
authors: [Monazir, Sattyam, Sheikh, Shammo]
phase: P2
size: L
needs: [T03, T04, T07]
requires: [real-data]
branch: ws1/T18-live-feed-code
touches: [ws3_anomaly/ingest/firms.py, ws3_anomaly/tests/test_ingest.py, scripts/export_area_catalog.py,
          ws2_platform/api/app.py, contracts/openapi.yaml, docs/project/contract-changes.md, ws5_frontend/src/App.tsx,
          ws5_frontend/src/components/Panels.tsx, ws5_frontend/src/i18n/en.json, ws5_frontend/src/i18n/bn.json,
          docs/guides/deployment.md]
creates: [ws3_anomaly/ingest/live.py, ws3_anomaly/tests/test_live.py, ws3_anomaly/live_inputs.json,
          ws2_platform/tests/test_api_live.py, ws5_frontend/src/live.ts, ws5_frontend/src/live.test.ts]
checks: ["CHECK-PLAN", "python -m pytest -q ws3_anomaly/tests/test_ingest.py ws3_anomaly/tests/test_live.py ws2_platform/tests/test_api_live.py ws2_platform/tests/test_tiny_api.py", "CHECK-WEB"]
---
## Goal
Punjab's paddy season peaks in early November, during judging. Show "this season so far" with near-real-time FIRMS
data, without retraining and without touching the pinned record. The Render backend fetches it on demand with the
key held only in Render's environment (H01), and caches it. Without the key, the endpoint says `off` and the UI shows
nothing new. T19 verifies it on Render.

## Context
- **Hosting.** One Render service runs `uvicorn ws2_platform.api.app:app` from the root `Dockerfile`, which copies
  `common/`, `ws2_platform/`, `ws3_anomaly/` and `ws4_outlook/`. Its Python packages are only `requirements-api.txt`:
  **no `requests`**. So the server-side fetch uses `urllib.request`. Don't change the Dockerfile or the requirements.
- **`ws3_anomaly/ingest/firms.py`** (local downloads; uses `requests`):
  - `fetch_window(session, key, source, bbox, first, n_days)` calls
    `https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{source}/{bbox}/{days}/{date}`, with `MAX_DAYS = 10` per
    call.
  - **Security bug:** a `requests` exception message can contain that URL, and so the key. `download()` logs it and
    `main()` prints it.
- `common.grid.cell_id` and `common.grid.local_solar_date` turn detections into cells and local solar days.
- Selectable areas are the ADM1 boundaries in `ws5_frontend/public/demo/areas.json` (`id`, `name`, `country`,
  `request.geometry`). The app applies one with `pickArea`.
- NRT detections have no `type` field. Drop cells listed as persistent hot spots, and keep VIIRS confidence `n` and `h`.

## Steps
1. **Redaction** (`firms.py`).
   - Add `redact(text: str, key: str | None) -> str`. It replaces the key with `***`, and any
     `/api/area/csv/<anything>/` segment with `/api/area/csv/***/`.
   - `fetch_window` re-raises every exception as `RuntimeError(redact(str(e), key))`, and redacts the HTTP body
     snippet.
   - `download()` uses the redacted text in gap entries and logs.
   - Tests in `test_ingest.py`:
     - a fake session raising `requests.ConnectionError("… /api/area/csv/SECRETKEY/VIIRS…")` gives a gap and log text
       without `SECRETKEY` (check with `caplog`);
     - `redact` is idempotent.
2. **`ws3_anomaly/ingest/live.py`** (stdlib `urllib` plus pandas; it imports nothing from `firms.py`):
   - `fetch_recent(key, bbox, since, today, opener=urllib.request.urlopen, source="VIIRS_NOAA20_NRT")`:
     - windows of at most 10 days, timeout 20 s;
     - any exception becomes `RuntimeError(redact(...))`, using a local copy of the same redact rule;
     - returns one DataFrame, de-duplicated on (`latitude`, `longitude`, `acq_date`, `acq_time`).
   - `build_live(inputs: dict, det: DataFrame, today) -> dict`:
     - keep confidence `n`/`h`, map to `cell_id`, keep each area's `cell_ids` and drop `hotspot_cells`;
     - local solar date and daily sums;
     - multiply by `n20_ratio[admin1_id][str(month)]`, falling back to `n20_ratio_default`.

     It returns
     `{generated_at, method_version, data_through, status, notes, areas: {id: {days, season: {season_year, to_date_total, percentile_at_cutoff, typical_to_date_total}}}}`.
     The `season` part adds the pinned record's in-progress season total to the new days, and compares with the
     area's `past_cum`.
   - `status` is one of:
     - `off`: no key;
     - `failed`: the fetch raised;
     - `stale`: `data_through < today - 3 days`;
     - `suspect`: any day exceeds 5 × that area's `max_daily`;
     - `ok` otherwise.
   - `LiveCache(ttl_s=10800)`: `get(now)` refetches at most every 3 hours. After a failure it keeps the last good
     payload, with `status: stale` and a note.
   - **Tests** (`test_live.py`), with no network: a fake opener serving a small recorded CSV string. Cover:
     - local dates across midnight UTC;
     - the ratio is applied;
     - de-duplication;
     - hotspots are dropped;
     - every status, including `off`;
     - the cache TTL and failure fallback;
     - the key never appears in the payload or in an exception message.
3. **Inputs export** (`scripts/export_hosted_demo.py`). Also write `ws3_anomaly/live_inputs.json`, under 300 KB:
   - for each area in `ws5_frontend/public/demo/areas.json` with cells:
     - `cell_ids`, `bbox`, `admin1_id`;
     - `max_daily`, from harmonized daily sums;
     - `past_cum`: from `season_profile`'s `season_years`, the cumulative total at each day offset 0-120 for each past
       complete season;
     - the in-progress season total so far;
   - `n20_ratio` from `data/interim/sheikh/b1_params.pkl`, read as `ws1_harmonize/run.py` reads it (`params["n20"]`
     maps `(admin1_id, month)` to a ratio; write it as nested string keys), plus `n20_ratio_default`
     (`params["b0_n20"]`) and `method_version`;
   - `hotspot_cells`: cells with detections in at least 80% of weeks in 2018-2025. List them in the hand-over.

   This only reads saved outputs; nothing is fitted.
4. **API** (`app.py`): add `GET /live/season?area=<id>`, before the frontend mount.
   - It reads `FIRMS_MAP_KEY` from the environment only, and never logs it or the request URL.
   - It loads `ws3_anomaly/live_inputs.json` once, and uses one module-level `LiveCache`.
   - It returns that area's entry plus the top-level status fields. An unknown area gives 404; no key gives
     `status: "off"`.
   - Add it to `contracts/openapi.yaml` and append a line to `docs/project/contract-changes.md`.
   - `test_api_live.py` uses the `tiny_api` fixture, with a monkeypatched fetch:
     - `off` without a key;
     - `ok` with a fake key and a fake fetch;
     - the key isn't in the response body.
5. **UI.**
   - `src/live.ts`:
     - `loadLive(areaId)` calls the API in live mode and returns `null` in snapshot mode, on errors and for `off`;
     - `liveFor(payload)` returns it only for `ok`, or `stale` with a warning.
   - The status card and the season card show `t("live.through", { date })`: "Data through {{date}} (near real time,
     NOAA-20 scaled to the Suomi NPP standard; not part of the model)". A stale feed gets an amber `t("live.stale")`.
   - `live.test.ts` covers both helpers.
6. **`docs/guides/deployment.md`.** Add a "Live season feed" section: what it fetches, that the key lives only in Render's
   environment, how to switch it off (delete the variable), how to rotate the key, and the 3-hour cache.
7. Run the checks, mark the card done, and hand over for commit.

## Acceptance
- [ ] The redaction tests prove the key can't reach logs, gap lists, exceptions or responses.
- [ ] All live tests pass with no network; the API answers `off` without a key.
- [ ] `live_inputs.json` is under 300 KB, and the Docker build context still needs no new package.

## Stop and ask if
- Any test needs real network access.
- The live code would need a package that isn't in `requirements-api.txt`.
