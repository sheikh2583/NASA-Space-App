"""Coverage audit for improvement I8. READ-ONLY: writes reports under data/interim/coverage_audit/ and changes no
pipeline output. Spec and the decisions it feeds: docs/specs/I8_COVERAGE.md.

Three questions, answered per demo region (BD, PB), local solar day (decision 23) and pass (D = day, N = night):
  1. Which (region, day, pass) does each registry outage overlap?  Outages are UTC intervals (common/outages.yaml);
     a pass is the span of local solar times at which that satellite's detections occur over the region, measured
     from the detections themselves (defaults when there are too few). The answer is an overlap fraction 0-1.
  2. Does our archive agree?  A pass fully inside an outage that still has detections is a contradiction: the
     registry entry or the pass window is wrong. (No detections proves nothing: there may simply be no fire.)
  3. Which days look like unrecorded gaps?  sensor_days calls a satellite operating every day between its first and
     last data, so internal gaps are invisible. A candidate gap is a region-day-pass with zero detections from the
     satellite while a reference satellite saw at least --min-ref. Candidates are for a person to check, not outages.

It also reports how many (date, sat) rows of the current sensor_days would change at several overlap thresholds,
so the partial-day policy can be chosen from measured counts.

Usage: python -m ws2_platform.coverage [--processed data/processed] [--registry common/outages.yaml]
                                       [--out data/interim/coverage_audit] [--min-ref 10]
"""
from __future__ import annotations

import argparse
import datetime as dt
import os

import numpy as np
import pandas as pd
import yaml

from common.grid import cell_id, local_solar_date
from common.regions import SATS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "common", "outages.yaml")
VERIFICATION = ("documented", "table_and_data", "transcribed", "rejected")
REQUIRED = ("id", "sat", "start_utc", "end_utc", "source", "products", "verification")
PASSES = ("D", "N")
# Local solar hours used when a (sat, region, pass) has too few detections. N wraps midnight (start > end).
DEFAULT_WINDOWS = {"D": (11.5, 15.5), "N": (23.5, 3.5)}
THRESHOLDS = (0.0, 0.25, 0.5, 1.0)
HOUR = pd.Timedelta(hours=1)


# ---------------------------------------------------------------- registry
def load_registry(path: str = REGISTRY) -> pd.DataFrame:
    """Validated registry: one row per event, start/end as naive UTC timestamps (end exclusive)."""
    with open(path, encoding="utf-8") as f:
        events = (yaml.safe_load(f) or {}).get("events") or []
    rows, errors = [], []
    for i, e in enumerate(events):
        name = e.get("id", f"#{i}")
        missing = [k for k in REQUIRED if not e.get(k)]
        if missing:
            errors.append(f"{name}: missing {', '.join(missing)}")
            continue
        if e["sat"] not in SATS:
            errors.append(f"{name}: unknown sat {e['sat']!r}")
        if e["verification"] not in VERIFICATION:
            errors.append(f"{name}: verification must be one of {VERIFICATION}")
        if e["verification"] != "documented" and not e.get("source_url"):
            errors.append(f"{name}: source_url required unless verification is 'documented'")
        try:
            s, t = (pd.Timestamp(e[k]) for k in ("start_utc", "end_utc"))
        except (ValueError, TypeError):
            errors.append(f"{name}: unreadable time")
            continue
        if s.tzinfo is None or t.tzinfo is None or s.utcoffset() != dt.timedelta(0) or t.utcoffset() != dt.timedelta(0):
            errors.append(f"{name}: times must be UTC with a trailing Z")
            continue
        if t <= s:
            errors.append(f"{name}: end_utc must be after start_utc")
        rows.append({**e, "start": s.tz_convert(None), "end": t.tz_convert(None)})
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        errors.append("duplicate ids")
    if errors:
        raise ValueError("outage registry: " + "; ".join(errors))
    cols = ["id", "sat", "start", "end", "source", "source_url", "products", "verification", "note"]
    return pd.DataFrame(rows).reindex(columns=cols)


def merge_events(reg: pd.DataFrame) -> pd.DataFrame:
    """Union of overlapping intervals per satellite (so overlap fractions can be summed); ids joined with '+'.
    Rejected entries are dropped."""
    out = []
    for sat, g in reg[reg["verification"] != "rejected"].sort_values("start").groupby("sat"):
        cur = None
        for r in g.itertuples():
            if cur and r.start <= cur["end"]:
                cur["end"] = max(cur["end"], r.end)
                cur["id"] += "+" + r.id
                cur["verification"] = _weakest(cur["verification"], r.verification)
            else:
                if cur:
                    out.append(cur)
                cur = {"sat": sat, "id": r.id, "start": r.start, "end": r.end, "verification": r.verification}
        out.append(cur)
    return pd.DataFrame(out, columns=["sat", "id", "start", "end", "verification"])


