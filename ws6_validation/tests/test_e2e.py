"""End-to-end demo path (prompt P6.4): Bangladesh AOI, then Punjab in October-November, plus the fallback."""
import json
import os

import pytest

from conftest import ROOT

BD = {"bbox": [89.5, 23.0, 90.5, 24.0], "start": "2000-11-01", "end": "2026-11-02", "res": "week"}
PB = {"geometry": {"type": "Polygon", "coordinates": [[[74.6, 29.8], [76.4, 29.8], [76.4, 31.2], [74.6, 31.2], [74.6, 29.8]]]},
      "start": "2000-11-01", "end": "2026-11-02", "res": "week"}


@pytest.mark.parametrize("req", [BD, PB], ids=["bangladesh", "punjab"])
def test_demo_path(client, req):
    s = client.post("/aoi/summary", json=req).json()
    pts = s["series"]
    assert len(pts) > 1000, "full record expected"
    sources = {p["source"] for p in pts}
    assert {"modeled_from_modis", "observed_viirs"} <= sources
    assert "2012-01-20" in s["seams"]
    before = [p for p in pts if p["t"] < "2012-01-16"]
    assert all(p["modeled_share"] == 1 for p in before if p["value"])
    assert any(p.get("anomaly", {}).get("flag") for p in pts), "no flagged weeks"
    assert any(p["lo"] is not None and p["hi"] is not None and p["hi"] > p["lo"] for p in before), "modeled weeks need intervals"
    o = client.post("/aoi/outlook", json=req).json()
    assert o["current_status"]["data_through"] and o["current_status"]["level"] in ("very_low", "low", "none", "watch", "high")
    c = client.post("/aoi/cells", json={**req, "start": "2016-10-01", "end": "2016-11-30"}).json()
    assert c["cells"], "where layer empty for a burning season"


def test_punjab_october_november_is_a_critical_period(client):
    ps = client.post("/aoi/critical-periods", json=PB).json()["periods"]
    months = [p["start"][5:7] for p in ps[:5]]
    assert any(m in ("09", "10", "11") for m in months)


def test_static_fallback_has_every_region():
    idx = os.path.join(ROOT, "ws2_platform", "static_fallback", "index.json")
    if not os.path.exists(idx):
        pytest.skip("static fallback not exported yet")
    index = json.load(open(idx))
    for r in index["regions"]:
        d = os.path.join(os.path.dirname(idx), "regions", r["region_id"])
        for f in ("summary", "critical-periods", "outlook", "drivers", "cells"):
            assert os.path.exists(os.path.join(d, f"{f}.json")), (r["region_id"], f)
