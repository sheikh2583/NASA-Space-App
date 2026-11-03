"""sensor_days.parquet: which satellite was operating on which local solar day (decision 18).

A satellite operates from its first to its last day of data (bounded by common.regions.WINDOWS), minus known
outage windows. The SNPP cutoff day (2 Nov 2026) is marked not operating: only its day pass exists, so the
day would be undercounted. grid_daily keeps every detection (so sum(n_det) = detections); consumers skip
non-operating days with drop_non_operating().

Usage: python -m ws2_platform.sensors [--grid data/processed/grid_daily.parquet] [--out data/processed/sensor_days.parquet]
"""
from __future__ import annotations

import argparse
import datetime as dt

import pandas as pd
import pyarrow as pa

from common.regions import OUTAGES, SATS, SNPP_CUTOFF, WINDOWS
from ws2_platform.grid import write

SCHEMA = pa.schema([("date", pa.date32()), ("sat", pa.string()), ("operating", pa.bool_()), ("note", pa.string())])


def sensor_days(grid: pd.DataFrame, end: dt.date | None = None) -> pd.DataFrame:
    first_seen = grid.groupby("sat")["date"].min().to_dict()
    last_seen = grid.groupby("sat")["date"].max().to_dict()
    end = end or max(last_seen.values())
    start = min(WINDOWS[s][0] for s in SATS)
    days = pd.date_range(start, end, freq="D").date
    rows = []
    for sat in SATS:
        w0, w1 = WINDOWS[sat]
        if sat not in first_seen:
            continue
        a = max(w0, first_seen[sat])
        b = min(w1, last_seen[sat]) if w1 else last_seen[sat]
        for d in days:
            op, note = a <= d <= b, ""
            if not op:
                note = "before first data" if d < a else "after last data"
            if sat == "SNPP" and d >= SNPP_CUTOFF:
                op, note = False, "SNPP ended 2 Nov 2026 13:00 UTC" + (" (partial day: day pass only)" if d == SNPP_CUTOFF else "")
            for s, o0, o1, why in OUTAGES:
                if s == sat and o0 <= d <= o1:
                    op, note = False, why
            rows.append((d, sat, op, note))
    return pd.DataFrame(rows, columns=["date", "sat", "operating", "note"])


def drop_non_operating(grid: pd.DataFrame, sd: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    ok = sd[sd["operating"]][["date", "sat"]]
    kept = grid.merge(ok, on=["date", "sat"], how="inner")
    return kept, len(grid) - len(kept)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", default="data/processed/grid_daily.parquet")
    ap.add_argument("--out", default="data/processed/sensor_days.parquet")
    a = ap.parse_args(argv)
    g = pd.read_parquet(a.grid)
    g["date"] = pd.to_datetime(g["date"]).dt.date
    sd = sensor_days(g)
    write(sd, a.out, SCHEMA)
    _, skipped = drop_non_operating(g, sd)
    print(f"sensor_days: {len(sd)} rows -> {a.out}; {skipped} grid rows fall on non-operating days (consumers skip them)")
    print(sd.groupby("sat").agg(first=("date", "min"), last=("date", "max"), operating_days=("operating", "sum")).to_string())


if __name__ == "__main__":
    main()
