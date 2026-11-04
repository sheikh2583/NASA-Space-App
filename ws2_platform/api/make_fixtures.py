"""Write contracts/fixtures/ from the running pipeline (prompt P2.1): one request and one response per endpoint for
a Bangladesh AOI and a Punjab AOI. Values come from SYNTHETIC data while real data is not loaded; the
fixtures fix the shapes, not the numbers.

Usage: python -m ws2_platform.api.make_fixtures
"""
from __future__ import annotations

import json
import os

from fastapi.testclient import TestClient

from ws2_platform.api.app import app, store

OUT = "contracts/fixtures"
AOIS = {
    "bangladesh": {"bbox": [89.5, 23.0, 90.5, 24.0], "start": "2000-11-01", "end": None, "res": "week"},
    "punjab": {"geometry": {"type": "Polygon", "coordinates": [[[74.6, 29.8], [76.4, 29.8], [76.4, 31.2], [74.6, 31.2], [74.6, 29.8]]]},
               "start": "2000-11-01", "end": None, "res": "week"},
}


def dump(name, obj):
    with open(os.path.join(OUT, name), "w") as f:
        json.dump(obj, f, indent=1 if "request" in name else None, separators=None if "request" in name else (",", ":"))


def main():
    os.makedirs(OUT, exist_ok=True)
    c = TestClient(app)
    end = store().data_end.date().isoformat()
    for name, req in AOIS.items():
        req = {**req, "end": end}
        dump(f"{name}_request.json", req)
        for path in ("summary", "critical-periods", "drivers", "outlook", "season"):
            dump(f"{name}_{path}.json", c.post(f"/aoi/{path}", json=req).json())
        recent = {**req, "start": "2025-10-01"}
        dump(f"{name}_cells_request.json", recent)
        dump(f"{name}_cells.json", c.post("/aoi/cells", json=recent).json())
    pair = {"a": {**AOIS["bangladesh"], "end": end, "start": "2016-01-01"}, "b": {**AOIS["punjab"], "end": end, "start": "2016-01-01"}}
    dump("compare_request.json", pair)
    dump("compare.json", c.post("/aoi/compare", json=pair).json())
    dump("meta_validation.json", c.get("/meta/validation").json())
    dump("empty_request.json", {"bbox": [0, 0, 0.5, 0.5], "start": "2016-01-01", "end": "2016-12-31", "res": "week"})
    dump("oversized_request.json", {"bbox": [60, 5, 100, 40], "start": "2016-01-01", "end": "2016-12-31", "res": "week"})
    print("fixtures ->", OUT, sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
