"""Same-week climatology and season helpers. Season = Oct 1 to Sep 30, labeled by the year it ends."""
from __future__ import annotations

import numpy as np
import pandas as pd

from common.regions import SEASON_START_MONTH


def week_of_year(week_start) -> pd.Series:
    """ISO week number with week 53 folded into 52 (decision 23)."""
    w = pd.to_datetime(pd.Series(week_start)).dt.isocalendar().week.astype(int)
    return w.clip(upper=52).reset_index(drop=True)


def season_of(date) -> pd.Series:
    d = pd.to_datetime(pd.Series(date)).reset_index(drop=True)
    return (d.dt.year + (d.dt.month >= SEASON_START_MONTH).astype(int)).rename("season")


def day_of_season(date) -> pd.Series:
    d = pd.to_datetime(pd.Series(date)).reset_index(drop=True)
    start = pd.to_datetime((season_of(d) - 1).astype(str) + f"-{SEASON_START_MONTH:02d}-01")
    return (d - start).dt.days.rename("day_of_season")


def _circular_window(w, window):
    return [((w - 1 + k) % 52) + 1 for k in range(-window, window + 1)]


def same_week_quantiles(weekly_df: pd.DataFrame, q, window: int = 2, exclude_season=None) -> pd.DataFrame:
    """Quantiles of `value` for each week of year, pooling +/- `window` weeks across all years.

    weekly_df: columns week_start, value (NaN = no sensor, ignored).
    q: float or list of floats. exclude_season: drop that season (leave-one-season-out).
    Returns columns week, q<NN> for each quantile.
    """
    qs = [q] if np.isscalar(q) else list(q)
    df = weekly_df[["week_start", "value"]].dropna().copy()
    if exclude_season is not None:
        df = df[season_of(df["week_start"]).values != exclude_season]
    df["week"] = week_of_year(df["week_start"]).values
    by_week = {w: g["value"].to_numpy() for w, g in df.groupby("week")}
    rows = []
    for w in range(1, 53):
        vals = np.concatenate([by_week.get(k, np.array([])) for k in _circular_window(w, window)])
        rows.append([w] + [float(np.quantile(vals, x)) if vals.size else np.nan for x in qs])
    return pd.DataFrame(rows, columns=["week"] + [f"q{int(round(x * 100)):02d}" for x in qs])


def percentile_of(value: float, reference) -> float:
    """Percentile (0-100) of value within reference values (mid-rank for ties)."""
    ref = np.asarray(reference, dtype=float)
    ref = ref[~np.isnan(ref)]
    if ref.size == 0 or np.isnan(value):
        return float("nan")
    return float(100.0 * ((ref < value).sum() + 0.5 * (ref == value).sum()) / ref.size)


def cumulative_by_season(weekly_df: pd.DataFrame) -> pd.DataFrame:
    """Adds season, week_of_season and cum_value (season-to-date total) to a weekly frame."""
    df = weekly_df.sort_values("week_start").copy()
    df["season"] = season_of(df["week_start"]).values
    df["week_of_season"] = (day_of_season(df["week_start"]).values // 7).astype(int)
    df["cum_value"] = df.groupby("season")["value"].cumsum()
    return df
