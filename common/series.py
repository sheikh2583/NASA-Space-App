"""AOI time series from the harmonized cell-day table (decisions 1, 17, 18, 20, 21).

harmonized.parquet is sparse: a missing (cell_id, date) row is zero on days a sensor was operating.
Which sensor applies on a day comes from sensor_days, so empty days still get the right source, and
days with no operating sensor are NaN, never zero.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common.intervals import apply_interval
from common.regions import SNPP_CUTOFF

OBSERVED = "observed_viirs"
ADJUSTED = "adjusted_from_noaa20"
MODELED = "modeled_from_modis"


def season_label(month: int) -> str:
    """Quarter-of-year label used for interval strata (q1 = Jan-Mar)."""
    return f"q{(int(month) - 1) // 3 + 1}"


def day_sources(sensor_days: pd.DataFrame, start, end) -> pd.Series:
    """Source of each day in [start, end]: observed SNPP; adjusted NOAA-20 after the cutoff or on an SNPP outage day
    when NOAA-20 operates (decision 24); modeled MODIS; or None."""
    days = pd.date_range(start, end, freq="D")
    op = sensor_days[sensor_days["operating"]].copy()
    op["date"] = pd.to_datetime(op["date"])
    have = op.groupby("sat")["date"].apply(set).to_dict()
    snpp, n20 = have.get("SNPP", set()), have.get("NOAA20", set())
    modis = have.get("Terra", set()) | have.get("Aqua", set())
    out = []
    for d in days:
        if d in snpp:
            out.append(OBSERVED)
        elif d in n20:                 # after the SNPP cutoff, or an SNPP outage day while NOAA-20 operates
            out.append(ADJUSTED)
        elif d in modis:
            out.append(MODELED)
        else:
            out.append(None)
    return pd.Series(out, index=days, name="source")


def select_cells(cells: pd.DataFrame, region_ids=None, bbox=None, cell_ids=None) -> pd.DataFrame:
    sel = cells
    if cell_ids is not None:
        sel = sel[sel["cell_id"].isin(np.asarray(cell_ids))]
    if region_ids is not None:
        sel = sel[sel["admin1_id"].isin(list(region_ids))]
    if bbox is not None:
        x0, y0, x1, y1 = bbox
        sel = sel[(sel["lon_c"] >= x0) & (sel["lon_c"] <= x1) & (sel["lat_c"] >= y0) & (sel["lat_c"] <= y1)]
    return sel


def _period_start(idx: pd.DatetimeIndex, res: str) -> pd.DatetimeIndex:
    if res == "day":
        return idx
    if res == "week":
        return idx - pd.to_timedelta(idx.dayofweek, unit="D")
    if res == "month":
        return idx.to_period("M").start_time
    raise ValueError(f"res must be day, week or month, not {res!r}")


def weekly_series(harmonized: pd.DataFrame, cells: pd.DataFrame, region_ids=None, bbox=None, res: str = "week",
                  *, cell_ids=None, start=None, end=None, sensor_days: pd.DataFrame | None = None,
                  table: dict | None = None, source_calendar: pd.Series | None = None) -> pd.DataFrame:
    """Aggregate cell-day values to an AOI series.

    Returns columns week_start, value, lo, hi, modeled_share, source, drift_flag (week_start is the period start
    for any res). lo/hi are NaN when no interval table is given or res == 'day'. Observed SNPP days contribute
    to lo and hi unchanged (decision 21); the interval is applied to the adjusted and modeled part.
    source_calendar may supply the sensor_days-derived daily sources once per immutable Store.
    """
    sel = select_cells(cells, region_ids, bbox, cell_ids)
    h = harmonized[harmonized["cell_id"].isin(sel["cell_id"])].copy()
    h["date"] = pd.to_datetime(h["date"])
    if start is None:
        start = h["date"].min() if len(h) else pd.Timestamp("2012-01-01")
    if end is None:
        end = h["date"].max() if len(h) else pd.Timestamp("2012-01-01")
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    h = h[(h["date"] >= start) & (h["date"] <= end)]
    days = pd.date_range(start, end, freq="D")
    if source_calendar is not None:
        src = source_calendar.reindex(days)
    elif sensor_days is not None:
        src = day_sources(sensor_days, start, end)
    else:
        src = pd.Series(np.where(days.date < np.datetime64("2012-01-20"), MODELED, OBSERVED), index=days)
    if "drift_flag" not in h:
        h["drift_flag"] = False
    daily = h.groupby("date").agg(value=("value_count", "sum"), drift=("drift_flag", "max"))
    daily = daily.reindex(days)
    daily["value"] = daily["value"].fillna(0.0)
    daily["drift"] = daily["drift"].astype("boolean").fillna(False).astype(bool)
    daily["source"] = src.values
    daily.loc[daily["source"].isna(), "value"] = np.nan
    daily["nonobs"] = np.where(daily["source"] == OBSERVED, 0.0, daily["value"])
    daily["nonobs_day"] = (daily["source"] != OBSERVED) & daily["source"].notna()
    daily["period"] = _period_start(days, res)
    g = daily.groupby("period")
    out = pd.DataFrame({
        "value": g["value"].sum(min_count=1),
        "nonobs": g["nonobs"].sum(min_count=1),
        "n_days": g["source"].count(),
        "n_nonobs_days": g["nonobs_day"].sum(),
        "drift_flag": g["drift"].max().astype(bool),
    })
    # Sorted source columns replace per-period set/list callbacks with presence reductions.
    sources = pd.get_dummies(daily["source"], dtype=bool).groupby(daily["period"]).any()
    n_sources = sources.sum(axis=1)
    out["source"] = None
    single = n_sources == 1
    if single.any():
        out.loc[single, "source"] = sources.loc[single].idxmax(axis=1)
    out.loc[n_sources > 1, "source"] = "mixed"
    with np.errstate(invalid="ignore", divide="ignore"):
        share = np.where(out["value"] > 0, out["nonobs"] / out["value"], out["n_nonobs_days"] / out["n_days"].clip(lower=1))
    out["modeled_share"] = np.clip(np.nan_to_num(share, nan=0.0), 0, 1)
    out["lo"], out["hi"] = np.nan, np.nan
    if table is not None and res != "day" and len(sel):
        adm = sel["admin1_id"].mode().iloc[0] if "admin1_id" in sel else None
        lc = sel["landcover_dom"].mode().iloc[0] if "landcover_dom" in sel and sel["landcover_dom"].notna().any() else None
        los, his = [], []
        for t, row in out.iterrows():
            if np.isnan(row["value"]):
                los.append(np.nan); his.append(np.nan); continue
            obs = row["value"] - row["nonobs"]
            if row["n_nonobs_days"] == 0:  # fully observed: no interval (decision 21)
                los.append(row["value"]); his.append(row["value"]); continue
            strata = [f"landcover:{lc}|season:{season_label(t.month)}", f"region:{adm}|month:{t.month}"]
            lo, hi = apply_interval(float(row["nonobs"]), res, strata, table)
            los.append(obs + (lo if lo is not None else row["nonobs"]))
            his.append(obs + (hi if hi is not None else row["nonobs"]))
        out["lo"], out["hi"] = los, his
    out = out.reset_index().rename(columns={"period": "week_start"})
    return out[["week_start", "value", "lo", "hi", "modeled_share", "source", "drift_flag"]]
