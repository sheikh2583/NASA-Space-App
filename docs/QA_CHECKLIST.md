# QA checklist (owner: Samiul; usable by anyone)

## Data (after G1)
- [ ] No duplicate (cell_id, date, sat) keys in grid_daily
- [ ] Points exactly on grid lines land in the cell given by decision 22
- [ ] Dates inside the expected range; no future dates
- [ ] Counts and FRP non-negative; no nulls in key columns
- [ ] Sum of grid_daily n_det equals the number of detection rows
- [ ] One chosen day and AOI matches the FIRMS web viewer count (count by UTC acq_date in detections.parquet; grid_daily uses local solar dates)
- [ ] Non-vegetation sources filtered; confidence mapped to 20/60/90
- [ ] cells.parquet: admin1 and land-cover fields filled

## Harmonized series
- [ ] lo <= value <= hi; no nulls; no negatives
- [ ] source set on every row; on SNPP operating days value equals observed SNPP
- [ ] Seam at 2012 visible (modeled share drops to zero); second seam at 2 Nov 2026 (source adjusted_from_noaa20)
- [ ] No zero values on days sensor_days marks a satellite as not operating

## API
- [ ] Every endpoint validates against contracts/openapi.yaml (mock and live)
- [ ] Empty AOI returns 200 with an empty series and a note; oversized AOI returns 422
- [ ] Typical AOI answers in under about 1.5 seconds
- [ ] Static fallback works when the API is unreachable

## App
- [ ] Where map layer shows cells for the selected week and recolours when the week changes
- [ ] Current-status card shows level, week percentile and the data-through date
- [ ] The app and slides state that the demo covers South Asia
- [ ] Draw area, calendar, flagged periods, band, badges work on the live API
- [ ] Modeled values are always labeled; no causal wording anywhere
- [ ] Bangla renders; no hard-coded strings; mobile layout works
- [ ] Demo path (Bangladesh, then Punjab Oct-Nov) passes on the deployed app and on the fallback
