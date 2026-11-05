"""Named AOI transport and exact membership checks; no fitting or production artifact writes."""
import json
from pathlib import Path

import numpy as np
import pytest
import yaml
from fastapi.testclient import TestClient
from openapi_schema_validator import OAS30Validator

from ws2_platform.api import app as api
from ws2_platform.api.query import Store
from ws2_platform.tests.conftest import tiny_request

ROOT = Path(__file__).resolve().parents[2]


def test_named_request_fixture_and_exclusive_area_contract():
    request = json.loads((ROOT / "contracts/fixtures/named_area_request.json").read_text())
    spec = yaml.safe_load((ROOT / "contracts/openapi.yaml").read_text(encoding="utf-8"))
    validator = OAS30Validator({"$ref": "#/components/schemas/AOIRequest", "components": spec["components"]})
    assert not list(validator.iter_errors(request))
    assert list(validator.iter_errors({**request, "bbox": [75, 30, 76, 31]}))
    assert list(validator.iter_errors({**request, "area_id": ""}))


def test_named_area_matches_polygon_for_every_api_product(tiny_api, tmp_path, monkeypatch):
    # Only one of Punjab's four admin-assigned cells lies in this polygon.
    geometry = {"type": "Polygon", "coordinates": [[[75, 30], [75.1, 30], [75.1, 30.1], [75, 30.1], [75, 30]]]}
    public = tmp_path / "public"
    (public / "demo").mkdir(parents=True)
    (public / "demo/areas.json").write_text(json.dumps({"areas": [{"id": "one-cell", "request": {"geometry": geometry}}]}))
    monkeypatch.setenv("FRONTEND_DIR", str(public))
    common = {"start": "2011-12-20", "end": "2012-02-20", "res": "week"}
    named, polygon = {**common, "area_id": "one-cell"}, {**common, "geometry": geometry}
    for endpoint in ("summary", "cells", "critical-periods", "outlook", "season", "drivers"):
        api._cache.clear()
        expected = tiny_api.post(f"/aoi/{endpoint}", json=polygon)
        api._cache.clear()
        actual = tiny_api.post(f"/aoi/{endpoint}", json=named)
        assert actual.status_code == expected.status_code == 200
        assert actual.json() == expected.json()
    s = api.store()
    assert len(s.select(area_id="one-cell")) == 1
    assert len(s.cells[s.cells.admin1_id == "PB-1"]) == 4
    for body in ({**named, "bbox": [75, 30, 76, 31]}, {**named, "geometry": geometry}, {**common, "area_id": "unknown"}, common):
        assert tiny_api.post("/aoi/summary", json=body).status_code == 422
    assert tiny_api.post("/export", json={**named, "view": "summary"}).status_code == 200
    assert tiny_api.post("/aoi/compare", json={"a": named, "b": polygon}).json()["a"] == tiny_api.post("/aoi/summary", json=named).json()


@pytest.mark.skipif(not (ROOT / "data/processed/harmonized.parquet").is_file(), reason="Saved artifacts absent")
def test_all_eleven_saved_catalog_memberships_equal_original_polygons_and_counts(monkeypatch):
    monkeypatch.setenv("FRONTEND_DIR", str(ROOT / "ws5_frontend/public"))
    s = Store(str(ROOT / "data/processed"))
    catalog = json.loads((ROOT / "ws5_frontend/public/demo/areas.json").read_text(encoding="utf-8"))
    assert len(catalog["areas"]) == 11
    for area in catalog["areas"]:
        by_id = s.select(area_id=area["id"])
        original = s.select(geometry=area["request"]["geometry"])
        assert np.array_equal(by_id.cell_id.to_numpy(), original.cell_id.to_numpy())
        assert len(by_id) == area["cellCount"]


def test_mock_routes_named_country_and_rejects_unknown_ids():
    from ws2_platform.api.mock_server import app
    request = json.loads((ROOT / "contracts/fixtures/named_area_request.json").read_text())
    with TestClient(app) as client:
        result = client.post("/aoi/summary", json=request)
        assert result.status_code == 200
        assert result.json() == json.loads((ROOT / "contracts/fixtures/punjab_summary.json").read_text())
        assert client.post("/aoi/summary", json={**request, "area_id": "unknown"}).status_code == 422
