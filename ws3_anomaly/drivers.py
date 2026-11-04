"""Driver associations (associations only, never causes): prompt P3.8, decision 20.

For each weather driver, lags 0-8 weeks are searched for the strongest Spearman correlation between
deseasonalized burning and the driver anomaly. Its p-value comes from a block permutation (8-week blocks)
of the max-over-lags statistic: every permuted driver series is searched over the same 9 lags, so the
p-value accounts for picking the best lag (decision 25). A block-bootstrap CI is given for the chosen lag.
Run in batch per admin1 region (too slow per request). Wording in every output string avoids causal verbs
(lint test).
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


def _shift(x: np.ndarray, lag: int) -> np.ndarray:
    """Same as pandas Series.shift(lag): value of week t - lag at week t, NaN for the first lag weeks."""
    if lag == 0:
        return x.copy()
    out = np.full_like(x, np.nan)
    out[lag:] = x[:-lag]
    return out


def _rho(b, d):
    ok = ~np.isnan(b) & ~np.isnan(d)
    if ok.sum() < 2 * 52:
        return None
    r = stats.spearmanr(b[ok], d[ok]).statistic
    return None if np.isnan(r) else float(r)


def _best_lag(b, d):
    """(lag, rho) with the largest |rho| over lags 0..MAX_LAG, or None."""
    best = None
    for lag in range(MAX_LAG + 1):
        r = _rho(b, _shift(d, lag))
        if r is not None and (best is None or abs(r) > abs(best[1])):
            best = (lag, r)
    return best


def _assoc_over_lags(b, d, rng):
    """(lag, rho, p, ci) for the best lag; p is the max-over-lags block-permutation p-value."""
    best = _best_lag(b, d)
    if best is None:
        return None
    lag, rho = best
    null = np.empty(N_PERM)
    for i in range(N_PERM):
        nb = _best_lag(b, _block_perm(d, rng))
        null[i] = 0.0 if nb is None else abs(nb[1])
    p = (1 + np.sum(null >= abs(rho))) / (N_PERM + 1)
    ds = _shift(d, lag)
    ok = ~np.isnan(b) & ~np.isnan(ds)
    bb, dd = b[ok], ds[ok]
    n, boots = bb.size, []
    for _ in range(N_BOOT):
        idx = np.concatenate([np.arange(s, min(s + BLOCK, n)) for s in rng.integers(0, n - BLOCK, n // BLOCK + 1)])[:n]
        boots.append(stats.spearmanr(bb[idx], dd[idx]).statistic)
    return lag, float(rho), float(p), [float(np.nanquantile(boots, 0.025)), float(np.nanquantile(boots, 0.975))]


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
        best = _assoc_over_lags(m["burn"].to_numpy(dtype=float), m[col].to_numpy(dtype=float), rng)
        if best and best[2] < 0.05:
            lag, rho, p, ci = best
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
