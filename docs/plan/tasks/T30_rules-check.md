---
id: T30
title: Check the Space Apps rules and record them with quotes
kind: agent
owner: Sheikh
authors: [Sheikh, Samiul]
phase: P0
size: S
needs: [T00]
requires: [network]
branch: ws1/T30-rules-check
touches: [docs/project/submission-checklist.md]
creates: [docs/RULES_CHECK.md]
checks: [CHECK-PLAN]
---
## Goal
Know, with quotes, what the 2026 rules say about work done before the event, team size, submission fields, deadlines
and AI use. A rules problem would undo everything else.

## Steps
1. Read these pages with your web tool:
   - https://www.spaceappschallenge.org/resources/participant-faqs/
   - https://spaceappschallenge.org/resources/judging-awards-guide
   - the 2026 challenge page linked from https://www.spaceappschallenge.org/2026/
   - any "terms", "rules" or "participant agreement" page linked from those.

   If you can't reach the web, write `UNVERIFIED: no web access` at the top and list the URLs to check.
2. Create `docs/RULES_CHECK.md` with one table: question, answer, **exact quote**, URL, and the date read. Cover:
   - work done before the event: allowed or not, and under what conditions;
   - team size and registration;
   - the submission deadline in local time;
   - required fields (video or slides limits, links, references);
   - any rule on AI tools;
   - the originality confirmation.

   Where a page doesn't answer, write "not stated". Never guess. Note that the 2026 Participant Guide and the Project
   Submission Guide are published on 13 Nov, and that card T35 re-checks them.
3. If any quote says pre-event work isn't allowed, put that in bold at the top, then **stop and ask Sheikh** before
   any other card.
4. Add a link to `docs/RULES_CHECK.md` at the top of `docs/project/submission-checklist.md`.
5. Run the checks, mark the card done, `split`, push and open the PR.

## Acceptance
- [ ] Every answer has a quote and a URL, or says "not stated".
- [ ] The read date is recorded.

## Stop and ask if
- Any rule limits pre-event work or AI use.
