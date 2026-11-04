---
id: T18
title: "Live season feed, part 1: redacted NRT fetcher, live builder and workflow step (off)"
kind: agent
owner: Monazir
authors: [Monazir, Sheikh, Shammo]
phase: P2
size: L
needs: [T03, T04, T07]
requires: []
branch: ws1/T18-live-feed-code
touches: [ws3_anomaly/ingest/firms.py, ws3_anomaly/tests/test_ingest.py, scripts/export_hosted_demo.py,
          .github/workflows/pages.yml, ws5_frontend/src/App.tsx, ws5_frontend/src/components/Panels.tsx,
          ws5_frontend/src/i18n/en.json, ws5_frontend/src/i18n/bn.json, docs/HOSTING.md]
creates: [ws3_anomaly/ingest/live.py, ws3_anomaly/tests/test_live.py, ws5_frontend/src/live.ts,
          ws5_frontend/src/live.test.ts]
checks: [CHECK-PLAN, CHECK-PY, CHECK-WEB, CHECK-SNAP]
---
## Goal
Punjab's paddy season peaks in early November, during judging. Keep "this season so far" current every night without
retraining and without any history in CI. This card builds and tests everything with the workflow step **switched
off**; T39 adds the secret and T19 switches it on.

## Context
- **`ws3_anomaly/ingest/firms.py`:**
  - `fetch_window(session, key, source, bbox, first, n_days)` calls
    `https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{source}/{bbox}/{days}/{date}`, with
    `MAX_DAYS = 10` per call.
  - **Security bug:** a `requests` exception message can contain that URL, and so the MAP_KEY. `download()` then logs
    it (`log.warning("gap …: %s", e)`) and `main()` prints it. In a public repository's Actions log that would leak
    the key.
  - `download()` caches each window as a CSV and skips windows already cached. Re-fetching recent days must bypass
    that cache.
- `common.grid.cell_id` and `common.grid.local_solar_date` turn detections into cells and local solar days.
- **NRT detections have no `type` field.** Static industrial heat sources can't be filtered by type, so drop
  detections in cells listed as persistent hot spots, and keep VIIRS confidence `n` and `h`.

## Steps
1. **Redaction** (`firms.py`).
   - Add `redact(text: str, key: str | None) -> str`. It replaces the key with `***` and any
     `/api/area/csv/<anything>/` path segment with `/api/area/csv/***/`.
   - In `fetch_window`, convert every exception to `RuntimeError(redact(str(e), key))` before raising, and redact
     the HTTP body snippet.
   - In `download()`, the gap entry and the log line use the redacted text.
   - Tests in `test_ingest.py`:
     - a fake session raising `requests.ConnectionError("… /api/area/csv/SECRETKEY/VIIRS…")` produces a gap and log
       text without `SECRETKEY` (use `caplog`);
     - `redact` is idempotent.
2. **`ws3_anomaly/ingest/live.py`.** Two functions:
   - `fetch_recent(key, bbox, since, today, source="VIIRS_NOAA20_NRT")` calls `fetch_window` directly (no cache) in
     windows of at most 10 days, from `since` (the last good `data_through` minus 3 days, because NRT arrives late)
     to `today`. It returns one DataFrame, with duplicates removed on (`latitude`, `longitude`, `acq_date`,
     `acq_time`).
   - `build_live(inputs: dict, det: DataFrame, today) -> dict`:
     - keep confidence `n`/`h`;
     - map to `cell_id`, keeping only `inputs["areas"][key]["cell_ids"]` and dropping `inputs["hotspot_cells"]`;
     - compute the local solar date and daily sums;
     - multiply by `inputs["n20_ratio"][admin1_id][str(month)]` (fallback `inputs["n20_ratio_default"]`). JSON keys
       are strings, so months are "1"…"12".

     It returns:
     ```
     {generated_at, method_version, data_through, status, notes, areas: {key: {days: [{date, value}],
      season: {season_year, to_date_total, percentile_at_cutoff, typical_to_date_total}}}}
     ```
   - **`season`** adds the snapshot's in-progress season total to the new days, then compares with
     `inputs["areas"][key]["past_cum"]`: the past seasons' cumulative totals at each day offset.
   - **`status` checks:**
     - `failed` if the fetch raised;
     - `stale` if `data_through < today - 3 days`;
     - `suspect` if any day exceeds 5 × `inputs["areas"][key]["max_daily"]`;
     - else `ok`.
   - **CLI:** `python -m ws3_anomaly.ingest.live --inputs ws5_frontend/public/demo/live_inputs.json --out ws5_frontend/public/live/live.json`.
     It reads `FIRMS_MAP_KEY` from the environment, never prints it, and exits 0 even on `failed`, writing the
     status so the site can say so.
   - **Tests** (`test_live.py`), with no network: recorded small CSV fixtures in the test, plus a fake fetch. Cover:
     - local-date mapping across midnight UTC;
     - the ratio is applied;
     - the 3-day overlap de-duplicates;
     - hotspot cells are dropped;
     - stale, failed and suspect statuses;
     - the key never appears in the output JSON.
3. **Inputs export** (`scripts/export_hosted_demo.py`). Also write `ws5_frontend/public/demo/live_inputs.json`:
   - for each demo area: `cell_ids`, `bbox`, `max_daily` (from harmonized daily sums) and `past_cum` (from
     `season_profile`'s `season_years`: for each past complete season of the current window, the cumulative total at
     each day offset 0-120);
   - `n20_ratio`: read `data/interim/sheikh/b1_params.pkl` as `ws1_harmonize/run.py` does. `params["n20"]` maps
     `(admin1_id, month)` tuples to ratios; write it as nested `{admin1_id: {str(month): ratio}}`. Also write
     `n20_ratio_default` = `params["b0_n20"]` and `method_version`.
   - `hotspot_cells`: cells with detections in at least 80% of all weeks in 2018-2025. These are likely industrial;
     list them in the PR.

   Size budget: 300 KB.
4. **Workflow** (`.github/workflows/pages.yml`), still **off**:
   - Add `actions/setup-python@v5` (3.11), install `pandas` and `requests` with pinned versions from
     `requirements.lock.txt`, and add a step running the CLI from step 2 with `env: FIRMS_MAP_KEY: ${{ secrets.FIRMS_MAP_KEY }}`.
   - Guard the step with `if: ${{ vars.LIVE_FEED == 'on' }}`, so it does nothing until T19.
   - Add the schedule trigger **commented out**: `# schedule: - cron: "41 1 * * *"` (07:41 Dhaka).
5. **UI.** New `src/live.ts`:
   - `loadLive()` fetches `live/live.json` and returns `null` on a 404 or bad JSON.
   - `liveFor(key, live)` returns the area entry only when `status` is `ok`, or `stale` (shown with a warning).
   - StatusCard and SeasonCard show `t("live.through", { date })`: "Data through {{date}} (near real time, NOAA-20
     scaled to the Suomi NPP standard)". When stale, add an amber note `t("live.stale")`.
   - Tests in `live.test.ts` for both helpers.
6. **`docs/HOSTING.md`.** Add a "Nightly live feed" section: what it fetches, where the key lives, how to switch it
   on (T19) and off (repository variable `LIVE_FEED`), and how to rotate the key.
7. Run the checks, mark the card done, `split`, push and open the PR.

## Acceptance
- [ ] The redaction tests prove that the key can't reach logs, gap lists or output.
- [ ] All live tests pass with no network.
- [ ] The Pages workflow still builds and deploys exactly as before while `LIVE_FEED` is unset.

## Stop and ask if
- Any test needs real network access.
- `live_inputs.json` would exceed 300 KB.
