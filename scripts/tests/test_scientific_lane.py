"""Scientific execution boundaries using tiny files and fake commands; no learners execute."""
from pathlib import Path
from types import SimpleNamespace, ModuleType
import json
import shutil
import subprocess
import sys

import pytest
from scripts import plan as plans
from scripts import workflow

PROJECT = Path(__file__).resolve().parents[2]
WF = "scripts/" + "workflow.py"


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.delenv("FIRESENSE_SCIENCE_MANIFEST", raising=False)
    monkeypatch.delenv("FIRESENSE_SCIENCE_TOKEN", raising=False)
    for directory in ("docs/plan/tasks", "docs/guides", "data/processed", "data/interim/sheikh", "data/raw/firms"):
        (tmp_path / directory).mkdir(parents=True, exist_ok=True)
    shutil.copy(PROJECT / "docs/plan/team.yaml", tmp_path / "docs/plan/team.yaml")
    spec = "# Scientific run\n\n## Question\nTest the boundary.\n\n## Protocol\nPreserve and measure.\n"
    (tmp_path / "docs/run.md").write_text(spec, encoding="utf-8")
    (tmp_path / "docs/guides/training.md").write_text(spec, encoding="utf-8")
    (tmp_path / "data/processed/original.bin").write_bytes(b"validated-output")
    (tmp_path / "data/interim/sheikh/parameters.bin").write_bytes(b"saved-parameters")
    (tmp_path / "data/raw/firms/archive.csv").write_text("date,count\n2020-01-01,1\n")
    (tmp_path / "example.py").write_text("answer = 42\n")
    (tmp_path / ".env").write_text("NEVER_COPY_THIS=private\n")
    card = plans.Card("T99", tmp_path / "docs/plan/tasks/T99_x.md", {
        "id": "T99", "title": "Boundary", "kind": "agent", "owner": "Sheikh", "authors": ["Sheikh"],
        "phase": "P1", "size": "S", "branch": "ws1/T99-boundary", "touches": [], "creates": [],
        "needs": [], "requires": [], "scientific_spec": "docs/run.md",
        "checks": ["git --version"], "human_checks": ["CHECK-PY", "CHECK-QA"]},
        "## Goal\nBoundary\n## Steps\nMock\n## Acceptance\nVerified\n## Stop and ask if\nBlocked\n")
    team = plans.yaml.safe_load((tmp_path / "docs/plan/team.yaml").read_text())
    p = plans.Plan(root=tmp_path, cards={"T99": card}, team=team,
                   status={"T99": {"Kind": "agent", "Title": "Boundary", "Owner": "Sheikh", "Needs": "–",
                                     "Status": "doing", "Note": ""}}, status_order=["T99"])
    return p, card


def receipts(p):
    return [json.loads(f.read_text()) for f in (p.root / "results/runs").glob("scientific-*/scientific.json")]


