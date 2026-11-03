"""Every endpoint against contracts/openapi.yaml (prompt P6.2). Run against the mock or live API:
    API_BASE_URL=http://localhost:8001 pytest ws6_validation/tests/test_contract.py
"""
import pytest
from openapi_schema_validator import OAS30Validator

BD = {"bbox": [89.5, 23.0, 90.5, 24.0], "start": "2015-01-01", "end": "2016-12-31", "res": "week"}
PB = {"geometry": {"type": "Polygon", "coordinates": [[[74.6, 29.8], [76.4, 29.8], [76.4, 31.2], [74.6, 31.2], [74.6, 29.8]]]},
      "start": "2015-01-01", "end": "2016-12-31", "res": "week"}


def validate(spec, schema_name, doc):
    v = OAS30Validator({"$ref": f"#/components/schemas/{schema_name}", "components": spec["components"]})
    errors = list(v.iter_errors(doc))
    assert not errors, f"{schema_name}: " + "; ".join(f"{list(e.path)}: {e.message}" for e in errors[:5])


@pytest.mark.parametrize("req", [BD, PB], ids=["bangladesh", "punjab"])
@pytest.mark.parametrize("path,schema", [
    ("/aoi/summary", "SummaryResponse"), ("/aoi/cells", "CellsResponse"),
    ("/aoi/critical-periods", "CriticalPeriodsResponse"), ("/aoi/drivers", "DriversResponse"),
    ("/aoi/outlook", "OutlookResponse")])
def test_aoi_endpoints(client, spec, req, path, schema):
    r = client.post(path, json=req)
    assert r.status_code == 200, r.text[:300]
    body = r.json()
    validate(spec, schema, body)
    assert body["day_convention"] == "local_solar_date" and body["schema_version"] and body["units"]


def test_every_summary_point_has_a_source(client):
    s = client.post("/aoi/summary", json=BD).json()["series"]
    assert s and all(p["source"] in ("observed_viirs", "adjusted_from_noaa20", "modeled_from_modis", "mixed") for p in s)


def test_compare(client, spec):
    r = client.post("/aoi/compare", json={"a": BD, "b": PB})
    assert r.status_code == 200
    validate(spec, "CompareResponse", r.json())


def test_meta_validation(client, spec):
    r = client.get("/meta/validation")
    assert r.status_code == 200
    validate(spec, "ValidationResponse", r.json())


def test_export_csv(client):
    r = client.post("/export", json={**BD, "view": "summary"})
    assert r.status_code == 200 and r.text.splitlines()[0].startswith("t,value,lo,hi,source")


def test_empty_aoi_returns_empty_series_with_note(client):
    r = client.post("/aoi/summary", json={"bbox": [0, 0, 0.5, 0.5], "start": "2016-01-01", "end": "2016-12-31", "res": "week"})
    assert r.status_code == 200 and r.json()["series"] == [] and r.json()["notes"]


def test_oversized_aoi_is_422(client, spec):
    r = client.post("/aoi/summary", json={"bbox": [60, 5, 100, 40], "start": "2016-01-01", "end": "2016-12-31", "res": "week"})
    assert r.status_code == 422
    validate(spec, "Error", r.json())


def test_invalid_request_is_422(client):
    assert client.post("/aoi/summary", json={"start": "2016-01-01", "end": "2016-12-31"}).status_code == 422
