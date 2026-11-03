"""Weekly weather anomalies for drivers and the outlook (prompt P3.7). Access is unverified (H0-05).

Sources:
  - NASA POWER daily point API (T2M, PRECTOTCORR, GWETTOP): sampled at each 0.5 degree tile centre in a bbox.
  - CHIRPS daily rainfall (global 0.05 degree GeoTIFFs) as an alternative rainfall source.
  - synthetic: data/raw/synthetic/weather_week.parquet while real data is not downloaded.
Output (cached Parquet): region, week_start, rain_anom, t2m_anom, soil_anom = standardized same-week anomalies.
"""
from __future__ import annotations

import json
import os
import time

import numpy as np
import pandas as pd
import requests

from common.climatology import week_of_year

POWER = ("https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,PRECTOTCORR,GWETTOP&community=AG"
         "&longitude={lon}&latitude={lat}&start={start}&end={end}&format=JSON")
CHIRPS = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/{y}/chirps-v2.0.{y}.{m:02d}.{d:02d}.tif.gz"


def tiles(bbox, step=0.5):
    x0, y0, x1, y1 = bbox
    xs = np.arange(np.floor(x0 / step) * step + step / 2, x1, step)
    ys = np.arange(np.floor(y0 / step) * step + step / 2, y1, step)
    return [(round(x, 3), round(y, 3)) for y in ys for x in xs]


def power_point(lon, lat, start, end, cache_dir="data/raw/power", session=None, retries=3) -> pd.DataFrame:
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, f"power_{lon}_{lat}_{start}_{end}.json")
    if not os.path.exists(path):
        session = session or requests.Session()
        for k in range(retries):
            r = session.get(POWER.format(lon=lon, lat=lat, start=start.replace("-", ""), end=end.replace("-", "")), timeout=120)
            if r.status_code == 200:
                with open(path, "w") as f:
                    f.write(r.text)
                break
            time.sleep(2 ** k)
        else:
            raise RuntimeError(f"POWER request failed for {lon},{lat}: HTTP {r.status_code}")
    p = json.load(open(path))["properties"]["parameter"]
    df = pd.DataFrame({k: pd.Series(v) for k, v in p.items()})
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    return df.replace(-999.0, np.nan)


def to_weekly_anomalies(daily: pd.DataFrame, region: str) -> pd.DataFrame:
    """Daily T2M/PRECTOTCORR/GWETTOP -> Monday weeks -> standardized same-week anomalies."""
    wk = daily.resample("W-MON", label="left", closed="left").agg({"PRECTOTCORR": "sum", "T2M": "mean", "GWETTOP": "mean"})
    wk.index.name = "week_start"
    wk = wk.reset_index()
    w = week_of_year(wk["week_start"]).values
    out = pd.DataFrame({"region": region, "week_start": wk["week_start"].dt.date})
    for src, dst in (("PRECTOTCORR", "rain_anom"), ("T2M", "t2m_anom"), ("GWETTOP", "soil_anom")):
        g = wk[src].groupby(w)
        out[dst] = ((wk[src] - g.transform("mean")) / g.transform("std").replace(0, np.nan)).values
    return out


def power_region(region: str, bbox, start, end, **kw) -> pd.DataFrame:
    frames = [power_point(lon, lat, start, end, **kw) for lon, lat in tiles(bbox)]
    return to_weekly_anomalies(pd.concat(frames).groupby(level=0).mean(), region)


def synthetic(path="data/raw/synthetic/weather_week.parquet") -> pd.DataFrame:
    return pd.read_parquet(path)


def load_weather(region_country: str, source: str = "auto") -> pd.DataFrame | None:
    """Weekly anomalies for a demo region code (BD, PB): the cache from power_region(), else synthetic weather but only
    when ALLOW_SYNTHETIC_WEATHER=1 (set by scripts/run_pipeline.py for synthetic runs). None when neither applies."""
    cache = f"data/interim/monazir/weather_{region_country}.parquet"
    if source in ("auto", "cache") and os.path.exists(cache):
        return pd.read_parquet(cache)
    if os.environ.get("ALLOW_SYNTHETIC_WEATHER") == "1" and os.path.exists("data/raw/synthetic/weather_week.parquet"):
        df = synthetic()
        return df[df["region"] == region_country].reset_index(drop=True)
    return None


def main(argv=None):
    """Download NASA POWER for both demo regions and cache weekly anomalies (python -m ws3_anomaly.loaders.weather)."""
    import argparse
    from common.regions import DEMO_REGIONS
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2000-11-01")
    ap.add_argument("--end", default=pd.Timestamp.today().strftime("%Y-%m-%d"))
    a = ap.parse_args(argv)
    os.makedirs("data/interim/monazir", exist_ok=True)
    for code, meta in DEMO_REGIONS.items():
        df = power_region(code, meta["bbox"], a.start, a.end)
        df.to_parquet(f"data/interim/monazir/weather_{code}.parquet", index=False)
        print(code, len(df), "weeks cached")


if __name__ == "__main__":
    main()
