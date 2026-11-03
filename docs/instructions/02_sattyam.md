# Sattyam (Team Member 2): your instructions
Your job: grid the data, build the API, keep the demo alive with a static fallback.
Folders: ws2_platform/ and contracts/. Prompt pack: prompts/ws2_sattyam.md. Paste docs/AI_PREAMBLE.md first.

## H0 to H3: contracts and mock
1. Open contracts/openapi.yaml (Sheikh's skeleton). Do P2.1: complete it and write the fixtures.
2. Talk to Shammo: ask which fields his heatmap and chart need, so the fixtures contain them.
3. Do P2.2: the mock server. At H3 post a HANDOFF to Shammo and Samiul with the mock URL and the fixture folder.

## H3 to H8: hosting and gridding
4. Do P2.3. Talk to Sheikh: confirm the hosting choice. Deploy a hello-world on both hosts by H4.
5. Talk to Monazir: ask for the first detections slice at H4 and agree the columns.
6. Do P2.4 on the slice. At H8 post a HANDOFF of grid_daily.parquet and cells.parquet to Sheikh, Samin, Monazir and Samiul.
7. Talk to Samiul: ask him to start the data QA right away.

## H8 to H16: first live API
8. Talk to Samin: ask for common/series.py and intervals.py at H10. Talk to Monazir: ask for the score_series stub (H8). Talk to Sheikh: ask for harmonized v0 and interval_table v0 at H14.
9. Do P2.5, then P2.6. Deploy /aoi/summary by H16. Do P2.7 (static fallback).
10. Talk to Shammo: send the live URL and the fallback URL pattern. Post a HANDOFF to Shammo and Samiul.

## H16 to H36: all endpoints
11. Do P2.8 (including /aoi/cells). Talk to Monazir (anomalies at H18, drivers at H36), Samin (outlook at H34) and Sheikh (harmonized v1 and interval v1 at H30). Switch the data source as each lands.
12. Do P2.9 by H34: /meta/validation merging every file in data/processed/validation/. Measure and fix slow AOI queries.

## H42 to H46
13. Do P2.10: final deploy and smoke test. Tell Shammo and Samiul the final URLs at H44.

## Rules and fallbacks
- Never change a contract field without Sheikh. Never re-implement anything in common/.
- Every response keeps its source flag; never sum cell-level lo/hi.
- If you fall behind, serve the static fallback only. It is enough for the floor.

## Manual tasks
Things an AI agent cannot do for you are listed under your name in docs/MANUAL_TASKS.md, and repeated inside each of your phase prompts (prompts/phases/).

## Your workspace, what you may write, how to verify
- Work in: your laptop (venv; Docker if available) and the hosting dashboards (API host, static fallback site). Branch prefix: ws2/. Run uvicorn on port 8000 only for your own testing; others use the hosted mock or live API.
- You may write: ws2_platform/; contracts/openapi.yaml and fixtures/; data/processed/grid_daily.parquet and cells.parquet; the API deployment; the static fallback site.
- You must not write: ws5_frontend/ (give Shammo the fallback URL pattern instead), common/ (ask Samin), or other people's data files.
- Verify before each HANDOFF: the contract test against your URL (API_BASE_URL=<url> pytest ws6_validation/tests/test_contract.py); the DuckDB row-sum and duplicate-key checks (docs/VERIFY.md); curl timing; open the app on a phone.
