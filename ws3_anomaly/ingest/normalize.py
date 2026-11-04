"""Raw FIRMS CSV (archive, API or synthetic) -> data/processed/detections.parquet (contracts/parquet_schemas.json).

- sat from the satellite column: Terra, Aqua, N (SNPP), N20 (NOAA20), N21 (NOAA21)
- VIIRS confidence l/n/h -> 20/60/90; MODIS confidence kept 0-100
- source_type kept; only vegetation fires (type 0) are kept; near-real-time files have no type and are kept
- acq_date stays the UTC date; acq_time is HHMM UTC
- duplicates (same sat, date, time, lat, lon) from overlapping standard and NRT files are dropped, standard first

Usage: python -m ws3_anomaly.ingest.normalize data/raw/firms/*.csv* --out data/processed/detections.parquet [--clip demo]
--clip demo keeps only detections inside the demo-region boxes (use it with FIRMS country yearly files, which cover
a whole country).
"""
from __future__ import annotations

import argparse
import glob
import os

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

SAT_MAP = {"Terra": "Terra", "T": "Terra", "Aqua": "Aqua", "A": "Aqua", "N": "SNPP", "NPP": "SNPP", "SNPP": "SNPP",
           "N20": "NOAA20", "1": "NOAA20", "NOAA20": "NOAA20", "N21": "NOAA21", "2": "NOAA21", "NOAA21": "NOAA21"}
VIIRS_CONF = {"l": 20.0, "low": 20.0, "n": 60.0, "nominal": 60.0, "h": 90.0, "high": 90.0}
SCHEMA = pa.schema([("sensor", pa.string()), ("sat", pa.string()), ("acq_date", pa.date32()), ("acq_time", pa.int32()),
                    ("lat", pa.float64()), ("lon", pa.float64()), ("frp", pa.float32()), ("conf", pa.float32()),
                    ("daynight", pa.string()), ("scan", pa.float32()), ("track", pa.float32()),
                    ("source_type", pa.int32()), ("product_version", pa.string())])


def normalize_frame(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Returns (detections, stats) for one raw file."""
    sat = raw["satellite"].astype(str).map(SAT_MAP)
    if sat.isna().any():
        bad = sorted(raw.loc[sat.isna(), "satellite"].astype(str).unique())
        raise ValueError(f"unknown satellite codes {bad}")
    # FIRMS archive exports currently label Suomi-NPP's instrument as "SNPP"
    # while NOAA-20/21 exports use "VIIRS".  Satellite identity is therefore
    # the reliable discriminator; keep the instrument check for API variants.
    viirs = sat.isin(["SNPP", "NOAA20", "NOAA21"]) | raw["instrument"].astype(str).str.upper().eq("VIIRS")
    conf_raw = raw["confidence"].astype(str).str.strip().str.lower()
    conf = np.where(viirs, conf_raw.map(VIIRS_CONF), pd.to_numeric(conf_raw, errors="coerce"))
    stype = pd.to_numeric(raw["type"], errors="coerce") if "type" in raw else pd.Series(np.nan, index=raw.index)
    df = pd.DataFrame({
        "sensor": np.where(viirs, "VIIRS", "MODIS"), "sat": sat.values,
        "acq_date": pd.to_datetime(raw["acq_date"]).dt.date, "acq_time": pd.to_numeric(raw["acq_time"]).astype("int32"),
        "lat": raw["latitude"].astype("float64"), "lon": raw["longitude"].astype("float64"),
        "frp": raw["frp"].astype("float32"), "conf": pd.Series(conf, index=raw.index).astype("float32"),
        "daynight": raw["daynight"].astype(str), "scan": raw["scan"].astype("float32"), "track": raw["track"].astype("float32"),
        "source_type": stype.fillna(-1).astype("int32"), "product_version": raw.get("version", pd.Series("", index=raw.index)).astype(str),
    })
    keep = df["source_type"].isin([0, -1])  # -1 = no type field (NRT): kept, noted in NOTES.md
    stats = {"rows_in": len(df), "dropped_non_vegetation": int((~keep).sum()), "rows_out": int(keep.sum())}
    return df[keep].reset_index(drop=True), stats


def clip_to_demo(df: pd.DataFrame) -> pd.DataFrame:
    from common.regions import DEMO_REGIONS
    keep = np.zeros(len(df), dtype=bool)
    for meta in DEMO_REGIONS.values():
        x0, y0, x1, y1 = meta["bbox"]
        keep |= df["lon"].between(x0, x1).values & df["lat"].between(y0, y1).values
    return df[keep]


def normalize_files(paths, out_path, clip=None):
    frames, report = [], []
    for p in paths:
        df, st = normalize_frame(pd.read_csv(p))
        if clip == "demo":
            df = clip_to_demo(df)
            st["rows_out"] = len(df)
        df["_nrt"] = df["product_version"].str.contains("NRT", case=False)
        frames.append(df)
        report.append((os.path.basename(p), st))
    det = pd.concat(frames, ignore_index=True)
    before = len(det)
    det = det.sort_values("_nrt").drop_duplicates(["sat", "acq_date", "acq_time", "lat", "lon"], keep="first")
    det = det.drop(columns="_nrt").sort_values(["sat", "acq_date", "acq_time"]).reset_index(drop=True)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    tmp = out_path + ".tmp"
    pq.write_table(pa.Table.from_pandas(det, schema=SCHEMA, preserve_index=False), tmp)
    os.replace(tmp, out_path)  # rename, so nobody reads half a file
    return det, report, before - len(det)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", default="data/processed/detections.parquet")
    ap.add_argument("--clip", choices=["demo"], default=None)
    a = ap.parse_args(argv)
    paths = sorted(p for pat in a.inputs for p in glob.glob(pat))
    det, report, dups = normalize_files(paths, a.out, a.clip)
    for name, st in report:
        print(f"{name:40} in={st['rows_in']:>8} dropped_non_veg={st['dropped_non_vegetation']:>6} out={st['rows_out']:>8}")
    print(f"duplicates dropped: {dups}; detections: {len(det)} -> {a.out}")
    print(det.groupby("sat")["acq_date"].agg(["count", "min", "max"]).to_string())


if __name__ == "__main__":
    main()
