"""Merge flagged weeks into ranked critical periods (prompt P3.5; decision 16).

severity = excess over baseline summed over the period / the series' mean weekly value, i.e. "how many
typical weeks of burning above normal". Dividing by the period's own baseline (the prompt's first draft)
let tiny off-season spikes outrank large in-season excesses.

agri_share = fraction of the period's detections that fall in cropland (cropland_frac-weighted), when the
scored frame carries an `agri_value` column; agri_tag = agri_share >= 0.5. Without land cover the tag
falls back to the region-season rule below (decision 8) and agri_share is None.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Region-season rule: months of known crop-residue burning, by country code of the demo regions.
AGRI_MONTHS = {"PB": {4, 5, 10, 11}, "BD": {3, 4}}
MAX_GAP_WEEKS = 1


def find_periods(scored: pd.DataFrame, country: str | None = None) -> list[dict]:
    s = scored.sort_values("week_start").reset_index(drop=True)
    flagged = np.nonzero(s["flag"].to_numpy(dtype=bool))[0]
    if flagged.size == 0:
        return []
    groups, cur = [], [flagged[0]]
    for i in flagged[1:]:
        if i - cur[-1] <= MAX_GAP_WEEKS + 1:
            cur.append(i)
        else:
            groups.append(cur)
            cur = [i]
    groups.append(cur)
    typical = max(float(s["value"].mean(skipna=True)), 1.0)
    periods = []
    for g in groups:
        rows = s.iloc[g[0]: g[-1] + 1]
        base = rows["baseline"].clip(lower=0)
        excess = (rows["value"] - base).clip(lower=0).sum()
        severity = float(excess / typical)
        if "agri_value" in rows and rows["agri_value"].notna().any() and rows["value"].sum() > 0:
            agri_share = float(np.clip(rows["agri_value"].sum() / rows["value"].sum(), 0, 1))
            agri_tag = agri_share >= 0.5
        else:
            agri_share = None
            months = set(rows["week_start"].dt.month)
            agri_tag = bool(country and months & AGRI_MONTHS.get(country, set()))
        end = rows["week_start"].iloc[-1] + pd.Timedelta(days=6)
        periods.append({
            "start": rows["week_start"].iloc[0].date().isoformat(), "end": end.date().isoformat(),
            "severity": round(severity, 3), "peak_value": round(float(rows["value"].max()), 2),
            "agri_tag": bool(agri_tag), "agri_share": None if agri_share is None else round(agri_share, 3),
            "n_weeks": int(len(rows)),
            "depends_on_modeled_history": bool(rows.loc[rows["flag"], "depends_on_modeled_history"].any())
            if "depends_on_modeled_history" in rows else False,
        })
    periods.sort(key=lambda p: -p["severity"])
    for r, p in enumerate(periods, start=1):
        p["rank"] = r
    return periods
