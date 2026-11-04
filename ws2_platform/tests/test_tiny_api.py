"""The tiny API fixture works end to end and its responses satisfy the published contract.
New endpoint tests (plan cards T04, T07, T11, T18, T22) build on `tiny_api` and `tiny_request`."""
import os

import pytest
import yaml
from openapi_schema_validator import OAS30Validator

from ws2_platform.tests.conftest import tiny_request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="module")
def spec():
    with open(os.path.join(ROOT, "contracts", "openapi.yaml")) as f:
        return yaml.safe_load(f)


def _valid(spec, name, doc):
    v = OAS30Validator({"$ref": f"#/components/schemas/{name}", "components": spec["components"]})
    errors = list(v.iter_errors(doc))
    assert not errors, f"{name}: " + "; ".join(f"{list(e.path)}: {e.message}" for e in errors[:5])


def test_health_reports_the_tiny_data(tiny_api):
    h = tiny_api.get("/health").json()
    assert h["method_version"] == "tiny-test" and h["data_through"] == "2016-12-31" and h["cells"] == 8


@pytest.mark.parametrize("area", ["pb", "bd"])
@pytest.mark.parametrize("path,schema", [("/aoi/summary", "SummaryResponse"), ("/aoi/critical-periods", "CriticalPeriodsResponse"),
                                         ("/aoi/outlook", "OutlookResponse"), ("/aoi/drivers", "DriversResponse")])
def test_endpoints_match_the_contract(tiny_api, spec, area, path, schema):
    r = tiny_api.post(path, json=tiny_request(area))
    assert r.status_code == 200, r.text[:300]
    _valid(spec, schema, r.json())


def test_summary_keeps_sources_apart_and_selects_the_right_cells(tiny_api):
    s = tiny_api.post("/aoi/summary", json=tiny_request("pb")).json()
    assert s["aoi"]["n_cells"] == 4
    sources = {p["source"] for p in s["series"]}
    assert {"modeled_from_modis", "observed_viirs"} <= sources
    observed = [p for p in s["series"] if p["source"] == "observed_viirs" and p["value"] is not None]
    assert observed and all(p["lo"] == p["value"] == p["hi"] for p in observed)   # decision 21


def test_empty_area_and_oversized_area(tiny_api):
    empty = tiny_api.post("/aoi/summary", json={"bbox": [0, 0, 0.5, 0.5], "start": "2010-01-01", "end": "2010-12-31"})
    assert empty.status_code == 200 and empty.json()["series"] == []
    big = tiny_api.post("/aoi/summary", json={"bbox": [60, 5, 100, 40], "start": "2010-01-01", "end": "2010-12-31"})
    assert big.status_code == 422
