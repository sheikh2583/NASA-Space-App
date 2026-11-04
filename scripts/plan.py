"""Plan tool for the coding agent and the team: the single, checkable source of "what to do next".

    python scripts/plan.py check                 # validate every card, the status board and their links
    python scripts/plan.py next [--all]          # the next agent card that can start here (or all of them)
    python scripts/plan.py show T07              # one card with its authors, branch and expanded checks
    python scripts/plan.py checks T07 [--run]    # print (or run, stopping at the first failure) a card's checks
    python scripts/plan.py split --card T07 -m "T07: season endpoint" [--run]
                                                 # commit the working-tree changes as one commit per owner
    python scripts/plan.py set T07 review --note "PR #14"
    python scripts/plan.py board [--fix]         # print the board (or rewrite STATUS.md columns from the cards)

Cards live in docs/plan/tasks/<ID>_<slug>.md with YAML front matter (docs/plan/README.md, "Card format").
Status lives only in docs/plan/STATUS.md. Team, authors and path ownership live in docs/plan/team.yaml.
Standard library + PyYAML only.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STATUSES = ("todo", "doing", "review", "done", "blocked", "cut")
FINISHED = ("done", "cut")              # "cut" = dropped on purpose (cut order); counts as finished for needs
KINDS = {"T": "agent", "H": "human", "G": "gate"}   # G is unused in the current plan; kept for future sign-off cards
PHASES = ("P0", "P1", "P2", "P3", "P4")
SIZES = ("S", "M", "L")
REQUIRES = ("real-data", "secret:FIRMS_MAP_KEY", "secret:EARTHDATA_TOKEN", "hf-token", "gh-auth", "earthdata-files", "network")
AGENT_KEYS = ("id", "title", "kind", "owner", "authors", "phase", "size", "needs", "branch", "touches", "creates", "checks")
HUMAN_KEYS = ("id", "title", "kind", "owner", "phase", "size", "needs")
AGENT_HEADINGS = ("## Goal", "## Steps", "## Acceptance", "## Stop and ask if")
HUMAN_HEADINGS = ("## Goal", "## Steps", "## Done when")
STATUS_COLUMNS = ("ID", "Kind", "Title", "Owner", "Needs", "Status", "Note")

# Named checks. Each is a list of (command, working directory relative to the repo root, extra environment).
CHECKS = {
    "CHECK-PY": [(["python", "-m", "pytest", "-q"], ".", {})],
    "CHECK-WEB": [(["npm", "test"], "ws5_frontend", {}), (["npm", "run", "check:strings"], "ws5_frontend", {}),
                  (["npm", "run", "build"], "ws5_frontend", {})],
    "CHECK-SNAP": [(["npm", "run", "build"], "ws5_frontend", {"VITE_DEMO_MODE": "snapshot", "VITE_DATA_MODE": "real"})],
    "CHECK-SMOKE": [(["python", "scripts/workflow.py", "smoke"], ".", {})],
    "CHECK-QA": [(["python", "scripts/workflow.py", "validate"], ".", {})],
    "CHECK-FILES": [(["python", "tools/verify_files.py", "--all"], ".", {})],
    "CHECK-PLAN": [(["python", "scripts/plan.py", "check"], ".", {})],
    "CHECK-GUARD": [(["python", "scripts/git/guard.py", "--range", "origin/main...HEAD", "--user", "{pr_user}",
                      "--branch", "{branch}"], ".", {})],
}
LITERAL = re.compile(r"^(python|npm|npx|git) ")
NOT_IN_SOURCE_ZIP = {".csv", ".parquet", ".hdf", ".gz"}   # scripts/share_zip.py leaves these out


@dataclass
class Card:
    id: str
    path: Path
    meta: dict
    body: str

    @property
    def kind(self) -> str:
        return self.meta.get("kind", "")

    def get(self, key, default=None):
        return self.meta.get(key, default)


@dataclass
class Plan:
    root: Path
    cards: dict = field(default_factory=dict)
    status: dict = field(default_factory=dict)       # id -> {"Status":..., "Note":..., ...columns}
    status_order: list = field(default_factory=list)
    team: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


# ------------------------------------------------------------------ loading
def _front_matter(text: str):
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, text
    return yaml.safe_load(text[4:end]) or {}, text[end + 5:]


def _git(root: Path, *args) -> str | None:
    try:
        r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    except OSError:
        return None
    return r.stdout if r.returncode == 0 else None


def main_status_text(root: Path) -> str | None:
    """STATUS.md as merged on main (origin/main if fetched, else local main). Cards only count as done once merged.
    "" when main exists but has no board yet (the plan isn't merged, so nothing is done); None when there is no main."""
    for ref in ("origin/main", "main"):
        if _git(root, "rev-parse", "--verify", "--quiet", ref + "^{commit}") is None:
            continue
        return _git(root, "show", f"{ref}:docs/plan/STATUS.md") or ""
    return None


def in_flight(root: Path, prefix: str = "ws1") -> set:
    """Cards with a local branch <prefix>/<ID>-...: started here but not merged yet."""
    out = _git(root, "branch", "--list", f"{prefix}/*", "--format=%(refname:short)") or ""
    return {m.group(1) for m in (re.match(rf"^{re.escape(prefix)}/([THG]\d{{2}})-", b.strip()) for b in out.splitlines()) if m}


def read_status(path: Path, text: str | None = None):
    rows, order = {}, []
    if text is None:
        if not path.exists():
            return rows, order
        text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) != len(STATUS_COLUMNS) or not re.match(r"^[THG]\d{2}$", cols[0]):
            continue
        rows[cols[0]] = dict(zip(STATUS_COLUMNS, cols))
        order.append(cols[0])
    return rows, order


