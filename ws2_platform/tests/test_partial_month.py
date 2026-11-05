import pytest
from ws2_platform.tests.conftest import tiny_request


@pytest.mark.parametrize("start,end,days,complete", [
    ("2016-12-15", "2016-12-31", 17, False),
    ("2016-12-01", "2016-12-31", 31, True),
    ("2016-12-15", "2016-12-20", 6, False),
    ("2016-12-31", "2017-01-10", 1, False),
    ("2016-02-01", "2016-02-29", 29, True),
])
def test_month_coverage_matches_actual_requested_days(tiny_api, start, end, days, complete):
    response = tiny_api.post("/aoi/summary", json=tiny_request("pb", start=start, end=end, res="month"))
    assert response.status_code == 200
    series = response.json()["series"]
    assert len(series) == 1
    assert series[0]["n_days"] == days
    assert series[0]["complete"] is complete
