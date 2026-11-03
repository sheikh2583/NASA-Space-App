# NOTES (ws2_platform)

## Decisions and assumptions
- grid_daily keyed by (cell_id, date, sat); date = local solar date (decisions 19, 23). grid keeps every detection
  (sum n_det = detections); rows on non-operating days are skipped by consumers (sensors.drop_non_operating).
- cells: admin1 matched with `intersects` so border cells get a region. Land cover: MCD12C1 via pyhdf, else synthetic.
- API implements openapi 0.2.0. AOI size limit is by drawn area (area in square degrees x 100 = grid cells, limit 6000).
  The 26-year weekly history per AOI is cached and shared by summary, critical periods and outlook (first call ~0.8 s).
- Static fallback: `python -m ws2_platform.api.static_export`; URL pattern documented in that file.
- Fixtures: `python -m ws2_platform.api.make_fixtures` (shapes are fixed; numbers are synthetic).

## Known issues
- Hosting not done (needs accounts): Dockerfile is ready for Hugging Face Spaces or Render; bake data/processed in.

## AI assistance log (where AI tools helped)
- 2026-11-03: everything in this folder was written with Claude (AI assistant) at Sheikh's direction before the event, on synthetic data, and assigned to this workstream's owner. Review it before relying on it; rerun on real data.
