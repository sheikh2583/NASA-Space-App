# NOTES (ws3_anomaly)

## Decisions and assumptions
- Baseline = same-week climatology (week-of-year median, +/-2 weeks). Robust STL is available (method="stl") but not
  the default: its trend absorbs a whole unusual season, which is what we want to flag.
- Severity = excess over baseline / the series' mean weekly value ("typical weeks above normal"); dividing by the period's own
  baseline let off-season spikes outrank in-season peaks.
- Flag rule (decision 21 outcome): with the lower-bound rule no week before 2012 was flagged (0.000 vs 0.018 after),
  so flags use the value; exceeds_lower_bound is kept and shown. Switch back with anomaly.FLAG_RULE = "lower_bound".
- A season-long anomaly of about 2x is flagged only at its edges (per-week noise is larger); the outlook's season-to-date
  percentile is the tool for whole seasons.
- drivers: Spearman + 8-week block permutation and bootstrap; learned-model permutation importance from P3.8 is not implemented.
  Run in batch per region only. Caveat strings are English; the app shows them untranslated for now.
- ingest/firms.py refuses VIIRS_SNPP_NRT (ended 2 Nov 2026).

## Known issues
- FIRMS key, archive requests and real downloads are manual (docs/plan/README.md). Weather loaders for NASA POWER and
  CHIRPS are written but untested against the real services (H0-05).

## AI assistance log (where AI tools helped)
- 2026-11-03: everything in this folder was written with Claude (AI assistant) at Sheikh's direction before the event, on synthetic data, and assigned to this workstream's owner. Review it before relying on it; rerun on real data.
