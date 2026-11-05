"""Forecast alerts (first to cut). Enter at the 90th percentile, leave at the 80th, and only when the
harmonized lower bound also clears the threshold. Off unless the forecast shows skill."""
from __future__ import annotations
import math

RULE = ("Alert level rises to high when this week's lower bound is above the 90th percentile for the time of year, "
        "and returns to none only when the value falls below the 80th percentile. Shown only when the forecast "
        "has demonstrated skill.")


def alert_level(week_percentiles, lower_bound_percentiles, status: str) -> dict:
    if status != "skill":
        return {"level": "none", "rule": "Forecast alerts are off: the forecast has not shown skill over climatology."}
    level = "none"
    points, lowers = list(week_percentiles), list(lower_bound_percentiles)
    if len(points) != len(lowers):
        raise ValueError("Point and lower-bound percentile sequences must have equal lengths")
    for p, lp in zip(points, lowers):
        if not all(isinstance(v, (int, float)) and math.isfinite(v) and 0 <= v <= 100 for v in (p, lp)) or lp > p:
            raise ValueError("Percentiles must be finite, in [0,100], and lower bound <= point")
        if lp >= 90:
            level = "high"
        elif level == "high" and p < 80:
            level = "none"
        elif level == "none" and p >= 80:
            level = "watch"
        elif level == "watch" and p < 80:
            level = "none"
    return {"level": level, "rule": RULE}


def no_forecast_bounds():
    return {"level": "none", "rule": "Forecast alerts are off: validated forecast lower-bound percentiles are unavailable."}
