import json
import pytest
from scripts import run_pipeline


def test_resume_rejects_mixed_model_backends(monkeypatch, tmp_path):
    monkeypatch.setattr(run_pipeline, "ROOT", str(tmp_path))
    path = tmp_path / "data/interim/sheikh/method.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"method": "b1", "compute_backend": "cpu"}))
    with pytest.raises(RuntimeError, match="avoid mixing backends"):
        run_pipeline.validate_resume_backend("intervals", "cuda")
    run_pipeline.validate_resume_backend("intervals", "cpu")
    run_pipeline.validate_resume_backend("model", "cuda")


def test_resume_requires_method_record(monkeypatch, tmp_path):
    monkeypatch.setattr(run_pipeline, "ROOT", str(tmp_path))
    with pytest.raises(RuntimeError, match="existing method.json"):
        run_pipeline.validate_resume_backend("outlook", "cuda")


def test_execution_placement_reports_only_selected_active_stages():
    todo = [("synth", None), ("drift", ["drift"]), ("qa", ["qa"])]
    assert run_pipeline.stage_placement(todo, "cuda") == (["drift"], ["qa"])
    assert run_pipeline.stage_placement(todo, "cpu") == ([], ["drift", "qa"])
