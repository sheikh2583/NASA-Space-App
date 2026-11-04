---
id: T04
title: Mark incomplete weeks and months
kind: agent
owner: Sattyam
authors: [Sattyam, Shammo]
phase: P0
size: S
needs: [T00]
requires: [real-data]
branch: ws1/T04-incomplete-periods
touches: [ws2_platform/api/app.py, contracts/openapi.yaml, docs/CONTRACT_CHANGES.md, ws5_frontend/src/types.ts,
          ws5_frontend/src/components/SeriesChart.tsx, ws5_frontend/src/components/Calendar.tsx,
          ws5_frontend/src/i18n/en.json, ws5_frontend/src/i18n/bn.json, ws5_frontend/public/demo/snapshot.json]
creates: [ws2_platform/tests/test_api_complete.py, ws5_frontend/src/components/Calendar.test.tsx]
checks: [CHECK-PLAN, CHECK-PY, CHECK-WEB, CHECK-SNAP]
---
## Goal
The last snapshot week (starting 2 Nov 2026) holds one day of data, but it is drawn as a full week (value 98). That
looks like a collapse. Mark periods that run past the end of the data, and draw them differently.

## Context
- `build_summary` in `ws2_platform/api/app.py`:
  - **Weekly points** come from `Store.full_history`, which runs to `data_end`. A week that starts on or before
    `data_end` but ends after it is partial.
  - **Month and day points** come from `Store.series(sel, req.start, end, res)` with `end = min(req.end, data_end)`.
- `common/series.weekly_series` doesn't return `n_days`. Don't change `common/` for this; compute from dates.
- On the calendar, diagonal hatching already means "modeled" and dots mean "adjusted". Partial periods need a third,
  different mark.

## Steps
1. **Contract.**
   - `SummaryPoint` in `contracts/openapi.yaml` gains two optional properties:
     - `complete`: boolean, "false when the period extends past the last day with data";
     - `n_days`: integer, minimum 0, "days of the period that have data".
   - Append a line to `docs/CONTRACT_CHANGES.md`.
2. **API.** In `build_summary`, for each point with period start `t`, set:

   | `req.res` | `period_end` | `complete` | `n_days` |
   |---|---|---|---|
   | `week` | `t + 6 days` | `period_end <= s.data_end` | `max(0, (min(period_end, s.data_end) - t).days + 1)` |
   | `month` | last day of the month | `period_end <= end` (the `end` already computed in `build_summary`) | `(min(period_end, end) - t).days + 1` |
   | `day` | — | `True` | `1` |

   Add both fields to every point.
3. **Tests** in `ws2_platform/tests/test_api_complete.py`, using `tiny_api` and `tiny_request`; the tiny data ends
   Saturday 31 Dec 2016.
   - Weekly request for "pb": the point `t == "2016-12-26"` has `complete is False` and `n_days == 6`, and every
     earlier point has `complete is True`.
   - Monthly request with `end="2016-12-15"`: the last point (December) has `complete is False` and `n_days == 15`.
   - The response validates against `SummaryResponse` (reuse the validator pattern in `test_tiny_api.py`).
4. **UI.**
   - `types.ts`: `SummaryPoint` gains `complete?: boolean; n_days?: number`. A missing field means complete.
   - `Calendar.tsx`: when `p.complete === false`, draw an extra
     `<rect ... fill="none" stroke="var(--ink)" strokeDasharray="2 2" pointerEvents="none" />` over the cell. Add
     `t("series.partial", { n: num(p.n_days) })` to the cell's label.
   - `SeriesChart.tsx`: don't draw the value line for incomplete points. Map `value: p.complete === false ? null : p.value`
     and add a separate `partial` data key drawn as a dot only, named `t("chart.partial")`.
   - i18n:
     - `series.partial`: en "Partial: {{n}} of 7 days have data", plus a bn sentence;
     - `chart.partial`: en "Partial period", plus bn;
     - a legend line `calendar.legend_partial`: en "Dashed outline = partial period", plus bn; render it in the
       `.keys` row of `Calendar.tsx`.
5. **Component test** `Calendar.test.tsx`, using `renderHtml`.
   - Render a two-point series whose second point has `complete: false`.
   - The HTML contains `stroke-dasharray="2 2"` exactly once, and the text contains "Partial".
6. **Republish.** Run `python scripts/export_hosted_demo.py`, then check that the snapshot's last Punjab point has
   `complete: false`.
7. Run the checks, mark the card done, then `split`, push and open the PR.

## Acceptance
- [ ] `test_api_complete.py` passes in CI, using tiny data.
- [ ] `Calendar.test.tsx` passes.
- [ ] Snapshot: exactly one Punjab point and one Bangladesh point have `complete: false` (the 2 Nov 2026 week).
- [ ] CHECK-WEB and CHECK-SNAP pass.

## Stop and ask if
- Any point other than the last one comes out incomplete on the real data.
