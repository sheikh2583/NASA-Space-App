# Prompt pack: Sattyam (Team Member 2), data platform and API
Folders: ws2_platform/ and contracts/

## P2.1 OpenAPI and fixtures (H0-3)  HANDOFF
Inputs: contracts/openapi.yaml skeleton (Sheikh, H1); docs/AI_PREAMBLE.md.
Prompt: "Complete contracts/openapi.yaml: full request and response schemas for /aoi/summary, /aoi/cells, /aoi/critical-periods, /aoi/drivers, /aoi/outlook, /aoi/compare, /meta/validation and /export. Every response has schema_version, units, day_convention and per-point source. Then write realistic fixture JSON in contracts/fixtures/ for a Bangladesh AOI and a Punjab AOI (weekly series for 2000-2025 with a visible seam at 2012, a few flagged weeks, intervals, one critical period with agri_tag, one drivers response with caveats, one outlook with status no_demonstrated_skill and a current_status, and one /aoi/cells response)."
Output: openapi.yaml, fixtures. HANDOFF: to Shammo, Samiul.
Test: openapi validates; every fixture validates against its schema.

## P2.2 Mock server (H2-3)
Prompt: "Write ws2_platform/api/mock_server.py (FastAPI, CORS enabled) serving every endpoint from contracts/fixtures/. Include a contract test that calls each endpoint and validates the response against contracts/openapi.yaml."
Output: mock server + contract test. HANDOFF: URL to Shammo, Samiul.
Test: contract test passes; Shammo's app loads data from it.

## P2.3 Hosting hello-world (H3-4)
Prompt: "Recommend one static front-end host and one free container-capable API host, then give the exact steps and files (Dockerfile, start command, health endpoint) to deploy the mock server and a static page, with a note on cold starts and how the static JSON fallback covers them."
Output: both hosts live with hello-world.
Test: hosted mock URL returns a fixture; static page loads.

## P2.4 Gridding and cells (H4-8)  HANDOFF
Inputs: detections.parquet (Monazir: slice H4, full H6).
Prompt: "Write grid.py: from detections.parquet compute cell_id = floor((lat+90)/0.1)*3600 + floor((lon+180)/0.1) and aggregate to the sparse grid_daily.parquet (n_det, n_hiconf = detections with VIIRS confidence 90 (high) or MODIS confidence >= 80, frp_sum, frp_max, n_day, n_night, mean_scan) per contracts/parquet_schemas.json. Write cells.py: cells.parquet with cell centres, admin1 from geoBoundaries ADM1, and land cover from a ready-made 0.05 degree product with class percentages (for example MODIS MCD12C1; unverified, see H0-03). If land cover takes more than 90 minutes, leave cropland_frac null and note it."
Output: grid_daily.parquet, cells.parquet. HANDOFF: to Sheikh, Samin, Monazir, Samiul.
Test: sum of n_det equals detection rows; admin1_id filled; schema validates.

## P2.5 AOI query layer (H8-12)
Inputs: common/series.py and intervals.py (Samin, H10).
Prompt: "Write ws2_platform/api/query.py: given a GeoJSON polygon or bbox, find cells whose centres fall inside (shapely STRtree), then use DuckDB over the Parquet files and common.series.weekly_series to return the series. Cap AOI size (return 422 with a clear message). Empty AOI returns an empty series and a note."
Output: query.py + tests.
Test: a known AOI returns the same totals as a direct pandas sum.

## P2.6 /aoi/summary live (H12-16)  HANDOFF
Inputs: harmonized.parquet v0 and interval_table v0 (Sheikh, H14); anomaly.score_series stub (Monazir, H8).
Prompt: "Write the FastAPI service from contracts/openapi.yaml. /aoi/summary uses query.py, builds lo/hi with common.intervals.apply_interval from interval_table.json, attaches source flags and drift flags, and calls anomaly.score_series (fall back to the fixture if the module is missing). Add response caching. Deploy to the API host."
Output: live /aoi/summary. HANDOFF: URL to Shammo, Samiul.
Test: contract test passes against the live URL; typical AOI under about 1.5 seconds.

## P2.7 Static fallback (H14-16)
Prompt: "Write static_export.py: precompute /aoi/summary-shaped JSON for every admin1 region in the demo regions and for 0.5 degree tiles, write them to a folder deployable on the static host, and give Shammo the URL pattern."
Output: static JSON folder deployed.
Test: the front-end can read a region file with the API switched off.

## P2.8 Remaining endpoints (H16-30)
Inputs: anomalies and critical periods (Monazir, H18); harmonized v1 and interval_table v1 (H30); drivers (H36); outlook (Samin, H34).
Prompt: "Implement /aoi/cells (per-cell totals for a period: cell_id, lat_c, lon_c, value, modeled_share; read from harmonized and cells), /aoi/critical-periods, /aoi/drivers, /aoi/outlook, /aoi/compare and /export by importing anomaly.find_periods, drivers.driver_associations and outlook.outlook (fixtures when the modules are absent). Switch the data source to harmonized v1 when it lands. Keep every response inside the contract."
Output: all endpoints live.
Test: contract tests pass for every endpoint on the live API.

## P2.9 Validation merge and performance (H30-36)
Prompt: "Implement /meta/validation merging every JSON in data/processed/validation/ keyed by producer, tolerating missing pieces. Profile the slowest AOI queries, add DuckDB indexes or precomputed weekly aggregates, and report timings before and after."
Output: /meta/validation; timing table.
Test: typical AOI under about 1.5 seconds; missing piece does not break the endpoint.

## P2.10 Final deploy (H42-44)
Prompt: "Give me a final deploy checklist: environment variables, health check, cold-start behaviour, fallback switch, rollback step, and a smoke test script that hits every endpoint."
Output: final deploy; smoke test passes.
Test: Samiul's end-to-end run passes on the hosted app.
