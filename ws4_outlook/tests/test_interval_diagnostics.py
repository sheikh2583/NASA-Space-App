import numpy as np
import pandas as pd
from ws4_outlook.conformal import _aggregate_samples
from ws4_outlook.interval_report import _magnitude_labels, report, stop_rows


def fixture():
    oof = pd.DataFrame({"cell_id": [1], "date": ["2020-01-06"], "split": ["test"],
                        "sat_combo": ["terra_only"], "block_id": [0],
                        "y_true_count": [1.0], "y_pred_count": [0.0]})
    cells = pd.DataFrame({"cell_id": [1], "landcover_dom": ["cropland"]})
    return oof, cells


def test_one_available_cell_never_reports_rectangle_area():
    oof, cells = fixture()
    samples = _aggregate_samples(oof, cells, "test", 100, "week", np.random.default_rng(7),
                                 sat_combo="terra_only", max_side=20)
    assert samples.n_cells.eq(1).all()
    assert samples.drawn_n_cells.max() > 1
    assert samples.y.eq(1).all()


def test_other_block_and_duplicate_month_rows_do_not_inflate_cell_count():
    oof, cells = fixture()
    other = oof.assign(cell_id=2, block_id=1, y_true_count=9999)
    oof = pd.concat([oof, oof.assign(date="2020-01-13"), other])
    cells = pd.concat([cells, cells.assign(cell_id=2)])
    samples = _aggregate_samples(oof, cells, "test", 50, "month", np.random.default_rng(7),
                                 sat_combo="terra_only", max_side=20)
    assert samples.n_cells.eq(1).all()
    assert set(samples.y).issubset({2, 9999})


def test_missing_satellite_combination_reports_empty_groups():
    oof, cells = fixture()
    table = {"entries": [{"res": res, "stratum": "all", "max_value": None,
                          "lo_mult": 0, "hi_mult": 1, "hi_add": 2} for res in ("week", "month")]}
    result = report(oof, cells, table, n=10)
    empty = [r for r in result["rows"] if r["sat_combo"] == "terra_aqua"]
    assert empty and all(r["n"] == 0 and r["coverage"] is None for r in empty)
    assert list(_magnitude_labels(pd.Series([0, 1]))) == ["zero", "q1"]


def test_stop_rule_includes_season_and_magnitude_not_only_area():
    rows = [{"dimension": dimension, "n": 500, "coverage": .79}
            for dimension in ("season", "magnitude", "area_size", "satellite_combination")]
    assert stop_rows(rows) == rows
    assert not stop_rows([{"n": 499, "coverage": .1}, {"n": 500, "coverage": .8}])
