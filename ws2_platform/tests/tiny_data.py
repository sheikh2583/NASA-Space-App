"""A tiny, deterministic data/processed folder for API tests that must run in CI (where data/ is absent).

make_tiny_processed(dir) writes the runtime files the API reads (the core serving files in the root Dockerfile runtime bundle):
cells.parquet, harmonized.parquet, sensor_days.parquet, interval_table.json, drivers_region.json,
outlook_region.json and validation/. Two demo regions, four cells each:
  - PB (country "PB", admin1 "PB-1" Punjab): a paddy-residue season peaking about 2 Nov and a smaller
    wheat-residue season peaking about 9 May;
  - BD (country "BD", admin1 "BD-1" Dhaka): a dry-season peak about mid-March.
Years 2004-2016: modeled_from_modis before 20 Jan 2012, observed_viirs after (lo = hi = value).
Use it through the `tiny_api` fixture in ws2_platform/tests/conftest.py.
"""
from __future__ import annotations

import datetime as dt
import json
import os

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from common.grid import cell_id

START, END = dt.date(2004, 1, 1), dt.date(2016, 12, 31)
SNPP_START = dt.date(2012, 1, 20)
PB_BOX = [74.6, 29.8, 76.4, 31.2]     # the Punjab demo polygon's bounding box (ws5_frontend/src/config.ts)
BD_BOX = [89.5, 23.0, 90.5, 24.0]     # the Bangladesh demo bbox
PB_CELLS = [(30.05, 75.05), (30.15, 75.15), (30.25, 75.55), (30.85, 76.05)]
BD_CELLS = [(23.25, 89.75), (23.45, 89.95), (23.65, 90.15), (23.85, 90.35)]
SEASONS = {  # region: list of (peak month, peak day, sd in days, detections per cell per season)
    "PB": [(11, 2, 9.0, 300.0), (5, 9, 7.0, 60.0)],
    "BD": [(3, 15, 14.0, 20.0)],
}


def _cells() -> pd.DataFrame:
    rows = []
    for code, pts, adm, name in (("PB", PB_CELLS, "PB-1", "Punjab"), ("BD", BD_CELLS, "BD-1", "Dhaka")):
        for lat, lon in pts:
            rows.append({"cell_id": int(cell_id(lat, lon)), "lat_c": lat, "lon_c": lon, "landcover_dom": "cropland",
                         "cropland_frac": 0.8, "forest_frac": 0.05, "admin1_id": adm, "admin1_name": name, "country": code})
    return pd.DataFrame(rows)


def _daily_expected(code: str, days: pd.DatetimeIndex) -> np.ndarray:
    out = np.zeros(len(days))
    for m, d, sd, total in SEASONS[code]:
        for y in range(days.year.min() - 1, days.year.max() + 2):
            c = pd.Timestamp(y, m, d)
            out += total * np.exp(-0.5 * (((days - c) / pd.Timedelta(days=1)).to_numpy() / sd) ** 2) / (sd * np.sqrt(2 * np.pi))
    return out


def _harmonized(cells: pd.DataFrame, rng) -> pd.DataFrame:
    days = pd.date_range(START, END, freq="D")
    frames = []
    for c in cells.itertuples():
        lam = _daily_expected(c.country, days) * np.exp(rng.normal(0, 0.2, len(days)))
        v = rng.poisson(lam).astype("float32")
        keep = v > 0
        d = days[keep]
        val = v[keep]
        observed = d.date >= SNPP_START
        frames.append(pd.DataFrame({
            "cell_id": np.int32(c.cell_id), "date": d.date, "value_count": val, "value_frp": val * 8.0,
            "modeled_count": val, "lo_count": np.where(observed, val, val * 0.6),
            "hi_count": np.where(observed, val, val * 1.5), "level": np.float32(0.9),
            "source": np.where(observed, "observed_viirs", "modeled_from_modis"), "drift_flag": False,
            "method_version": "tiny-test"}))
    return pd.concat(frames, ignore_index=True).sort_values(["cell_id", "date"]).reset_index(drop=True)


def _sensor_days() -> pd.DataFrame:
    days = pd.date_range(START, END, freq="D").date
    rows = []
    for sat in ("Terra", "Aqua", "SNPP"):
        for d in days:
            on = d >= SNPP_START if sat == "SNPP" else True
            rows.append((d, sat, on, "" if on else "before first data"))
    return pd.DataFrame(rows, columns=["date", "sat", "operating", "note"])


def _write_parquet(df: pd.DataFrame, path: str, name: str):
    from tools.verify_files import arrow_schema
    pq.write_table(pa.Table.from_pandas(df, schema=arrow_schema(name), preserve_index=False), path)


def make_tiny_processed(out_dir) -> str:
    out = str(out_dir)
    os.makedirs(os.path.join(out, "validation"), exist_ok=True)
    rng = np.random.default_rng(11)
    cells = _cells()
    _write_parquet(cells, os.path.join(out, "cells.parquet"), "cells")
    _write_parquet(_harmonized(cells, rng), os.path.join(out, "harmonized.parquet"), "harmonized")
    _write_parquet(_sensor_days(), os.path.join(out, "sensor_days.parquet"), "sensor_days")
    table = {"version": "tiny-test", "level": 0.9, "entries": [
        {"res": r, "stratum": "all", "max_value": None, "lo_mult": 0.6, "hi_mult": 1.5, "hi_add": 1.0} for r in ("week", "month")]}
    with open(os.path.join(out, "interval_table.json"), "w") as f:
        json.dump(table, f)
    now = dt.datetime(2017, 1, 2, tzinfo=dt.timezone.utc).isoformat()
    for name in ("drivers_region", "outlook_region"):
        with open(os.path.join(out, f"{name}.json"), "w") as f:
            json.dump({"schema_version": "1.0", "generated_at": now, "regions": {}}, f)
    with open(os.path.join(out, "validation", "qa.json"), "w") as f:
        json.dump({"schema_version": "1.0", "generated_at": now, "producer": "qa",
                   "metrics": {"checks": [{"name": "tiny", "result": "pass"}]}, "limitations": ["Tiny test data."]}, f)
    return out
