#!/usr/bin/env python3
"""Ownership guard: checks that changed files belong to the person making the change.
Local:  guard.py --staged                      (used by the pre-commit hook)
CI:     guard.py --range BASE...HEAD --user LOGIN --branch NAME
Set GUARD_OVERRIDE=1 locally to bypass (never in CI). Stdlib only."""
import argparse, csv, os, subprocess, sys

ROOT = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
APPEND_ONLY = {"data/MANIFEST.md", "docs/project/contract-changes.md"}
SHARED_OK = APPEND_ONLY
DATA_OK = {"data/MANIFEST.md", "data/README.md", "data/.gitkeep"}
BLOCKED_PREFIXES = ("data/", "node_modules/", ".venv/")
BLOCKED_NAMES = (".env",)
MAX_BYTES = 5 * 1024 * 1024

def git(*a):
    return subprocess.check_output(["git", *a], text=True, cwd=ROOT)

def team():
    with open(os.path.join(ROOT, "scripts", "team.csv"), newline="") as f:
        return {r["github"].lower(): r for r in csv.DictReader(f)}

def ok_path(path, prefixes):
    return any(path == p or (p.endswith("/") and path.startswith(p)) for p in prefixes)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staged", action="store_true")
    ap.add_argument("--range")
    ap.add_argument("--user")
    ap.add_argument("--branch")
    a = ap.parse_args()
    if os.environ.get("GUARD_OVERRIDE") == "1" and not os.environ.get("CI"):
        print("guard: override on (local only)"); return 0
    t = team()
    if a.staged:
        me_file = os.path.join(ROOT, ".git", "team-me")
        user = open(me_file).read().strip() if os.path.exists(me_file) else ""
        if not user:
            print("guard: run  bash scripts/git/setup.sh <your-github-username>  first"); return 1
        status = git("diff", "--cached", "--name-status", "--no-renames")
        numstat = git("diff", "--cached", "--numstat", "--no-renames")
        size_of = lambda p: int(git("cat-file", "-s", ":" + p).strip())
    else:
        user = a.user or ""
        status = git("diff", "--name-status", "--no-renames", a.range)
        numstat = git("diff", "--numstat", "--no-renames", a.range)
        head = a.range.split("...")[-1]
        size_of = lambda p: int(git("cat-file", "-s", head + ":" + p).strip())
    row = t.get(user.lower())
    if row is None:
        print(f"guard: '{user}' is not in scripts/team.csv"); return 1
    allowed = row["allowed"].split(":")
    deletions = {}
    for line in numstat.splitlines():
        add, dele, path = line.split("\t", 2)
        deletions[path] = 0 if dele == "-" else int(dele)
    errors = []
    if a.branch and not a.branch.startswith(row["prefix"] + "/"):
        errors.append(f"branch '{a.branch}' must start with '{row['prefix']}/'")
    for line in status.splitlines():
        st, path = line.split("\t", 1)
        if path in DATA_OK:
            pass
        elif path.startswith(BLOCKED_PREFIXES) or os.path.basename(path) in BLOCKED_NAMES:
            errors.append(f"{path}: data, keys and environments never go into git")
            continue
        if path in SHARED_OK:
            if deletions.get(path, 0) > 0 or st == "D":
                errors.append(f"{path}: append-only file; do not delete or edit existing lines")
            continue
        if not ok_path(path, allowed) and path not in DATA_OK:
            errors.append(f"{path}: not yours (you may change: {', '.join(allowed)})")
        if st != "D":
            try:
                if size_of(path) > MAX_BYTES:
                    errors.append(f"{path}: larger than 5 MB; put big files on the shared drive")
            except Exception:
                pass
    if errors:
        print("guard: blocked")
        for e in errors: print("  - " + e)
        print("Fix: unstage with  git restore --staged <path>  and, if you need a change in someone else's file, ask the owner (CONTRIBUTING.md).")
        return 1
    print("guard: ok"); return 0

if __name__ == "__main__":
    sys.exit(main())
