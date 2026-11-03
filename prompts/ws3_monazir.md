# Prompt pack: Monazir (Team Member 3), ingestion, anomalies and drivers
Folder: ws3_anomaly/ (ingestion code in ws3_anomaly/ingest/ for the first eight hours)

## P3.1 FIRMS access probe (H0-2)
Inputs: your own FIRMS MAP_KEY in .env.
Prompt: "Help me probe NASA FIRMS access: (1) what the archive download route offers for country-level standard-product files for MODIS and VIIRS SNPP 375 m, (2) the area API's per-request day limit and rate limit for my key, (3) whether SNPP near-real-time data is still available. Write a tiny script that pulls one day for a small bbox from each source and prints the columns. Note the answers in NOTES.md."
Output: written answers in NOTES.md; a one-day pull for MODIS and VIIRS.
Test: both pulls return rows with the expected columns; limits recorded.

## P3.2 First slice (H2-4)  HANDOFF
Prompt: "Write ingest/normalize.py that converts raw FIRMS files to the detections.parquet schema in contracts/parquet_schemas.json: map VIIRS confidence classes low/nominal/high to 20/60/90, keep MODIS confidence 0-100, keep source_type and drop non-vegetation detections, label sensor MODIS (Terra and Aqua together) or VIIRS (SNPP), UTC date and HHMM time, cache raw files. Run it for Bangladesh, all available years."
Output: detections.parquet first slice. HANDOFF: to Sattyam, Samiul.
Test: schema validates; rows after filtering equal raw rows minus dropped sources.

## P3.3 Full ingestion (H4-6)  HANDOFF
Prompt: "Extend ingest to the full demo regions (Bangladesh and Punjab-Haryana-Delhi), using the archive route first and the area API in small day windows run in parallel as a fallback; retry on failure, resume after interruption, log gaps. Add the current season from near-real-time data (NOAA-20 if SNPP near-real-time is unavailable, noting the switch). Then widen to the rest of South Asia as time allows."
Output: detections.parquet for demo regions (wider South Asia later). HANDOFF: to Sattyam, Samiul.
Test: no date gaps longer than the satellites' known outages; row counts per year look sane.

## P3.4 score_series stub (H6-8)  HANDOFF
Inputs: common/climatology.py (Samin, H10; use a local stand-in until then).
Prompt: "Write ws3_anomaly/anomaly.py with score_series(df[week_start, value, lo, hi]) returning the frame plus baseline, score, flag and exceeds_lower_bound using the percentile method: baseline = median of same-week values across years, flag = value above the 90th percentile of same-week climatology, exceeds_lower_bound = lo above that percentile. Include tests with an injected spike."
Output: stub score_series. HANDOFF: to Sattyam.
Test: spike flagged; returns the agreed columns on a fixture.

## P3.5 Anomalies and periods v0 (H8-18)  HANDOFF
Inputs: cells.parquet (H8); common/series.py (H10); harmonized v0 (H14).
Prompt: "Write periods.py: find_periods(scored_df) merges consecutive flagged weeks into periods with start, end, severity (sum of excess over baseline / mean baseline), rank, peak_value, n_weeks agri_share (fraction of detections in cropland) and agri_tag (most detections in cropland, or the region-season rule if cropland_frac is missing). Write a batch script that precomputes anomalies_region_week.parquet and critical_periods.parquet for every admin1 region."
Output: anomalies_region_week.parquet, critical_periods.parquet v0. HANDOFF: to Sattyam.
Test: contracts schemas validate; a spike-injected series yields one ranked period.

## P3.6 Robust anomalies and seam check (H18-26)
Inputs: harmonized v0.
Prompt: "Upgrade score_series: log1p transform; robust STL (period 52) when at least 8 years exist, else the week-of-year median with a +/-2 week window; score = residual / (1.4826 x MAD) within the same season; flag when score > 2 AND lo exceeds the baseline's 90th percentile (exceeds_lower_bound). Add the seam check: also compute baselines on 2012 onward only, and mark flags that appear only with the full series as depends_on_modeled_history. Keep the function signature unchanged."
Output: robust v1 of score_series.
Test: spike flagged; pure seasonal noise gives few flags; seam-dependent flags are marked.

## P3.7 Driver loaders (H26-30)
Note: access to CHIRPS and NASA POWER, their resolution and the soil-wetness field are unverified (H0-05).
Prompt: "Write ws3_anomaly/loaders/: weekly CHIRPS rainfall and NASA POWER temperature, precipitation and soil wetness for a bbox and year range, aggregated to 0.5 degree tiles and to admin1 regions, cached to Parquet, returning anomalies relative to same-week climatology. Small requests, retry on failure, no credentials in code."
Output: loaders + cached anomaly tables. HANDOFF: to Samin (weather anomalies for the outlook).
Test: a known week returns plausible values; reruns use the cache.

## P3.8 Driver associations and wording review (H30-36, review H44)  HANDOFF
Prompt: "Write drivers.py: driver_associations(weekly_df, bbox, start, end). For each driver and lag 0 to 8 weeks, Spearman correlation between deseasonalized burning and driver anomalies, with block-permutation p-values (8-week blocks) and block-bootstrap CI; add LightGBM permutation importance with season-block CV. Return the top 3 items {driver, lag_weeks, direction, strength, ci, evidence weak/moderate/strong} and caveats (associations only; burning follows farming calendars; spatially aggregated). Output strings must never use cause, because, due to, leads to or drives. Add a lint test for that."
Output: drivers.py, drivers_region.json. HANDOFF: to Sattyam, Shammo.
Test: schema validates; lint test passes; sparse AOI returns an insufficient-data result.
