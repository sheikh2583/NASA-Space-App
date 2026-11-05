"""Periods that run past the last day with data are marked incomplete (plan card T04). Tiny data ends Sat 31 Dec 2016."""
import os

import yaml
from openapi_schema_validator import OAS30Validator

from ws2_platform.tests.conftest import tiny_request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _assert_valid_summary(doc):
    with open(os.path.join(ROOT, "contracts", "openapi.yaml"), encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    v = OAS30Validator({"$ref": "#/components/schemas/SummaryResponse", "components": spec["components"]})
    errors = list(v.iter_errors(doc))
    assert not errors, "; ".join(f"{list(e.path)}: {e.message}" for e in errors[:5])


def test_last_week_is_partial_and_earlier_weeks_are_complete(tiny_api):
    doc = tiny_api.post("/aoi/summary", json=tiny_request("pb")).json()
    _assert_valid_summary(doc)
    pts = doc["series"]
    last = [p for p in pts if p["t"] == "2016-12-26"]
    assert len(last) == 1 and last[0]["complete"] is False and last[0]["n_days"] == 6
    # The tiny record starts on Thursday 1 Jan 2004: its first week has 4 observed days and is not complete.
    first = [p for p in pts if p["t"] == "2003-12-29"]
    assert len(first) == 1 and first[0]["complete"] is False and first[0]["n_days"] == 4
    earlier = [p for p in pts if "2003-12-29" < p["t"] < "2016-12-26"]
    assert earlier and all(p["complete"] is True and p["n_days"] == 7 for p in earlier)


def test_month_cut_by_the_requested_end_is_partial(tiny_api):
    doc = tiny_api.post("/aoi/summary", json=tiny_request("pb", end="2016-12-15", res="month")).json()
    _assert_valid_summary(doc)
    last = doc["series"][-1]
    assert last["t"].startswith("2016-12") and last["complete"] is False and last["n_days"] == 15
    assert all(p["complete"] is True for p in doc["series"][:-1])


def test_days_are_always_complete(tiny_api):
    doc = tiny_api.post("/aoi/summary", json=tiny_request("bd", start="2016-12-20", end="2016-12-31", res="day")).json()
    _assert_valid_summary(doc)
    assert doc["series"] and all(p["complete"] is True and p["n_days"] == 1 for p in doc["series"])