def test_explicit_lane_runs_only_declared_commands_after_verified_preservation(project, monkeypatch):
    p, card = project
    ran = []

    def fake(command, *, cwd, env, log):
        receipt = json.loads(Path(env["FIRESENSE_SCIENCE_MANIFEST"]).read_text())
        assert receipt["baseline_verified"] and receipt["status"] == "running"
        assert (Path(receipt["backup"]) / "processed/original.bin").read_bytes() == b"validated-output"
        assert (p.root / "results/.scientific-writer.lock").exists()
        log.write("mocked command output\n")
        ran.append(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(plans, "_execute_scientific", fake)
    assert plans.run_scientific_checks(p, card) == 0
    assert ran == [["python", "-m", "pytest", "-q"], ["python", WF, "validate"]]
    report = receipts(p)[0]
    assert report["status"] == "passed" and len(report["steps"]) == 2
    assert not (p.root / "results/.scientific-writer.lock").exists()
    snapshot = next((p.root / "results/runs").glob("scientific-*/source"))
    assert (snapshot / "example.py").read_text() == "answer = 42\n"
    assert not (snapshot / ".env").exists() and not (snapshot / "data").exists()


def test_cli_preview_is_nonexecuting_and_explicit_run_routes_only_scientific_lane(project, monkeypatch):
    p, _ = project
    calls = []
    monkeypatch.setattr(plans, "load", lambda *a, **k: p)
    monkeypatch.setattr(plans, "ROOT", p.root)
    monkeypatch.setattr(plans, "_execute_scientific", lambda command, **k: calls.append(command) or SimpleNamespace(returncode=0))
    assert plans.main(["checks", "T99", "--scientific"]) == 0
    assert plans.main(["show", "T99", "--scientific"]) == 0
    assert calls == [] and not (p.root / "results/runs").exists()
    assert plans.main(["checks", "T99", "--scientific", "--run"]) == 0
    assert len(calls) == 2 and all(c[0] == "python" for c in calls)


@pytest.mark.parametrize("value", [None, "", "../outside.md", "/outside.md", "docs/missing.md", 12])
def test_invalid_spec_never_starts_a_command(project, monkeypatch, value):
    p, card = project
    card.meta["scientific_spec"] = value
    monkeypatch.setattr(plans, "_execute_scientific", lambda *a, **k: pytest.fail("must refuse before execution"))
    assert plans.run_scientific_checks(p, card) == 2
    assert not (p.root / "results/.scientific-writer.lock").exists()


def test_empty_protocol_and_empty_command_list_are_rejected(project):
    p, card = project
    (p.root / "docs/run.md").write_text("# A title only\n")
    with pytest.raises(ValueError, match="protocol sections"):
        plans.scientific_steps(p, card)
    (p.root / "docs/run.md").write_text("# Run\n## Question\nx\n## Protocol\nx\n")
    card.meta["human_checks"] = []
    with pytest.raises(ValueError, match="No scientific commands"):
        plans.scientific_steps(p, card)


def test_human_evidence_card_cannot_be_executed_as_scientific_work(project, monkeypatch):
    p, card = project
    card.meta["kind"] = "human"
    monkeypatch.setattr(plans, "_execute_scientific", lambda *a, **k: pytest.fail("human evidence is not automated"))
    assert plans.run_scientific_checks(p, card) == 2


def test_uncommitted_prerequisite_and_missing_requirement_refuse_execution(project, monkeypatch):
    p, card = project
    monkeypatch.setattr(plans, "_execute_scientific", lambda *a, **k: pytest.fail("no scientific command"))
    card.meta["needs"] = ["T01"]
    assert plans.run_scientific_checks(p, card) == 2
    card.meta["needs"] = []
    card.meta["requires"] = ["real-data"]
    assert plans.run_scientific_checks(p, card) == 2


def test_existing_writer_lock_is_preserved_and_refuses_second_writer(project, monkeypatch):
    p, card = project
    lock = p.root / "results/.scientific-writer.lock"
    lock.parent.mkdir()
    lock.write_text('{"pid": 123}')
    monkeypatch.setattr(plans, "_execute_scientific", lambda *a, **k: pytest.fail("second writer"))
    assert plans.run_scientific_checks(p, card) == 2
    assert lock.read_text() == '{"pid": 123}'


def test_backup_failure_prevents_execution_and_keeps_failure_record(project, monkeypatch):
    p, card = project
    tools = plans._scientific_tools()

    def corrupt(source, destination):
        Path(destination).mkdir(parents=True)
        (Path(destination) / "original.bin").write_bytes(b"corrupt")

    monkeypatch.setattr(tools.shutil, "copytree", corrupt)
    monkeypatch.setattr(plans, "_execute_scientific", lambda *a, **k: pytest.fail("unverified backup"))
    assert plans.run_scientific_checks(p, card) == 2
    assert receipts(p)[0]["status"] == "failed"
    assert not (p.root / "results/.scientific-writer.lock").exists()
    assert (p.root / "data/processed/original.bin").read_bytes() == b"validated-output"


def test_disk_precondition_prevents_execution(project, monkeypatch):
    p, card = project
    tools = plans._scientific_tools()
    monkeypatch.setattr(tools.shutil, "disk_usage", lambda root: SimpleNamespace(free=0))
    monkeypatch.setattr(plans, "_execute_scientific", lambda *a, **k: pytest.fail("disk precondition"))
    assert plans.run_scientific_checks(p, card) == 2
    assert receipts(p)[0]["baseline_verified"] is False


def test_failed_command_stops_remaining_commands_and_records_exit(project, monkeypatch):
    p, card = project
    calls = []

    def fail(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=7)

    monkeypatch.setattr(plans, "_execute_scientific", fail)
    assert plans.run_scientific_checks(p, card) == 7
    report = receipts(p)[0]
    assert len(calls) == 1 and report["status"] == "failed"
    assert report["steps"][0]["exit_code"] == 7
    assert not (p.root / "results/.scientific-writer.lock").exists()


def test_raw_input_mutation_cannot_finish_successfully(project, monkeypatch):
    p, card = project

    def change(command, **kwargs):
        (p.root / "data/raw/firms/archive.csv").write_text("changed\n")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(plans, "_execute_scientific", change)
    assert plans.run_scientific_checks(p, card) == 2
    assert receipts(p)[0]["status"] == "failed"


@pytest.mark.parametrize("target", ["source", "backup"])
def test_protected_source_or_backup_mutation_rejects_success(project, monkeypatch, target):
    p, card = project

    def change(command, *, env, **kwargs):
        if target == "source":
            (p.root / "example.py").write_text("changed = True\n")
        else:
            record = json.loads(Path(env["FIRESENSE_SCIENCE_MANIFEST"]).read_text())
            (Path(record["backup"]) / "processed/original.bin").write_bytes(b"corrupt")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(plans, "_execute_scientific", change)
    assert plans.run_scientific_checks(p, card) == 2
    assert receipts(p)[0]["status"] == "failed"


def test_documented_contract_fixture_regeneration_is_recorded_not_called_a_source_edit(project, monkeypatch):
    p, card = project
    fixture = p.root / "contracts/fixtures/example.json"
    fixture.parent.mkdir(parents=True)
    fixture.write_text('{"old": true}')

    def refresh(command, **kwargs):
        fixture.write_text('{"new": true}')
        (fixture.parent / "created.json").write_text('{"created": true}')
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(plans, "_execute_scientific", refresh)
    assert plans.run_scientific_checks(p, card) == 0
    generated = receipts(p)[0]["generated_source_outputs"]
    by_name = {row["path"]: row for row in generated}
    assert by_name["contracts/fixtures/example.json"]["before_sha256"] != by_name["contracts/fixtures/example.json"]["after_sha256"]
    assert by_name["contracts/fixtures/created.json"]["before_sha256"] is None
    assert by_name["contracts/fixtures/created.json"]["after_sha256"]


def test_source_commit_patch_inputs_and_configuration_are_attributable(project, monkeypatch):
    p, card = project
    subprocess.run(["git", "init", "-q"], cwd=p.root, check=True)
    subprocess.run(["git", "add", "example.py"], cwd=p.root, check=True)
    subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                    "commit", "-qm", "source"], cwd=p.root, check=True)
    (p.root / "example.py").write_text("answer = 43\n")
    monkeypatch.setenv("FIRESENSE_THREADS", "3")
    monkeypatch.setattr(plans, "_execute_scientific", lambda *a, **k: SimpleNamespace(returncode=0))
    assert plans.run_scientific_checks(p, card) == 0
    report = receipts(p)[0]
    assert len(report["source"]["commit"]) == 40
    assert report["configuration"] == {"FIRESENSE_THREADS": "3"}
    assert report["spec_sha256"] and report["baseline_members"]["sheikh"]
    folder = next((p.root / "results/runs").glob("scientific-*"))
    assert "+answer = 43" in (folder / "source.patch").read_text()
    assert "archive.csv" in (folder / "raw-inputs.json").read_text()
    assert not any("NEVER_COPY_THIS" in f.read_text() for f in folder.rglob("*") if f.is_file())


