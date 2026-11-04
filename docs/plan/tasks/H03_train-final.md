---
id: H03
title: "Sheikh: final training run for the release (by 12 Nov)"
kind: human
owner: Sheikh
phase: P3
size: S
needs: [T34]
---
## Goal
One last full run on the frozen code, so that everything shown at the event comes from one reproducible state. The
agent then validates, publishes and tags it (T28).

## Steps
1. Make sure every feature pull request you want is merged. After this run, only fixes go in.
2. Run `git switch main && git pull`, then `git status --short`; it must print nothing.
3. Run `.venv\Scripts\python scripts\workflow.py prepare`, then `.venv\Scripts\python scripts\workflow.py train`
   (full).
4. Tell the agent: "H03 is done". It continues with T28: validate, export, tag `v1.0-event`.

## Done when
- The full run finished by 12 Nov, 20:00 Dhaka.
