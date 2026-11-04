---
id: T24
title: Independent check against MODIS burned area (MCD64A1)
kind: agent
owner: Samin
authors: [Samin, Samiul, Shammo]
phase: P2
size: M
needs: [T33]
requires: [real-data, earthdata-files]
branch: ws1/T24-burned-area-check
touches: [ws5_frontend/src/components/Pages.tsx, ws5_frontend/src/i18n/en.json, ws5_frontend/src/i18n/bn.json,
          ws5_frontend/public/demo/snapshot.json, docs/science/method_en.md]
creates: [ws6_validation/mcd64.py, ws6_validation/tests/test_mcd64.py]
checks: [CHECK-PLAN, "python -m pytest -q ws6_validation/tests/test_mcd64.py", CHECK-FILES, CHECK-WEB, CHECK-SNAP]
human_checks: [CHECK-QA]
---
## Goal
Everything we validate today compares active-fire products with each other. A burned-area product (post-fire surface
change, a different algorithm) is **independent** evidence for both amount and timing.

## Context
- MCD64A1 HDF files hold two layers we use: `Burn Date` (day of year; 0 means unburned, negative values are
  no-data or water) and `QA`.
- Pixels are 463.3 m; the area per pixel is 0.2147 km².
- `ws2_platform/cells.py` already reads HDF4 with `pyhdf`, for MCD12C1. Reuse the same import pattern.
- Known limit: MCD64A1 misses many small, quick crop-residue burns. Compare **year-to-year variation and timing**, not
  absolute area.

## Steps
1. **`ws6_validation/mcd64.py`:**
   - `sinusoidal_to_latlon(h, v, row, col)`: the MODIS sinusoidal grid, with sphere radius 6371007.181 m, tile size
     1111950.5197665 m, 2400 × 2400 pixels per tile, and pixel centres at +0.5.
   - `read_tile(path) -> DataFrame`: per burned pixel, `lat`, `lon` and `burn_doy`.
   - `season_stats(pixels, cells, area_key, season, years) -> DataFrame`, per season year:
     - `burned_km2`, counting only pixels whose cell (`common.grid.cell_id`) is in the area;
     - `p10`, `p50` and `p90` burn day as an offset from the window start, using the same crossing rule as
       `ws4_outlook.season_profile._crossing` applied to daily counts.
   - `compare(stats, profile_season) -> dict`, against our season profile:
     - the Spearman correlation of totals, 2012-2025;
     - the median absolute difference of p50 days;
     - whether both timing trends have the same sign.
2. **Tests** (`test_mcd64.py`):
   - Coordinates: `sinusoidal_to_latlon(18, 4, 1200, 0)` is lat 45.00 and lon 0.00, to within 0.01°. The grid origin
     is x = -20015109.354 m, y = 10007554.677 m.
   - The point lat 30.5, lon 75 falls in tile h24v05: the inverse function, or a brute-force search over the tile,
     finds it there.
   - `season_stats` on a hand-made pixel set: known totals and p50.
   - `compare` on perfectly correlated inputs gives ρ = 1.
3. **Run.** `python -m ws6_validation.mcd64` writes `data/processed/validation/burned_area_check.json` with
   `producer: "burned_area_check"`, the per-season table, the comparison and the limitations ("small burns are
   missed; compare variation and timing, not totals").
4. **UI.** On the Validation page, add a scatter of our season total against burned km², per year, and the sentence
   `t("burned.result", { rho, days })`. Show the values exactly as measured, even if the agreement is weak.
5. **Method page** (`docs/science/method_en.md`). Add one bullet under "How we checked" (from T10) with the measured ρ and
   timing difference, using only supported Markdown.
6. Republish the legacy snapshot (`python scripts/export_hosted_demo.py`). QA is Sheikh's (`human_checks`). Render
   serves the piece after the next runtime release (T40 or T28). Run the checks, mark the card done, and hand over
   for commit.

## Acceptance
- [ ] Tests pass. The piece validates. The result is on the Validation page and the Method page, with the measured
  numbers.

## Stop and ask if
- No burned pixels fall inside the Punjab demo cells. That would mean a coordinate bug; check the corner test.