def test_child_reuses_valid_owner_but_not_a_wrong_token(project, monkeypatch):
    p, _ = project
    tools = plans._scientific_tools()
    with tools.scientific_session(p.root, "owner", p.root / "docs/run.md", []) as owner:
        with tools.scientific_environment(owner["env"]):
            with tools.scientific_session(p.root, "child", p.root / "docs/run.md", [], inherit=True) as child:
                assert child["manifest"] == owner["manifest"]
            monkeypatch.setenv("FIRESENSE_SCIENCE_TOKEN", "wrong")
            with pytest.raises(RuntimeError, match="ownership"):
                tools.inherited_science(p.root)
        assert (p.root / "results/.scientific-writer.lock").exists()
    assert len(receipts(p)) == 1


def test_training_workflow_cannot_fall_back_when_real_inputs_are_missing(project, monkeypatch):
    p, _ = project
    (p.root / "data/raw/firms/archive.csv").unlink()
    monkeypatch.setattr(workflow, "ROOT", p.root)
    monkeypatch.setattr(workflow, "run", lambda *a, **k: pytest.fail("no fitting readiness before input check"))
    with pytest.raises(RuntimeError, match="synthetic fallback"):
        workflow.train(False, None)


def test_direct_pipeline_requires_explicit_synthetic_opt_in_without_fitting(project, monkeypatch):
    p, _ = project
    tools = plans._scientific_tools()
    (p.root / "data/raw/firms/archive.csv").unlink()
    monkeypatch.setattr(tools, "ROOT", str(p.root))
    calls = []
    def fake_pipeline(args, context):
        calls.append(args.allow_synthetic)
        (p.root / "data/raw/firms/synthetic_new.csv").write_text("generated\n")
    monkeypatch.setattr(tools, "_pipeline_run", fake_pipeline)
    monkeypatch.setattr(sys, "argv", ["pipeline", "--backend", "cuda"])
    with pytest.raises(RuntimeError, match="synthetic fallback"):
        tools.main()
    assert calls == []
    monkeypatch.setattr(sys, "argv", ["pipeline", "--backend", "cuda", "--allow-synthetic"])
    tools.main()
    assert calls == [True]
    passed = next(r for r in receipts(p) if r["status"] == "passed")
    assert passed["generated_raw_inputs"]["after"][0]["path"] == "firms/synthetic_new.csv"
    assert passed["protected_raw_inputs_unchanged"] and not passed["raw_inputs_unchanged"]