def load(root: Path = ROOT, status_from_main: bool = False) -> Plan:
    plan = Plan(root=root)
    plan.team = yaml.safe_load((root / "docs/plan/team.yaml").read_text(encoding="utf-8"))
    for p in sorted((root / "docs/plan/tasks").glob("*.md")):
        m = re.match(r"^([THG]\d{2})_[a-z0-9-]+\.md$", p.name)
        if not m:
            plan.errors.append(f"{p.name}: file name must be <ID>_<slug>.md, e.g. T07_season-api.md")
            continue
        meta, body = _front_matter(p.read_text(encoding="utf-8"))
        if meta is None:
            plan.errors.append(f"{p.name}: missing YAML front matter between '---' lines")
            continue
        plan.cards[m.group(1)] = Card(m.group(1), p, meta, body)
    text = main_status_text(root) if status_from_main else None
    plan.status, plan.status_order = read_status(root / "docs/plan/STATUS.md", text)
    return plan


def status_of(plan: Plan, cid: str) -> str:
    return plan.status.get(cid, {}).get("Status", "todo")


def needs_str(card: Card) -> str:
    return ", ".join(card.get("needs") or []) or "–"


# ------------------------------------------------------------------ validation
def _exists(root: Path, path: str) -> bool:
    if any(ch in path for ch in "*?["):
        return bool(glob.glob(str(root / path), recursive=True))
    return (root / path).exists()


def _ancestors(plan: Plan, cid: str, seen=None) -> set:
    seen = set() if seen is None else seen
    for n in plan.cards[cid].get("needs") or []:
        if n in plan.cards and n not in seen:
            seen.add(n)
            _ancestors(plan, n, seen)
    return seen


def _cycle(plan: Plan):
    state = {}

    def visit(c, stack):
        state[c] = 1
        for n in plan.cards[c].get("needs") or []:
            if n not in plan.cards:
                continue
            if state.get(n) == 1:
                return stack + [c, n]
            if state.get(n) is None:
                found = visit(n, stack + [c])
                if found:
                    return found
        state[c] = 2
        return None

    for c in plan.cards:
        if state.get(c) is None:
            found = visit(c, [])
            if found:
                return found
    return None


