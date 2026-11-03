"""Baselines B0 (one ratio) and B1 (ratio per admin1 x calendar month), fitted per MODIS satellite combination,
plus the NOAA-20 -> SNPP adjustment ratio used after the SNPP cutoff (decisions 17, 19).

All ratios use only full weeks on which every satellite involved operated all 7 days.
terra_only ratios are fitted on overlap weeks using Terra counts alone, so they apply to Nov 2000 - Jul 2002.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def modis_input(panel: pd.DataFrame, combo: str | pd.Series) -> np.ndarray:
    """MODIS count for the given combination: Terra alone, or Terra + Aqua."""
    combo = combo if isinstance(combo, pd.Series) else pd.Series(combo, index=panel.index)
    return np.where(combo == "terra_only", panel["terra_n"], panel["terra_n"] + panel["aqua_n"])


def overlap(panel: pd.DataFrame, need=("terra", "aqua", "snpp")) -> pd.Series:
    ok = pd.Series(True, index=panel.index)
    for s in need:
        ok &= panel[f"{s}_days"] == 7
    return ok


def _ratio(num, den, prior=None, k=20.0):
    """Shrunk ratio: (num + k * prior) / (den + k); falls back to prior for empty groups."""
    if prior is None:
        return num / den if den > 0 else np.nan
    return (num + k * prior) / (den + k)


def fit(panel: pd.DataFrame, target: str = "snpp_n") -> dict:
    """Returns {'b0': {combo: r}, 'b1': {combo: {(admin1, month): r}}, 'n20': {...}, 'b0_n20': r}."""
    ov = panel[overlap(panel)]
    out = {"b0": {}, "b1": {}, "b0_frp": {}}
    for combo in ("terra_only", "terra_aqua"):
        m = modis_input(ov, combo)
        r0 = _ratio(ov[target].sum(), m.sum())
        out["b0"][combo] = float(r0)
        mf = np.where(combo == "terra_only", ov["terra_frp"], ov["terra_frp"] + ov["aqua_frp"])
        out["b0_frp"][combo] = float(_ratio(ov["snpp_frp"].sum(), mf.sum()))
        t = ov.assign(_m=m, _month=ov["week_start"].dt.month).groupby(["admin1_id", "_month"])[[target, "_m"]].sum()
        out["b1"][combo] = {k: float(_ratio(v[target], v["_m"], r0)) for k, v in t.iterrows()}
    ov2 = panel[overlap(panel, ("snpp", "n20"))]
    b0n = _ratio(ov2["snpp_n"].sum(), ov2["n20_n"].sum())
    out["b0_n20"] = float(b0n)
    t = ov2.assign(_month=ov2["week_start"].dt.month).groupby(["admin1_id", "_month"])[["snpp_n", "n20_n"]].sum()
    out["n20"] = {k: float(_ratio(v["snpp_n"], v["n20_n"], b0n)) for k, v in t.iterrows()}
    out["n_overlap_weeks"] = int(ov["week_start"].nunique())
    out["n_n20_overlap_weeks"] = int(ov2["week_start"].nunique())
    return out


def predict_b0(params: dict, panel: pd.DataFrame) -> np.ndarray:
    r = panel["sat_combo"].map(params["b0"]).values
    return r * modis_input(panel, panel["sat_combo"])


def predict_b0_frp(params: dict, panel: pd.DataFrame) -> np.ndarray:
    r = panel["sat_combo"].map(params["b0_frp"]).values
    return r * np.where(panel["sat_combo"] == "terra_only", panel["terra_frp"], panel["terra_frp"] + panel["aqua_frp"])


def predict_b1(params: dict, panel: pd.DataFrame) -> np.ndarray:
    month = panel["week_start"].dt.month.values
    r = np.array([params["b1"][c].get((a, m), params["b0"][c]) for c, a, m in
                  zip(panel["sat_combo"].values, panel["admin1_id"].values, month)])
    return r * modis_input(panel, panel["sat_combo"])


def n20_ratio(params: dict, admin1, month) -> np.ndarray:
    return np.array([params["n20"].get((a, m), params["b0_n20"]) for a, m in zip(admin1, month)])


def ratio_quantiles(panel: pd.DataFrame, pred: np.ndarray, target="snpp_n", q=(0.05, 0.5, 0.95)) -> pd.DataFrame:
    """Quantiles of observed / predicted weekly region totals per admin1 x month (for interval_table v0)."""
    ov = panel[overlap(panel)].assign(_p=pred[overlap(panel).values])
    w = ov.groupby(["admin1_id", "week_start"])[[target, "_p"]].sum()
    w = w[w["_p"] > 1.0]
    w["r"] = w[target] / w["_p"]
    w = w.reset_index()
    w["month"] = w["week_start"].dt.month
    qs = w.groupby(["admin1_id", "month"])["r"].quantile(list(q)).unstack()
    qs.columns = ["q05", "q50", "q95"]
    qs["n"] = w.groupby(["admin1_id", "month"]).size()
    return qs.reset_index()


def interval_table_v0(qs: pd.DataFrame, version="v0-b1") -> dict:
    """interval_table.json v0: stratum region x month; lo/hi = 5th/95th ratio quantile over the median."""
    entries = []
    allq = qs[["q05", "q50", "q95"]].median()
    for res in ("week", "month"):
        for _, r in qs.iterrows():
            if r["n"] < 8 or r["q50"] <= 0:
                continue
            entries.append({"res": res, "stratum": f"region:{r['admin1_id']}|month:{int(r['month'])}", "max_value": None,
                            "lo_mult": round(float(r["q05"] / r["q50"]), 4), "hi_mult": round(float(r["q95"] / r["q50"]), 4),
                            "hi_add": 1.0 if res == "week" else 2.0})
        entries.append({"res": res, "stratum": "all", "max_value": None, "lo_mult": round(float(allq["q05"] / allq["q50"]), 4),
                        "hi_mult": round(float(allq["q95"] / allq["q50"]), 4), "hi_add": 1.0 if res == "week" else 2.0})
    return {"version": version, "level": 0.9, "entries": entries}
