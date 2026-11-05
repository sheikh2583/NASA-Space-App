"""Monthly interval samples use calendar months, like the served monthly totals. Pure data checks; nothing is fitted."""
import numpy as np
import pandas as pd
import pytest

from common.grid import N_COLS
from common.series import weekly_series
from ws4_outlook import conformal

CELL = 500 * N_COLS + 500
WEEKS = pd.date_range("2021-03-01", "2021-04-26", freq="7D")       # covers 1 Mar - 2 May: March and April complete
STRADDLE = pd.date_range("2021-03-29", "2021-04-04")              # 3 days in March, 4 in April


def fixture(snpp_per_day=1.0):
    y = [7.0 * snpp_per_day if w == pd.Timestamp("2021-03-29") else 0.0 for w in WEEKS]
    oof = pd.DataFrame({"cell_id": CELL, "date": WEEKS.date, "y_true_count": y, "y_pred_count": y,
                        "y_true_frp": 0.0, "y_pred_frp": 0.0, "fold": 0, "block_id": 1, "split": "test",
                        "sat_combo": "terra_aqua"})
    grid = pd.concat([pd.DataFrame({"cell_id": CELL, "date": STRADDLE, "sat": sat, "n_det": snpp_per_day})
                      for sat in ("SNPP", "Terra")], ignore_index=True)
    cells = pd.DataFrame({"cell_id": [CELL], "landcover_dom": ["cropland"], "admin1_id": ["X"],
                          "lon_c": [0.0], "lat_c": [0.0]})
    return oof, grid, cells


def samples(oof, cells, daily):
    s = conformal._aggregate_samples(oof, cells, "test", 40, "month", np.random.default_rng(0), daily=daily)
    return s.groupby("period")[["y", "pred"]].first()


def test_month_samples_split_a_straddling_week_like_the_served_series():
    oof, grid, cells = fixture()
    got = samples(oof, cells, conformal.daily_oof(oof, grid))
    assert got.loc[pd.Timestamp("2021-03-01")].tolist() == [3.0, 3.0]
    assert got.loc[pd.Timestamp("2021-04-01")].tolist() == [4.0, 4.0]
    served = weekly_series(grid[grid["sat"] == "SNPP"].rename(columns={"n_det": "value_count"}), cells,
                           cell_ids=[CELL], res="month", start="2021-03-01", end="2021-04-30")
    assert served["value"].tolist() == [3.0, 4.0]


def test_legacy_target_without_daily_rows_is_whole_weeks_by_monday_month():
    oof, _, cells = fixture()
    got = samples(oof, cells, None)
    assert got.loc[pd.Timestamp("2021-03-01")].tolist() == [7.0, 7.0]
    assert conformal.month_target(None) == conformal.LEGACY_MONTH


def test_only_fully_covered_calendar_months_are_sampled():
    assert conformal._complete_months(WEEKS) == [pd.Timestamp("2021-03-01"), pd.Timestamp("2021-04-01")]
    assert conformal._complete_months(WEEKS[1:]) == [pd.Timestamp("2021-04-01")]   # 1-7 March missing


def test_daily_truth_must_add_up_to_weekly_truth():
    oof, grid, _ = fixture()
    grid.loc[grid["sat"] == "SNPP", "n_det"] = 2.0
    with pytest.raises(ValueError, match="disagrees"):
        conformal.daily_oof(oof, grid)


def test_report_separates_zero_predictions_with_positive_truth_and_reports_width():
    from ws4_outlook.interval_report import report
    oof, grid, cells = fixture()
    oof["y_pred_count"] = 0.0                                    # the model sees nothing; SNPP saw 7
    oof = pd.concat([oof, oof.assign(sat_combo="terra_only")], ignore_index=True)
    table = {"version": "t", "level": 0.9, "entries": [
        {"res": r, "stratum": "all", "max_value": None, "lo_mult": 0.5, "hi_mult": 1.5, "hi_add": 2.0} for r in ("week", "month")]}
    out = report(oof, cells, table, n=200, daily=conformal.daily_oof(oof, grid))
    rows = {r["stratum"]: r for r in out["rows"]}
    zero = rows["week | terra_aqua | prediction:zero_with_positive_truth"]
    assert zero["n"] > 0 and zero["coverage"] == 0.0 and zero["above_upper"] == 1.0   # hi = hi_add = 2 < 7
    assert zero["mean_width"] == 2.0
    assert out["month_target"] == conformal.CALENDAR_MONTH
