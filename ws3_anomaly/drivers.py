"""Driver associations (associations only, never causes): prompt P3.8, decision 20.

For each weather driver and lag 0-8 weeks: Spearman correlation between deseasonalized burning and the
driver anomaly, a block-permutation p-value (8-week blocks) and a block-bootstrap CI. Run in batch per
admin1 region (too slow per request). Wording in every output string avoids causal verbs (lint test).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from common.climatology import week_of_year

DRIVERS = {"rain_anom": "rainfall anomaly", "t2m_anom": "temperature anomaly", "soil_anom": "soil wetness anomaly"}
MAX_LAG = 8
BLOCK = 8
N_PERM = 300
N_BOOT = 300
CAVEATS = [
    "These are associations between weekly anomalies, not evidence of what starts fires.",
    "Much burning follows farming calendars; weather explains only part of the variation.",
    "Values are averaged over the region, so local differences are hidden.",
    "Before 20 Jan 2012 burning values are modeled from MODIS, which adds uncertainty.",
]
FORBIDDEN_WORDS = ("cause", "because", "due to", "leads to", "drives")


def deseasonalize(weekly: pd.DataFrame) -> pd.Series:
    y = np.log1p(weekly["value"].astype(float))
    w = week_of_year(weekly["week_start"]).values
    med = pd.Series(y.values).groupby(w).transform("median")
    return pd.Series(y.values - med.values, index=weekly.index)


def _block_perm(x, rng):
    n = len(x)
    starts = rng.permutation(np.arange(0, n, BLOCK))
    return np.concatenate([x[s:s + BLOCK] for s in starts])[:n]


def _assoc(b, d, rng):
    ok = ~np.isnan(b) & ~np.isnan(d)
    b, d = b[ok], d[ok]
    if b.size < 2 * 52:
        return None
    rho = stats.spearmanr(b, d).statistic
    null = np.array([stats.spearmanr(b, _block_perm(d, rng)).statistic for _ in range(N_PERM)])
    p = (1 + np.sum(np.abs(null) >= abs(rho))) / (N_PERM + 1)
    n, boots = b.size, []
    for _ in range(N_BOOT):
        idx = np.concatenate([np.arange(s, min(s + BLOCK, n)) for s in rng.integers(0, n - BLOCK, n // BLOCK + 1)])[:n]
        boots.append(stats.spearmanr(b[idx], d[idx]).statistic)
    return float(rho), float(p), [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]


def evidence_label(p: float, rho: float) -> str:
    if p < 0.001 and abs(rho) >= 0.3:
        return "strong"
    if p < 0.01:
        return "moderate"
    return "weak"


def driver_associations(weekly_df: pd.DataFrame, weather: pd.DataFrame, region_name: str = "", seed: int = 5) -> dict:
    """weekly_df: week_start, value. weather: week_start + DRIVERS columns (standardized anomalies)."""
    rng = np.random.default_rng(seed)
    if weather is None:
        return {"region_name": region_name, "status": "insufficient_data", "items": [],
                "caveats": ["Weather data has not been loaded yet, so associations cannot be estimated."]}
    w = weekly_df[["week_start", "value"]].dropna().copy()
    w["week_start"] = pd.to_datetime(w["week_start"])
    if (w["value"] > 0).sum() < 2 * 52:
        return {"region_name": region_name, "status": "insufficient_data", "items": [],
                "caveats": ["Too few weeks with detected burning to estimate associations."] + CAVEATS[:1]}
    w["burn"] = deseasonalize(w).values
    wx = weather.copy()
    wx["week_start"] = pd.to_datetime(wx["week_start"])
    m = w.merge(wx, on="week_start", how="inner").sort_values("week_start")
    found = []
    for col, label in DRIVERS.items():
        best = None
        for lag in range(MAX_LAG + 1):
            d = m[col].shift(lag).to_numpy(dtype=float)
            r = _assoc(m["burn"].to_numpy(dtype=float), d, rng)
            if r and (best is None or abs(r[0]) > abs(best[1][0])):
                best = (lag, r)
        if best and best[1][1] < 0.05:
            lag, (rho, p, ci) = best
            found.append({"driver": label, "lag_weeks": lag, "direction": "positive" if rho > 0 else "negative",
                          "strength": round(rho, 3), "ci": [round(ci[0], 3), round(ci[1], 3)], "evidence": evidence_label(p, rho),
                          "_p": p})
    found.sort(key=lambda x: -abs(x["strength"]))
    items = [{k: v for k, v in f.items() if k != "_p"} for f in found[:3]]
    return {"region_name": region_name, "status": "ok", "items": items, "caveats": CAVEATS}


def describe(item: dict) -> str:
    """Plain-language sentence for the app (association wording only)."""
    when = "the same week" if item["lag_weeks"] == 0 else f"{item['lag_weeks']} week(s) earlier"
    more = "more" if item["direction"] == "positive" else "less"
    return (f"Weeks with a higher {item['driver']} in {when} tend to show {more} burning "
            f"(rank correlation {item['strength']:+.2f}, {item['evidence']} evidence).")
