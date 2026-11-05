"""Current status (core, never cut) and season outlook (prompts P4.7, P4.8; decision 14).

current_status(weekly, as_of): percentile of the latest complete week against the same week in earlier
years; high when the lower bound reaches the 90th percentile, watch at the 80th, low at the 25th, very_low when the
upper bound is at or below the 10th; a difference under 10 detections from typical is never unusual (none);
data_through = last day with data.
outlook(weekly, as_of): current_status + season-to-date percentile and the expected range of cumulative
activity at this point of the season (from earlier seasons). Complete weeks are bounded by as_of and record_end.
forecast skill (evaluate_forecast): 2-4 week ahead quantile learner, forward-season folds, skill against
climatology and persistence with bootstrap CIs; status = no_demonstrated_skill when the CI includes 0.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common.climatology import cumulative_by_season, percentile_of, season_of, week_of_year
from common import compute

WATCH, HIGH = 80.0, 90.0
LOW, VERY_LOW, MIN_CHANGE = 25.0, 10.0, 10.0
LEVEL_WORDS = {"none": "within the usual range", "watch": "higher than usual", "high": "much higher than usual",
               "low": "lower than usual", "very_low": "much lower than usual"}


def _prep(weekly: pd.DataFrame, as_of, *, record_end=None) -> pd.DataFrame:
    """Keep weeks complete by the issue date and, when supplied, the actual record end."""
    w = weekly[["week_start", "value"] + [c for c in ("lo", "hi", "source") if c in weekly]].copy()
    w["week_start"] = pd.to_datetime(w["week_start"])
    cutoff = pd.Timestamp(as_of)
    if record_end is not None:
        cutoff = min(cutoff, pd.Timestamp(record_end))
    return w[w["week_start"] + pd.Timedelta(days=6) <= cutoff].sort_values("week_start").reset_index(drop=True)


def current_status(weekly: pd.DataFrame, as_of, data_through=None, *, record_end=None) -> dict:
    w = _prep(weekly, as_of, record_end=record_end).dropna(subset=["value"])
    if w.empty:
        through = data_through or record_end or as_of
        return {"week_percentile": None, "level": "insufficient_history",
                "data_through": pd.Timestamp(through).date().isoformat(),
                "message": "No complete week with data is available for this area."}
    last = w.iloc[-1]
    data_source = last.get("source", "harmonized")
    if pd.isna(data_source):
        data_source = "harmonized"
    through = data_through or (last["week_start"] + pd.Timedelta(days=6)).date().isoformat()
    wk = week_of_year([last["week_start"]]).iloc[0]
    same = w[(week_of_year(w["week_start"]).values == wk) & (w["week_start"] < last["week_start"])]["value"]
    if same.empty:
        return {"week_percentile": None, "level": "insufficient_history", "data_through": str(through),
                "data_source": data_source, "message": "Not enough same-week history to compare burning activity."}
    pct = percentile_of(float(last["value"]), same.values)
    value = float(last["value"])
    lo = last.get("lo", np.nan)
    hi = last.get("hi", np.nan)
    lo_pct = percentile_of(value if pd.isna(lo) else float(lo), same.values)
    hi_pct = percentile_of(value if pd.isna(hi) else float(hi), same.values)
    typical = float(np.nanmedian(same.values)) if same.notna().any() else 0.0
    small = abs(value - typical) < MIN_CHANGE
    if small:
        level = "none"
    elif lo_pct >= HIGH:
        level = "high"
    elif pct >= WATCH:
        level = "watch"
    elif hi_pct <= VERY_LOW:
        level = "very_low"
    elif pct <= LOW:
        level = "low"
    else:
        level = "none"
    week_txt = last["week_start"].strftime("%d %b %Y")
    n = int(same.notna().sum())
    if small and typical < MIN_CHANGE:
        msg = f"Little or no burning in the week of {week_txt}, as usual for this time of year."
    else:
        msg = (f"Burning in the week of {week_txt} was {LEVEL_WORDS[level]} for this time of year "
               f"(percentile {pct:.0f} of the same week in {n} past years).")
    return {"week_percentile": round(float(pct), 1), "level": level, "data_through": str(through),
            "data_source": data_source, "message": msg}


def season_position(weekly: pd.DataFrame, as_of, *, record_end=None) -> dict:
    # C07: missing-to-zero handling is unchanged pending a separate scientific specification.
    w = cumulative_by_season(_prep(weekly, as_of, record_end=record_end).fillna({"value": 0}))
    if w.empty:
        return {"season_to_date_percentile": None, "expected_range": {"q10": 0.0, "q50": 0.0, "q90": 0.0}}
    cur = w.iloc[-1]
    prev = w[(w["season"] < cur["season"]) & (w["week_of_season"] == cur["week_of_season"])]["cum_value"].values
    if not prev.size:
        return {"season_to_date_percentile": None, "expected_range": {"q10": 0.0, "q50": 0.0, "q90": 0.0}}
    pct = percentile_of(float(cur["cum_value"]), prev)
    q = np.quantile(prev, [0.1, 0.5, 0.9]) if prev.size else [0, 0, 0]
    return {"season_to_date_percentile": round(float(pct), 1),
            "expected_range": {"q10": round(float(q[0]), 1), "q50": round(float(q[1]), 1), "q90": round(float(q[2]), 1)}}


# ---------------------------------------------------------------- forecast and skill (P4.8)
HORIZON = (2, 4)


def forecast_frame(weekly: pd.DataFrame, weather: pd.DataFrame | None = None, *, reference=None) -> pd.DataFrame:
    base = weekly[["week_start", "value"]].copy()
    base["week_start"] = pd.to_datetime(base["week_start"])
    base = base.sort_values("week_start").set_index("week_start")
    if base.index.has_duplicates:
        raise ValueError("Forecast weeks must be unique")
    if not base.empty:
        base = base.reindex(pd.date_range(base.index.min(), base.index.max(), freq="7D"))
    w = cumulative_by_season(base.rename_axis("week_start").reset_index())
    w = w.reset_index(drop=True)
    wk = week_of_year(w["week_start"]).values
    w["clim"] = np.nan
    for season in w["season"].unique():
        ref = w[w["season"] < season] if reference is None else reference.copy()
        ref = ref.dropna(subset=["value"])
        climatology = pd.Series(np.log1p(ref["value"].to_numpy())).groupby(
            week_of_year(ref["week_start"]).to_numpy()).median()
        selected = w["season"].eq(season)
        w.loc[selected, "clim"] = pd.Series(wk[selected]).map(climatology).to_numpy()
    w["anom"] = np.log1p(w["value"]) - w["clim"]
    w["last4"] = np.log1p(w["value"]).rolling(4, min_periods=4).mean()
    w["std_anom"] = w.groupby("season")["anom"].cumsum() / (w["week_of_season"] + 1)
    fut = sum(w["value"].shift(-h) for h in range(HORIZON[0], HORIZON[1] + 1))
    w["target"] = np.log1p(fut)
    w["target_clim"] = sum(pd.Series(np.expm1(w["clim"].values)).shift(-h) for h in range(HORIZON[0], HORIZON[1] + 1)).values
    w["target_persist"] = 3 * w["value"]
    w["target_end"] = w["week_start"] + pd.Timedelta(weeks=HORIZON[1])
    if weather is not None:
        wx = weather.assign(week_start=pd.to_datetime(weather["week_start"]))
        w = w.merge(wx[["week_start", "rain_anom", "t2m_anom", "soil_anom"]], on="week_start", how="left")
    return w


FEATS = ["anom", "last4", "std_anom", "week_of_season", "clim"]


def forecast_fold(weekly, evaluation_season):
    """Pure fold construction. No held-out or later outcomes enter reference/training data."""
    dates = pd.to_datetime(weekly["week_start"])
    seasons = season_of(dates).to_numpy()
    reference = weekly.loc[seasons < evaluation_season, ["week_start", "value"]].copy()
    available = weekly.loc[seasons <= evaluation_season].copy()
    frame = forecast_frame(available, reference=reference)
    cutoff = pd.Timestamp(year=int(evaluation_season) - 1, month=10, day=1)
    valid = frame.dropna(subset=FEATS + ["target", "target_clim", "target_persist"])
    train = valid[(valid["season"] < evaluation_season) & (valid["target_end"] < cutoff)]
    test = valid[(valid["season"] == evaluation_season) &
                 (season_of(valid["target_end"]).to_numpy() == evaluation_season)]
    return train.copy(), test.copy()


def evaluate_forecast(weekly, weather=None, seed=2):
    """Forward-season pinball loss; weather excluded until its normalization is fold-audited."""
    feats = FEATS
    losses = []
    for s in sorted(season_of(weekly["week_start"]).unique())[3:]:
        tr, te = forecast_fold(weekly, s)
        if tr.empty or te.empty:
            continue
        if compute.backend() == "cuda":
            m = compute.train_cuda(tr[feats], tr["target"], objective="reg:quantileerror", quantile_alpha=0.5,
                                   rounds=150, learning_rate=0.05, max_leaves=15, purpose="outlook-quantile")
            pred = compute.predict_cuda(m, te[feats])
        else:
            # Internal human-run reference fitting; API serving never imports ML libraries.
            import lightgbm as lgb
            m = lgb.LGBMRegressor(objective="quantile", alpha=0.5, n_estimators=150, learning_rate=0.05, num_leaves=15,
                                  min_child_samples=20, verbose=-1, n_jobs=compute.threads()).fit(tr[feats], tr["target"])
            pred = m.predict(te[feats])
        y = te["target"].values
        losses.append({"season": int(s), "model": np.mean(np.abs(y - pred)) / 2,
                       "clim": np.mean(np.abs(y - np.log1p(te["target_clim"].values))) / 2,
                       "persist": np.mean(np.abs(y - np.log1p(te["target_persist"].values))) / 2})
    L = pd.DataFrame(losses)
    if L.empty or len(L) < 3 or (L[["clim", "persist"]].sum() <= 0).any():
        return {"vs_climatology": 0.0, "vs_persistence": 0.0, "ci": [0.0, 0.0],
                "n_seasons": len(L)}, "no_demonstrated_skill"
    rng = np.random.default_rng(seed)

    def skill(ref):
        s = 1 - L["model"].sum() / L[ref].sum()
        boots = [1 - L["model"].values[i].sum() / max(L[ref].values[i].sum(), np.finfo(float).eps)
                 for i in (rng.integers(0, len(L), len(L)) for _ in range(1000))]
        return float(s), [float(np.quantile(boots, 0.05)), float(np.quantile(boots, 0.95))]

    s_c, ci_c = skill("clim")
    s_p, _ = skill("persist")
    status = "skill" if ci_c[0] > 0 else "no_demonstrated_skill"
    return {"vs_climatology": round(s_c, 3), "vs_persistence": round(s_p, 3), "ci": [round(ci_c[0], 3), round(ci_c[1], 3)],
            "n_seasons": int(len(L))}, status


def outlook(weekly_df: pd.DataFrame, bbox=None, as_of=None, skill: dict | None = None, status: str = "no_demonstrated_skill",
            alert: dict | None = None, data_through=None, *, record_end=None) -> dict:
    as_of = pd.Timestamp(as_of or pd.Timestamp.today().normalize())
    out = {"as_of": as_of.date().isoformat(),
           "current_status": current_status(weekly_df, as_of, data_through, record_end=record_end),
           **season_position(weekly_df, as_of, record_end=record_end),
           "skill": skill or {"n_seasons": 0},
           "status": status,
           "alert": alert or {"level": "none", "rule": "Forecast alerts are off until the forecast shows skill."}}
    return out
