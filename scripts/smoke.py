"""Fast unit, fixture API, optional real-output QA, and UI build checks. No retraining."""
from __future__ import annotations

from pathlib import Path
import sys

from workflow import ROOT, run


def main():
    run(sys.executable, "-m", "pytest", "common", "ws1_harmonize/tests", "ws2_platform/tests", "ws3_anomaly/tests", "ws4_outlook/tests", "scripts/tests", "-q")
    # Fixtures make the source-only ZIP useful before NASA data is downloaded.
    sys.path.insert(0, str(ROOT))
    from fastapi.testclient import TestClient
    from ws2_platform.api.mock_server import app
    import json
    with TestClient(app) as client:
        request = json.loads((ROOT / "contracts/fixtures/bangladesh_request.json").read_text())
        response = client.post("/aoi/summary", json=request)
        assert response.status_code == 200 and response.json()["series"], "Fixture API smoke failed"
    print("PASS fixture API summary", flush=True)
    if (ROOT / "data/processed/harmonized.parquet").exists():
        run(sys.executable, "-m", "ws6_validation.qa")
    else:
        print("SKIP real-output QA: no trained outputs in this checkout", flush=True)
    run("npm", "test", cwd=ROOT / "ws5_frontend")
    run("npm", "run", "check:strings", cwd=ROOT / "ws5_frontend")
    run("npm", "run", "build", cwd=ROOT / "ws5_frontend")
    print("SMOKE PASSED. Quick training is a separate workflow: train --quick.")


if __name__ == "__main__":
    main()