def _weakest(a: str, b: str) -> str:
    order = {"transcribed": 0, "table_and_data": 1, "documented": 2}
    return a if order.get(a, 0) <= order.get(b, 0) else b


# ---------------------------------------------------------------- pass windows
def local_hours(acq_time, lon) -> np.ndarray:
    t = np.asarray(acq_time, dtype="int64")
    return ((t // 100) + (t % 100) / 60.0 + np.asarray(lon, dtype="float64") / 15.0) % 24.0


def pass_windows(det: pd.DataFrame, min_n: int = 50, q: tuple[float, float] = (0.005, 0.995)) -> pd.DataFrame:
    """Local solar hour span (start, end) of each (sat, region, pass) from detections with columns
    sat, region, daynight, acq_time, lon. A night span crossing midnight has start > end."""
    rows = []
    h = local_hours(det["acq_time"], det["lon"]) if len(det) else np.array([])
    d = det.assign(h=h)
    for (sat, region), g in d.groupby(["sat", "region"]):
        for p in PASSES:
            x = g.loc[g["daynight"] == p, "h"].to_numpy()
            if len(x) < min_n:
                a, b = DEFAULT_WINDOWS[p]
                rows.append((sat, region, p, a, b, len(x), "default"))
                continue
            if p == "N":  # centre on midnight so the span does not split
                y = (x + 12.0) % 24.0
                a, b = ((np.quantile(y, q[0]) - 12.0) % 24.0, (np.quantile(y, q[1]) - 12.0) % 24.0)
            else:
                a, b = np.quantile(x, q[0]), np.quantile(x, q[1])
            rows.append((sat, region, p, float(a), float(b), len(x), "measured"))
    return pd.DataFrame(rows, columns=["sat", "region", "pass", "start_h", "end_h", "n", "basis"])


def _segments(a: float, b: float) -> list[tuple[float, float]]:
    return [(a, b)] if a <= b else [(a, 24.0), (0.0, b)]


def utc_segments(local_date, a: float, b: float, lon_min: float, lon_max: float) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """UTC intervals in which a pass of local solar date `local_date` can occur anywhere in [lon_min, lon_max]."""
    day = pd.Timestamp(local_date)
    return [(day + (s - lon_max / 15.0) * HOUR, day + (e - lon_min / 15.0) * HOUR) for s, e in _segments(a, b)]


def _window(win: pd.DataFrame | None, sat: str, region: str, p: str) -> tuple[float, float]:
    if win is not None and len(win):
        m = win[(win["sat"] == sat) & (win["region"] == region) & (win["pass"] == p)]
        if len(m):
            return float(m.iloc[0]["start_h"]), float(m.iloc[0]["end_h"])
    return DEFAULT_WINDOWS[p]


# ---------------------------------------------------------------- 1. registry -> affected passes
def affected_passes(reg: pd.DataFrame, extents: dict[str, tuple[float, float]], win: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per (event, region, local date, pass) with overlap_frac > 0.
    extents: region -> (lon_min, lon_max)."""
    rows = []
    for ev in merge_events(reg).itertuples():
        for region, (lo, hi) in extents.items():
            d0 = (ev.start + (lo / 15.0 - 1) * HOUR).normalize()
            d1 = (ev.end + (hi / 15.0 + 1) * HOUR).normalize()
            for day in pd.date_range(d0, d1, freq="D"):
                for p in PASSES:
                    a, b = _window(win, ev.sat, region, p)
                    segs = utc_segments(day, a, b, lo, hi)
                    total = sum((e - s) / HOUR for s, e in segs)
                    ov = sum(max(0.0, (min(e, ev.end) - max(s, ev.start)) / HOUR) for s, e in segs)
                    if ov > 0:
                        rows.append((ev.sat, ev.id, ev.verification, region, day.date(), p, round(min(1.0, ov / total), 4)))
    return pd.DataFrame(rows, columns=["sat", "event_id", "verification", "region", "date", "pass", "overlap_frac"])


def day_table(aff: pd.DataFrame) -> pd.DataFrame:
    """Per (sat, region, date): overlap_D, overlap_N (0-1; events are merged so sums are exact), event ids."""
    if aff.empty:
        return pd.DataFrame(columns=["sat", "region", "date", "overlap_D", "overlap_N", "event_ids", "verification"])
    t = aff.pivot_table(index=["sat", "region", "date"], columns="pass", values="overlap_frac", aggfunc="sum", fill_value=0.0)
    t = t.reindex(columns=list(PASSES), fill_value=0.0).clip(upper=1.0).add_prefix("overlap_").reset_index()
    t.columns.name = None
    meta = aff.groupby(["sat", "region", "date"]).agg(
        event_ids=("event_id", lambda s: ";".join(sorted(set(s)))),
        verification=("verification", lambda s: ";".join(sorted(set(s))))).reset_index()
    return t.merge(meta, on=["sat", "region", "date"])


def excluded(days: pd.DataFrame, threshold: float) -> pd.Series:
    """Policy under test: a (sat, region, day) is excluded when any pass overlap exceeds `threshold`
    (threshold 0 = any overlap; 1.0 = only a fully covered pass)."""
    m = days[["overlap_D", "overlap_N"]].max(axis=1)
    return m >= threshold if threshold >= 1.0 else m > threshold


# ---------------------------------------------------------------- 2. contradictions
def pass_counts(det: pd.DataFrame) -> pd.DataFrame:
    """Detections per (sat, region, local date, pass)."""
    d = det.assign(date=local_solar_date(det["acq_date"].values, det["acq_time"].values, det["lon"].values).values)
    return d.groupby(["sat", "region", "date", "daynight"]).size().rename("n").reset_index().rename(columns={"daynight": "pass"})


def contradictions(days: pd.DataFrame, counts: pd.DataFrame) -> pd.DataFrame:
    """Fully covered passes (overlap 1.0) that still have detections from that satellite."""
    long = days.melt(id_vars=["sat", "region", "date", "event_ids"], value_vars=["overlap_D", "overlap_N"],
                     var_name="pass", value_name="overlap_frac")
    long["pass"] = long["pass"].str[-1]
    full = long[long["overlap_frac"] >= 1.0]
    out = full.merge(counts, on=["sat", "region", "date", "pass"], how="inner")
    return out[out["n"] > 0].sort_values(["sat", "region", "date", "pass"]).reset_index(drop=True)


# ---------------------------------------------------------------- 3. candidate gaps
def region_day_counts(grid: pd.DataFrame, cells: pd.DataFrame) -> pd.DataFrame:
    """Day and night detections per (region, date, sat) from grid_daily; cells.country is the demo region code."""
    g = grid.merge(cells[["cell_id", "country"]], on="cell_id", how="inner").rename(columns={"country": "region"})
    return g.groupby(["region", "date", "sat"])[["n_day", "n_night"]].sum().reset_index()


def candidate_gaps(counts: pd.DataFrame, sd: pd.DataFrame, sat: str = "SNPP", refs=("NOAA20", "Aqua", "Terra"),
                   min_ref: int = 10) -> pd.DataFrame:
    """Region-day-passes where `sat` was marked operating, saw nothing, and the first operating reference satellite
    saw at least min_ref detections in the same pass. Day pass of VIIRS vs MODIS are hours apart; treat as a hint."""
    sd = sd.copy()
    sd["date"] = pd.to_datetime(sd["date"]).dt.date
    op = {s: set(sd.loc[(sd["sat"] == s) & sd["operating"], "date"]) for s in (sat, *refs)}
    regions = sorted(counts["region"].unique())
    days = sorted(op[sat])
    if not days or not regions:
        return pd.DataFrame(columns=["region", "date", "pass", "sat", "ref_sat", "ref_n"])
    idx = pd.MultiIndex.from_product([regions, days], names=["region", "date"])
    wide = {s: counts[counts["sat"] == s].set_index(["region", "date"])[["n_day", "n_night"]].reindex(idx, fill_value=0)
            for s in (sat, *refs)}
    rows = []
    for col, p in (("n_day", "D"), ("n_night", "N")):
        zero = wide[sat][col] == 0
        for region, day in zero[zero].index:
            for ref in refs:
                if day in op[ref]:
                    n = int(wide[ref].at[(region, day), col])
                    if n >= min_ref:
                        rows.append((region, day, p, sat, ref, n))
                    break
    return pd.DataFrame(rows, columns=["region", "date", "pass", "sat", "ref_sat", "ref_n"])


# ---------------------------------------------------------------- what the current sensor_days would lose
def would_flip(days: pd.DataFrame, sd: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """(date, sat) rows that are operating in sensor_days but excluded in at least one region under `threshold`.
    sensor_days has no region key, so the proposal (spec option A) excludes a day if any demo region is affected."""
    sd = sd.copy()
    sd["date"] = pd.to_datetime(sd["date"]).dt.date
    ex = days[excluded(days, threshold)]
    if ex.empty:
        return pd.DataFrame(columns=["date", "sat", "regions", "event_ids"])
    ex = ex.groupby(["date", "sat"]).agg(regions=("region", lambda s: ";".join(sorted(set(s)))),
                                         event_ids=("event_ids", lambda s: ";".join(sorted(set(";".join(s).split(";")))))).reset_index()
    on = sd[sd["operating"]][["date", "sat"]]
    return ex.merge(on, on=["date", "sat"], how="inner").sort_values(["sat", "date"]).reset_index(drop=True)


# ---------------------------------------------------------------- CLI
def _extents(cells: pd.DataFrame) -> dict[str, tuple[float, float]]:
    g = cells.groupby("country")["lon_c"].agg(["min", "max"])
    return {r: (float(a) - 0.05, float(b) + 0.05) for r, (a, b) in g.iterrows()}


def audit(processed: str, registry: str, out: str, min_ref: int = 10) -> dict:
    reg = load_registry(registry)
    cells = pd.read_parquet(f"{processed}/cells.parquet", columns=["cell_id", "lon_c", "country"])
    det = pd.read_parquet(f"{processed}/detections.parquet", columns=["sat", "acq_date", "acq_time", "lat", "lon", "daynight"])
    det = det.assign(cell_id=cell_id(det["lat"].values, det["lon"].values))
    det = det.merge(cells[["cell_id", "country"]], on="cell_id", how="inner").rename(columns={"country": "region"})
    grid = pd.read_parquet(f"{processed}/grid_daily.parquet", columns=["cell_id", "date", "sat", "n_day", "n_night"])
    grid["date"] = pd.to_datetime(grid["date"]).dt.date
    sd = pd.read_parquet(f"{processed}/sensor_days.parquet")

    win = pass_windows(det)
    days = day_table(affected_passes(reg, _extents(cells), win))
    contra = contradictions(days, pass_counts(det)) if len(days) else pd.DataFrame()
    gaps = candidate_gaps(region_day_counts(grid, cells), sd, min_ref=min_ref)
    if len(gaps) and len(days):
        key = set(zip(days["region"], days["date"]))
        gaps["in_registry"] = [(r, d) in key for r, d in zip(gaps["region"], gaps["date"])]
    flips = {t: would_flip(days, sd, t) for t in THRESHOLDS}

    os.makedirs(out, exist_ok=True)
    win.to_csv(f"{out}/pass_windows.csv", index=False)
    days.to_csv(f"{out}/affected_days.csv", index=False)
    contra.to_csv(f"{out}/contradictions.csv", index=False)
    gaps.to_csv(f"{out}/candidate_gaps.csv", index=False)
    for t, f in flips.items():
        f.to_csv(f"{out}/would_flip_{t:g}.csv", index=False)
    summary = {
        "registry_events": int(len(reg)),
        "registry_unchecked": int((reg["verification"] == "transcribed").sum()),
        "affected_region_days": int(len(days)),
        "contradictions": int(len(contra)),
        "candidate_gaps": int(len(gaps)),
        "candidate_gaps_not_in_registry": int((~gaps["in_registry"]).sum()) if "in_registry" in gaps else int(len(gaps)),
        "would_flip_sensor_days": {f"{t:g}": int(len(f)) for t, f in flips.items()},
        "pass_windows_measured": int((win["basis"] == "measured").sum()),
    }
    with open(f"{out}/summary.md", "w", encoding="utf-8") as f:
        f.write("# Coverage audit (read-only)\n\n")
        for k, v in summary.items():
            f.write(f"- {k}: {v}\n")
        f.write("\nNothing in data/processed was changed. See docs/specs/I8_COVERAGE.md for how to read these files.\n")
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read-only coverage audit (I8)")
    ap.add_argument("--processed", default="data/processed")
    ap.add_argument("--registry", default=REGISTRY)
    ap.add_argument("--out", default="data/interim/coverage_audit")
    ap.add_argument("--min-ref", type=int, default=10)
    a = ap.parse_args(argv)
    s = audit(a.processed, a.registry, a.out, a.min_ref)
    for k, v in s.items():
        print(f"{k}: {v}")
    print(f"reports -> {a.out}")


if __name__ == "__main__":
    main()
