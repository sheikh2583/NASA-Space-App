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
