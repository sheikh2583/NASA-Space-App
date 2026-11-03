# contracts/ (openapi.yaml and fixtures/: Sattyam; parquet_schemas.json and json_schemas/: Sheikh; see docs/FILE_OWNERSHIP.md)
The agreements between workstreams.

- openapi.yaml            API contract: request and response schemas for every endpoint (draft 0.2.0); Sattyam finalizes at H3
- parquet_schemas.json    column names and types of every Parquet file (data/processed/), plus _enums (allowed string values) and _keys (unique keys)
- json_schemas/           JSON Schemas for interval_table, drivers_region, outlook_region, validation pieces
- fixtures/               realistic example responses (Bangladesh AOI, Punjab AOI) used by the mock server and tests

Rules
1. After G0 (H3) never rename or remove a field. Adding a field is fine.
2. Every change: log it in docs/CONTRACT_CHANGES.md (old shape, new shape, who is affected), post in the channel, wait for GOT IT from each consumer.
3. Samiul's contract tests read these files; keep them valid.
