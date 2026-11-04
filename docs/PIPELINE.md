# The project in plain words

Satellites detect fires, but two families see them differently. MODIS (since 2000) and VIIRS (since 2012)
have different pixel sizes and overpass times, so their records cannot simply be stacked. We build one
consistent history, in SNPP VIIRS terms, for any area a user draws. Where SNPP VIIRS exists (2012 to
2 Nov 2026) it is shown as observed; since FIRMS stopped SNPP on 2 Nov 2026 we show NOAA-20 VIIRS adjusted
to SNPP terms; before 2012 we show an estimate made from MODIS. Adjusted and modeled values are labeled
and shown with an uncertainty band. On top we flag unusual weeks and rank critical periods (including agricultural burns),
show associated weather and land-cover factors (never causes), and compare the current season with normal.

Limits we state in the app: pre-2012 values are modeled; values after 2 Nov 2026 are adjusted from NOAA-20; drivers are associations; the outlook may show no skill.

## The chain
1. Ingest (Monazir): FIRMS downloads (MODIS, SNPP, NOAA-20) -> detections.parquet
2. Grid and cells (Sattyam): -> grid_daily.parquet (per satellite), sensor_days.parquet, cells.parquet
3. Harmonize (Sheikh): -> harmonized.parquet, predictions_oof.parquet, interval_table v0
4. Intervals and drift (Samin): -> interval_table v1, drift_flags.parquet
5. Anomalies and drivers (Monazir): -> anomalies, critical periods, drivers
6. Outlook (Samin): -> outlook_region.json
7. API (Sattyam): serves everything, plus a static fallback
8. Web app (Shammo): the product users see
Across all (Samiul): QA, validation content, method text, slides, video

## Run the workflows

`scripts/workflow.py` is the operating-system-neutral entry point after setup:

```bash
python scripts/workflow.py train --quick
python scripts/workflow.py validate
python scripts/workflow.py results
python scripts/workflow.py test
python scripts/workflow.py build
python scripts/workflow.py dev
```

Windows can bootstrap and dispatch any workflow with `scripts\init.ps1`; Linux and macOS use
`scripts/init.sh`. A successful pipeline now ends by writing local summaries to
`results/latest.json` and `results/latest.md`.

Pipeline stages are resumable with `python scripts/workflow.py train --quick --from <stage>`.
The ordered stages are: `synth`, `ingest`, `grid`, `sensors`, `cells`, `panel`, `v0`, `model`,
`intervals`, `drift`, `v1`, `anomalies`, `outlook`, `validation`, `fixtures`, `fallback`, `qa`,
and `results`.

## What each person contributes
- Sheikh: science core and glue; builds the harmonized series, sets up the repo, keeps hand-offs and gates on time.
- Sattyam: turns raw detections into a fast service: grid, API for any area, static fallback.
- Monazir: gets raw data flowing, then finds and ranks unusual periods and reports accompanying factors.
- Samin: shared yardstick and trust layer: common functions, calibrated bands, drift checks, outlook.
- Shammo: makes it usable: map, calendar, bands, panels, Bangla/English.
- Samiul: makes it believable: tests every stage, validation content, method text, slides and video.
