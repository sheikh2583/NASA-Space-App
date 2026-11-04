import numpy as np
import pandas as pd

from ws4_outlook import alerts, outlook


def weekly(years=12, seed=0):
    rng = np.random.default_rng(seed)
    ws = pd.date_range("2010-10-04", periods=52 * years, freq="7D")
    doy = ws.dayofyear.values
    v = rng.poisson(5 + 60 * np.exp(-0.5 * ((doy - 80) / 20) ** 2)).astype(float)
    return pd.DataFrame({"week_start": ws, "value": v, "lo": v, "hi": v})


def test_as_of_never_uses_later_data():
    w = weekly()
    as_of = pd.Timestamp("2018-03-20")
    a = outlook.outlook(w, as_of=as_of)
    later = w.copy()
    later.loc[later["week_start"] > as_of, "value"] = 10_000
    b = outlook.outlook(later, as_of=as_of)
    assert a == b


def test_current_status_levels_and_message():
    w = weekly()
    last = w.index[-1]
    w.loc[last, ["value", "lo", "hi"]] = 10_000
    cs = outlook.current_status(w, w.loc[last, "week_start"] + pd.Timedelta(days=7))
    assert cs["level"] == "high" and cs["week_percentile"] > 99 and "much higher than usual" in cs["message"]
    w.loc[last, "lo"] = 0.0
    assert outlook.current_status(w, w.loc[last, "week_start"] + pd.Timedelta(days=7))["level"] == "watch"


def test_season_position_ranges_are_ordered():
    o = outlook.outlook(weekly(), as_of="2021-02-15")
    r = o["expected_range"]
    assert r["q10"] <= r["q50"] <= r["q90"] and 0 <= o["season_to_date_percentile"] <= 100


def test_alerts_off_without_skill_and_hysteresis_with_skill():
    assert alerts.alert_level([95], [95], "no_demonstrated_skill")["level"] == "none"
    assert alerts.alert_level([95], [95], "skill")["level"] == "high"
    assert alerts.alert_level([95, 85], [95, 70], "skill")["level"] == "high"
    assert alerts.alert_level([95, 70], [95, 60], "skill")["level"] == "none"


def _same_week(past, last_value, lo=None, hi=None, years=12, seed=1):
    """A weekly series whose same week in every past year comes from `past`, and whose last week is `last_value`."""
    from common.climatology import week_of_year
    w = weekly(years=years)
    last = w.index[-1]
    wk = week_of_year(w["week_start"]).values
    idx = w.index[(wk == wk[last]) & (w.index != last)]
    rng = np.random.default_rng(seed)
    vals = rng.choice(np.asarray(past, float), size=len(idx))
    for col in ("value", "lo", "hi"):
        w.loc[idx, col] = vals
    w.loc[last, ["value", "lo", "hi"]] = [last_value, last_value if lo is None else lo, last_value if hi is None else hi]
    return outlook.current_status(w, w.loc[last, "week_start"] + pd.Timedelta(days=7))


def test_record_low_week_is_very_low():
    cs = _same_week(past=[95, 100, 105, 110], last_value=5)
    assert cs["level"] == "very_low" and "much lower" in cs["message"]
    assert "percentile 0 of the same week in" in cs["message"]


def test_a_few_fires_where_none_is_typical_is_usual():
    cs = _same_week(past=[0, 0, 1], last_value=3)
    assert cs["level"] == "none" and cs["message"].startswith("Little or no burning")


def test_zero_where_about_two_is_typical_is_usual():
    assert _same_week(past=[1, 2, 3], last_value=0)["level"] == "none"


def test_a_median_week_is_usual():
    cs = _same_week(past=[80, 100, 120], last_value=100)
    assert cs["level"] == "none" and "within the usual range" in cs["message"]


def test_somewhat_low_week_is_low_not_very_low():
    cs = _same_week(past=[100, 110, 120, 130, 140, 150], last_value=105, hi=125)
    assert cs["level"] == "low" and "lower than usual" in cs["message"] and "much lower" not in cs["message"]
