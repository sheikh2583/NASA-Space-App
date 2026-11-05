"""Missing/corrupt report visibility using the non-fitting tiny API and a temporary report directory."""
import json
from pathlib import Path

import yaml
from openapi_schema_validator import OAS30Validator

from ws2_platform.api import app as api


def test_validation_lists_corrupt_and_missing_pieces_without_hiding_healthy_ones(tiny_api, tmp_path, monkeypatch):
    # Initialize the tiny Store, then point only its report lookup at our isolated directory.
    saved_store = api.store()
    validation = tmp_path / "validation"
    validation.mkdir()
    good = {"schema_version": "1.0", "generated_at": "2026-11-06T00:00:00Z", "producer": "qa",
            "metrics": {}, "limitations": ["Tiny test only."]}
    (validation / "qa.json").write_text(json.dumps(good), encoding="utf-8")
    (validation / "intervals.json").write_text('{"broken":', encoding="utf-8")
    monkeypatch.setattr(saved_store, "data_dir", str(tmp_path))
    response = tiny_api.get("/meta/validation")
    assert response.status_code == 200
    body = response.json()
    assert body["pieces"] == {"qa": good}
    assert body["corrupt"] == ["intervals.json"]
    assert body["missing"] == ["harmonization", "intervals", "drift", "outlook_skill", "intervals_by_stratum"]
    json.dumps(body, allow_nan=False)

    spec_path = Path(__file__).resolve().parents[2] / "contracts/openapi.yaml"
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    validator = OAS30Validator({"$ref": "#/components/schemas/ValidationResponse", "components": spec["components"]})
    assert not list(validator.iter_errors(body))

    (validation / "intervals.json").unlink()
    good["producer"] = "intervals_by_stratum"
    (validation / "intervals_by_stratum.json").write_text(json.dumps(good), encoding="utf-8")
    recovered = tiny_api.get("/meta/validation").json()
    assert recovered["corrupt"] == []
    assert "intervals_by_stratum" not in recovered["missing"]
