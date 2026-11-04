"""scripts/plan.py: the real plan is valid, and the checker catches the mistakes an agent or a person would make."""
from pathlib import Path
import importlib.util
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("plan", ROOT / "scripts" / "plan.py")
plan_mod = importlib.util.module_from_spec(spec)
sys.modules["plan"] = plan_mod          # dataclasses need the module registered
spec.loader.exec_module(plan_mod)

AGENT = """---
id: {id}
title: {title}
kind: agent
owner: {owner}
authors: [{authors}]
phase: {phase}
size: S
needs: [{needs}]
requires: [{requires}]
branch: ws1/{id}-x
touches: [{touches}]
creates: [{creates}]
checks: [CHECK-PLAN]
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

HUMAN = """---
id: {id}
title: {title}
kind: {kind}
owner: Sheikh
phase: P0
size: S
needs: [{needs}]
---
## Goal
g
## Steps
1. s
## Done when
- d
"""


def make_plan(tmp_path, cards, statuses, files=("docs/a.md",)):
    (tmp_path / "docs/plan/tasks").mkdir(parents=True)
    shutil.copy(ROOT / "docs/plan/team.yaml", tmp_path / "docs/plan/team.yaml")
    for f in files:
        (tmp_path / f).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / f).write_text("x", encoding="utf-8")
    rows = []
    for c in cards:
        d = {"title": c["id"] + " title", "owner": "Sheikh", "authors": "Sheikh", "phase": "P0", "needs": "",
             "requires": "", "touches": "", "creates": "", "kind": c.get("kind"), **c}
        tpl = AGENT if c["id"].startswith("T") else HUMAN
        if not d["kind"]:
            d["kind"] = {"H": "human", "G": "gate"}.get(c["id"][0], "agent")
        (tmp_path / f"docs/plan/tasks/{c['id']}_x.md").write_text(tpl.format(**d), encoding="utf-8")
        needs = ", ".join(x.strip() for x in d["needs"].split(",") if x.strip()) or "–"
        rows.append(f"| {c['id']} | {d['kind']} | {d['title']} | {d['owner']} | {needs} | {statuses.get(c['id'], 'todo')} |  |")
    (tmp_path / "docs/plan/STATUS.md").write_text(
        "# Board\n\n| ID | Kind | Title | Owner | Needs | Status | Note |\n|---|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n\nfooter\n",
        encoding="utf-8")
    return tmp_path


def check(root):
    return plan_mod.validate(plan_mod.load(Path(root)))


def test_the_real_plan_is_valid():
    p = check(ROOT)
    assert not p.errors, "\n".join(p.errors)
    assert len(p.cards) >= 30


def test_a_good_small_plan_passes_and_next_respects_needs_and_people(tmp_path):
    root = make_plan(tmp_path, [
        {"id": "T00", "touches": "docs/a.md", "creates": "docs/b.md"},
        {"id": "H01"},
        {"id": "T01", "needs": "T00", "touches": "docs/b.md"},
        {"id": "T02", "needs": "H01", "touches": "docs/a.md"},
        {"id": "T03", "touches": "docs/a.md", "requires": "real-data"},
    ], {"T00": "done"})
    p = check(root)
    assert not p.errors, p.errors
    ready, people, unmet = plan_mod.eligible(p, met=lambda r: False)
    assert ready == ["T01"] and people == ["H01"] and unmet == [("T03", ["real-data"])]


@pytest.mark.parametrize("cards,statuses,expected", [
    ([{"id": "T00", "needs": "T01"}, {"id": "T01", "needs": "T00"}], {}, "dependency cycle"),
    ([{"id": "T00", "needs": "T09"}], {}, "needs unknown card T09"),
    ([{"id": "T00", "touches": "docs/missing.md"}], {}, "does not exist and is not created by a card it needs"),
    ([{"id": "T00", "touches": "docs/a.md", "authors": "Sattyam", "owner": "Sattyam"},
      {"id": "T01", "touches": "docs/a.md", "owner": "Nobody"}], {}, "is not in docs/plan/team.yaml"),
    ([{"id": "T00", "creates": "docs/a.md"}], {}, "already exists"),
    ([{"id": "T00", "creates": "docs/n.md"}, {"id": "T01", "creates": "docs/n.md"}], {}, "created by more than one card"),
    ([{"id": "T00", "phase": "P0", "needs": "T01"}, {"id": "T01", "phase": "P2"}], {}, "later phase"),
    ([{"id": "T00"}], {"T00": "finished"}, "is not one of"),
    ([{"id": "T00", "touches": "docs/a.md", "creates": "ws3_anomaly/new.py"}], {}, "belongs to Monazir, who is not in authors"),
    ([{"id": "T00", "touches": "docs/a.md", "creates": "nowhere/new.py"}], {}, "nobody owns"),
])
def test_checker_catches_mistakes(tmp_path, cards, statuses, expected):
    p = check(make_plan(tmp_path, cards, statuses))
    assert any(expected in e for e in p.errors), p.errors


def test_a_card_in_progress_may_have_its_new_files(tmp_path):
    # The loop runs `checks --run` (which runs `plan.py check`) before `set done`, so `doing` must allow the card's files.
    p = check(make_plan(tmp_path, [{"id": "T00", "creates": "docs/a.md"}], {"T00": "doing"}))
    assert not any("already exists" in e for e in p.errors), p.errors


def test_board_mismatch_is_reported_and_fixed(tmp_path):
    root = make_plan(tmp_path, [{"id": "T00", "touches": "docs/a.md"}], {"T00": "review"})
    status = root / "docs/plan/STATUS.md"
    status.write_text(status.read_text(encoding="utf-8").replace("T00 title", "old title"), encoding="utf-8")
    assert any("column Title" in e for e in check(root).errors)
    plan_mod.write_board(plan_mod.load(root))
    text = status.read_text(encoding="utf-8")
    assert "T00 title" in text and "| review |" in text and text.startswith("# Board") and text.rstrip().endswith("footer")
    assert not check(root).errors


def test_set_status_changes_one_row(tmp_path):
    root = make_plan(tmp_path, [{"id": "T00", "touches": "docs/a.md"}, {"id": "H01"}], {})
    plan_mod.set_status(root, "T00", "review", "PR #3")
    rows, _ = plan_mod.read_status(root / "docs/plan/STATUS.md")
    assert rows["T00"]["Status"] == "review" and rows["T00"]["Note"] == "PR #3" and rows["H01"]["Status"] == "todo"
    with pytest.raises(SystemExit):
        plan_mod.set_status(root, "T00", "finished", None)


def test_checks_expand_with_environment_and_branch(tmp_path):
    p = plan_mod.load(ROOT)
    card = plan_mod.Card("T99", ROOT / "x.md", {"checks": ["CHECK-SNAP", "CHECK-GUARD", "python -m pytest ws4_outlook -q"],
                                                "branch": "ws1/T99-x"}, "")
    steps = plan_mod.expand_checks(p, card)
    assert steps[0][1] == ["npm", "run", "build"] and steps[0][3] == {"VITE_DEMO_MODE": "snapshot", "VITE_DATA_MODE": "real"}
    assert steps[1][1][-1] == "ws1/T99-x" and "sheikh2583" in steps[1][1]
    assert steps[2][1][:3] == ["python", "-m", "pytest"]
    assert plan_mod._resolve(["python", "-V"])[0] == sys.executable


def test_split_groups_changes_by_owner(tmp_path):
    root = make_plan(tmp_path, [{"id": "T00", "authors": "Sheikh, Sattyam, Shammo", "touches": "docs/a.md"}], {})
    p = plan_mod.load(root)
    card = p.cards["T00"]
    groups = plan_mod.split_commits(p, card, ["ws2_platform/api/app.py", "docs/project/contract-changes.md",
                                              "ws5_frontend/src/App.tsx", "contracts/openapi.yaml", "docs/plan/STATUS.md"])
    assert [(g[0], g[2]) for g in groups] == [
        ("Sheikh", ["docs/plan/STATUS.md", "docs/project/contract-changes.md"]),
        ("Sattyam", ["contracts/openapi.yaml", "ws2_platform/api/app.py"]),
        ("Shammo", ["ws5_frontend/src/App.tsx"])]
    with pytest.raises(SystemExit, match="belong to"):
        plan_mod.split_commits(p, card, ["ws3_anomaly/batch.py"])


def test_split_runs_commits_with_owner_authors(tmp_path, monkeypatch):
    root = make_plan(tmp_path, [{"id": "T00", "authors": "Sheikh, Samin", "touches": "docs/a.md"}], {})
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@x"]
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(git + ["add", "-A"], cwd=root, check=True)
    subprocess.run(git + ["commit", "-qm", "base"], cwd=root, check=True)
    (root / "common").mkdir()
    (root / "common/new.py").write_text("x = 1\n", encoding="utf-8")
    (root / "docs/plan/STATUS.md").write_text((root / "docs/plan/STATUS.md").read_text(encoding="utf-8") + "\n", encoding="utf-8")
    monkeypatch.setattr(plan_mod, "ROOT", root)
    monkeypatch.setenv("GIT_COMMITTER_NAME", "t")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "t@x")
    assert plan_mod.main(["split", "--card", "T00", "-m", "T00: test", "--run"]) == 0
    log = subprocess.run(["git", "log", "--format=%an|%s", "-2"], cwd=root, capture_output=True, text=True).stdout.split("\n")
    assert log[0] == "Samin Abdullah|T00: test" and log[1] == "Sheikh Mosheul Akbar|T00: test"


def test_cut_counts_as_finished_and_in_flight_cards_wait(tmp_path):
    root = make_plan(tmp_path, [
        {"id": "T00", "touches": "docs/a.md"},
        {"id": "T01", "needs": "T00", "touches": "docs/a.md"},
        {"id": "T02", "needs": "T01", "touches": "docs/a.md"},
        {"id": "T03", "touches": "docs/a.md"},
    ], {"T00": "cut"})
    p = check(root)
    assert not p.errors, p.errors
    ready, _, _ = plan_mod.eligible(p, met=lambda r: True, flying={"T01"})
    assert ready == ["T03"]                                   # T01 in flight, T02 waits for it
    ready, _, _ = plan_mod.eligible(p, met=lambda r: True, flying=set())
    assert ready == ["T01", "T03"]                            # cut T00 counts as finished


def test_in_flight_reads_local_branches(tmp_path):
    root = make_plan(tmp_path, [{"id": "T00", "touches": "docs/a.md"}], {})
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@x"]
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
    subprocess.run(git + ["add", "-A"], cwd=root, check=True)
    subprocess.run(git + ["commit", "-qm", "base"], cwd=root, check=True)
    subprocess.run(["git", "branch", "ws1/T00-x"], cwd=root, check=True)
    subprocess.run(["git", "branch", "ws2/T05-other"], cwd=root, check=True)
    assert plan_mod.in_flight(root) == {"T00"}
    # `next` reads the board as merged on main, not the working tree
    (root / "docs/plan/STATUS.md").write_text((root / "docs/plan/STATUS.md").read_text(encoding="utf-8").replace("| todo |", "| done |"), encoding="utf-8")
    assert plan_mod.load(root, status_from_main=True).status["T00"]["Status"] == "todo"
    assert plan_mod.load(root).status["T00"]["Status"] == "done"


def test_board_not_yet_on_main_means_nothing_is_done(tmp_path):
    root = make_plan(tmp_path, [{"id": "T00", "touches": "docs/a.md"}, {"id": "T01", "needs": "T00", "touches": "docs/a.md"}],
                     {"T00": "done"})
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@x"]
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
    subprocess.run(git + ["add", "docs/a.md"], cwd=root, check=True)           # main has code but no plan yet
    subprocess.run(git + ["commit", "-qm", "base"], cwd=root, check=True)
    subprocess.run(["git", "switch", "-q", "-c", "ws1/T00-install"], cwd=root, check=True)
    p = plan_mod.load(root, status_from_main=True)
    assert p.status == {}                                                        # T00 is not done until merged
    ready, _, _ = plan_mod.eligible(p, met=lambda r: True)
    assert ready == []                                                           # T00 in flight, T01 waits
