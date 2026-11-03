# How to verify each deliverable

> Disclaimer: the queries below were run only on tiny synthetic tables, not on real data. The DuckDB command line is optional; from Python use: python -c "import duckdb; print(duckdb.sql('select 1').fetchall())" with your query in place of select 1.

Rule: the producer verifies before the HANDOFF; the receiver verifies again before saying GOT IT; Samiul's end-to-end run verifies the whole.
Commands assume you run them from the repo root. DuckDB can be used from the command line (`duckdb -c "..."`) or from Python.

| Stage | Deliverable | How to verify | Pass |
|---|---|---|---|
| H3 | openapi.yaml, fixtures, mock | open the mock URL in a browser; run the contract test against it (`API_BASE_URL=<mock> pytest ws6_validation/tests/test_contract.py`) | all endpoints return valid shapes |
| H4/H6 | detections.parquet | `duckdb -c "select sensor, count(*), min(acq_date), max(acq_date) from 'data/processed/detections.parquet' group by 1"`; open the FIRMS web map for one day and small area and compare | rows exist for both sensors; dates in range; counts match the viewer |
| H8 | grid_daily.parquet | `duckdb -c "select sum(n_det) from 'data/processed/grid_daily.parquet'"` equals `select count(*) from detections`; `select count(*) from (select cell_id, sensor, date from grid_daily group by 1,2,3 having count(*) > 1)` returns 0 | sums equal; no duplicate keys |
| H8 | cells.parquet | `select count(*) from cells where admin1_id is null` | 0 (or documented) |
| H10 | common/ functions | `pytest common/` | all pass |
| H14 | harmonized.parquet v0 | `select count(*) from 'data/processed/harmonized.parquet' where lo_count > value_count or value_count > hi_count or value_count < 0 or source is null` | 0 |
| H14 | interval_table.json | validate against contracts/json_schemas/interval_table.schema.json (tools/verify_files.py) | valid |
| H16 | live /aoi/summary | `curl -s -w ' %{time_total}s' -X POST <API>/aoi/summary -H 'Content-Type: application/json' -d @contracts/fixtures/<aoi request>.json`; open the app on a phone | valid response; under about 1.5 seconds; app shows data |
| H16 | static fallback | switch the API off (or point the app at a wrong URL) and reload the app | app still shows a region from the fallback |
| H24 | predictions_oof.parquet | `select split, count(*) from 'data/processed/predictions_oof.parquet' group by 1`; check no calib or test row was used for training (the test in ws1_harmonize/tests) | three splits present; leakage test passes |
| H26 | robust anomalies | `pytest ws3_anomaly/tests` (injected spike flagged; seasonal noise gives few flags) | pass |
| H30 | interval_table v1, drift_flags | verify schema; read the coverage table: empirical coverage near 90 percent, or the gap is written in limitations | valid; gap reported |
| H30 | harmonized v1 | same query as H14, plus the 2012 seam: `select year(date), avg(case when source = 'modeled_from_modis' then 1 else 0 end) from harmonized group by 1 order by 1` | modeled share drops to 0 at 2012 |
| H30 | /aoi/cells and current status | `curl` the live /aoi/cells for a demo AOI and a flagged week; open the app and select that week; check the status card shows the data-through date | cells returned; map recolours; date shown |
| H34 | validation pieces | verify each against validation_piece.schema.json; open /meta/validation | all present pieces valid |
| H36 | drivers | `pytest ws3_anomaly/tests` includes the lint for cause, because, due to, leads to, drives | no causal words |
| H36 | web app | `npm run build` succeeds; `grep` finds no hard-coded UI strings; open on phone and laptop in English and Bangla | build passes; no stray strings; Bangla renders |
| Each gate | whole system | Samiul's end-to-end run on the live API and on the fallback | no severity-1 bugs |
| H46 | submission | open every link in a private browser window | all work for outsiders |

## Verification helper
Sheikh's prompt P1.10 creates tools/verify_files.py: it checks any Parquet or JSON file in data/processed/ against contracts/parquet_schemas.json and contracts/json_schemas/ and prints PASS or the failing rows. Everyone runs it before a HANDOFF.
