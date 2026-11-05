"""scripts/plan.py: card checks stay agent-safe under AGENTS.md (no training, no fitting, no blanket pytest)."""
from pathlib import Path
import importlib.util
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
if "plan" in sys.modules:
    plan_mod = sys.modules["plan"]
else:
    spec = importlib.util.spec_from_file_location("plan", ROOT / "scripts" / "plan.py")
    plan_mod = importlib.util.module_from_spec(spec)
    sys.modules["plan"] = plan_mod          # dataclasses need the module registered
    spec.loader.exec_module(plan_mod)

# Split strings, so that this file's own text never matches plan.FIT_PATTERNS (it is a reviewed test itself).
WF = "scripts/" + "workflow.py"
FIT = ".fi" + "t("
PIPELINE = "run_" + "pipeline.py"
HARMONIZE_MODEL = "from ws1_harmonize " + "import model"
CARD = """---
id: T00
title: T00 title
kind: agent
owner: Sheikh
authors: [Sheikh]
phase: P0
size: S
needs: []
requires: []
branch: ws1/T00-x
touches: [docs/a.md]
creates: [{creates}]
checks: [{checks}]
human_checks: [{human}]
---
## Goal
g
## Steps
1. s
## Acceptance
- a
## Stop and ask if
- never
"""


def one_card(tmp_path, checks, human="", creates=""):
    (tmp_path / "docs/plan/tasks").mkdir(parents=True)
    shutil.copy(ROOT / "docs/plan/team.yaml", tmp_path / "docs/plan/team.yaml")
    (tmp_path / "docs/a.md").write_text("x", encoding="utf-8")
    for t in plan_mod.SAFE_TESTS:
        (tmp_path / t).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / t).write_text("def test_x():\n    assert True\n", encoding="utf-8")
    (tmp_path / "docs/plan/tasks/T00_x.md").write_text(CARD.format(checks=checks, human=human, creates=creates),
                                                       encoding="utf-8")
    (tmp_path / "docs/plan/STATUS.md").write_text(
        "| ID | Kind | Title | Owner | Needs | Status | Note |\n|---|---|---|---|---|---|---|\n"
        "| T00 | agent | T00 title | Sheikh | – | todo |  |\n", encoding="utf-8")
    return plan_mod.validate(plan_mod.load(tmp_path))


def test_the_real_plan_has_only_agent_safe_checks():
    p = plan_mod.validate(plan_mod.load(ROOT))
    assert not p.errors and not p.warnings, p.errors + p.warnings
    for card in p.cards.values():
        created = plan_mod.created_by_plan(p, card)
        for name, cmd, _, _ in plan_mod.expand_checks(p, card):
            assert name not in plan_mod.HUMAN_ONLY, (card.id, name)
            assert plan_mod.unsafe_reason(cmd, card, created) is None, (card.id, name)


def test_every_reviewed_test_file_exists():
    assert [t for t in plan_mod.SAFE_TESTS if not (ROOT / t).exists()] == []


def test_reviewed_tests_have_no_fitting_code():
    for t in plan_mod.SAFE_TESTS:
        assert plan_mod.fitting_hits(ROOT, t) == [], t


def test_safe_checks_pass(tmp_path):
    p = one_card(tmp_path, '"CHECK-PLAN", "CHECK-TESTS", "CHECK-WEB", "python -m pytest -q ws4_outlook/tests/test_outlook.py"',
                 human='"CHECK-PY", "CHECK-QA"')
    assert not p.errors, p.errors


def test_human_only_named_checks_are_rejected(tmp_path):
    for name in ("CHECK-PY", "CHECK-SMOKE", "CHECK-QA"):
        shutil.rmtree(tmp_path, ignore_errors=True)
        p = one_card(tmp_path, f'"{name}"')
        assert any("is human-only" in e for e in p.errors), (name, p.errors)


