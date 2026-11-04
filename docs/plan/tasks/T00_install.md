---
id: T00
title: Finish the plan install (integration permissions and baseline checks)
kind: agent
owner: Sheikh
authors: [Sheikh]
phase: P0
size: S
needs: []
requires: []
branch: ws1/T00-install-plan
touches: [scripts/team.csv, docs/plan/STATUS.md]
creates: []
checks: [CHECK-PLAN, CHECK-TESTS, CHECK-WEB, CHECK-SNAP]
---
## Goal
The plan, its tools and the tested libraries are already on `main`; Sheikh merged them by hand. Finish the install
without changing any number on the site:
- record a clean baseline of the agent-safe checks;
- let the optional pull-request flow pass the ownership guard.

## Context
- Sheikh normally commits and pushes to `main` himself (`AGENTS.md`, "Work plan").
- When he asks for the pull-request flow instead, every PR is opened as sheikh2583. `scripts/git/guard.py` then checks
  every changed file against sheikh2583's row in `scripts/team.csv`, and requires branches to start with `ws1/`. Today
  that row only covers Sheikh's folders, so any card that touches a teammate's folder would be blocked.

## Steps
1. `git status --short` must print nothing. Then `git switch main && git pull --ff-only`.
2. **Integration permissions.** In `scripts/team.csv`, find the row whose first column is `sheikh2583`, and append
   this to the end of its `allowed` column (colon-separated, no spaces):
   `:common/:ws2_platform/:ws3_anomaly/:ws4_outlook/:ws5_frontend/:ws6_validation/:contracts/:deployment/:Dockerfile:render.yaml:CLAUDE.md:AGENTS.md:pytest.ini:LICENSE`.
   Don't change any other row. Commits still carry each owner's name (`--author`).
3. Run `python scripts/plan.py check`. It must print `0 errors, 0 warnings`.
4. Run `python scripts/plan.py checks T00 --run`. These are the agent-safe checks only:
   - the reviewed non-fitting tests (CHECK-TESTS);
   - the web tests, string check and build, the way the Render image builds them (CHECK-WEB);
   - the legacy snapshot build (CHECK-SNAP).
5. Run `python scripts/plan.py set T00 done --note "plan installed; agent-safe baseline green"`, then hand over for
   commit. Sheikh commits, unless he asked for the pull-request flow.

## Acceptance
- [ ] `python scripts/plan.py check`: 0 errors, 0 warnings.
- [ ] The CHECK-TESTS, CHECK-WEB and CHECK-SNAP results are pasted into the hand-over, with the number of tests
  passed.
- [ ] After Sheikh pushes, Render rebuilds. The data is unchanged, so `/health` still reports the same
  `data_through`; T17 checks this with a script.

## Stop and ask if
- `scripts/team.csv` has no `sheikh2583` row, or its columns differ from `github,name,slot,prefix,folder,allowed`.
- Any agent-safe check fails on a clean `main`.
