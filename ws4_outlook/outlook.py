"""Current status (core, never cut) and season outlook (prompts P4.7, P4.8; decision 14).

current_status(weekly, as_of): percentile of the latest complete week against the same week in earlier
years; watch at the 80th percentile, high at the 90th; data_through = last day with data.
outlook(weekly, as_of): current_status + season-to-date percentile and the expected range of cumulative
activity at this point of the season (from earlier seasons). Uses only data up to as_of.
forecast skill (evaluate_forecast): 2-4 week ahead quantile LightGBM, leave-one-season-out, skill against
climatology and persistence with bootstrap CIs; status = no_demonstrated_skill when the CI includes 0.
"""
from __future__ import annotations

import lightgbm as lgb
import numpy as np
import pandas as pd

from common.climatology import cumulative_by_season, percentile_of, season_of, week_of_year
from common import compute

WATCH, HIGH = 80.0, 90.0
LEVEL_WORDS = {"none": "within the normal range", "watch": "higher than usual", "high": "much higher than usual"}


def _prep(weekly: pd.DataFrame, as_of) -> pd.DataFrame:
    w = weekly[["week_start", "value"] + [c for c in ("lo", "hi") if c in weekly]].copy()
    w["week_start"] = pd.to_datetime(w["week_start"])
    as_of = pd.Timestamp(as_of)
    return w[w["week_start"] + pd.Timedelta(days=6) <= as_of].sort_values("week_start").reset_index(drop=True)


def current_status(weekly: pd.DataFrame, as_of, data_through=None, data_source="VIIRS_NOAA20_NRT") -> dict:
    w = _prep(weekly, as_of).dropna(subset=["value"])
    if w.empty:
        return {"week_percentile": 0.0, "level": "none", "data_through": pd.Timestamp(as_of).date().isoformat(),
                "data_source": data_source, "message": "No recent data for this area."}
    last = w.iloc[-1]
    wk = week_of_year([last["week_start"]]).iloc[0]
    same = w[(week_of_year(w["week_start"]).values == wk) & (w["week_start"] < last["week_start"])]["value"]
    pct = percentile_of(float(last["value"]), same.values)
    lo_pct = percentile_of(float(last.get("lo", last["value"]) if not pd.isna(last.get("lo", np.nan)) else last["value"]), same.values)
    level = "high" if lo_pct >= HIGH else ("watch" if pct >= WATCH else "none")
    week_txt = last["week_start"].strftime("%d %b %Y")
    msg = (f"Burning in the week of {week_txt} was {LEVEL_WORDS[level]} for this time of year "
           f"(higher than {pct:.0f}% of the same week in past years).")
    through = data_through or (last["week_start"] + pd.Timedelta(days=6)).date().isoformat()
    return {"week_percentile": round(float(pct), 1), "level": level, "data_through": str(through),
            "data_source": data_source, "message": msg}


def season_position(weekly: pd.DataFrame, as_of) -> dict:
    w = cumulative_by_season(_prep(weekly, as_of).fillna({"value": 0}))
    if w.empty:
        return {"season_to_date_percentile": 0.0, "expected_range": {"q10": 0.0, "q50": 0.0, "q90": 0.0}}
    cur = w.iloc[-1]
    prev = w[(w["season"] < cur["season"]) & (w["week_of_season"] == cur["week_of_season"])]["cum_value"].values
    pct = percentile_of(float(cur["cum_value"]), prev)
    q = np.quantile(prev, [0.1, 0.5, 0.9]) if prev.size else [0, 0, 0]
    return {"season_to_date_percentile": round(float(pct), 1),
            "expected_range": {"q10": round(float(q[0]), 1), "q50": round(float(q[1]), 1), "q90": round(float(q[2]), 1)}}


# ---------------------------------------------------------------- forecast and skill (P4.8)
HORIZON = (2, 4)


