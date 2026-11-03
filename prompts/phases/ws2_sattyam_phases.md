# Phase prompts: Sattyam (Team Member 2). Detailed sub-prompts: prompts/ws2_sattyam.md

## PHASE 1: Kickoff (H0-3)
```
GOAL: Contracts complete, fixtures and mock server ready at H3 so Shammo and Samiul can start.
INPUTS: contracts/openapi.yaml skeleton (Sheikh, H1); docs/AI_PREAMBLE.md.
STEPS:
1. Ask Shammo which fields his heatmap and chart need.
2. Run P2.1: complete openapi.yaml and write fixtures (Bangladesh, Punjab) including the 2012 seam.
3. Run P2.2: the mock server with CORS and a contract test.
4. At H3 print the HANDOFF to Shammo and Samiul with the mock URL.
DELIVER: openapi.yaml, fixtures, mock server.
DONE WHEN: the contract test passes against the mock; fixtures validate.
DO NOT: invent fields beyond the contract.
IF BLOCKED: ask Sheikh to cut the fixtures to one AOI.
MANUAL (you do these yourself; the agent cannot):
- Create accounts on a static host and a container-capable API host (free tiers) and share access with Sheikh
- Read each host's free-tier limits (sleep time, memory, build minutes) and tell Sheikh
```

## PHASE 2: Data (H3-8)
```
GOAL: Hosting hello-world at H4; grid_daily and cells at H8.
INPUTS: detections slice (Monazir, H4; full H6).
STEPS:
1. Run P2.3: deploy hello-world on both hosts; confirm the choice with Sheikh.
2. Ask Monazir for the first slice at H4; check the columns against parquet_schemas.json.
3. Run P2.4 on the slice, then on the full demo regions at H6.
4. At H8 print the HANDOFF to Sheikh, Samin, Monazir, Samiul. Ask Samiul to start the data QA.
DELIVER: grid_daily.parquet, cells.parquet.
DONE WHEN: sum of n_det equals the number of detection rows; admin1 ids filled.
DO NOT: block on land cover; follow decision 8 (90-minute limit).
IF BLOCKED: ask Monazir for a smaller slice and grid that first.
MANUAL (you do these yourself; the agent cannot):
- Download boundary files (geoBoundaries ADM1) and the land-cover product by hand if they need a web form or login; put them in the shared drive
- Connect the repo to the hosting dashboards for the hello-world deploy
```

## PHASE 3: Floor (H8-24)
```
GOAL: Live /aoi/summary and static fallback at H16; support the floor gate at H24.
INPUTS: common/series, intervals (Samin, H10); harmonized v0 and interval_table v0 (Sheikh, H14); score_series stub (Monazir, H8).
STEPS:
1. Run P2.5: the AOI query layer on top of common.series.
2. Run P2.6: /aoi/summary with intervals, source flags and the anomaly stub; deploy.
3. Run P2.7: the static fallback; tell Shammo the URL pattern.
4. Print the HANDOFF to Shammo and Samiul at H16.
5. Fix the items on Samiul's H24 bug list that belong to you.
DELIVER: live /aoi/summary; static fallback.
DONE WHEN: contract test passes on the live URL; typical AOI under about 1.5 seconds.
DO NOT: re-implement anything in common/.
IF BLOCKED: serve the static fallback only.
MANUAL (you do these yourself; the agent cannot):
- Set environment variables in the hosting dashboard and press deploy; open the URL on your phone
```

## PHASE 4: Core (H24-30)
```
GOAL: All endpoints live on v1 data by H30.
INPUTS: anomalies and critical periods (Monazir, H18); harmonized v1 and interval_table v1 (Sheikh and Samin, H30).
STEPS:
1. Run P2.8 for /aoi/cells, /aoi/critical-periods, /aoi/drivers, /aoi/outlook, /aoi/compare, /export (fixtures while modules are missing).
2. Switch the data source to harmonized v1 when it lands; confirm interval_table v1 loads.
3. Run the contract test on every endpoint.
DELIVER: all endpoints in contract.
DONE WHEN: contract tests pass for every endpoint on the live API.
IF BLOCKED: serve v0 and tell Sheikh.
MANUAL (you do these yourself; the agent cannot):
- Check the cold-start delay by hand after the API has been idle
```

## PHASE 5: Scale-up (H30-36)
```
GOAL: /meta/validation merged and fast; ready for the freeze at H36.
STEPS:
1. Run P2.9: merge every file in data/processed/validation/; tolerate missing pieces.
2. Profile the slowest AOI queries; add caching or precomputed aggregates; record timings.
3. Plug in drivers (Monazir, H36) and outlook (Samin, H34) as they arrive.
DELIVER: /meta/validation; timing table.
DONE WHEN: typical AOI under about 1.5 seconds; a missing piece does not break the endpoint.
IF BLOCKED: shrink the AOI size limit rather than miss the freeze.
MANUAL (you do these yourself; the agent cannot):
- Time a typical AOI from your phone and laptop on the live site
```

## PHASE 6: Polish (H36-42)
```
GOAL: Stable, fast API; fallback verified.
STEPS:
1. Fix every API item on Samiul's H36 bug list.
2. Test cold-start behaviour; verify the static fallback with the API off.
3. Freeze changes at H42.
DELIVER: stable API.
DONE WHEN: no severity-1 bug open for you.
MANUAL (you do these yourself; the agent cannot):
- Test the static fallback by switching the API off in the dashboard and loading the app
```

## PHASE 7: Ship (H42-48)
```
GOAL: Final deploy at H44.
STEPS:
1. Run P2.10: deploy checklist and smoke test.
2. Tell Shammo and Samiul the final URLs at H44.
3. Stay on call until Sheikh submits at H46.
DELIVER: final deploy.
DONE WHEN: Samiul's end-to-end run passes on the hosted app.
IF BLOCKED: roll back to the last tagged build.
MANUAL (you do these yourself; the agent cannot):
- Do the final deploy in the dashboard, note the rollback step, and open the URLs from a different network
```
