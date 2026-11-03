# Samiul (Team Member 6): your instructions
Your job: check that what we show is true, and tell the story clearly.
Folders: ws6_validation/ and docs/. Prompt pack: prompts/ws6_samiul.md. Paste docs/AI_PREAMBLE.md first.

## H0 to H10: checks ready, data checked
1. Do P6.1. Talk to Sheikh: ask what the checklist must cover. Talk to Sattyam: ask when the mock URL lands (H3).
2. Do P6.2 once the mock is up.
3. Do P6.3: ask Monazir for detections (H6) and Sattyam for grid_daily and cells (H8). At H10 post a HANDOFF of the data QA report to both.
4. At H8 collect the en.json key list from Shammo.

## H12 to H24: story and first end-to-end run
5. Draft the slide outline and demo script (P6.7). Talk to Sheikh: confirm the story (observed vs modeled, limits).
6. Do P6.4 when the live API is up (H16). Send the bug list to Shammo and Sattyam. At H24 run the full end-to-end check.

## H30 to H42: validation content, method text
7. Repeat P6.4 at H30, H36 and H42.
8. Do P6.5: ask Sheikh for method notes and Samin for the validation pieces by H34. Post qa.json to Sattyam.
9. Do P6.6: write the method text (H38). Talk to Shammo: send it. Find a fluent teammate for the Bangla review (H42).

## H40 to H46: ship
10. Finish the slides (H40), record the video (H44), complete docs/SUBMISSION_CHECKLIST.md (H46). Talk to Sheikh: hand him the checklist for the submission.
11. Stretch only if ahead: P6.9 PM2.5. Talk to Monazir for the wording review.

## Rules and fallbacks
- Trace every number on a slide to a file. Never present PM2.5 as ground truth.
- If you fall behind, drop PM2.5, keep the checks, and protect time for the video and submission.

## Manual tasks
Things an AI agent cannot do for you are listed under your name in docs/MANUAL_TASKS.md, and repeated inside each of your phase prompts (prompts/phases/).

## Your workspace, what you may write, how to verify
- Work in: your laptop. Tests run against hosted URLs (API_BASE_URL=<url> pytest ws6_validation/tests). Branch prefix: ws6/.
- You may write: ws6_validation/; docs/method_en.md, method_bn.md, slides, demo script, QA and submission checklists; data/processed/validation/qa.json and pm25.json.
- You must not write: other people's code. File a bug in your list with the exact failing request and a screenshot; the owner fixes it.
- Verify before each HANDOFF: run your own tests against both the mock and the live API; open the app by hand on a phone; check every number on a slide against a file (docs/VERIFY.md).
