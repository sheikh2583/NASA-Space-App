"""Verified registry outages make sensor-days non-operating (plan card T06, decision 24). No data, no network."""
import datetime as dt

import pandas as pd

from ws2_platform import sensors


def grid(days=("2024-11-02", "2024-11-08")):
    d = pd.date_range(*days).date
    return pd.DataFrame({"sat": ["SNPP"] * len(d) + ["NOAA20"] * len(d), "date": list(d) * 2})


def cov(date, overlap, verification="table_and_data", event="snpp-2024-11-02-gps", region="PB", sat="SNPP"):
    return pd.DataFrame([{"sat": sat, "region": region, "date": dt.date.fromisoformat(date), "overlap_D": overlap,
                          "overlap_N": 0.0, "event_ids": event, "verification": verification}])


def snpp(sd):
    return sd[sd["sat"] == "SNPP"].set_index("date")


def in_range(s):
    """Only the test's own days: sensor_days also lists every earlier day, before the first data."""
    return s[s.index >= dt.date(2024, 11, 2)]


def test_a_verified_outage_day_is_not_operating_and_names_the_event():
    s = snpp(sensors.sensor_days(grid(), coverage_days=cov("2024-11-04", 1.0)))
    day = dt.date(2024, 11, 4)
    assert not s.loc[day, "operating"]
    assert "snpp-2024-11-02-gps" in s.loc[day, "note"] and "table_and_data" in s.loc[day, "note"]
    assert s.loc[dt.date(2024, 11, 3), "operating"] and s.loc[dt.date(2024, 11, 7), "operating"]


def test_unverified_rows_change_nothing():
    for v in ("transcribed", "rejected"):
        s = snpp(sensors.sensor_days(grid(), coverage_days=cov("2024-11-04", 1.0, verification=v)))
        assert in_range(s)["operating"].all(), v


def test_threshold_keeps_a_small_overlap_at_quarter_and_drops_it_at_zero():
    day = dt.date(2024, 11, 4)
    assert snpp(sensors.sensor_days(grid(), coverage_days=cov("2024-11-04", 0.1), threshold=0.25)).loc[day, "operating"]
    assert not snpp(sensors.sensor_days(grid(), coverage_days=cov("2024-11-04", 0.1), threshold=0.0)).loc[day, "operating"]


def test_any_region_is_enough_and_other_satellites_are_untouched():
    c = pd.concat([cov("2024-11-05", 0.0, region="BD"), cov("2024-11-05", 0.9, region="PB")], ignore_index=True)
    sd = sensors.sensor_days(grid(), coverage_days=c)
    assert not snpp(sd).loc[dt.date(2024, 11, 5), "operating"]
    assert in_range(sd[sd["sat"] == "NOAA20"].set_index("date"))["operating"].all()


def test_without_a_coverage_table_nothing_changes():
    assert sensors.sensor_days(grid()).equals(sensors.sensor_days(grid(), coverage_days=None))