def forecast_frame(weekly: pd.DataFrame, weather: pd.DataFrame | None = None) -> pd.DataFrame:
    w = cumulative_by_season(weekly[["week_start", "value"]].dropna().assign(week_start=lambda d: pd.to_datetime(d["week_start"])))
    w = w.reset_index(drop=True)
    wk = week_of_year(w["week_start"]).values
    w["clim"] = pd.Series(np.log1p(w["value"].values)).groupby(wk).transform("median").values
    w["anom"] = np.log1p(w["value"]) - w["clim"]
    w["last4"] = np.log1p(w["value"]).rolling(4, min_periods=1).mean()
    w["std_anom"] = w.groupby("season")["anom"].cumsum() / (w["week_of_season"] + 1)
    fut = sum(w["value"].shift(-h) for h in range(HORIZON[0], HORIZON[1] + 1))
    w["target"] = np.log1p(fut)
    w["target_clim"] = sum(pd.Series(np.expm1(w["clim"].values)).shift(-h) for h in range(HORIZON[0], HORIZON[1] + 1)).values
    w["target_persist"] = 3 * w["value"]
    if weather is not None:
        wx = weather.assign(week_start=pd.to_datetime(weather["week_start"]))
        w = w.merge(wx[["week_start", "rain_anom", "t2m_anom", "soil_anom"]], on="week_start", how="left")
    return w


FEATS = ["anom", "last4", "std_anom", "week_of_season", "clim"]


def evaluate_forecast(weekly, weather=None, seed=2):
    """Leave-one-season-out pinball loss of the median forecast vs climatology and persistence."""
    w = forecast_frame(weekly, weather).dropna(subset=["target"])
    feats = FEATS + [c for c in ("rain_anom", "t2m_anom", "soil_anom") if c in w]
    losses = []
    for s in sorted(w["season"].unique())[3:]:
        tr, te = w[w["season"] != s], w[w["season"] == s]
        if compute.backend() == "cuda":
            m = compute.train_cuda(tr[feats], tr["target"], objective="reg:quantileerror", quantile_alpha=0.5,
                                   rounds=150, learning_rate=0.05, max_leaves=15, purpose="outlook-quantile")
            pred = compute.predict_cuda(m, te[feats])
        else:
            m = lgb.LGBMRegressor(objective="quantile", alpha=0.5, n_estimators=150, learning_rate=0.05, num_leaves=15,
                                  min_child_samples=20, verbose=-1, n_jobs=compute.threads()).fit(tr[feats], tr["target"])
            pred = m.predict(te[feats])
        y = te["target"].values
        losses.append({"season": int(s), "model": np.mean(np.abs(y - pred)) / 2,
                       "clim": np.mean(np.abs(y - np.log1p(te["target_clim"].values))) / 2,
                       "persist": np.mean(np.abs(y - np.log1p(te["target_persist"].values))) / 2})
    L = pd.DataFrame(losses)
    rng = np.random.default_rng(seed)

    def skill(ref):
        s = 1 - L["model"].sum() / L[ref].sum()
        boots = [1 - L["model"].values[i].sum() / L[ref].values[i].sum()
                 for i in (rng.integers(0, len(L), len(L)) for _ in range(1000))]
        return float(s), [float(np.quantile(boots, 0.05)), float(np.quantile(boots, 0.95))]

    s_c, ci_c = skill("clim")
    s_p, _ = skill("persist")
    status = "skill" if ci_c[0] > 0 else "no_demonstrated_skill"
    return {"vs_climatology": round(s_c, 3), "vs_persistence": round(s_p, 3), "ci": [round(ci_c[0], 3), round(ci_c[1], 3)],
            "n_seasons": int(len(L))}, status


def outlook(weekly_df: pd.DataFrame, bbox=None, as_of=None, skill: dict | None = None, status: str = "no_demonstrated_skill",
            alert: dict | None = None, data_through=None) -> dict:
    as_of = pd.Timestamp(as_of or pd.Timestamp.today().normalize())
    out = {"as_of": as_of.date().isoformat(),
           "current_status": current_status(weekly_df, as_of, data_through),
           **season_position(weekly_df, as_of),
           "skill": skill or {"n_seasons": 0},
           "status": status,
           "alert": alert or {"level": "none", "rule": "Forecast alerts are off until the forecast shows skill."}}
    return out
