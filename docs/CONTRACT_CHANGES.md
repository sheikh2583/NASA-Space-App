# Contract change log
Adding a field is fine. After G0 (H3) never rename or remove one. Sheikh approves every entry.

| Time | Contract | Old shape | New shape | Affected people | Acknowledged by |
|---|---|---|---|---|---|
| 2026-11-03 (pre-event) | parquet_schemas.json | grid_daily keyed by (cell_id, date, sensor); no sensor_days; source and split types as prose | grid_daily adds sat, key (cell_id, date, sat); new sensor_days; depends_on_modeled_history on anomalies and critical_periods; predictions_oof.sat_combo; _enums and _keys blocks | Sattyam, Sheikh, Monazir, Samin, Samiul | pending Sheikh |
| 2026-11-03 (pre-event) | openapi.yaml 0.1.0 -> 0.2.0 | 1 of 8 endpoints with a response schema; no request body for compare and export | every endpoint has request and response schemas; Envelope; AOIRequest oneOf geometry/bbox, start and end required; SummaryPoint gains modeled_share and adjusted_from_noaa20; Region on drivers and outlook; day_convention local_solar_date | Sattyam, Shammo, Samiul | pending Sheikh |
| 2026-11-03 (pre-event) | drivers_region, outlook_region schemas | one object, no region key; current_status optional | {schema_version, generated_at, regions{admin1_id: entry}}; current_status required; skill.ci exactly 2 numbers | Monazir, Samin, Sattyam, Shammo | pending Sheikh |
