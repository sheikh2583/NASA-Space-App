"""Forecast alerts (first to cut). Enter at the 90th percentile, leave at the 80th, and only when the
harmonized lower bound also clears the threshold. Off unless the forecast shows skill."""
from __future__ import annotations

RULE = ("Alert level rises to high when this week's lower bound is above the 90th percentile for the time of year, "
        "and returns to none only when the value falls below the 80th percentile. Shown only when the forecast "
        "has demonstrated skill.")


def alert_level(week_percentiles, lower_bound_percentiles, status: str) -> dict:
    if status != "skill":
        return {"level": "none", "rule": "Forecast alerts are off: the forecast has not shown skill over climatology."}
    level = "none"
    for p, lp in zip(week_percentiles, lower_bound_percentiles):
        if level == "none" and lp >= 90:
            level = "high"
        elif level == "high" and p < 80:
            level = "none"
        elif level == "none" and p >= 80:
            level = "watch"
        elif level == "watch" and p < 80:
            level = "none"
    return {"level": level, "rule": RULE}
