---
id: T29
title: Draft the submission text, slide content and video script from measured numbers
kind: agent
owner: Samiul
authors: [Samiul]
phase: P3
size: S
needs: [T28]
requires: []
branch: ws1/T29-submission-draft
touches: [docs/project/submission-checklist.md, docs/project/demo-script.md]
creates: [docs/submission/project_page.md, docs/submission/slides.md, docs/submission/video_script.md]
checks: [CHECK-PLAN]
---
## Goal
Write ready-to-edit drafts in which every claim traces to a measured number or a cited source. The agent turns them
into assets (T35), and Sheikh submits (H04).

## Steps
1. Read:
   - `docs/results/training-results.md` (the "Release v1.0-event" section);
   - `docs/REFERENCES.md`, `docs/AI_USE.md` and `docs/RULES_CHECK.md`;
   - the Validation page pieces in `ws5_frontend/public/demo/snapshot.json`.
2. **`docs/submission/project_page.md`:**
   - a title;
   - a summary of at most 300 words: problem, data, method, product, findings, users;
   - "How we used NASA data", one bullet per product;
   - the live site URL, the repository URL and the tag;
   - "References" (copied from `docs/REFERENCES.md`) and "Use of AI" (from `docs/AI_USE.md`).
3. **`docs/submission/slides.md`:** 7 slides at most, each with a title, 3 bullets and a speaker note.
   1. Problem
   2. Data (2000-2026, three satellite eras)
   3. Method (harmonization, held-out CCC, calibrated bands, outage handling)
   4. Findings (the three-part Punjab result, and the Bangladesh contrast)
   5. Product (calendar, season card, brief, story, regions, live data)
   6. Validation (held-out metrics, truth checks, the independent burned-area check)
   7. Impact and next steps
4. **`docs/submission/video_script.md`:** 30 seconds, 4 shots, each with seconds, the on-screen view (a story-mode
   step) and voice-over. English, with subtitles noted if any Bangla is spoken:

   | Seconds | Shot |
   |---|---|
   | 0-5 | Problem |
   | 5-12 | 26 years, one record (the seam) |
   | 12-22 | What we found (trends and blind spot) |
   | 22-30 | Use it (regions, brief, Bangla, URL) |

5. **Numbers.** Every number in the three files is copied from the release section, with the source in a trailing
   HTML comment, for example `<!-- TRAINING_RESULTS v1.0-event, CCC -->`.
6. Add the three files to `docs/project/submission-checklist.md`, and make sure `docs/project/demo-script.md` matches story mode.
7. Run the checks, mark the card done, `split`, push and open the PR.

## Acceptance
- [ ] Each number has a source comment. No claim says "proves", "causes" or "detects all fires".
- [ ] The project page summary is at most 300 words: `python -c "import re;t=open('docs/submission/project_page.md').read();print(len(re.findall(r'\w+', t.split('## ')[1])))"`
  prints ≤ 300. Adjust the split if the headings differ.

## Stop and ask if
- `docs/RULES_CHECK.md` gives different limits for the video or the slides.
