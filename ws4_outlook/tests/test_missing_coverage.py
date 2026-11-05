"""Verified zero, unobserved and partially observed weeks stay distinct in the outlook (C07). Pure; nothing is fitted."""
import numpy as np
import pandas as pd

from common.series import weekly_series
from ws4_outlook import outlook


def history(current, current_days=None):
    """Three earlier seasons with 10 detections a week, then the current season's weeks."""
    rows = [(d, 10.0, 7) for yr in (2022, 2023, 2024) for d in pd.date_range(f"{yr}-10-06", periods=4, freq="7D")]
    days = current_days or [7] * len(current)
    rows += [(d, v, n) for d, v, n in zip(pd.date_range("2025-10-06", periods=len(current), freq="7D"), current, days)]
    return pd.DataFrame(rows, columns=["week_start", "value", "n_days"])


AS_OF = "2025-11-03"


def test_verified_zero_weeks_are_compared():
    out = outlook.season_position(history([0.0, 0.0, 0.0, 0.0]), AS_OF)
    assert out["season_to_date_status"] == "ok" and out["season_to_date_percentile"] == 0.0


def test_unobserved_week_is_not_counted_as_zero():
    out = outlook.season_position(history([10.0, np.nan, np.nan, 10.0], [7, 0, 0, 7]), AS_OF)
    assert out["season_to_date_status"] == "incomplete_coverage"
    assert out["season_to_date_percentile"] is None


def test_partially_observed_week_is_not_compared_as_a_full_week():
    w = history([10.0, 10.0, 10.0, 3.0], [7, 7, 7, 2])
    status = outlook.current_status(w, AS_OF)
    assert status["level"] == "incomplete_coverage" and status["week_percentile"] is None
    assert "2 of 7 days" in status["message"]
    assert outlook.season_position(w, AS_OF)["season_to_date_status"] == "incomplete_coverage"


def test_incomplete_reference_seasons_are_left_out_not_zeroed():
    w = history([10.0, 10.0, 10.0, 10.0])
    w.loc[(w["week_start"] == "2023-10-13"), ["value", "n_days"]] = [np.nan, 0]   # 2024 season, week 2
    out = outlook.season_position(w, AS_OF)
    assert out["season_to_date_status"] == "ok"
    assert out["season_to_date_percentile"] == 50.0                                 # two clean references, both 40
    assert out["expected_range"] == {"q10": 40.0, "q50": 40.0, "q90": 40.0}


def test_series_reports_operating_days_so_gaps_reach_the_outlook():
    cells = pd.DataFrame({"cell_id": [1], "admin1_id": ["X"], "lon_c": [0.0], "lat_c": [0.0]})
    h = pd.DataFrame({"cell_id": 1, "date": pd.to_datetime(["2025-10-06"]), "value_count": [4.0], "drift_flag": False})
    sd = pd.DataFrame([(d, "SNPP", d.day != 9) for d in pd.date_range("2025-10-06", "2025-10-12")],
                      columns=["date", "sat", "operating"])
    w = weekly_series(h, cells, cell_ids=[1], start="2025-10-06", end="2025-10-12", sensor_days=sd)
    assert w["n_days"].tolist() == [6] and w["value"].tolist() == [4.0]
