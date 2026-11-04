import json
import re

import numpy as np
import pandas as pd

from ws3_anomaly import drivers
from ws3_anomaly.anomaly import score_series
from ws3_anomaly.periods import find_periods


def seasonal(years=14, seed=0, start="2005-01-03"):
    rng = np.random.default_rng(seed)
    ws = pd.date_range(start, periods=52 * years, freq="7D")
    doy = ws.dayofyear.values
    base = 5 + 80 * np.exp(-0.5 * ((doy - 80) / 20) ** 2)
    v = rng.poisson(base * np.exp(rng.normal(0, 0.15, len(ws)))).astype(float)
    return pd.DataFrame({"week_start": ws, "value": v, "lo": v, "hi": v})


def test_injected_spike_is_flagged_and_becomes_a_period():
    df = seasonal()
    i = df.index[(df["week_start"].dt.year == 2016) & (df["week_start"].dt.month == 3)][1]
    df.loc[i, ["value", "lo", "hi"]] = 900
    s = score_series(df)
    assert s.loc[i, "flag"]
    ps = find_periods(s)
    assert ps and ps[0]["rank"] == 1 and ps[0]["start"] == s.loc[i, "week_start"].date().isoformat()


def test_seasonal_noise_gives_few_flags():
    s = score_series(seasonal(seed=3))
    assert s["flag"].mean() < 0.02


def test_wide_lower_bound_blocks_flag_only_under_lower_bound_rule(monkeypatch):
    from ws3_anomaly import anomaly
    df = seasonal()
    i = 400
    df.loc[i, "value"] = 900
    df.loc[i, "lo"] = 0.0
    s = score_series(df)
    assert s.loc[i, "flag"] and not s.loc[i, "exceeds_lower_bound"]
    monkeypatch.setattr(anomaly, "FLAG_RULE", "lower_bound")
    assert not score_series(df).loc[i, "flag"]


def test_modeled_flags_marked():
    df = seasonal(years=14, start="2003-01-06")
    df["modeled_share"] = np.where(df["week_start"] < "2012-01-20", 1.0, 0.0)
    i = df.index[(df["week_start"].dt.year == 2008) & (df["week_start"].dt.month == 3)][1]
    df.loc[i, ["value", "lo", "hi"]] = 900
    s = score_series(df)
    assert s.loc[i, "flag"] and s.loc[i, "depends_on_modeled_history"]


def test_agri_share_and_tag():
    s = score_series(seasonal())
    s.loc[50, ["flag", "value", "baseline"]] = [True, 100.0, 10.0]
    s["agri_value"] = s["value"] * 0.8
    p = [x for x in find_periods(s) if x["start"] == s.loc[50, "week_start"].date().isoformat()][0]
    assert p["agri_tag"] and abs(p["agri_share"] - 0.8) < 1e-6


def test_drivers_find_planted_rain_association_and_use_no_causal_words():
    rng = np.random.default_rng(4)
    df = seasonal(years=10)
    rain = rng.normal(0, 1, len(df))
    df["value"] = np.round(df["value"] * np.exp(-0.5 * np.r_[0, rain[:-1]]))
    wx = pd.DataFrame({"week_start": df["week_start"], "rain_anom": rain, "t2m_anom": rng.normal(0, 1, len(df)),
                       "soil_anom": rng.normal(0, 1, len(df))})
    out = drivers.driver_associations(df, wx, "Test")
    rain_items = [x for x in out["items"] if x["driver"] == "rainfall anomaly"]
    assert rain_items and rain_items[0]["direction"] == "negative" and rain_items[0]["lag_weeks"] == 1
    text = json.dumps(out).lower() + " ".join(drivers.describe(x) for x in out["items"]).lower()
    for w in drivers.FORBIDDEN_WORDS:
        assert not re.search(rf"\b{w}\b", text), w


def test_sparse_area_is_insufficient():
    df = seasonal(years=3)
    df["value"] = 0.0
    out = drivers.driver_associations(df, pd.DataFrame({"week_start": df["week_start"], "rain_anom": 0.0, "t2m_anom": 0.0, "soil_anom": 0.0}))
    assert out["status"] == "insufficient_data"


def test_lag_search_p_value_keeps_false_positives_near_nominal(monkeypatch):
    """Pure noise: picking the best of 9 lags must not inflate p<0.05 hits (decision 25).
    Unadjusted per-lag p-values give roughly 25-35% here; the max-over-lags test gives about 5%."""
    monkeypatch.setattr(drivers, "N_PERM", 99)
    monkeypatch.setattr(drivers, "N_BOOT", 20)
    rng = np.random.default_rng(11)
    trials, hits = 40, 0
    for _ in range(trials):
        b = rng.normal(0, 1, 260)
        d = rng.normal(0, 1, 260)
        out = drivers._assoc_over_lags(b, d, rng)
        hits += out is not None and out[2] < 0.05
    assert hits / trials <= 0.15, hits


def test_shift_matches_pandas():
    x = np.arange(10, dtype=float)
    for lag in (0, 1, 8):
        np.testing.assert_array_equal(drivers._shift(x, lag), pd.Series(x).shift(lag).to_numpy())
