---
id: H02
title: "Sheikh: full training run with the outage handling"
kind: human
owner: Sheikh
phase: P1
size: S
needs: [T06]
---
## Goal
Apply the outage correction (T06) to the whole record. All training is your manual step (`AGENTS.md`). This run also
covers the human-only checks that cards have listed since the last run. The agent reports the results afterwards
(T40).

## Steps
Commands are from `docs/guides/training.md`.
1. Commit T06 (and anything else ready), then make sure `git status --short` prints nothing.
2. Run the one-command training with the deployment ZIP:
   - Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\train.ps1 -Pack`
   - Linux: `bash scripts/train.sh --pack`

   It runs, in order: weather (if missing), readiness, the quick run, a pause, the full run, QA (`validate`), the
   results summary, and the runtime ZIP. Add `-Yes` / `--yes` to skip the pause. Note the wall time. If it stops,
   read the log it names, fix the cause, and resume with `-From <stage>` / `--from <stage>`. Or send the error to
   the agent.
3. Human-only checks, batched (`.venv\Scripts\python` on Windows, `.venv/bin/python` on Linux):
   - `python -m pytest -q` (the full suite, including tests that fit learners);
   - `python scripts/workflow.py smoke`.

   To see what the cards asked for, run `python scripts/plan.py show <ID>` for each card done since the last run.
4. Tell the agent: "H02 is done, training took <minutes>; QA, pytest and smoke passed" (or paste the failures). It
   runs `python scripts/plan.py set H02 done` and continues with T40, which publishes `share/firesense-runtime.zip`.

## Done when
- The full run finished with every step at exit code 0 (`results/latest.md`), and the pytest and smoke results are
  reported.
