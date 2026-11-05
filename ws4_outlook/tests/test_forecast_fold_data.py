"""Pure data preparation regressions; no forecast learner executes."""
import numpy as np
import pandas as pd

from common.climatology import season_of
from ws4_outlook.outlook import FEATS, forecast_fold, forecast_frame


def weekly():
    dates = pd.date_range("2010-10-04", "2020-09-28", freq="7D")
    return pd.DataFrame({"week_start": dates, "value": 10 + np.arange(len(dates)) % 17})


def test_held_out_and_future_values_cannot_change_training_or_reference():
    data = weekly()
    train, test = forecast_fold(data, 2018)
    altered = data.copy()
    altered.loc[season_of(altered.week_start).to_numpy() >= 2018, "value"] = 99999
    new_train, new_test = forecast_fold(altered, 2018)
    pd.testing.assert_frame_equal(train, new_train)
    pd.testing.assert_series_equal(test["clim"], new_test["clim"])
    pd.testing.assert_series_equal(test["target_clim"], new_test["target_clim"])


def test_targets_do_not_cross_fold_boundary():
    train, test = forecast_fold(weekly(), 2018)
    assert len(train) and len(test)
    assert (train.target_end < pd.Timestamp("2017-10-01")).all()
    assert (season_of(test.target_end) == 2018).all()
    assert (train.season < 2018).all()


def test_missing_calendar_week_does_not_shift_target_horizon():
    data = weekly()
    missing = data.iloc[300].week_start
    sparse = data[data.week_start != missing]
    frame = forecast_frame(sparse, reference=data.iloc[:200])
    issue = frame[frame.week_start == missing - pd.Timedelta(weeks=2)].iloc[0]
    assert pd.isna(issue.target)


def test_features_are_available_at_issue_time():
    data = weekly()
    issue = pd.Timestamp("2018-02-05")
    before = forecast_frame(data, reference=data.iloc[:200])
    altered = data.copy()
    altered.loc[altered.week_start > issue, "value"] = 100000
    after = forecast_frame(altered, reference=data.iloc[:200])
    pd.testing.assert_frame_equal(before.loc[before.week_start <= issue, FEATS],
                                  after.loc[after.week_start <= issue, FEATS])
