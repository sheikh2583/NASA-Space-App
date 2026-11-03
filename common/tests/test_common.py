import datetime as dt
import math

import numpy as np
import pandas as pd
import pytest

from common import climatology, grid, intervals, metrics, series, splits


# grid ---------------------------------------------------------------------------------------------
def test_grid_lines_never_misbin():
    lats = np.arange(-900, 900) / 10
    rows = grid.cell_id(lats, np.zeros_like(lats)) // grid.N_COLS
    assert (rows == np.arange(1800)).all()


def test_grid_edges_clamped_and_distinct():
    assert grid.cell_id(90.0, 0.0) // grid.N_COLS == 1799
    assert grid.cell_id(10.05, 180.0) != grid.cell_id(10.15, -180.0)
    assert grid.cell_id(23.7, 90.0) // grid.N_COLS == 1137


def test_cell_center_roundtrip():
    cid = grid.cell_id(23.73, 90.41)
    lat, lon = grid.cell_center(cid)
    assert grid.cell_id(lat, lon) == cid and abs(lat - 23.75) < 1e-9 and abs(lon - 90.45) < 1e-9


def test_local_solar_date_moves_night_pass():
    # 19:30 UTC at lon 90 is 01:30 local solar time the next day
    d = grid.local_solar_date(["2024-03-01"], [1930], [90.0])
    assert d.iloc[0] == dt.date(2024, 3, 2)


# climatology --------------------------------------------------------------------------------------
def test_week_53_folded():
    assert climatology.week_of_year(["2020-12-28"]).iloc[0] == 52


def test_same_week_quantiles_hand_example():
    weeks = pd.date_range("2015-01-05", periods=5 * 52, freq="7D")
    df = pd.DataFrame({"week_start": weeks, "value": np.tile(np.arange(52, dtype=float), 5)})
    qs = climatology.same_week_quantiles(df, [0.5], window=0)
    assert qs.loc[qs["week"] == 10, "q50"].iloc[0] == pytest.approx(9.0)


def test_season_helpers():
    assert climatology.season_of(["2020-10-01", "2020-09-30"]).tolist() == [2021, 2020]
    assert climatology.day_of_season(["2020-10-03"]).iloc[0] == 2


# intervals ----------------------------------------------------------------------------------------
TABLE = {"version": "t", "level": 0.9, "entries": [
    {"res": "week", "stratum": "region:A|month:1", "max_value": 10, "lo_mult": 0.5, "hi_mult": 2.0, "hi_add": 1},
    {"res": "week", "stratum": "region:A|month:1", "max_value": None, "lo_mult": 0.8, "hi_mult": 1.3, "hi_add": 0},
    {"res": "week", "stratum": "all", "max_value": None, "lo_mult": 0.6, "hi_mult": 1.6, "hi_add": 0}]}


def test_interval_specific_stratum_and_bins():
    assert intervals.apply_interval(5, "week", "region:A|month:1", TABLE) == (2.5, 11.0)
    assert intervals.apply_interval(100, "week", "region:A|month:1", TABLE) == pytest.approx((80, 130))


def test_interval_fallbacks():
    assert intervals.apply_interval(10, "week", ["missing"], TABLE) == pytest.approx((6, 16))
    assert intervals.apply_interval(10, "month", "x", TABLE) == (None, None)
    lo, hi = intervals.apply_interval(10, "week", "region:A|month:1", TABLE)
    assert lo <= 10 <= hi


# splits -------------------------------------------------------------------------------------------
def test_splits_deterministic_and_proportions():
    cid = grid.cells_in_bbox(70, 10, 100, 35)
    a, b = splits.split_label(cid), splits.split_label(cid)
    assert (a == b).all()
    blocks = pd.Series(splits.block_id(cid)).unique()
    assert set(np.unique(a)) == {"train", "calib", "test"} and len(blocks) > 50


def test_buffer_only_on_train_cells_next_to_heldout_blocks():
    cid = grid.cells_in_bbox(70, 10, 100, 35)
    f = splits.labels_frame(cid)
    assert (f.loc[f["buffer"], "split"] == "train").all() and f["buffer"].any()


def test_backward_holdout_disjoint():
    yrs = np.arange(2001, 2027)
    tr, te = splits.backward_holdout(yrs)
    assert not (tr & te).any() and te.sum() == 3


# metrics ------------------------------------------------------------------------------------------
def test_metrics_perfect_and_biased():
    y = np.array([0, 1, 2, 5, 10.0])
    assert metrics.relative_bias(y, y) == 0 and metrics.lins_ccc(y, y) == pytest.approx(1)
    assert metrics.relative_bias(y, 2 * y) == pytest.approx(1.0)
    assert metrics.coverage(y, y - 1, y + 1) == 1.0
    assert metrics.interval_score([5], [6], [7], alpha=0.1) == pytest.approx(1 + 20)


# series -------------------------------------------------------------------------------------------
def _toy():
    cells = pd.DataFrame({"cell_id": [1, 2, 3], "lat_c": [23.05, 23.15, 30.0], "lon_c": [90.05, 90.15, 75.0],
                          "admin1_id": ["A", "A", "B"], "landcover_dom": ["cropland"] * 3})
    days = pd.date_range("2011-12-26", "2012-02-05", freq="D")
    rows = []
    for d in days:
        src = "modeled_from_modis" if d < pd.Timestamp("2012-01-20") else "observed_viirs"
        rows += [(1, d, 2.0, src), (2, d, 1.0, src), (3, d, 50.0, src)]
    h = pd.DataFrame(rows, columns=["cell_id", "date", "value_count", "source"])
    h["drift_flag"] = False
    sd = []
    for d in days:
        sd += [(d, "Terra", True), (d, "Aqua", True), (d, "SNPP", d >= pd.Timestamp("2012-01-20"))]
    sd = pd.DataFrame(sd, columns=["date", "sat", "operating"])
    return h, cells, sd


def test_series_totals_and_share():
    h, cells, sd = _toy()
    s = series.weekly_series(h, cells, region_ids=["A"], sensor_days=sd, start="2011-12-26", end="2012-02-05")
    assert s["value"].sum() == pytest.approx(3.0 * 42)
    first, last = s.iloc[0], s.iloc[-1]
    assert first["source"] == "modeled_from_modis" and first["modeled_share"] == 1
    assert last["source"] == "observed_viirs" and last["modeled_share"] == 0
    assert (s["source"] == "mixed").sum() == 1
    assert pd.Timestamp(s["week_start"].iloc[1]).dayofweek == 0


def test_series_days_without_sensor_are_nan_not_zero():
    h, cells, sd = _toy()
    sd = sd[~((sd["sat"].isin(["Terra", "Aqua"])) & (sd["date"] < "2012-01-02"))]
    s = series.weekly_series(h, cells, bbox=(90, 23, 90.2, 23.2), sensor_days=sd, start="2011-12-26", end="2012-01-15")
    assert math.isnan(s["value"].iloc[0])


def test_series_intervals_only_on_nonobserved_part():
    h, cells, sd = _toy()
    s = series.weekly_series(h, cells, region_ids=["A"], sensor_days=sd, start="2011-12-26", end="2012-02-05", table=TABLE)
    obs = s[s["source"] == "observed_viirs"]
    assert (obs["lo"] == obs["value"]).all() and (obs["hi"] == obs["value"]).all()
    mod = s[s["source"] == "modeled_from_modis"]
    assert (mod["lo"] < mod["value"]).all() and (mod["hi"] > mod["value"]).all()