def test_inherited_lane_cannot_downgrade_a_real_input_requirement(project):
    p, _ = project
    tools = plans._scientific_tools()
    with tools.scientific_session(p.root, "parent", p.root / "docs/run.md", []) as context:
        with tools.scientific_environment(context["env"]):
            archive = p.root / "data/raw/firms/archive.csv"
            original = archive.read_bytes()
            archive.unlink()
            with pytest.raises(RuntimeError, match="synthetic fallback"):
                with tools.scientific_session(p.root, "child", p.root / "docs/run.md", [],
                                              require_real=True, inherit=True):
                    pytest.fail("missing inputs must refuse before a child starts")
            archive.write_bytes(original)


@pytest.mark.parametrize("exit_code", [0, 7])
def test_pipeline_backup_log_and_failure_status(project, monkeypatch, exit_code):
    p, _ = project
    tools = plans._scientific_tools()
    events = []
    original = tools.preserve_outputs

    def preserve(root, destination):
        result = original(root, destination)
        events.append("backup")
        return result

    def fake_probe():
        assert events == ["backup"]
        log = Path(tools.os.environ["FIRESENSE_COMPUTE_LOG"])
        assert log.parent.exists()
        events.append("probe")
        return {"device": "mocked"}

    module = ModuleType("common")
    module.compute = SimpleNamespace(configure_cuda_training=lambda: None, **{"probe_" + "cuda": fake_probe})
    monkeypatch.setitem(sys.modules, "common", module)
    monkeypatch.setattr(tools, "ROOT", str(p.root))
    monkeypatch.setattr(tools, "preserve_outputs", preserve)
    monkeypatch.setattr(tools, "selected_steps", lambda *a: [("grid", ["fake-stage.py"])])
    monkeypatch.setattr(tools.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=exit_code))
    for key in ("FIRESENSE_COMPUTE_LOG", "FIRESENSE_BACKEND", "FIRESENSE_GPU_ID", "FIRESENSE_THREADS"):
        monkeypatch.setenv(key, "0" if key == "FIRESENSE_GPU_ID" else "1")
    args = SimpleNamespace(backend="cuda", gpu_id=0, threads=1, quick=False, start=None)
    if exit_code:
        with pytest.raises(SystemExit) as failure:
            tools._pipeline_run(args, {"manifest": p.root / "mock-scientific.json"})
        assert failure.value.code == exit_code
    else:
        tools._pipeline_run(args, {"manifest": p.root / "mock-scientific.json"})
    assert events == ["backup", "probe"]
    report = json.loads(next((p.root / "results/runs").glob("*/execution.json")).read_text())
    assert report["status"] == ("failed" if exit_code else "passed")
    if exit_code:
        assert report["exit_code"] == 7 and "--from grid" in report["resume_command"]
