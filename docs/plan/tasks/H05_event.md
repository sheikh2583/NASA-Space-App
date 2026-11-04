---
id: H05
title: "Sheikh: event days (14-15 Nov)"
kind: human
owner: Sheikh
phase: P4
size: S
needs: [H04]
---
## Goal
A calm event: no new features, fixes only, and a fallback for everything.

## Steps
1. **Morning of 14 Nov.** Open the Render URL once, to wake it; that takes about a minute after a sleep. Then ask the
   agent to run `python scripts/check_render.py` (T17). All checks must pass.
   - The live season feed (T19) must show "Data through" yesterday or the day before.

   If something fails, the local fallback still carries the demo. Stop debugging after 30 minutes.
2. **During the event.** Allow only bug fixes from the agent. Each must pass its card's agent-safe checks and
   CHECK-WEB.
3. **Demo.** Follow `docs/project/demo-script.md`, which follows story mode, for 3 minutes. Rehearse once. Open the site
   10 minutes before you present, so it is awake.
4. **If something breaks:**

   | Problem | Action |
   |---|---|
   | Render down or stuck | In the Render dashboard: Manual Deploy → Deploy latest commit. Otherwise run `scripts\start.ps1` (Linux: `bash scripts/start.sh`) and present from `localhost`. |
   | Wrong data after a deploy | Put the previous URL and SHA256 back in `deployment/runtime.json`, commit; Render rebuilds (`docs/guides/deployment.md`). |
   | FIRMS down | The live feed says stale, with a note; the record itself is unaffected. |
   | Out of memory on the free tier | Present from `localhost`; don't upgrade the plan during judging. |

## Done when
- Judging is over.
