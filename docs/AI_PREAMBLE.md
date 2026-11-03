# Shared context: paste this into your AI tool first

```
PROJECT
Official challenge: build a web app that harmonizes MODIS and VIIRS active-fire records into a burning-activity
calendar so early-warning staff, emergency responders, scientists and land managers can examine WHEN and WHERE
burning occurred, unusual conditions and critical periods (wildfires and agricultural burns) in a selected area.
Team of six at NASA Space Apps 2026 (Bangladesh, 14-15 Nov). 48-hour build, free tools only.
We build a web app that merges MODIS and VIIRS fire hot-spot records into ONE burning-activity
calendar for a user-drawn area: harmonized series with uncertainty, flagged unusual periods
(including agricultural burns), driver associations (never causes) and a current-season outlook.
Demo regions: Bangladesh (lon 88.0-92.7, lat 20.5-26.7) and Punjab-Haryana-Delhi
(lon 73.5-78.0, lat 28.0-32.5).

HOW YOU MUST WORK
- Do what your prompt lists. Do not add files, columns, endpoints or units that are not listed.
- Write small, tested functions. Run on a small slice (one region, one year) before full data.
- No secrets in code; keys come from environment variables.
- If something is unclear, use the stated default, write the assumption in NOTES.md, move on.
- Never claim causes. Never hide that a value is modeled.
- Tiers: FLOOR works end to end by H24; CORE by H30; SCALE-UP by H36.
  Cut order if late: Bangla polish, forecast alerts, PM2.5, comparison, forecast outlook (the current-status card and the where-map are never cut).
- Gates: G0 H3 contracts frozen; G1 H8 gridded data; G2 H24 floor works; G3 H30 core integrated;
  H36 feature freeze; H42 code freeze; H46 submit.

CONVENTIONS
- Grid 0.1 degree: i=min(floor(round((lat+90)*10, 6)), 1799), j=min(floor(round((lon+180)*10, 6)), 3599),
  cell_id=i*3600+j (int32). Use exactly this expression everywhere (Python, DuckDB, front end).
- Day: detections keep UTC acq_date/acq_time; grid_daily.date is the LOCAL SOLAR date (UTC + lon/15 hours).
  Week starts Monday. ISO week 53 folds into week 52 for climatology. Season = Oct 1 to Sep 30.
- grid_daily is sparse and keyed by (cell_id, date, sat): a missing row means zero detections ONLY on days
  sensor_days.parquet says that satellite was operating; otherwise the value is missing, never zero.
- Satellites: Terra (Nov 2000 on), Aqua (Jul 2002 on), SNPP (20 Jan 2012 to 2 Nov 2026: FIRMS stopped new SNPP
  data at 13:00 UTC on 2 Nov 2026), NOAA20, NOAA21. MODIS (Terra, Aqua) shuts down late 2026 / early 2027.
- Reference sensor: VIIRS SNPP 375 m. After the SNPP cutoff, observed values come from NOAA-20 adjusted to
  SNPP terms (region x month ratio from the overlap years). Model inputs: MODIS, fitted per satellite
  combination (terra_only before Jul 2002, terra_aqua after). Near-real-time source: VIIRS_NOAA20_NRT.
- Only vegetation fires count (source_type 0, or persistent-hotspot mask).
- VIIRS confidence classes map to numbers: low=20, nominal=60, high=90.
- Repo: contracts/ (openapi.yaml, parquet_schemas.json, json_schemas/, fixtures/), common/ (shared
  Python), data/ (not in git; shared drive mirror; data/MANIFEST.md is in git), docs/, ws1_harmonize/,
  ws2_platform/, ws3_anomaly/, ws4_outlook/, ws5_frontend/, ws6_validation/. Edit only your own
  folder. Changes to contracts/ and common/ need Sheikh's OK.

FILE CONTRACTS: see contracts/parquet_schemas.json and contracts/json_schemas/ (paste the one you
need into the chat). Key rules:
- harmonized value_count = observed SNPP VIIRS on SNPP operating days (2012 to 2 Nov 2026), NOAA-20
  adjusted to SNPP after that, else the model value;
  source = observed_viirs | adjusted_from_noaa20 | modeled_from_modis | mixed; modeled_count = model
  prediction wherever MODIS inputs exist. Observed rows have lo = hi = value. Cell-level lo/hi are
  indicative and are never summed.
- Drawn AOIs: series, anomalies, critical periods and current status are computed live for the AOI;
  drivers, drift and the forecast outlook come from the admin1 region holding most of the AOI's cells,
  and the response names that region.
- interval_table.json: version, level, entries[{res, stratum, max_value, lo_mult, hi_mult, hi_add}];
  lookup = most specific stratum first, then magnitude bin; used to build AOI-level intervals.
- predictions_oof.parquet split = train | calib | test (from common/splits).
- validation/*.json: one file per producer: schema_version, generated_at, producer, metrics, limitations[].

API (owner Sattyam): /aoi/summary, /aoi/cells (where map layer: cell_id, lat_c, lon_c, value, modeled_share), /aoi/critical-periods, /aoi/drivers, /aoi/outlook, /aoi/compare,
/meta/validation, /export. Every JSON response has schema_version, units and day_convention (the Envelope
schema in openapi.yaml). /aoi/summary points: t, value, lo, hi, source, modeled_share, drift_flag,
anomaly{flag, score, depends_on_modeled_history}. contracts/openapi.yaml has the full response schemas.

SHARED PYTHON (owner Samin, folder common/)
  series.weekly_series(harmonized, cells, region_ids|bbox, res) -> week_start, value, lo, hi, modeled_share
  climatology: same-week quantiles, season helpers
  intervals.apply_interval(value, res, stratum, table) -> lo, hi
  splits: 2x2 degree spatial blocks, yearly folds, backward holdout, calibration blocks
  metrics: relative bias, RMSE on log1p, Spearman, Lin's CCC, coverage, interval score
FUNCTIONS THE API IMPORTS
  anomaly.score_series(df[week_start, value, lo, hi]) -> + baseline, score, flag, exceeds_lower_bound
  anomaly.find_periods(scored_df) -> list of periods
  drivers.driver_associations(weekly_df, bbox, start, end) -> dict
  outlook.outlook(weekly_df, bbox, as_of) -> dict (includes current_status: week_percentile, level none/watch/high, data_through, message)

HANDOFF MESSAGE (post when a deliverable passes its tests)
HANDOFF | from | to | file path | version | rows or size | 20-row sample | check command | known limits
The receiver replies within 15 minutes: GOT IT, or what is missing.
```