def test_unsafe_literal_commands_are_rejected(tmp_path):
    bad = [f"python {WF} train --backend cuda", f"python {WF} smoke", f"python {WF} prepare", f"python {WF} gpu-check",
           f"python {WF} validate", "python -m pytest -q", "python -m pytest -q ws1_harmonize",
           "python -m pytest -q ws1_harmonize/tests/test_harmonize.py", "python -m pytest -k fit -q ws4_outlook/tests/test_outlook.py",
           "python -m ws4_outlook.run interval_report", "python -m ws6_validation.qa", f"python scripts/{PIPELINE}"]
    for cmd in bad:
        assert plan_mod.unsafe_reason(cmd.split()) is not None, cmd
    ok = ["python scripts/plan.py check", f"python {WF} build", "python -m ws4_outlook.season_profile --area pb",
          "python -m pytest -q ws2_platform/tests/test_tiny_api.py::test_x", "npm test", "git status"]
    for cmd in ok:
        assert plan_mod.unsafe_reason(cmd.split()) is None, cmd
    p = one_card(tmp_path, f'"python {WF} train"')
    assert any("not agent-safe" in e for e in p.errors), p.errors


def test_a_test_the_card_creates_is_allowed_but_scanned(tmp_path):
    p = one_card(tmp_path, '"python -m pytest -q scripts/tests/test_new.py"', creates="scripts/tests/test_new.py")
    assert not p.errors, p.errors
    card = p.cards["T00"]
    new = tmp_path / "scripts/tests/test_new.py"
    new.write_text("def test_ok():\n    assert 1\n", encoding="utf-8")
    cmd = ["python", "-m", "pytest", "-q", "scripts/tests/test_new.py"]
    assert plan_mod.refusal(p, card, "x", cmd) is None
    new.write_text("import lightgbm as lgb\n\ndef test_fit():\n    lgb.LGBMRegressor()" + FIT + "[[1]], [1])\n", encoding="utf-8")
    assert "fitting code" in plan_mod.refusal(p, card, "x", cmd)
    new.write_text("def test_ok():\n    assert 1\n", encoding="utf-8")
    (tmp_path / "scripts/tests/conftest.py").write_text(HARMONIZE_MODEL + "\n", encoding="utf-8")
    assert "conftest.py" in plan_mod.refusal(p, card, "x", cmd)


def test_run_refuses_a_human_only_step_even_if_the_card_lists_it(tmp_path, capsys):
    p = one_card(tmp_path, '"CHECK-QA"')
    assert plan_mod.run_checks(p, p.cards["T00"]) == 2
    assert "REFUSED CHECK-QA" in capsys.readouterr().out


def test_human_checks_are_printed_not_run(tmp_path, capsys, monkeypatch):
    p = one_card(tmp_path, '"git --version"', human='"CHECK-PY", "' + f"python {WF} train --backend cuda" + '"')
    ran = []
    real_run = plan_mod.subprocess.run
    monkeypatch.setattr(plan_mod.subprocess, "run",
                        lambda cmd, **k: ran.append(cmd) or real_run(cmd, **k))
    assert plan_mod.run_checks(p, p.cards["T00"]) == 0
    out = capsys.readouterr().out
    assert "Sheikh runs" in out and "CHECK-PY" in out and "train --backend cuda" in out
    assert not any("pytest" in " ".join(map(str, c)) or "workflow.py" in " ".join(map(str, c)) for c in ran)


def test_web_check_builds_like_the_render_image():
    p = plan_mod.load(ROOT)
    card = plan_mod.Card("T99", ROOT / "x.md", {"checks": ["CHECK-WEB"], "branch": "ws1/T99-x"}, "")
    steps = plan_mod.expand_checks(p, card)
    assert [s[1] for s in steps] == [["npm", "test"], ["npm", "run", "check:strings"], ["npm", "run", "build"]]
    assert all(s[3] == {"VITE_API_BASE_URL": "/", "VITE_DATA_MODE": "real"} for s in steps)
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "VITE_API_BASE_URL=/ VITE_DATA_MODE=real" in dockerfile


def test_env_requirement_reads_dotenv_without_printing(tmp_path, monkeypatch):
    monkeypatch.delenv("RENDER_URL", raising=False)
    assert not plan_mod.requirement_met(tmp_path, "env:RENDER_URL")
    (tmp_path / ".env").write_text("RENDER_URL=https://example.onrender.com\n", encoding="utf-8")
    assert plan_mod.requirement_met(tmp_path, "env:RENDER_URL")