def validate(plan: Plan) -> Plan:
    E, W = plan.errors, plan.warnings
    people = plan.team.get("people", {})
    prefix = plan.team.get("branch_prefix", "ws1")
    creators = {}
    for cid, c in plan.cards.items():
        m = c.meta
        expected_kind = KINDS[cid[0]]
        keys = AGENT_KEYS if expected_kind == "agent" else HUMAN_KEYS
        for k in keys:
            if k not in m:
                E.append(f"{cid}: front matter is missing '{k}'")
        if m.get("id") != cid:
            E.append(f"{cid}: front matter id '{m.get('id')}' does not match the file name")
        if m.get("kind") != expected_kind:
            E.append(f"{cid}: kind must be '{expected_kind}' for an id starting with {cid[0]}")
        if m.get("owner") not in people:
            E.append(f"{cid}: owner '{m.get('owner')}' is not in docs/plan/team.yaml")
        if m.get("phase") not in PHASES:
            E.append(f"{cid}: phase must be one of {PHASES}")
        if m.get("size") not in SIZES:
            E.append(f"{cid}: size must be one of {SIZES}")
        for n in m.get("needs") or []:
            if n not in plan.cards:
                E.append(f"{cid}: needs unknown card {n}")
            elif n == cid:
                E.append(f"{cid}: needs itself")
            elif PHASES.index(plan.cards[n].get("phase", "P4")) > PHASES.index(m.get("phase", "P0")):
                E.append(f"{cid}: needs {n}, which is in a later phase ({plan.cards[n].get('phase')})")
        for r in m.get("requires") or []:
            if r not in REQUIRES:
                E.append(f"{cid}: unknown requirement '{r}' (allowed: {', '.join(REQUIRES)})")
        headings = AGENT_HEADINGS if expected_kind == "agent" else HUMAN_HEADINGS
        for h in headings:
            if not re.search(rf"^{re.escape(h)}\s*$", c.body, re.M):
                E.append(f"{cid}: body is missing the heading '{h}'")
        if expected_kind != "agent":
            continue
        for a in m.get("authors") or []:
            if a not in people:
                E.append(f"{cid}: author '{a}' is not in docs/plan/team.yaml")
        if m.get("owner") not in (m.get("authors") or []):
            E.append(f"{cid}: the owner must also be one of the authors")
        if not re.match(rf"^{re.escape(prefix)}/{cid}-[a-z0-9-]+$", str(m.get("branch", ""))):
            E.append(f"{cid}: branch must look like {prefix}/{cid}-short-name (PRs are opened as {plan.team.get('pr_user')})")
        for ch in m.get("checks") or []:
            if ch not in CHECKS and not LITERAL.match(str(ch)):
                E.append(f"{cid}: check '{ch}' is neither a named check ({', '.join(CHECKS)}) nor a python/npm/git command")
        for p in m.get("creates") or []:
            creators.setdefault(p, []).append(cid)
        authors = set(m.get("authors") or [])
        for p in list(m.get("touches") or []) + list(m.get("creates") or []):
            who = m.get("owner") if p in plan.team.get("shared", []) else owner_of(plan.team, p)
            if who is None:
                E.append(f"{cid}: nobody owns '{p}' in docs/plan/team.yaml")
            elif who not in authors:
                E.append(f"{cid}: '{p}' belongs to {who}, who is not in authors (split would refuse the commit)")
    for p, ids in creators.items():
        if len(ids) > 1:
            E.append(f"{p}: created by more than one card ({', '.join(ids)}); give it to one and make the other need it")
    for cid, c in plan.cards.items():
        if c.kind != "agent":
            continue
        st = status_of(plan, cid)
        upstream = set()
        for a in _ancestors(plan, cid):
            upstream.update(plan.cards[a].get("creates") or [])
        own = set(c.get("creates") or [])
        for p in c.get("touches") or []:
            if p in own:
                E.append(f"{cid}: '{p}' is listed in both touches and creates")
            elif not _exists(plan.root, p) and p not in upstream:
                if Path(p).suffix in NOT_IN_SOURCE_ZIP:
                    W.append(f"{cid}: cannot check '{p}' here (this file type is not in the source zip)")
                else:
                    E.append(f"{cid}: touches '{p}', which does not exist and is not created by a card it needs")
        if st in ("todo", "doing"):
            for p in own:
                if _exists(plan.root, p):
                    E.append(f"{cid}: creates '{p}', but it already exists (status {st})")
    cyc = _cycle(plan)
    if cyc:
        E.append("dependency cycle: " + " -> ".join(cyc))
    # board
    if not plan.status:
        E.append("docs/plan/STATUS.md has no rows")
    for cid in plan.cards:
        if cid not in plan.status:
            E.append(f"{cid}: no row in STATUS.md (run: python scripts/plan.py board --fix)")
    for cid, row in plan.status.items():
        if cid not in plan.cards:
            E.append(f"STATUS.md row {cid} has no card file")
            continue
        c = plan.cards[cid]
        if row["Status"] not in STATUSES:
            E.append(f"STATUS.md {cid}: status '{row['Status']}' is not one of {STATUSES}")
        expect = {"Kind": c.kind, "Title": c.get("title", ""), "Owner": c.get("owner", ""), "Needs": needs_str(c)}
        for col, val in expect.items():
            if row[col] != val:
                E.append(f"STATUS.md {cid}: column {col} is '{row[col]}', card says '{val}' (run: python scripts/plan.py board --fix)")
        if row["Status"] in ("doing", "review", "done"):
            for n in c.get("needs") or []:
                if status_of(plan, n) not in FINISHED:
                    W.append(f"{cid} is '{row['Status']}' but needs {n}, which is '{status_of(plan, n)}'")
    return plan


