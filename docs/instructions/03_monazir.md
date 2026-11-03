# Monazir (Team Member 3): your instructions
Your job: get raw data flowing, then find unusual periods and report associated drivers.
Folder: ws3_anomaly/. Prompt pack: prompts/ws3_monazir.md. Paste docs/AI_PREAMBLE.md first.

## Before the event
1. Register your own FIRMS key and put it in .env.

## H0 to H6: ingestion
2. Do P3.1: find out the archive route, the area API's limits and whether NOAA-20 near-real-time works (SNPP ended 2 Nov 2026). Talk to Sheikh: tell him what you found.
3. Do P3.2: normalize the Bangladesh slice. At H4 post a HANDOFF to Sattyam and Samiul. Talk to Sattyam: confirm he can read the columns.
4. Do P3.3: full demo regions by H6, then wider South Asia if time allows. Post a HANDOFF. Talk to Samiul: ask for the data QA report by H10.

## H6 to H18: first anomalies
5. Do P3.4: the score_series stub by H8. Talk to Sattyam: confirm the function signature.
6. Talk to Samin: ask for common/series.py and climatology.py at H10. Talk to Sattyam: confirm cells.parquet has admin1 ids (H8). Talk to Sheikh: ask for harmonized v0 at H14.
7. Do P3.5. At H18 post a HANDOFF of anomalies_region_week.parquet and critical_periods.parquet to Sattyam.

## H18 to H36: robust anomalies and drivers
8. Do P3.6 by H26. Talk to Sheikh: agree how the 2012 seam is shown in flags.
9. Do P3.7. At H26 post a HANDOFF of the weather loaders to Samin (he needs them for the outlook).
10. Do P3.8 by H36. Talk to Shammo: show him the driver wording and the evidence labels. Talk to Samiul: ask him to read the strings.

## H44
11. Review every driver string in the app. Talk to Shammo: fix any causal wording.

## Rules and fallbacks
- Never claim causes. Never skip the seam check. Never change a contract field without Sheikh.
- If you fall behind, keep the percentile method and ship drivers as a short list of descriptive correlations.

## Manual tasks
Things an AI agent cannot do for you are listed under your name in docs/MANUAL_TASKS.md, and repeated inside each of your phase prompts (prompts/phases/).

## Your workspace, what you may write, how to verify
- Work in: your laptop. Put big raw files straight into data/raw/ on the shared drive. Branch prefix: ws3/.
- You may write: ws3_anomaly/; data/processed/detections.parquet, anomalies_region_week.parquet, critical_periods.parquet, drivers_region.json.
- You must not write: ws2_platform/ (ingestion code lives in ws3_anomaly/ingest/), common/, or other people's data files.
- Verify before each HANDOFF: DuckDB counts by sensor and date; compare one day with the FIRMS web map; pytest ws3_anomaly/tests (including the causal-word lint); tools/verify_files.py on every file you hand over.
