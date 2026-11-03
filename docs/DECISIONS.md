# Decisions (these close gaps in the plan; where they conflict with older notes, they win)

> Several decisions rest on unverified facts (FIRMS access, land cover, driver data, hosting). Check them in docs/H0_VERIFICATION.md and record changes here.

1. Final value rule: value_count is observed SNPP VIIRS where it exists (2012 onward), else the model value; source says which; modeled_count is kept wherever MODIS inputs exist. The history has a seam at 2012 and the app shows it.
2. Seam check: anomaly baselines are also computed on 2012 onward alone; flags that appear only with the full series are marked depends_on_modeled_history.
3. One interval_table schema, two versions: v0 by Sheikh at H14 (region x month ratio quantiles), v1 by Samin at H30 (land cover x season, magnitude bins). Cell-level lo/hi are indicative only and never summed.
4. common/ is owned by Samin: series, climatology, intervals (H10); splits, metrics (H12). Nobody re-implements them.
5. predictions_oof.parquet (Sheikh, H24): columns as in contracts/parquet_schemas.json; Samin calibrates only on split == calib.
6. Validation is reported in pieces: each producer writes its own file in data/processed/validation/; Sattyam's /meta/validation merges them.
7. Ingestion: FIRMS archive download first, area API in small parallel day windows as fallback; confirm limits and SNPP near-real-time at H0 (fallback NOAA-20 for the current season).
8. Land cover: a ready-made 0.05 degree product with class percentages (for example MODIS MCD12C1; verify at H0). If it takes over 90 minutes, ship without cropland_frac and tag agricultural-likely by region and season.
9. Drivers: NASA POWER and CHIRPS at 0.5 degree tiles; no request-queue sources.
10. Hosting: static front-end host plus one container-capable API host; parquet baked into the image; static JSON fallback on the front-end host; decide at H3, hello-world at H4.
11. Large files in a shared drive mirror of data/; git holds code, contracts and small JSON; one line per hand-off in data/MANIFEST.md.
12. Sheikh commits the skeleton openapi.yaml at H1; Sattyam completes it and writes fixtures by H3.
13. Keys in .env (own FIRMS key each); pinned Python 3.11 and Node LTS; AI assistance noted in each NOTES.md in case disclosure is required.
14. The official challenge asks for when AND where, and for use in early warning. So: add /aoi/cells (the where map layer) and a current-status card (outlook.current_status: latest complete week against same-week normal, with the data-through date). Both are core and never cut; forecast-based alerts and the forecast outlook remain cuttable.
15. Scope: the pipeline is global-capable; the demo loads South Asia only (Bangladesh and Punjab-Haryana-Delhi first). The app and pitch say so plainly.
16. Critical periods carry agri_share (fraction of detections in cropland) next to agri_tag, so wildfires and agricultural burns can be told apart.
