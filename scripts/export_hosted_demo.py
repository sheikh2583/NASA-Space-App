"""Export two exact, real-data AOIs for the public GitHub Pages demo."""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    from fastapi.testclient import TestClient
    from ws2_platform.api.app import app
    from ws2_platform.api.make_fixtures import AOIS

    os.environ["DATA_DIR"] = str(ROOT / "data/processed")
    qa = json.loads((ROOT / "data/processed/validation/qa.json").read_text())
    if not all(check["result"] == "pass" for check in qa["metrics"]["checks"]):
        raise RuntimeError("Export requires passing real-data QA.")
    with TestClient(app) as client:
        validation = client.get("/meta/validation")
        validation.raise_for_status()
        snapshot = {"generated_at": dt.datetime.now(dt.timezone.utc).isoformat(), "data_mode": "real",
                    "data_through": "2026-11-02", "validation": validation.json(), "areas": {}}
        for key, name in (("bd", "bangladesh"), ("pb", "punjab")):
            request = {**AOIS[name], "end": snapshot["data_through"]}
            area = {"request": request}
            for endpoint in ("summary", "critical-periods", "drivers", "outlook"):
                response = client.post(f"/aoi/{endpoint}", json=request)
                response.raise_for_status()
                area[endpoint] = response.json()
            snapshot["areas"][key] = area
    path = ROOT / "ws5_frontend/public/demo/snapshot.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    print(f"Exported {path} ({path.stat().st_size:,} bytes). Review, commit, and push to refresh hosted data.")


if __name__ == "__main__":
    main()
