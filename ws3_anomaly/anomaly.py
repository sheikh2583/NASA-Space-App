"""Unusual-week scoring for an AOI or region weekly series (prompts P3.4, P3.6; decisions 2, 21, 23).

score_series(df[week_start, value, lo, hi]) adds baseline, score, flag, exceeds_lower_bound and
depends_on_modeled_history. Method:
  - work on log1p(value); baseline = the week-of-year median with a +/-2 week window across all years
    (ISO week 53 folded into 52). method="stl" uses robust STL (period 52) instead; it is not the default
    because STL's trend absorbs a whole unusual season, which is exactly what we want to flag;
  - score = residual / (1.4826 x MAD of residuals in the same +/-2 week window);
  - flag when score > 2 AND the value exceeds the 90th percentile of same-week values (FLAG_RULE, decision 21);
    exceeds_lower_bound says whether the band's lower edge also exceeds it;
  - seam check: the same scoring on the observed era only (from 20 Jan 2012); a flag that appears only with
    the full series, or a flagged week that is itself mostly modeled, is depends_on_modeled_history.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL

from common.climatology import week_of_year

OBSERVED_FROM = pd.Timestamp("2012-01-20")
WINDOW = 2
SCORE_MIN = 2.0
PCTL = 0.90
# Decision 21 outcome (QA, 3 Nov 2026, synthetic data): with the lower-bound rule the flag rate before 2012 was 0.000 vs
# 0.018 after, because modeled weeks carry wide bands. As decision 21 prescribes, flags use the value; exceeds_lower_bound
# is still computed and shown, so a reader can see which flags survive the uncertainty band.
FLAG_RULE = "value"  # or "lower_bound"


def _window_stat(weeks: np.ndarray, x: np.ndarray, fn) -> np.ndarray:
    out = np.full(53, np.nan)
    for w in range(1, 53):
        near = [((w - 1 + k) % 52) + 1 for k in range(-WINDOW, WINDOW + 1)]
        v = x[np.isin(weeks, near) & ~np.isnan(x)]
        if v.size:
            out[w] = fn(v)
    return out[weeks]


def _score(df: pd.DataFrame, method: str = "climatology", rule: str | None = None):
    y = np.log1p(df["value"].to_numpy(dtype=float))
    weeks = week_of_year(df["week_start"]).to_numpy()
    n_years = df.loc[~np.isnan(y), "week_start"].dt.year.nunique()
    if method == "stl" and n_years >= 8 and np.isfinite(y).sum() >= 8 * 52:
        filled = pd.Series(y).interpolate(limit_direction="both").to_numpy()
        fit = STL(filled, period=52, robust=True).fit()
        base_log = fit.trend + fit.seasonal
    else:
        base_log = _window_stat(weeks, y, np.median)
    resid = y - base_log
    mad = _window_stat(weeks, np.abs(resid - _window_stat(weeks, resid, np.median)), np.median)
    scale = np.maximum(1.4826 * mad, 0.05)
    score = resid / scale
    p90 = _window_stat(weeks, df["value"].to_numpy(dtype=float), lambda v: np.quantile(v, PCTL))
    lo = df["lo"].to_numpy(dtype=float) if "lo" in df else np.full(len(df), np.nan)
    lo = np.where(np.isnan(lo), df["value"].to_numpy(dtype=float), lo)
    exceeds = lo > p90
    above = exceeds if (rule or FLAG_RULE) == "lower_bound" else df["value"].to_numpy(dtype=float) > p90
    flag = (score > SCORE_MIN) & above & ~np.isnan(y)
    return np.expm1(base_log), score, flag, exceeds


def score_series(df: pd.DataFrame, method: str = "climatology") -> pd.DataFrame:
    """df: week_start, value, lo, hi (+ optional modeled_share). Returns a copy with the scoring columns."""
    out = df.copy().sort_values("week_start").reset_index(drop=True)
    out["week_start"] = pd.to_datetime(out["week_start"])
    if len(out) < 10 or out["value"].notna().sum() < 10:
        return out.assign(baseline=np.nan, score=np.nan, flag=False, exceeds_lower_bound=False,
                          depends_on_modeled_history=False)
    base, score, flag, exceeds = _score(out, method)
    out["baseline"], out["score"], out["flag"], out["exceeds_lower_bound"] = base, score, flag, exceeds
    obs = out["week_start"] >= OBSERVED_FROM
    dep = np.zeros(len(out), dtype=bool)
    if obs.sum() >= 3 * 52:
        _, _, flag_obs, _ = _score(out[obs].reset_index(drop=True), method)
        only_full = np.zeros(len(out), dtype=bool)
        only_full[np.nonzero(obs.to_numpy())[0]] = ~flag_obs
        dep |= flag & only_full
    else:
        dep |= flag  # too little observed history to check: every flag leans on modeled years
    if "modeled_share" in out:
        dep |= flag & (out["modeled_share"].to_numpy(dtype=float) > 0.5)
    out["depends_on_modeled_history"] = dep
    return out
