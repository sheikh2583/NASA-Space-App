"""Assemble harmonized.parquet (v0 = B1, v1 = LightGBM) with the value rule of decisions 1, 17, 18, 21.

value_count per cell-day:
  observed SNPP count on SNPP operating days (source observed_viirs, lo = hi = value);
  NOAA-20 count x NOAA-20->SNPP ratio after the SNPP cutoff (adjusted_from_noaa20);
  else the MODIS-based estimate (modeled_from_modis).
Weekly estimates are split into days in proportion to MODIS daily counts; a week with no MODIS detection
books its (small) estimate on the Monday. The table is sparse: a missing row is zero on a day with an
operating sensor. Rows with no operating sensor never appear (common.series turns those days into NaN).
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from common.intervals import apply_interval_many
from common.series import ADJUSTED, MODELED, OBSERVED, day_sources
from ws1_harmonize.panel import week_start
from ws2_platform.sensors import drop_non_operating

SCHEMA = pa.schema([("cell_id", pa.int32()), ("date", pa.date32()), ("value_count", pa.float32()), ("value_frp", pa.float32()),
                    ("modeled_count", pa.float32()), ("lo_count", pa.float32()), ("hi_count", pa.float32()),
                    ("level", pa.float32()), ("source", pa.string()), ("drift_flag", pa.bool_()), ("method_version", pa.string())])


def disaggregate(panel: pd.DataFrame, pred_count, pred_frp, grid: pd.DataFrame) -> pd.DataFrame:
    """Weekly cell estimates -> daily rows (cell_id, date, modeled_count, modeled_frp)."""
    w = panel[["cell_id", "week_start", "sat_combo"]].assign(pc=pred_count, pf=pred_frp)
    w = w[(w["pc"] > 0) | (w["pf"] > 0)]
    m = grid[grid["sat"].isin(["Terra", "Aqua"])].copy()
    m["week_start"] = week_start(m["date"]).values
    m = m.merge(w[["cell_id", "week_start", "sat_combo"]], on=["cell_id", "week_start"], how="inner")
    m = m[(m["sat"] == "Terra") | (m["sat_combo"] == "terra_aqua")]
    daily = m.groupby(["cell_id", "week_start", "date"])["n_det"].sum().rename("md").reset_index()
    tot = daily.groupby(["cell_id", "week_start"])["md"].transform("sum")
    daily = daily.merge(w, on=["cell_id", "week_start"])
    daily["modeled_count"] = daily["pc"] * daily["md"] / tot
    daily["modeled_frp"] = daily["pf"] * daily["md"] / tot
    seen = daily[["cell_id", "week_start"]].drop_duplicates().assign(_seen=True)
    rest = w.merge(seen, on=["cell_id", "week_start"], how="left")
    rest = rest[rest["_seen"].isna()]
    rest = rest.assign(date=rest["week_start"].dt.date, modeled_count=rest["pc"], modeled_frp=rest["pf"])
    out = pd.concat([daily[["cell_id", "date", "modeled_count", "modeled_frp"]],
                     rest[["cell_id", "date", "modeled_count", "modeled_frp"]]], ignore_index=True)
    out["date"] = pd.to_datetime(out["date"]).dt.date
    return out


def assemble(panel, pred_count, pred_frp, grid, cells, sensor_days, n20_ratio_fn, table, method_version,
             drift_flags: pd.DataFrame | None = None) -> pd.DataFrame:
    g = grid.copy()
    g["date"] = pd.to_datetime(g["date"]).dt.date
    sd = sensor_days.copy()
    sd["date"] = pd.to_datetime(sd["date"]).dt.date
    g, _ = drop_non_operating(g, sd)
    mod = disaggregate(panel, pred_count, pred_frp, g)
    obs = g[g["sat"] == "SNPP"][["cell_id", "date", "n_det", "frp_sum"]].rename(columns={"n_det": "snpp", "frp_sum": "snpp_frp"})
    n20 = g[g["sat"] == "NOAA20"][["cell_id", "date", "n_det", "frp_sum"]].rename(columns={"n_det": "n20", "frp_sum": "n20_frp"})
    h = mod.merge(obs, on=["cell_id", "date"], how="outer").merge(n20, on=["cell_id", "date"], how="outer").fillna(0)
    src = day_sources(sd, min(sd["date"]), max(sd["date"]))
    src.index = src.index.date
    h["source"] = h["date"].map(src)
    h = h[h["source"].notna()]
    h = h.merge(cells[["cell_id", "admin1_id", "landcover_dom"]], on="cell_id", how="left")
    month = pd.to_datetime(h["date"]).dt.month.values
    is_obs, is_adj = (h["source"] == OBSERVED).values, (h["source"] == ADJUSTED).values
    ratio = np.where(is_adj, n20_ratio_fn(h["admin1_id"].values, month), 1.0)
    h["value_count"] = np.where(is_obs, h["snpp"], np.where(is_adj, h["n20"] * ratio, h["modeled_count"]))
    h["value_frp"] = np.where(is_obs, h["snpp_frp"], np.where(is_adj, h["n20_frp"] * ratio, h["modeled_frp"]))
    # modeled_count beyond the modeled era is kept only where MODIS saw something or a value exists (keeps the table sparse)
    h = h[(h["value_count"] > 0) | (h["modeled_count"] > 0)]
    vals = h["value_count"].values.astype("float64")
    nonobs = ~(h["source"] == OBSERVED).values
    m2 = pd.to_datetime(h["date"]).dt.month.values
    strata = [(f"landcover:{lc}|season:q{(mth - 1) // 3 + 1}", f"region:{adm}|month:{mth}")
              for lc, adm, mth in zip(h["landcover_dom"].values, h["admin1_id"].values, m2)]
    l, u = apply_interval_many(vals, strata, "week", table)  # cell-level: indicative only, never summed
    h["lo_count"] = np.where(nonobs & ~np.isnan(l), l, vals)
    h["hi_count"] = np.where(nonobs & ~np.isnan(u), u, vals)
    h["level"] = float(table.get("level", 0.9))
    h["drift_flag"] = False
    if drift_flags is not None and len(drift_flags):
        df = drift_flags.assign(year=drift_flags["year"].astype(int))
        key = dict(zip(zip(df["region_id"], df["year"]), df["drift_flag"]))
        yrs = pd.to_datetime(h["date"]).dt.year.values
        h["drift_flag"] = [bool(key.get((a, y), False)) and s != OBSERVED for a, y, s in zip(h["admin1_id"], yrs, h["source"])]
    h["method_version"] = method_version
    out = h[[f.name for f in SCHEMA]].sort_values(["cell_id", "date"]).reset_index(drop=True)
    for c in ("value_count", "value_frp", "modeled_count", "lo_count", "hi_count", "level"):
        out[c] = out[c].astype("float32")
    out["cell_id"] = out["cell_id"].astype("int32")
    return out


def write(df: pd.DataFrame, path: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    pq.write_table(pa.Table.from_pandas(df, schema=SCHEMA, preserve_index=False), path + ".tmp")
    os.replace(path + ".tmp", path)
