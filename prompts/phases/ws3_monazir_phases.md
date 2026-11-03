# Phase prompts: Monazir (Team Member 3). Detailed sub-prompts: prompts/ws3_monazir.md

## PHASE 1: Kickoff (H0-3)
```
GOAL: Know exactly how we get FIRMS data; start the first slice.
INPUTS: your own FIRMS MAP_KEY in .env.
STEPS:
1. Run P3.1: archive route, area API limits, SNPP near-real-time status. Write the answers in NOTES.md.
2. Tell Sheikh what you found.
3. Start P3.2 (normalization) on one day of data.
DELIVER: written access notes; a working one-day pull.
DONE WHEN: both pulls return rows with the expected columns.
IF BLOCKED: ask Sheikh whether another team member can help with account access.
MANUAL (you do these yourself; the agent cannot):
- Register your own FIRMS MAP_KEY and an Earthdata login; put the key in your .env
- Submit the FIRMS archive download requests (MODIS and VIIRS SNPP, demo regions) on the website as early as possible
```

## PHASE 2: Data (H3-8)
```
GOAL: detections.parquet for Bangladesh by H4 and for the demo regions by H6; the stub by H8.
STEPS:
1. Finish P3.2 for Bangladesh; print the HANDOFF to Sattyam and Samiul at H4.
2. Run P3.3: Bangladesh and Punjab-Haryana-Delhi; print the HANDOFF at H6.
3. Ask Samiul for the data QA report by H10.
4. Run P3.4: the score_series stub; tell Sattyam the signature at H8.
DELIVER: detections.parquet; score_series stub.
DONE WHEN: schema validates; rows after filtering equal raw rows minus dropped sources.
DO NOT: wait for the wider South Asia pull.
IF BLOCKED: deliver Bangladesh only and say so; pull the rest in the background.
MANUAL (you do these yourself; the agent cannot):
- Check your email for the archive download links, download the big files, and move them to the shared drive
- Check you have enough free disk space on your laptop
```

## PHASE 3: Floor (H8-24)
```
GOAL: anomalies and critical periods v0 at H18.
INPUTS: cells (Sattyam, H8); common/series and climatology (Samin, H10); harmonized v0 (Sheikh, H14).
STEPS:
1. Fix ingestion issues from Samiul's QA report.
2. Run P3.5: find_periods and the batch script for every admin1 region.
3. Print the HANDOFF of anomalies_region_week.parquet and critical_periods.parquet to Sattyam at H18.
4. Start P3.6 (robust version).
DELIVER: anomalies and critical periods v0.
DONE WHEN: schemas validate; a spike-injected series yields one ranked period.
IF BLOCKED: use the percentile method on the baseline series only.
MANUAL (you do these yourself; the agent cannot):
- Open the FIRMS web map for one day and one small area and compare it with your rows
```

## PHASE 4: Core (H24-30)
```
GOAL: robust anomalies by H26; weather loaders handed to Samin.
STEPS:
1. Run P3.6: robust STL or median baseline, the interval-aware flag, the seam check.
2. Talk to Sheikh about how the 2012 seam appears in flags.
3. Run P3.7: weather loaders; print the HANDOFF to Samin at H26.
DELIVER: robust score_series; weather loaders.
DONE WHEN: spike flagged; noise gives few flags; seam-dependent flags marked.
IF BLOCKED: keep the percentile method; mark flags as basic.
MANUAL (you do these yourself; the agent cannot):
- Check that the weather data sources (CHIRPS, NASA POWER) are reachable from your network and note any sign-in needed
```

## PHASE 5: Scale-up (H30-36)
```
GOAL: drivers by H36.
STEPS:
1. Run P3.8: driver_associations with block-permutation p-values and bootstrap CIs.
2. Run the lint test for causal words.
3. Show Shammo the wording; ask Samiul to read the strings.
4. Print the HANDOFF to Sattyam and Shammo.
DELIVER: drivers.py; drivers_region.json.
DONE WHEN: schema validates; lint passes; sparse AOI returns insufficient data.
IF BLOCKED: ship a short list of descriptive correlations.
MANUAL (you do these yourself; the agent cannot):
- Read every driver sentence aloud with Shammo and decide the final wording together
```

## PHASE 6: Polish (H36-42)
```
GOAL: wording and flags are trustworthy.
STEPS:
1. Review every driver and anomaly string in the app; fix any causal wording with Shammo.
2. Fix your items on Samiul's bug lists.
DELIVER: reviewed wording.
DONE WHEN: no causal words found.
MANUAL (you do these yourself; the agent cannot):
- Review the anomaly and driver text in the running app with your own eyes and fix any causal wording
```

## PHASE 7: Ship (H42-48)
```
GOAL: support the final run-through.
STEPS:
1. Check anomaly, period and driver outputs on the deployed app for both demo regions.
2. Review Samiul's PM2.5 wording if it exists.
3. Stay on call until submission.
DELIVER: confirmation message to Sheikh.
MANUAL (you do these yourself; the agent cannot):
- Check the anomaly and period outputs on the deployed app for both demo regions
```
