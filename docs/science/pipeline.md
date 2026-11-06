# The project in plain words

Reviewed against `e97d49f`, 6 November 2026. Start with this overview, then read the [architecture](../project/architecture.md) and [harmonization walkthrough](harmonization-walkthrough.md).

MODIS and VIIRS see active fires differently. Their detection counts cannot simply be added into one consistent history. FireSense expresses the record in Suomi NPP VIIRS-equivalent terms for the supported Bangladesh and northern India regions.

It uses observed SNPP where available, adjusted NOAA-20 when SNPP is unavailable, and a MODIS-based estimate when neither VIIRS source is available. Operating-day metadata determines the source, including outages inside the SNPP era. Missing observation is distinct from zero detections.

Users choose named administrative areas through the map and area inspector. The calendar, time series, spatial layer and critical periods help explore historical activity. Season profiles describe a central activity window; weather panels show associations. Detections are not burned area, and cropland context does not prove ignition cause.

The uncertainty bands have a nominal target, not demonstrated uniform reliability. The saved detailed report records conditional coverage failures. Forecast alerts remain disabled in the inspected artifacts. See the [dated assessment](../project/review-2026-11-06.md) before quoting results.

## The chain

1. Normalize FIRMS downloads into `detections.parquet`.
2. Grid detections, retain administrative cells and build sensor availability.
3. Build the weekly panel; fit and compare harmonization methods on holdouts.
4. Calibrate aggregate intervals, report conditional coverage and assess drift.
5. Write the harmonized cell-day record and derive anomalies, periods and weather associations.
6. Produce regional outlook evidence, validation reports and QA summaries.
7. Package reviewed existing artifacts in a checksum-pinned runtime release.
8. Render serves the React UI and live FastAPI from one origin. Requests aggregate saved artifacts; they do not train.

GitHub Pages, snapshot mode and the static fallback are retired. The delivered interface is English; Bengali place names remain searchable. Planned features are not delivered capabilities.

## Scientific workflow

**Agent-operated training and validation were explicitly authorized on 6 November 2026.** Follow [AGENTS.md](../../AGENTS.md): declare the scientific run, preserve existing outputs, inspect execution paths and report actual evidence. Routine checks remain non-fitting; default setup includes fitting probes and belongs to the scientific execution workflow.

The [training guide](../guides/training.md) documents the commands and CUDA requirements. `scripts/train.ps1` / `scripts/train.sh` wrap the workflow; successful runs write `results/latest.json` and `results/latest.md`. These files describe that run, not later source revisions.

The current order in [run_pipeline.py](../../scripts/run_pipeline.py) is:

```text
synth (skipped when real inputs exist) -> ingest -> grid -> cells -> sensors
-> panel -> v0 -> model -> intervals -> interval_report -> drift -> v1
-> anomalies -> outlook -> validation -> fixtures -> qa -> results
```

Execute this order through a planned scientific run rather than an incidental documentation/UI check. A code/UI build does not regenerate the record or update its numerical evidence. The distinction between source, artifact and deployment evidence is described in the [review](../project/review-2026-11-06.md).

## Workstreams

The `ws1` through `ws6` directories separate harmonization, platform, anomalies, outlook, frontend and validation responsibilities. They form one application, not six independently deployed services. Current ownership and work order are in [the plan](../plan/README.md); the architecture's source map explains where to read each implementation.