# ------------------------------------------------------------------ next
def _env_has(root: Path, name: str) -> bool:
    """True when the variable is set in the environment or in .env (the value is never read out or printed)."""
    if os.environ.get(name):
        return True
    env = root / ".env"
    return env.exists() and any(re.match(rf"^\s*{name}\s*=\s*\S+", line) for line in env.read_text(encoding="utf-8").splitlines())


def requirement_met(root: Path, req: str) -> bool:
    if req == "real-data":
        return (root / "data/processed/harmonized.parquet").exists()
    if req.startswith("secret:"):
        return _env_has(root, req.split(":", 1)[1])
    if req == "hf-token":
        return bool(os.environ.get("HF_TOKEN")) or (Path.home() / ".cache/huggingface/token").exists()
    if req == "gh-auth":
        try:
            return subprocess.run(["gh", "auth", "status"], capture_output=True).returncode == 0
        except OSError:
            return False
    if req == "earthdata-files":
        return bool(glob.glob(str(root / "data/raw/mcd64a1/*.hdf")))
    return True


def eligible(plan: Plan, met=None, flying: set | None = None):
    met = met or (lambda r: requirement_met(plan.root, r))
    flying = in_flight(plan.root, plan.team.get("branch_prefix", "ws1")) if flying is None else flying
    order = [c for c in plan.status_order if c in plan.cards] or sorted(plan.cards)
    ready, waiting_people, unmet = [], [], []
    for cid in order:
        c = plan.cards[cid]
        if status_of(plan, cid) != "todo" or cid in flying:
            continue
        if not all(status_of(plan, n) in FINISHED for n in c.get("needs") or []):
            continue
        if c.kind != "agent":
            waiting_people.append(cid)
            continue
        missing = [r for r in c.get("requires") or [] if not met(r)]
        (unmet if missing else ready).append((cid, missing))
    return [r[0] for r in ready], waiting_people, unmet


# ------------------------------------------------------------------ commands
def expand_checks(plan: Plan, card: Card, branch: str | None = None):
    out = []
    for ch in card.get("checks") or []:
        steps = CHECKS.get(ch)
        if steps is None:
            steps = [(shlex.split(ch), ".", {})]
        for cmd, cwd, env in steps:
            cmd = [x.format(pr_user=plan.team.get("pr_user", ""), branch=branch or card.get("branch", "")) for x in cmd]
            out.append((ch, cmd, cwd, env))
    return out


def _resolve(cmd):
    if cmd[0] == "python":
        return [sys.executable, *cmd[1:]]
    if cmd[0] in ("npm", "npx") and os.name == "nt":
        return [cmd[0] + ".cmd", *cmd[1:]]
    return cmd


def run_checks(plan: Plan, card: Card) -> int:
    branch = subprocess.run(["git", "branch", "--show-current"], cwd=plan.root, capture_output=True, text=True).stdout.strip()
    for name, cmd, cwd, env in expand_checks(plan, card, branch or None):
        shown = " ".join(cmd)
        print(f"--- {name}: {shown}  (in {cwd})", flush=True)
        r = subprocess.run(_resolve(cmd), cwd=plan.root / cwd, env={**os.environ, **env})
        if r.returncode != 0:
            print(f"FAIL {name}: {shown}  (exit {r.returncode}). Fix the cause; never weaken a test.", flush=True)
            return r.returncode
        print(f"PASS {name}", flush=True)
    print(f"ALL CHECKS PASSED for {card.id}")
    return 0


