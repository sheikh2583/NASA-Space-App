# File ownership: one writer per path

Everyone else reads. If you need a change, ask the owner (docs/WORKING_TOGETHER.md, section 7).

| Path | Only writer | Readers |
|---|---|---|
| ws1_harmonize/ | Sheikh | everyone |
| ws2_platform/ | Sattyam | everyone |
| ws3_anomaly/ | Monazir | everyone |
| ws4_outlook/ | Samin | everyone |
| ws5_frontend/ | Shammo | everyone |
| ws6_validation/ | Samiul | everyone |
| common/ | Samin (Sheikh reviews) | everyone imports, nobody edits |
| contracts/openapi.yaml, fixtures/ | Sattyam (Sheikh approves) | everyone |
| contracts/parquet_schemas.json, json_schemas/ | Sheikh | everyone |
| docs/ (instructions, checklists, TIMELINE, DECISIONS, LEAD_GUIDE) | Sheikh | everyone |
| docs/method_en.md, method_bn.md, slides, demo script, QA and submission checklists | Samiul | everyone |
| data/MANIFEST.md, docs/CONTRACT_CHANGES.md | append-only: each person adds their own line at the bottom | everyone |
| data/processed/detections.parquet | Monazir | Sattyam, Samiul, Sheikh |
| data/processed/grid_daily.parquet, cells.parquet | Sattyam | everyone |
| data/processed/harmonized.parquet, predictions_oof.parquet | Sheikh | Sattyam, Monazir, Samin |
| data/processed/interval_table.json | Sheikh writes v0 (H14); Samin writes v1 (H30) | Sattyam |
| data/processed/drift_flags.parquet | Samin | Sheikh, Sattyam |
| data/processed/anomalies_region_week.parquet, critical_periods.parquet | Monazir | Sattyam |
| data/processed/drivers_region.json | Monazir | Sattyam, Shammo |
| data/processed/outlook_region.json | Samin | Sattyam, Shammo |
| data/processed/validation/harmonization.json | Sheikh | Sattyam |
| data/processed/validation/intervals.json, drift.json, outlook_skill.json, mcd64a1.json | Samin | Sattyam |
| data/processed/validation/qa.json, pm25.json | Samiul | Sattyam |
