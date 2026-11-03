"""detections.parquet -> grid_daily.parquet: sparse (cell_id, date, sat) aggregates.

cell_id follows decision 22 (common.grid); date is the local solar date (decision 23).
n_hiconf counts VIIRS high (90) and MODIS confidence >= 80.

Usage: python -m ws2_platform.grid [--det data/processed/detections.parquet] [--out data/processed/grid_daily.parquet]
"""
from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from common.grid import cell_id, local_solar_date

SCHEMA = pa.schema([("cell_id", pa.int32()), ("date", pa.date32()), ("sat", pa.string()), ("sensor", pa.string()),
                    ("n_det", pa.int32()), ("n_hiconf", pa.int32()), ("frp_sum", pa.float32()), ("frp_max", pa.float32()),
                    ("n_day", pa.int32()), ("n_night", pa.int32()), ("mean_scan", pa.float32())])


def grid_daily(det: pd.DataFrame) -> pd.DataFrame:
    d = pd.DataFrame({
        "cell_id": cell_id(det["lat"].values, det["lon"].values),
        "date": local_solar_date(det["acq_date"].values, det["acq_time"].values, det["lon"].values).values,
        "sat": det["sat"].values, "sensor": det["sensor"].values,
        "hi": np.where(det["sensor"].values == "VIIRS", det["conf"].values >= 90, det["conf"].values >= 80),
        "frp": det["frp"].values, "day": det["daynight"].values == "D", "scan": det["scan"].values,
    })
    g = d.groupby(["cell_id", "date", "sat", "sensor"], sort=True)
    out = g.agg(n_det=("frp", "size"), n_hiconf=("hi", "sum"), frp_sum=("frp", "sum"), frp_max=("frp", "max"),
                n_day=("day", "sum"), mean_scan=("scan", "mean")).reset_index()
    out["n_night"] = out["n_det"] - out["n_day"]
    for c in ("n_det", "n_hiconf", "n_day", "n_night"):
        out[c] = out[c].astype("int32")
    for c in ("frp_sum", "frp_max", "mean_scan"):
        out[c] = out[c].astype("float32")
    return out[[f.name for f in SCHEMA]]


def write(df: pd.DataFrame, path: str, schema: pa.Schema):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    pq.write_table(pa.Table.from_pandas(df, schema=schema, preserve_index=False), path + ".tmp")
    os.replace(path + ".tmp", path)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--det", default="data/processed/detections.parquet")
    ap.add_argument("--out", default="data/processed/grid_daily.parquet")
    a = ap.parse_args(argv)
    det = pd.read_parquet(a.det)
    g = grid_daily(det)
    write(g, a.out, SCHEMA)
    assert int(g["n_det"].sum()) == len(det), "sum of n_det must equal detection rows"
    print(f"grid_daily: {len(g)} rows, n_det sum {int(g['n_det'].sum())} = detections {len(det)} -> {a.out}")


if __name__ == "__main__":
    main()