def owner_of(team: dict, path: str) -> str | None:
    best, who = -1, None
    for name, p in team.get("people", {}).items():
        for prefix in p.get("owns", []):
            hit = path == prefix or (prefix.endswith("/") and path.startswith(prefix))
            if hit and len(prefix) > best:
                best, who = len(prefix), name
    return who


def changed_paths(root: Path) -> list[str]:
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=root, capture_output=True,
                         text=True, check=True).stdout
    paths = []
    for line in out.splitlines():
        p = line[3:]
        if " -> " in p:
            p = p.split(" -> ", 1)[1]
        paths.append(p.strip().strip('"'))
    return paths


def split_commits(plan: Plan, card: Card, paths: list[str]):
    """[(person, author, [paths])] in a stable order; shared append-only files go with the card owner."""
    team = plan.team
    groups = {}
    for p in paths:
        who = card.get("owner") if p in team.get("shared", []) else owner_of(team, p)
        if who is None:
            raise SystemExit(f"split: nobody owns '{p}' in docs/plan/team.yaml; add it there or leave it out")
        groups.setdefault(who, []).append(p)
    authors = card.get("authors") or [card.get("owner")]
    stray = [w for w in groups if w not in authors]
    if stray:
        raise SystemExit(f"split: {card.id} lists authors {authors}, but changed files belong to {stray}: "
                         + "; ".join(f"{w}: {', '.join(groups[w])}" for w in stray)
                         + ". Either the change is out of scope for this card, or add the author to the card.")
    order = [a for a in authors if a in groups]
    return [(w, team["people"][w]["author"], sorted(groups[w])) for w in order]


def commit_note(card: Card, person: str) -> str:
    return (f"Plan card {card.id} ({card.get('title')}). Written with an AI coding agent at Sheikh's direction; "
            f"{person} reviews it in the pull request before merge.")


def set_status(root: Path, cid: str, status: str, note: str | None):
    if status not in STATUSES:
        raise SystemExit(f"status must be one of {STATUSES}")
    path = root / "docs/plan/STATUS.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        cols = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else []
        if cols and cols[0] == cid and len(cols) == len(STATUS_COLUMNS):
            cols[5] = status
            if note is not None:
                cols[6] = note.replace("|", "/")
            lines[i] = "| " + " | ".join(cols) + " |"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise SystemExit(f"{cid}: no row in STATUS.md")


def board_rows(plan: Plan) -> list[list[str]]:
    ids = [c for c in plan.status_order if c in plan.cards]
    ids += sorted(c for c in plan.cards if c not in ids)
    rows = []
    for cid in ids:
        c = plan.cards[cid]
        st = plan.status.get(cid, {})
        rows.append([cid, c.kind, c.get("title", ""), c.get("owner", ""), needs_str(c), st.get("Status", "todo"), st.get("Note", "")])
    return rows


def write_board(plan: Plan):
    """Rewrite the table in STATUS.md from the cards, keeping each row's status and note and all text around it."""
    path = plan.root / "docs/plan/STATUS.md"
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    first = next((i for i, ln in enumerate(lines) if ln.startswith("|")), len(lines))
    last = first
    while last < len(lines) and lines[last].startswith("|"):
        last += 1
    table = ["| " + " | ".join(STATUS_COLUMNS) + " |", "|" + "|".join("---" for _ in STATUS_COLUMNS) + "|"]
    table += ["| " + " | ".join(r) + " |" for r in board_rows(plan)]
    path.write_text("\n".join(lines[:first] + table + lines[last:]).rstrip("\n") + "\n", encoding="utf-8")


def show(plan: Plan, card: Card):
    team = plan.team["people"]
    print(f"{card.id}  {card.get('title')}")
    print(f"  file:     {card.path.relative_to(plan.root).as_posix()}")
    print(f"  kind:     {card.kind}   phase {card.get('phase')}   size {card.get('size')}   status {status_of(plan, card.id)}")
    print(f"  owner:    {card.get('owner')}   needs: {needs_str(card)}")
    if card.get("requires"):
        print(f"  requires: {', '.join(card.get('requires'))}")
    if card.kind == "agent":
        print(f"  branch:   {card.get('branch')}")
        for a in card.get("authors") or []:
            print(f"  author:   {a}: --author \"{team[a]['author']}\"")
        print("  checks:")
        for name, cmd, cwd, env in expand_checks(plan, card):
            envs = " ".join(f"{k}={v}" for k, v in env.items())
            print(f"    {name}: {(envs + ' ') if envs else ''}{' '.join(cmd)}  (in {cwd})")
    print(card.body)


