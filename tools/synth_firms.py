"""Synthetic FIRMS-like inputs for building and testing the pipeline before real data is downloaded.

Everything this writes is SYNTHETIC: fire counts, admin1 boundaries, land cover and weather are invented
with known structure (seasons, planted anomalies, a rainfall association, sensor sensitivities, the Terra
drift, the SNPP cutoff) so each stage can be checked against a known truth. Never present these numbers
as real. Real inputs replace them file by file (data/raw/firms, boundaries, land cover, weather).

Usage: python tools/synth_firms.py [--out data/raw] [--end 2026-11-02] [--scale 1.0] [--seed 7]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.grid import cell_center, cells_in_bbox  # noqa: E402
from common.regions import DEMO_REGIONS, OUTAGES, SNPP_CUTOFF, WINDOWS  # noqa: E402

# Expected detections relative to "true" activity (SNPP = 1). Terra sees the morning pass, when fewer fires burn.
SENSITIVITY = {"Terra": 0.20, "Aqua": 0.30, "SNPP": 1.0, "NOAA20": 0.92, "NOAA21": 0.95}
# Local overpass times (day, night) as HHMM.
OVERPASS = {"Terra": (1030, 2230), "Aqua": (1330, 130), "SNPP": (1330, 130), "NOAA20": (1240, 40), "NOAA21": (1300, 100)}
SAT_CODE = {"Terra": "Terra", "Aqua": "Aqua", "SNPP": "N", "NOAA20": "N20", "NOAA21": "N21"}
# Seasonal peaks: (day of year, spread in days, weight).
SEASONS = {"BD": [(80, 25, 1.0)], "PB": [(300, 14, 0.7), (122, 14, 0.3)]}
# Planted anomalies the pipeline should find: (region, season-year months, multiplier).
PLANTED = {("BD", 2021): 1.9, ("PB", 2016): 1.8, ("PB", 2024): 0.45}
# Admin1 split points for synthetic regions (lon, lat).
SPLIT = {"BD": (90.35, 23.6), "PB": (75.75, 30.25)}


def admin1_polygons():
    """Four synthetic admin1 quadrants per demo region, as GeoJSON features (geoBoundaries-like properties)."""
    feats = []
    for code, meta in DEMO_REGIONS.items():
        x0, y0, x1, y1 = meta["bbox"]
        sx, sy = SPLIT[code]
        quads = {"SW": (x0, y0, sx, sy), "SE": (sx, y0, x1, sy), "NW": (x0, sy, sx, y1), "NE": (sx, sy, x1, y1)}
        for k, (a, b, c, d) in quads.items():
            feats.append({"type": "Feature",
                          "properties": {"shapeID": f"{code}-{k}", "shapeName": f"{meta['name']} {k} (synthetic)",
                                         "shapeGroup": code},
                          "geometry": {"type": "Polygon", "coordinates": [[[a, b], [c, b], [c, d], [a, d], [a, b]]]}})
    return {"type": "FeatureCollection", "features": feats}


def seasonal(code, doy):
    s = np.zeros_like(doy, dtype="float64")
    for peak, spread, w in SEASONS[code]:
        dist = np.minimum(np.abs(doy - peak), 365 - np.abs(doy - peak))
        s += w * np.exp(-0.5 * (dist / spread) ** 2)
    return 0.03 + s


def operating(sat, day: dt.date) -> bool:
    start, end = WINDOWS[sat]
    if day < start or (end is not None and day > end):
        return False
    if sat == "SNPP" and day == SNPP_CUTOFF:
        return True  # the day pass happens before the 13:00 UTC cutoff; the night pass is dropped below
    return not any(s == sat and a <= day <= b for s, a, b, _ in OUTAGES)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/raw")
    ap.add_argument("--start", default="2000-11-01")
    ap.add_argument("--end", default="2026-11-02")
    ap.add_argument("--scale", type=float, default=1.0, help="multiplies detection counts")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args(argv)
    rng = np.random.default_rng(a.seed)
    out_firms = os.path.join(a.out, "firms")
    out_syn = os.path.join(a.out, "synthetic")
    os.makedirs(out_firms, exist_ok=True)
    os.makedirs(out_syn, exist_ok=True)
    days = pd.date_range(a.start, a.end, freq="D")
    dates = days.date
    doy = days.dayofyear.values
    weeks = days.to_period("W-SUN").start_time
    week_idx, week_starts = pd.factorize(weeks, sort=True)

    with open(os.path.join(out_syn, "admin1.geojson"), "w") as f:
        json.dump(admin1_polygons(), f)

    lc_rows, wx_rows = [], []
    for code, meta in DEMO_REGIONS.items():
        cells = cells_in_bbox(*meta["bbox"])
        active = cells[rng.random(cells.size) < 0.35]
        n = active.size
        crop = rng.beta(2, 2, n).astype("float32")
        forest = ((1 - crop) * rng.beta(2, 3, n)).astype("float32")
        lc_rows.append(pd.DataFrame({"cell_id": active, "cropland_frac": crop, "forest_frac": forest}))
        # Weather: weekly anomalies (standardized), AR(1). Rain suppresses burning the next week; heat adds a little.
        nw = len(week_starts)
        rain = np.zeros(nw)
        t2m = np.zeros(nw)
        for k in range(1, nw):
            rain[k] = 0.5 * rain[k - 1] + rng.normal(0, 0.87)
            t2m[k] = 0.6 * t2m[k - 1] + rng.normal(0, 0.8)
        soil = 0.7 * np.concatenate([[0], rain[:-1]]) + rng.normal(0, 0.5, nw)
        wx_rows.append(pd.DataFrame({"region": code, "week_start": week_starts.date, "rain_anom": rain,
                                     "t2m_anom": t2m, "soil_anom": soil}))
        wx_mult = np.exp(-0.30 * np.concatenate([[0], rain[:-1]]) + 0.12 * t2m)
        week_noise = np.exp(rng.normal(0, 0.30, nw))
        years = np.arange(days.year.min(), days.year.max() + 2)
        year_f = dict(zip(years, np.exp(rng.normal(0, 0.22, years.size))))
        season_year = np.where(days.month >= 10, days.year + 1, days.year)  # Oct-Sep season, labeled by end year
        # BD planted anomalies refer to the season (labeled by its end year, the Mar-Apr peak);
        # PB planted anomalies refer to the Oct-Nov peak of that calendar year.
        yf = np.array([year_f[y] * PLANTED.get((code, y), 1.0) for y in season_year])
        if code == "PB":
            yf = np.array([year_f[sy] * PLANTED.get((code, cal), 1.0) if m in (10, 11) else year_f[sy]
                           for sy, cal, m in zip(season_year, days.year, days.month)])
        base = np.exp(rng.normal(0, 1.0, n)) * (0.2 + crop) * 0.55
        persistent = rng.choice(n, size=3, replace=False)  # industrial hot spots (type 2), filtered at ingest
        day_factor = (seasonal(code, doy) * yf * week_noise[week_idx] * wx_mult[week_idx]).astype("float32")
        target = 15000.0 * a.scale * (365.0 / 365.0)
        norm = target / (base.sum() * day_factor.mean() * 365.0)
        base = base * norm
        lat_c, lon_c = cell_center(active)
        for sat in ("Terra", "Aqua", "SNPP", "NOAA20", "NOAA21"):
            ok = np.array([operating(sat, d) for d in dates])
            sens = np.full(len(days), SENSITIVITY[sat])
            if sat == "Terra":  # orbit drift lowers Terra's counts from 2021 on
                sens = sens * np.clip(1 - 0.05 * np.maximum(days.year.values - 2021, 0), 0.6, 1)
            if sat == "Aqua":
                sens = sens * np.clip(1 - 0.03 * np.maximum(days.year.values - 2022, 0), 0.7, 1)
            frames = []
            for y in np.unique(days.year):
                sel = (days.year == y) & ok
                if not sel.any():
                    continue
                lam = np.outer(base, day_factor[sel] * sens[sel])  # cells x days
                counts = rng.poisson(lam)
                counts[persistent, :] = rng.poisson(2.0 * SENSITIVITY[sat], (persistent.size, sel.sum()))
                ci, di = np.nonzero(counts)
                k = counts[ci, di]
                ci, di = np.repeat(ci, k), np.repeat(di, k)
                m = ci.size
                if m == 0:
                    continue
                night = rng.random(m) < 0.12
                lat = lat_c[ci] + rng.uniform(-0.05, 0.05, m)
                lon = lon_c[ci] + rng.uniform(-0.05, 0.05, m)
                local = np.where(night, OVERPASS[sat][1], OVERPASS[sat][0])
                local_min = (local // 100) * 60 + local % 100 + rng.integers(-20, 21, m)
                utc_min = local_min - lon / 15.0 * 60.0
                day_shift = np.floor(utc_min / 1440.0).astype(int)
                utc_min = np.mod(utc_min, 1440).astype(int)
                sel_dates = days[sel]
                acq = (sel_dates[di] + pd.to_timedelta(day_shift, unit="D")).strftime("%Y-%m-%d")
                hhmm = (utc_min // 60) * 100 + utc_min % 60
                is_pers = np.isin(ci, persistent)
                viirs = sat in ("SNPP", "NOAA20", "NOAA21")
                frp = np.round(np.exp(rng.normal(1.6 if viirs else 2.6, 0.9, m)), 2)
                if viirs:
                    conf = rng.choice(["l", "n", "h"], m, p=[0.15, 0.7, 0.15])
                    bright = np.round(rng.normal(335, 12, m), 2)
                else:
                    conf = rng.integers(30, 101, m)
                    bright = np.round(rng.normal(320, 10, m), 1)
                df = pd.DataFrame({
                    "latitude": np.round(lat, 5), "longitude": np.round(lon, 5),
                    ("bright_ti4" if viirs else "brightness"): bright,
                    "scan": np.round(rng.uniform(0.32 if viirs else 1.0, 0.8 if viirs else 4.0, m), 2),
                    "track": np.round(rng.uniform(0.36 if viirs else 1.0, 0.75 if viirs else 2.0, m), 2),
                    "acq_date": acq, "acq_time": hhmm, "satellite": SAT_CODE[sat],
                    "instrument": "VIIRS" if viirs else "MODIS", "confidence": conf,
                    "version": "2.0SP" if viirs else "6.1SP",
                    ("bright_ti5" if viirs else "bright_t31"): np.round(rng.normal(295, 6, m), 2),
                    "frp": frp, "daynight": np.where(night, "N", "D"), "type": np.where(is_pers, 2, 0),
                })
                if sat == "SNPP":  # FIRMS stopped SNPP at 13:00 UTC on the cutoff day
                    late = (df["acq_date"] > SNPP_CUTOFF.isoformat()) | (
                        (df["acq_date"] == SNPP_CUTOFF.isoformat()) & (df["acq_time"] >= 1300))
                    df = df[~late]
                frames.append(df)
            out = pd.concat(frames, ignore_index=True)
            path = os.path.join(out_firms, f"synthetic_{code}_{sat}.csv.gz")
            out.to_csv(path, index=False)
            print(f"{code} {sat:6} {len(out):>8} detections -> {path}")
    lc = pd.concat(lc_rows, ignore_index=True)
    lc["landcover_dom"] = np.where(lc["cropland_frac"] >= 0.5, "cropland",
                                   np.where(lc["forest_frac"] >= 0.3, "forest", "mosaic"))
    lc.to_parquet(os.path.join(out_syn, "landcover.parquet"), index=False)
    pd.concat(wx_rows, ignore_index=True).to_parquet(os.path.join(out_syn, "weather_week.parquet"), index=False)
    with open(os.path.join(out_syn, "TRUTH.json"), "w") as f:
        json.dump({"note": "synthetic inputs; planted anomalies to recover", "planted": {f"{k[0]}-{k[1]}": v for k, v in PLANTED.items()},
                   "sensitivity": SENSITIVITY, "rain_effect": "burning x exp(-0.30 * rain anomaly of the previous week)"}, f, indent=2)
    print("landcover, weather, admin1 ->", out_syn)


if __name__ == "__main__":
    main()
