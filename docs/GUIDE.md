# End-to-end guide (start here)

One path from today to submission. Everything else is linked from here.

## 0. What this is
A web app that merges MODIS and VIIRS fire detections into one burning-activity calendar for any area a user draws, with uncertainty,
unusual periods, associated drivers and a season outlook. Six people, six workstreams, 48 hours. Read docs/PIPELINE.md (5 minutes)
and docs/KNOWN_GAPS.md (what is not verified). Words you do not know: docs/GLOSSARY.md.

## 1. Before the event (no project code)
1. Everyone: accounts (GitHub, Earthdata, your own FIRMS key); accept Sheikh's GitHub invitation; sign in (`gh auth login`); clone and run `bash scripts/git/setup.sh <your-github-username>` (docs/GIT_WORKFLOW.md section 0); install git, Python 3.11, Node LTS (Shammo); see docs/MANUAL_TASKS.md.
2. Everyone: read the file with your name in docs/instructions/, then your prompt pack in prompts/.
3. Sheikh: ask the organizers the questions in docs/H0_VERIFICATION.md (H0-01) and share the answers. Confirm the team is registered.
4. Everyone: bring chargers, power strips and a hotspot.

## 2. Day one, hour by hour
Follow docs/TIMELINE.md. In short: Kickoff H0-3, Data H3-8, Floor H8-24, Core H24-30, Scale-up H30-36, Polish H36-42, Ship H42-48.
- First 90 minutes: do the H0 verification list (docs/H0_VERIFICATION.md) and record results in docs/DECISIONS.md.
- Sheikh runs the gates and check-ins (docs/LEAD_GUIDE.md).

## 3. How each person works inside a phase
1. Open your AI chat. Paste docs/AI_PREAMBLE.md once.
2. At the start of each phase paste prompts/phases/00_agent_loop.md and your phase prompt (prompts/phases/wsN_..._phases.md).
3. Do the MANUAL items first; the agent cannot. Confirm them to the agent.
4. Let the agent work through the steps; use the numbered prompts (prompts/wsN_...md) for detail.
5. When a deliverable passes its test, run docs/VERIFY.md checks, post the HANDOFF message (docs/HANDOFF_TEMPLATE.md), and add a line to data/MANIFEST.md.

## 4. Hand-offs, ownership and safety
- Who talks to whom, when: docs/TALK_TO.md. Hand-off tracker: docs/LEAD_GUIDE.md.
- One writer per path: docs/FILE_OWNERSHIP.md. Rules for not interfering: docs/WORKING_TOGETHER.md.
- Contracts: contracts/ (change only through Sheikh; log in docs/CONTRACT_CHANGES.md).
- Where things live and run: docs/WHERE_TO_WORK.md. Stack: docs/TECH_STACK.md.

## 5. Verifying
Each deliverable has a check in docs/VERIFY.md. Producers verify before the HANDOFF; receivers verify before GOT IT; Samiul runs the end-to-end
check at H24, H30, H36 and H42 (docs/QA_CHECKLIST.md).

## 6. When things go wrong
- A hand-off is late: keep working on the fixture or stub; the sender says when it will land.
- A gate fails: cut by the order (Bangla polish, forecast alerts, PM2.5, comparison, forecast outlook (the current-status card and the where-map are never cut)); keep the floor; never move a gate more than two hours.
- The API is down: the static fallback keeps the demo alive.
- A check from H0 fails: change the decision in docs/DECISIONS.md first, then tell the affected person. See docs/RISKS.md.
- Someone is stuck: ask for the exact missing piece, then pair (docs/LEAD_GUIDE.md).

## 7. Ship
Samiul completes docs/SUBMISSION_CHECKLIST.md; Sheikh submits at H46 with a buffer and opens every link in a private window.

## 8. Index
| Need | File |
|---|---|
| Does the plan match the official challenge | docs/CHALLENGE_ALIGNMENT.md |
| What is not verified | docs/KNOWN_GAPS.md |
| First 90 minutes | docs/H0_VERIFICATION.md |
| Plain-language project | docs/PIPELINE.md, docs/GLOSSARY.md |
| Hour by hour | docs/TIMELINE.md |
| Your steps | docs/instructions/ |
| Your prompts | prompts/, prompts/phases/ |
| Things only people can do | docs/MANUAL_TASKS.md |
| Git commands and scripts | docs/GIT_WORKFLOW.md |
| Stack, locations, ownership, rules | docs/TECH_STACK.md, WHERE_TO_WORK.md, FILE_OWNERSHIP.md, WORKING_TOGETHER.md |
| Verification | docs/VERIFY.md |
| Lead's guide | docs/LEAD_GUIDE.md |
| Risks and decisions | docs/RISKS.md, DECISIONS.md |
