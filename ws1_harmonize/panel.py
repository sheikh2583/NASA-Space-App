"""Weekly cell panel: per satellite counts side by side for every cell that ever had a detection.

The learned model and the baselines work at cell-week level (daily cell counts are too sparse and noisy);
write_harmonized splits weekly estimates back into days. Only days on which a satellite was operating
(sensor_days) count; *_days columns say how many operating days each satellite had in the week, so
partial weeks can be excluded from fitting.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common.regions import AQUA_START
from ws2_platform.sensors import drop_non_operating

SAT_PREFIX = {"Terra": "terra", "Aqua": "aqua", "SNPP": "snpp", "NOAA20": "n20"}
VALUE_COLS = ["n_det", "n_hiconf", "frp_sum", "frp_max", "n_day", "n_night", "mean_scan"]


def week_start(dates) -> pd.Series:
    d = pd.to_datetime(pd.Series(dates))
    return (d - pd.to_timedelta(d.dt.dayofweek, unit="D")).dt.normalize()


def build_panel(grid: pd.DataFrame, cells: pd.DataFrame, sensor_days: pd.DataFrame, start=None, end=None) -> pd.DataFrame:
    g = grid[grid["sat"].isin(SAT_PREFIX)].copy()
    # cells.parquet defines the actual administrative AOI. Country downloads
    # and their broad request boxes can contain detections from neighbouring
    # states or offshore cells, which must not enter model training.
    g = g[g["cell_id"].isin(cells["cell_id"])]
    g["date"] = pd.to_datetime(g["date"]).dt.date
    sd = sensor_days.copy()
    sd["date"] = pd.to_datetime(sd["date"]).dt.date
    g, _ = drop_non_operating(g, sd)
    g["week_start"] = week_start(g["date"]).values
    g["scan_x"] = g["mean_scan"].astype("float64") * g["n_det"]
    agg = g.groupby(["cell_id", "week_start", "sat"]).agg(
        n=("n_det", "sum"), hi=("n_hiconf", "sum"), frp=("frp_sum", "sum"), frp_max=("frp_max", "max"),
        n_day=("n_day", "sum"), n_night=("n_night", "sum"), scan_x=("scan_x", "sum")).reset_index()
    agg["scan_w"] = agg["scan_x"] / agg["n"]
    agg = agg.drop(columns="scan_x")
    wide = agg.pivot_table(index=["cell_id", "week_start"], columns="sat",
                           values=["n", "hi", "frp", "frp_max", "n_day", "n_night", "scan_w"])
    wide.columns = [f"{SAT_PREFIX[s]}_{v}" for v, s in wide.columns]
    wide = wide.reset_index()

    ops = sd[sd["operating"] & sd["sat"].isin(SAT_PREFIX)].copy()
    ops["week_start"] = week_start(ops["date"]).values
    days = ops.groupby(["week_start", "sat"]).size().unstack(fill_value=0)
    days.columns = [f"{SAT_PREFIX[s]}_days" for s in days.columns]
    days = days.reset_index()
    if start is not None:
        days = days[days["week_start"] >= pd.Timestamp(start)]
    if end is not None:
        days = days[days["week_start"] <= pd.Timestamp(end)]

    active = np.sort(g["cell_id"].unique())
    idx = pd.MultiIndex.from_product([active, days["week_start"]], names=["cell_id", "week_start"]).to_frame(index=False)
    p = idx.merge(days, on="week_start", how="left").merge(wide, on=["cell_id", "week_start"], how="left")
    for sat in SAT_PREFIX.values():
        for v in ("n", "hi", "frp", "frp_max", "n_day", "n_night"):
            col = f"{sat}_{v}"
            p[col] = p[col].fillna(0.0).astype("float32") if col in p else np.float32(0)
        if f"{sat}_scan_w" not in p:
            p[f"{sat}_scan_w"] = np.nan
        if f"{sat}_days" not in p:
            p[f"{sat}_days"] = 0
    p["modis_n"] = p["terra_n"] + p["aqua_n"]
    p["sat_combo"] = np.where(p["week_start"] < pd.Timestamp(AQUA_START), "terra_only", "terra_aqua")
    p = p.merge(cells[["cell_id", "lat_c", "lon_c", "admin1_id", "landcover_dom", "cropland_frac", "forest_frac"]],
                on="cell_id", how="left")
    return p
