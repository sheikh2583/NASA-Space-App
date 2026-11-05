import numpy as np
import pandas as pd

from common.grid import N_COLS
from ws4_outlook import conformal
from ws4_outlook.interval_report import report


def _data():
    cell_ids = np.array([i * N_COLS + j for i in range(20) for j in range(20)], dtype="int32")
    cells = pd.DataFrame({"cell_id": cell_ids, "landcover_dom": "cropland"})
    dates = pd.date_range("2019-01-01", periods=48, freq="MS")
    # Four of 48 periods fall outside the interval, giving expected coverage close to 90%.
    multipliers = np.ones(len(dates))
    multipliers[[7, 18, 29, 40]] = 2.0
    frames = []
    for sat_combo in ("terra_aqua", "terra_only"):
        for date, multiplier in zip(dates, multipliers):
            frames.append(pd.DataFrame({
                "cell_id": cell_ids,
                "date": date,
                "y_true_count": 10.0 * multiplier,
                "y_pred_count": 10.0,
                "y_true_frp": 0.0,
                "y_pred_frp": 0.0,
                "fold": 0,
                "block_id": 1,
                "split": "test",
                "sat_combo": sat_combo,
            }))
    return pd.concat(frames, ignore_index=True), cells


def _table():
    return {
        "version": "test",
        "level": 0.9,
        "entries": [
            {"res": res, "stratum": "all", "max_value": None,
             "lo_mult": 0.5, "hi_mult": 1.5, "hi_add": 0.0}
            for res in ("week", "month")
        ],
    }


def test_aggregate_defaults_match_explicit_legacy_parameters_and_add_area_size():
    oof, cells = _data()
    a = conformal._aggregate_samples(oof, cells, "test", 40, "week", np.random.default_rng(3))
    b = conformal._aggregate_samples(
        oof, cells, "test", 40, "week", np.random.default_rng(3),
        sat_combo="terra_aqua", max_side=10,
    )
    pd.testing.assert_frame_equal(a, b)
    assert a["n_cells"].between(1, 100).all()


def test_report_has_finite_metrics_and_every_requested_stratum():
    oof, cells = _data()
    result = report(oof, cells, _table(), n=2200, seed=7)
    rows = pd.DataFrame(result["rows"])

    overall = rows[rows["dimension"] == "satellite_combination"]
    assert overall["n"].ge(2000).all()
    assert overall["coverage"].between(0.85, 0.95).all()
    assert np.isfinite(overall["interval_score"]).all()
    assert result["nominal"] == 0.9

    expected = {
        "area_size": {"1-10", "11-50", "51-100", "101-400"},
        "magnitude": {"zero", "q1", "q2", "q3", "q4"},
        "season": {"q1", "q2", "q3", "q4"},
        "satellite_combination": {"terra_aqua", "terra_only"},
    }
    for dimension, values in expected.items():
        assert set(rows.loc[rows["dimension"] == dimension, "value"]) == values
    assert (rows.loc[rows["n"] < 30, "note"] == "too few samples").all()
