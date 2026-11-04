"""sensor_days.parquet: which satellite was operating on which local solar day (decision 18).

A satellite operates from its first to its last day of data (bounded by common.regions.WINDOWS), minus known
outage windows: common.regions.OUTAGES, and the verified registry outages in common/outages.yaml that cover more
than the decided share of a pass window in any demo region (decision 24; coverage_days.parquet records the overlaps). The SNPP cutoff day (2 Nov 2026) is marked not operating: only its day pass exists, so the
day would be undercounted. grid_daily keeps every detection (so sum(n_det) = detections); consumers skip
non-operating days with drop_non_operating().

Usage: python -m ws2_platform.sensors [--grid data/processed/grid_daily.parquet] [--out data/processed/sensor_days.parquet]
             [--registry common/outages.yaml] [--threshold 0.25] [--coverage-out data/processed/coverage_days.parquet]
"""
from __future__ import annotations

import argparse
import datetime as dt
import os

import pandas as pd
import pyarrow as pa

from common.regions import OUTAGES, SATS, SNPP_CUTOFF, WINDOWS
from ws2_platform.grid import write

SCHEMA = pa.schema([("date", pa.date32()), ("sat", pa.string()), ("operating", pa.bool_()), ("note", pa.string())])


THRESHOLD = 0.25          # decision 24: exclude a day when an outage covers more than a quarter of a pass window
UNVERIFIED = ("transcribed", "rejected")


def _registry_outages(coverage_days: pd.DataFrame | None, threshold: float) -> dict:
    """(date, sat) -> note, for verified registry outages excluded in any region at this threshold."""
    if coverage_days is None or coverage_days.empty:
        return {}
    from ws2_platform.coverage import excluded
    cd = coverage_days[~coverage_days["verification"].fillna("").str.contains("|".join(UNVERIFIED))]
    if cd.empty:
        return {}
    cd = cd[excluded(cd, threshold).values]
    out = {}
    for (d, sat), g in cd.groupby([pd.to_datetime(cd["date"]).dt.date, "sat"]):
        ids = ";".join(sorted({i for s in g["event_ids"] for i in str(s).split(";") if i}))
        ver = ";".join(sorted({v for s in g["verification"] for v in str(s).split(";") if v}))
        out[(d, sat)] = f"outage: {ids} ({ver})"
    return out


def sensor_days(grid: pd.DataFrame, end: dt.date | None = None, coverage_days: pd.DataFrame | None = None,
                threshold: float = THRESHOLD) -> pd.DataFrame:
    first_seen = grid.groupby("sat")["date"].min().to_dict()
    last_seen = grid.groupby("sat")["date"].max().to_dict()
    end = end or max(last_seen.values())
    start = min(WINDOWS[s][0] for s in SATS)
    days = pd.date_range(start, end, freq="D").date
    registry = _registry_outages(coverage_days, threshold)
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
            if op and (d, sat) in registry:
                op, note = False, registry[(d, sat)]
            rows.append((d, sat, op, note))
    return pd.DataFrame(rows, columns=["date", "sat", "operating", "note"])


def coverage_table(processed: str, registry: str) -> pd.DataFrame:
    """Per (sat, region, local date): the share of each pass window that registry outages cover (coverage_days)."""
    from common.grid import cell_id
    from ws2_platform.coverage import _extents, affected_passes, day_table, load_registry, pass_windows
    cells = pd.read_parquet(f"{processed}/cells.parquet", columns=["cell_id", "lon_c", "country"])
    det = pd.read_parquet(f"{processed}/detections.parquet", columns=["sat", "acq_date", "acq_time", "lat", "lon", "daynight"])
    det = det.assign(cell_id=cell_id(det["lat"].values, det["lon"].values))
    det = det.merge(cells[["cell_id", "country"]], on="cell_id", how="inner").rename(columns={"country": "region"})
    days = day_table(affected_passes(load_registry(registry), _extents(cells), pass_windows(det)))
    days["date"] = pd.to_datetime(days["date"]).dt.date
    return days.astype({"overlap_D": "float32", "overlap_N": "float32"})


def drop_non_operating(grid: pd.DataFrame, sd: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    ok = sd[sd["operating"]][["date", "sat"]]
    kept = grid.merge(ok, on=["date", "sat"], how="inner")
    return kept, len(grid) - len(kept)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", default="data/processed/grid_daily.parquet")
    ap.add_argument("--out", default="data/processed/sensor_days.parquet")
    ap.add_argument("--registry", default="common/outages.yaml")
    ap.add_argument("--threshold", type=float, default=THRESHOLD)
    ap.add_argument("--coverage-out", default="data/processed/coverage_days.parquet")
    a = ap.parse_args(argv)
    g = pd.read_parquet(a.grid)
    g["date"] = pd.to_datetime(g["date"]).dt.date
    from tools.verify_files import write_parquet_contract   # pipeline-only; the API image has no tools/
    cov = coverage_table(os.path.dirname(a.grid) or ".", a.registry)
    write_parquet_contract(cov, a.coverage_out, "coverage_days")
    print(f"coverage_days: {len(cov)} rows -> {a.coverage_out}")
    sd = sensor_days(g, coverage_days=cov, threshold=a.threshold)
    write(sd, a.out, SCHEMA)
    _, skipped = drop_non_operating(g, sd)
    print(f"sensor_days: {len(sd)} rows -> {a.out}; {skipped} grid rows fall on non-operating days (consumers skip them)")
    print(sd.groupby("sat").agg(first=("date", "min"), last=("date", "max"), operating_days=("operating", "sum")).to_string())


if __name__ == "__main__":
    main()