# ------------------------------------------------------------------ CLI
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    n = sub.add_parser("next")
    n.add_argument("--all", action="store_true")
    s = sub.add_parser("show")
    s.add_argument("id")
    c = sub.add_parser("checks")
    c.add_argument("id")
    c.add_argument("--run", action="store_true")
    sp = sub.add_parser("split")
    sp.add_argument("--card", required=True)
    sp.add_argument("-m", "--message", required=True)
    sp.add_argument("--run", action="store_true")
    st = sub.add_parser("set")
    st.add_argument("id")
    st.add_argument("status")
    st.add_argument("--note")
    b = sub.add_parser("board")
    b.add_argument("--fix", action="store_true")
    a = ap.parse_args(argv)

    plan = load(ROOT)
    if a.cmd == "check":
        validate(plan)
        for w in plan.warnings:
            print("WARN ", w)
        for e in plan.errors:
            print("ERROR", e)
        print(f"plan: {len(plan.cards)} cards, {len(plan.errors)} errors, {len(plan.warnings)} warnings")
        return 1 if plan.errors else 0
    if a.cmd == "board":
        if a.fix:
            write_board(plan)
            print("STATUS.md columns rewritten from the cards (status and notes kept)")
            return 0
        for r in board_rows(plan):
            print(" | ".join(r))
        return 0
    if a.cmd == "set":
        set_status(plan.root, a.id, a.status, a.note)
        print(f"{a.id} -> {a.status}")
        return 0
    if a.cmd in ("show", "checks") and a.id not in plan.cards:
        raise SystemExit(f"unknown card {a.id}")
    if a.cmd == "show":
        show(plan, plan.cards[a.id])
        return 0
    if a.cmd == "checks":
        card = plan.cards[a.id]
        if a.run:
            return run_checks(plan, card)
        for name, cmd, cwd, env in expand_checks(plan, card):
            envs = " ".join(f"{k}={v}" for k, v in env.items())
            print(f"{name}: {(envs + ' ') if envs else ''}{' '.join(cmd)}  (in {cwd})")
        return 0
    if a.cmd == "next":
        validate(plan)
        if plan.errors:
            print("The plan has errors; fix them first (python scripts/plan.py check).")
            return 1
        plan = load(ROOT, status_from_main=True)       # done = merged on main
        flying = in_flight(plan.root, plan.team.get("branch_prefix", "ws1"))
        for cid in sorted(flying):
            if status_of(plan, cid) not in FINISHED:
                print(f"IN FLIGHT {cid}: branch exists, not merged yet (cards that need it wait)")
        ready, people, unmet = eligible(plan, flying=flying)
        if not ready:
            print("No agent card can start here right now.")
        for cid in (ready if a.all else ready[:1]):
            card = plan.cards[cid]
            print(f"NEXT {cid}: {card.get('title')}  (owner {card.get('owner')})")
            print(f"     read: {card.path.relative_to(plan.root).as_posix()}   branch: {card.get('branch')}")
        for cid in people:
            card = plan.cards[cid]
            print(f"WAITING ON {card.get('owner')}: {cid} {card.get('title')} ({card.kind})")
        for cid, missing in unmet:
            print(f"SKIPPED {cid}: needs {', '.join(missing)} on this machine")
        return 0
    if a.cmd == "split":
        if a.card not in plan.cards:
            raise SystemExit(f"unknown card {a.card}")
        card = plan.cards[a.card]
        staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=plan.root)
        if staged.returncode != 0:
            raise SystemExit("split: something is already staged; unstage it (git restore --staged .) and rerun")
        groups = split_commits(plan, card, changed_paths(plan.root))
        if not groups:
            print("Nothing to commit.")
            return 0
        for person, author, paths in groups:
            add = ["git", "add", "--", *paths]
            commit = ["git", "commit", "--author", author, "-m", a.message, "-m", commit_note(card, person)]
            print(" ".join(shlex.quote(x) for x in add))
            print(" ".join(shlex.quote(x) for x in commit))
            if a.run:
                subprocess.run(add, cwd=plan.root, check=True)
                subprocess.run(commit, cwd=plan.root, check=True)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
