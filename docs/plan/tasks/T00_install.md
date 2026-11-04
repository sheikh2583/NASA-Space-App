---
id: T00
title: Install the plan and set integration permissions
kind: agent
owner: Sheikh
authors: [Sheikh, Sattyam, Samin, Shammo]
phase: P0
size: S
needs: []
requires: []
branch: ws1/T00-install-plan
touches: [scripts/team.csv, docs/plan/STATUS.md]
creates: []
checks: [CHECK-PLAN, CHECK-PY, CHECK-WEB, CHECK-SNAP]
---
## Goal
Put the plan, its tools and the already-tested libraries on `main` without changing any number on the live site.
This also lets one machine (Sheikh's laptop, account sheikh2583) open every pull request.

## Context
`firesense-win-plan.patch` (delivered in chat on 4 Nov) adds:
- `docs/plan/` and `scripts/plan.py`, plus the root `AGENTS.md`;
- the outage audit (`ws2_platform/coverage.py`, `common/outages.yaml`);
- the season-profile library (`ws4_outlook/season_profile.py`) with its draft schema and fixture;
- the CI-safe API test fixture (`ws2_platform/tests/conftest.py`, `tiny_data.py`);
- the web component-test helper (`ws5_frontend/src/test/render.tsx`);
- `tools/verify_files.py --all`.

PRs are opened as sheikh2583, so `scripts/git/guard.py` checks every changed file against sheikh2583's row in
`scripts/team.csv` and requires branch names to start with `ws1/`. Today that row only covers Sheikh's folders, so any
card that touches a teammate's folder would be blocked (in CI, and locally by the pre-commit hook).

## Steps
1. Make sure the working tree is clean: `git status --short` prints nothing. Then:
   `git switch main && git pull --ff-only && git switch -c ws1/T00-install-plan`.
2. Copy `firesense-win-plan.patch` to the repo root and run `git apply --check firesense-win-plan.patch`. If it fails,
   stop and report the first failing file.
3. Run `git apply firesense-win-plan.patch`, then `del firesense-win-plan.patch` (PowerShell) or
   `rm firesense-win-plan.patch`.
4. **Integration permissions.** Open `scripts/team.csv` and find the row whose first column is `sheikh2583`.
   - Append the following to the end of its `allowed` column (colon-separated, no spaces):
     `:common/:ws2_platform/:ws3_anomaly/:ws4_outlook/:ws5_frontend/:ws6_validation/:contracts/:CLAUDE.md:AGENTS.md:pytest.ini:LICENSE`
   - Don't change any other row. Commits still carry each owner's name (`--author`), and owners still review their
     folders in the PR. Only the account that opens the PR changes.
5. Run `python scripts/plan.py check`; it must print `0 errors`.
6. Run the checks: `python scripts/plan.py checks T00 --run`.
7. Run `python scripts/plan.py set T00 done --note "plan installed"`.
8. Commit one commit per owner: `python scripts/plan.py split --card T00 -m "T00: install the win plan" --run`.
9. Check ownership before pushing:
   `python scripts/git/guard.py --range origin/main...HEAD --user sheikh2583 --branch ws1/T00-install-plan`.
   It must print `guard: ok`.
10. `git push -u origin ws1/T00-install-plan` and open a PR titled "T00: install the win plan". In the description,
    list the new folders, and include the CHECK results under "Measured".

## Acceptance
- [ ] `python scripts/plan.py check`: 0 errors.
- [ ] CHECK-PY passes, including 54 new tests: 13 coverage, 10 season profile, 11 tiny API and 20 plan tool. No test
  that passed before fails.
- [ ] CHECK-WEB and CHECK-SNAP pass. That includes the component-harness test.
- [ ] The guard prints `guard: ok`.
- [ ] After merge, the Pages deploy is green and the site looks unchanged, because `snapshot.json` is untouched.

## Stop and ask if
- `git apply --check` fails.
- `scripts/team.csv` has no `sheikh2583` row, or its columns differ from `github,name,slot,prefix,folder,allowed`.
- Any existing test fails after the patch.
