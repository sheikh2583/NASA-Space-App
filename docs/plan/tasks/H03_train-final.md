---
id: H03
title: "Sheikh: final training run for the release (by 12 Nov)"
kind: human
owner: Sheikh
phase: P3
size: S
needs: [H02]
---
## Goal
One last full run on the frozen code, so that everything shown at the event comes from one reproducible state. The
agent then reports, publishes to Render and tags it (T28).

## Steps
Commands are from `docs/guides/training.md`.
1. Make sure every feature you want is committed. After this run, only fixes go in.
2. Run `git status --short`; it must print nothing.
3. Run the one-command training with the deployment ZIP:
   - Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\train.ps1 -Pack`
   - Linux: `bash scripts/train.sh --pack`

   This includes readiness, the quick and full runs, QA and the results summary. Note the wall time.
4. Human-only checks for the release: `python -m pytest -q` and `python scripts/workflow.py smoke`, with the
   project's `.venv` Python.
5. Tell the agent: "H03 is done", with the wall time and the check results. It continues with T28: report, publish
   the runtime data to Render, tag `v1.0-event`.

## Done when
- The full run and the checks finished by 12 Nov, 20:00 Dhaka.
