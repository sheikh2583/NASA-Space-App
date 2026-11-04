"""Shared fixtures for API tests that must run in CI without data/processed.

    def test_something(tiny_api):
        r = tiny_api.post("/aoi/summary", json=tiny_request("pb"))

`tiny_api` is a FastAPI TestClient whose Store reads the tiny folder from tiny_data.make_tiny_processed();
the module-level store and response cache are reset before and after each test.
"""
from __future__ import annotations

import pytest

from ws2_platform.tests.tiny_data import BD_BOX, PB_BOX, make_tiny_processed


def tiny_request(area: str, start: str = "2004-01-01", end: str = "2016-12-31", res: str = "week") -> dict:
    """Request body for one of the two tiny demo areas, shaped like the web app's (PB as a polygon, BD as a bbox)."""
    if area == "pb":
        x0, y0, x1, y1 = PB_BOX
        geom = {"type": "Polygon", "coordinates": [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]]}
        return {"geometry": geom, "start": start, "end": end, "res": res}
    return {"bbox": list(BD_BOX), "start": start, "end": end, "res": res}


@pytest.fixture(scope="session")
def tiny_processed(tmp_path_factory) -> str:
    return make_tiny_processed(tmp_path_factory.mktemp("tiny") / "processed")


@pytest.fixture
def tiny_api(tiny_processed, monkeypatch):
    from fastapi.testclient import TestClient
    from ws2_platform.api import app as appmod
    monkeypatch.setenv("DATA_DIR", tiny_processed)
    monkeypatch.setattr(appmod, "_store", None)
    appmod._cache.clear()
    with TestClient(appmod.app) as client:
        yield client
    appmod._cache.clear()
