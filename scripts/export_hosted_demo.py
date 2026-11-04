"""Export named regions and example AOIs from passing real-data outputs."""
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
    from scripts.export_area_catalog import main as export_catalog

    os.environ["DATA_DIR"] = str(ROOT / "data/processed")
    qa = json.loads((ROOT / "data/processed/validation/qa.json").read_text())
    if not all(check["result"] == "pass" for check in qa["metrics"]["checks"]):
        raise RuntimeError("Export requires passing real-data QA.")
    validation_path = ROOT / 'data/processed/validation/harmonization.json'
    if json.loads(validation_path.read_text())['metrics'].get('data_mode') != 'real':
        raise RuntimeError('Export requires validation marked as real observations.')
    export_catalog()
    catalog = json.loads((ROOT / 'ws5_frontend/public/demo/areas.json').read_text(encoding='utf-8'))
    with TestClient(app) as client:
        validation = client.get("/meta/validation")
        validation.raise_for_status()
        snapshot = {"generated_at": dt.datetime.now(dt.timezone.utc).isoformat(), "data_mode": "real",
                    "data_through": "2026-11-02", "validation": validation.json(), "areas": {}}
        requests = [(key, AOIS[name]) for key, name in (("bd", "bangladesh"), ("pb", "punjab"))]
        requests += [(a['id'], {**a['request'], 'start': '2000-11-01', 'res': 'week'}) for a in catalog['areas']]
        for key, request in requests:
            request = {**request, "end": snapshot["data_through"]}
            area = {"request": request}
            for endpoint in ("summary", "critical-periods", "drivers", "outlook"):
                response = client.post(f"/aoi/{endpoint}", json=request)
                response.raise_for_status()
                area[endpoint] = response.json()
            snapshot["areas"][key] = area
            print(f'Exported responses for area {key}', flush=True)
    path = ROOT / "ws5_frontend/public/demo/snapshot.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix('.json.part')
    pending.write_text(json.dumps(snapshot, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    pending.replace(path)
    print(f"Exported {path} ({path.stat().st_size:,} bytes). Review, commit, and push to refresh hosted data.")


if __name__ == "__main__":
    main()
