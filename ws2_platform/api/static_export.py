"""Static fallback (prompt P2.7): API-shaped JSON for every admin1 region, deployable on any static host.

Layout (URL pattern for the web app, VITE_FALLBACK_BASE_URL = the folder's URL):
  index.json                              regions with bbox, name, country, data_through
  regions/<admin1_id>/summary.json        /aoi/summary for the region, weekly, full record
  regions/<admin1_id>/critical-periods.json, outlook.json, drivers.json, cells.json (last 52 weeks)
  meta/validation.json

Usage: python -m ws2_platform.api.static_export --out ws2_platform/static_fallback
"""
from __future__ import annotations

import argparse
import json
import os

import pandas as pd
from fastapi.testclient import TestClient

from ws2_platform.api.app import app, store


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="ws2_platform/static_fallback")
    a = ap.parse_args(argv)
    c = TestClient(app)
    s = store()
    end = s.data_end.date()
    index = {"schema_version": "0.2.0", "data_through": end.isoformat(), "regions": []}
    for (rid, name, country), g in s.cells.groupby(["admin1_id", "admin1_name", "country"]):
        bbox = [round(float(g["lon_c"].min()) - 0.05, 3), round(float(g["lat_c"].min()) - 0.05, 3),
                round(float(g["lon_c"].max()) + 0.05, 3), round(float(g["lat_c"].max()) + 0.05, 3)]
        req = {"bbox": bbox, "start": "2000-11-01", "end": end.isoformat(), "res": "week"}
        d = os.path.join(a.out, "regions", rid)
        os.makedirs(d, exist_ok=True)
        recent = {**req, "start": (pd.Timestamp(end) - pd.Timedelta(days=364)).date().isoformat()}
        for path, body in (("summary", req), ("critical-periods", req), ("outlook", req), ("drivers", req), ("cells", recent)):
            r = c.post(f"/aoi/{path}", json=body)
            r.raise_for_status()
            with open(os.path.join(d, f"{path}.json"), "w") as f:
                json.dump(r.json(), f, separators=(",", ":"))
        index["regions"].append({"region_id": rid, "region_name": name, "country": country, "bbox": bbox})
        print("exported", rid)
    os.makedirs(os.path.join(a.out, "meta"), exist_ok=True)
    with open(os.path.join(a.out, "meta", "validation.json"), "w") as f:
        json.dump(c.get("/meta/validation").json(), f)
    with open(os.path.join(a.out, "index.json"), "w") as f:
        json.dump(index, f, indent=1)
    print(f"static fallback: {len(index['regions'])} regions -> {a.out}")


if __name__ == "__main__":
    main()
