"""Small hand-computed serving cases; synthetic frames only, no learners or scientific files."""
import numpy as np
import pandas as pd

from common.series import day_sources, weekly_series
from ws2_platform.api.query import Store
from ws2_platform.api import app as api
from ws2_platform.api import query
from common import series


def frames():
    cells = pd.DataFrame({"cell_id": [1], "admin1_id": ["r"], "landcover_dom": ["cropland"]})
    days = pd.date_range("2026-10-26", "2026-11-15")
    h = pd.DataFrame({"cell_id": [1] * len(days), "date": days, "value_count": [4.0] * len(days)})
    rows = []
    for day in days:
        observed = day < pd.Timestamp("2026-11-02") and day != pd.Timestamp("2026-10-28")
        adjusted = (day == pd.Timestamp("2026-10-28") or pd.Timestamp("2026-11-02") <= day <= pd.Timestamp("2026-11-08")) and day != pd.Timestamp("2026-11-03")
        rows.extend([(day, "SNPP", observed), (day, "NOAA20", adjusted)])
    sd = pd.DataFrame(rows, columns=["date", "sat", "operating"])
    table = {"entries": [{"res": res, "stratum": "all", "max_value": None,
                           "lo_mult": .5, "hi_mult": 2, "hi_add": 1} for res in ("week", "month")]}
    return h, cells, sd, table


def test_mixed_cutoff_and_no_sensor_weeks_keep_exact_totals_and_intervals():
    h, cells, sd, table = frames()
    result = weekly_series(h, cells, sensor_days=sd, table=table, start="2026-10-26", end="2026-11-15")
    first, second, missing = [row for _, row in result.iterrows()]
    assert (first.value, first.lo, first.hi, first.source) == (28, 26, 33, "mixed")
    assert first.modeled_share == 4 / 28
    assert (second.value, second.lo, second.hi, second.source) == (24, 12, 49, "adjusted_from_noaa20")
    assert second.modeled_share == 1
    assert np.isnan(missing.value) and np.isnan(missing.lo) and np.isnan(missing.hi)
    assert missing.source is None


def test_partial_calendar_month_and_day_missingness_keep_existing_semantics():
    h, cells, sd, table = frames()
    result = weekly_series(h, cells, sensor_days=sd, table=table, res="month", start="2026-10-28", end="2026-11-05")
    october, november = [row for _, row in result.iterrows()]
    assert (october.value, october.lo, october.hi) == (16, 14, 21)
    assert (november.value, november.lo, november.hi) == (16, 10, 29)
    daily = weekly_series(h, cells, sensor_days=sd, res="day", start="2026-11-02", end="2026-11-04")
    assert daily.value.iloc[0] == 4 and np.isnan(daily.value.iloc[1]) and daily.value.iloc[2] == 4


def test_agricultural_totals_match_full_series_including_float32_and_empty_selections():
    h, cells, sd, _ = frames()
    for crop in (.5, .3):
        s = object.__new__(Store)
        s.cells, s.sensor_days = cells, sd
        s.harmonized = h.assign(value_count=h.value_count.astype("float32"), cropland_frac=np.float32(crop))
        s.source_calendar = day_sources(sd, sd.date.min(), sd.date.max())
        for selected in (cells, cells.iloc[:0]):
            reference = weekly_series(
                s.harmonized.assign(value_count=s.harmonized.value_count * s.harmonized.cropland_frac.fillna(0)),
                cells, cell_ids=selected.cell_id, sensor_days=sd, start="2026-10-26", end="2026-11-15",
            )["value"]
            actual = s.agri_series(selected, "2026-10-26", "2026-11-15")
            pd.testing.assert_series_equal(actual, reference, check_exact=True)
            if crop == .5 and not selected.empty:
                assert actual.iloc[:2].tolist() == [14, 12]
                assert np.isnan(actual.iloc[2])


def test_store_reuses_source_calendar_and_preserves_dates_outside_its_range(tiny_api, monkeypatch):
    s = api.store()
    selected = s.cells
    start, end = "2003-12-20", "2004-01-10"
    expected = weekly_series(s.harmonized, s.cells, cell_ids=selected.cell_id,
                             start=start, end=end, sensor_days=s.sensor_days, table=s.table)
    weighted = s.harmonized.assign(value_count=s.harmonized.value_count * s.harmonized.cropland_frac.fillna(0))
    expected_agri = weekly_series(weighted, s.cells, cell_ids=selected.cell_id,
                                  start=start, end=end, sensor_days=s.sensor_days)["value"]

    def repeated(*args, **kwargs):
        raise AssertionError("Store requests must reuse the precomputed source calendar")

    monkeypatch.setattr(series, "day_sources", repeated)
    monkeypatch.setattr(query, "day_sources", repeated)
    pd.testing.assert_frame_equal(s.series(selected, start, end), expected, check_exact=True)
    pd.testing.assert_series_equal(s.agri_series(selected, start, end), expected_agri, check_exact=True)
