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
1. **Morning of 14 Nov.** Ask the agent to check the live site:
   - the latest Pages run is green;
   - "Data through" is yesterday or the day before (T19);
   - `/health` of the hosted API answers (T17).

   If something fails, the snapshot still carries the demo. Stop debugging after 30 minutes.
2. **During the event.** Allow only bug-fix pull requests from the agent, and each must pass CHECK-SNAP.
3. **Demo.** Follow `docs/demo_script.md`, which follows story mode, for 3 minutes. Rehearse once.
4. **If something breaks:**

   | Problem | Action |
   |---|---|
   | Site down | Ask the agent to re-run the Pages workflow. Otherwise run `START_HERE.cmd` locally. |
   | API down | Hybrid mode falls back to the snapshot. |
   | FIRMS down | The status card shows stale data with a note. |

## Done when
- Judging is over.
