---
id: T25
title: Fire intensity (FRP) view, labelled uncalibrated
kind: agent
owner: Sattyam
authors: [Sattyam, Shammo, Sheikh]
phase: P2
size: S
needs: [T07]
requires: [real-data]
branch: ws1/T25-frp-view
touches: [ws2_platform/api/app.py, contracts/openapi.yaml, docs/project/contract-changes.md, scripts/export_hosted_demo.py,
          ws5_frontend/src/types.ts, ws5_frontend/src/snapshot.ts, ws5_frontend/src/App.tsx,
          ws5_frontend/src/components/AnalysisControls.tsx, ws5_frontend/src/components/SeriesChart.tsx,
          ws5_frontend/src/i18n/en.json, ws5_frontend/src/i18n/bn.json]
creates: [ws2_platform/tests/test_api_frp.py, ws5_frontend/public/demo/frp_bd.json, ws5_frontend/public/demo/frp_pb.json]
checks: [CHECK-PLAN, CHECK-PY, CHECK-WEB, CHECK-SNAP]
---
## Goal
Show fire radiative power (FRP) as a second view without overclaiming. It has no uncertainty band, is labelled
uncalibrated, and is never called energy.

## Context
- `harmonized.parquet` has `value_frp`.
- For NOAA-20-adjusted rows, `ws1_harmonize/write_harmonized.py` multiplies `n20_frp` by the **count** ratio. No FRP
  ratio exists for NOAA-20 (`baselines.fit` computes `b0_frp` only for MODIS). That is a known limitation; write it
  down.
- A weekly FRP value is a sum of sampled values at overpass times. It is not energy, and not continuous intensity.

## Steps
1. **API.**
   - `AOIRequest` gains `metric: Literal["count", "frp"] = "count"`.
   - In `build_summary`, for `metric == "frp"`, aggregate `value_frp` instead of `value_count`. `weekly_series` sums
     `value_count`, so pass `harmonized.assign(value_count=harmonized["value_frp"])` through a `Store` helper
     `frp_history(sel)`, cached like `full_history`.
   - Set `lo = hi = null` on every point and `units = "Sum of sampled fire radiative power, MW per week (uncalibrated)"`.
   - Skip anomaly flags for FRP.
   - Add the field to OpenAPI and a line to `docs/project/contract-changes.md`.
2. **Tests** (`test_api_frp.py`, `tiny_api`). The tiny `value_frp` is 8 × the count, so:
   - FRP totals are 8 × the count totals;
   - the bands are null;
   - the units mention "uncalibrated".
3. **Snapshot**, in separate lazy files. The export writes `ws5_frontend/public/demo/frp_<key>.json` (the FRP
   summary response). `snapshot.ts` fetches it once, cached, when `body.metric === "frp"`.
4. **UI.**
   - An AnalysisControls toggle (`t("controls.metric_count")` / `t("controls.metric_frp")`) sets `metric` in requests.
   - With FRP, the chart hides the band and shows a badge `t("chart.uncalibrated")`, and the calendar keeps counts.
     Only the chart switches, to keep the calendar's meaning stable.
   - Add a help topic `help.frp`: "Fire radiative power: how much heat the detected fires gave off at the moment the
     satellite passed. A sum of snapshots, not total energy."
5. Republish. Run the checks, mark the card done, `split`, push and open the PR. Note the NOAA-20 FRP limitation in
   the PR.

## Acceptance
- [ ] Tests pass. FRP is viewable in both modes, always without a band and with the "uncalibrated" badge.

## Stop and ask if
- An `frp_<key>.json` file is over 400 KB.
