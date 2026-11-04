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
Apply the outage correction (T06) to the whole record. Training is your manual step; the agent reports the results
afterwards (T40).

## Steps
1. Merge the T06 pull request, then run `git switch main && git pull`.
2. Run `.venv\Scripts\python scripts\workflow.py train` (full, not `--quick`; about 12 minutes on 4 Nov). Note the
   wall time.
3. If it stops with "step '<name>' failed", resume with
   `.venv\Scripts\python scripts\workflow.py train --from <name>` after the fix, or send the error to the agent.
4. Tell the agent: "H02 is done, training took <minutes>". It runs `python scripts/plan.py set H02 done` and continues
   with T40.

## Done when
- The full run finished with every stage at exit code 0.
