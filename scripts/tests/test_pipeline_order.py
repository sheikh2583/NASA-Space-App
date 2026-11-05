"""Static pipeline planning only; no stages, probes, or learners execute."""
from scripts import run_pipeline


def test_clean_pipeline_dependency_order(monkeypatch, tmp_path):
    monkeypatch.setattr(run_pipeline, "ROOT", str(tmp_path))
    names = [name for name, _ in run_pipeline.selected_steps(False)]
    for prerequisite, consumer in (
        ("ingest", "grid"), ("grid", "cells"), ("cells", "sensors"),
        ("sensors", "panel"), ("cells", "panel"), ("panel", "model"),
    ):
        assert names.index(prerequisite) < names.index(consumer)


def test_sensors_resume_rebuilds_cells_even_when_stale_output_exists(monkeypatch, tmp_path):
    monkeypatch.setattr(run_pipeline, "ROOT", str(tmp_path))
    stale = tmp_path / "data/processed/cells.parquet"
    stale.parent.mkdir(parents=True)
    stale.write_bytes(b"stale-placeholder-not-a-parquet")
    boundary = tmp_path / "data/raw/boundaries/new.geojson"
    boundary.parent.mkdir(parents=True)
    boundary.write_text("{}")
    selected = run_pipeline.selected_steps(False, "sensors")
    assert [name for name, _ in selected[:2]] == ["cells", "sensors"]
    assert str(boundary) in selected[0][1]
    assert stale.read_bytes() == b"stale-placeholder-not-a-parquet"


def test_downstream_resume_preserves_start_and_never_executes(monkeypatch, tmp_path):
    monkeypatch.setattr(run_pipeline, "ROOT", str(tmp_path))

    def forbidden(*args, **kwargs):
        raise AssertionError("Planning must not launch subprocesses")

    monkeypatch.setattr(run_pipeline.subprocess, "run", forbidden)
    assert run_pipeline.selected_steps(False, "v1")[0][0] == "v1"
    assert run_pipeline.selected_steps(False, "cells")[0][0] == "cells"
    model_args = dict(run_pipeline.selected_steps(True))["model"]
    assert "--quick" in model_args
