---
id: T35
title: Submission assets (slides page, recorded story video) and a 13 Nov rules re-check
kind: agent
owner: Samiul
authors: [Samiul, Sheikh]
phase: P3
size: M
needs: [T29, T30]
requires: [network]
branch: ws1/T35-submission-assets
touches: [docs/RULES_CHECK.md, docs/SUBMISSION_CHECKLIST.md]
creates: [docs/submission/slides.html, scripts/record_story.mjs]
checks: [CHECK-PLAN]
---
## Goal
Turn the T29 drafts into assets Sheikh can submit as they are: a slide deck that prints to PDF, and a 30-second
screen recording of story mode.

## Steps
1. **Rules re-check.** On or after 13 Nov, read the 2026 Participant Guide and the Project Submission Guide (linked
   from https://www.spaceappschallenge.org/2026/). Update `docs/RULES_CHECK.md` and `docs/SUBMISSION_CHECKLIST.md`
   with the exact fields and limits: video length, slide count, deadline. If they differ from T29's assumptions, adapt
   steps 2-3.
2. **`docs/submission/slides.html`.** A self-contained page (inline CSS, no external scripts). Each slide from
   `docs/submission/slides.md` is a 16:9 `<section>` with `page-break-after: always`. It uses the app's colours and
   fonts (IBM Plex Sans, Noto Sans Bengali, both from Google Fonts).
   - Numbers must keep their source comments.
   - Check it in the browser's print preview: one slide per page.
   - Export the PDF to `share/submission/slides.pdf` with Chrome headless:
     `"<chrome path>" --headless=new --print-to-pdf=share/submission/slides.pdf docs/submission/slides.html`.
3. **`scripts/record_story.mjs`.** A Playwright script, run with `npx --yes playwright@1.48.2`. It doesn't go into
   `package.json`.
   - Open the snapshot preview at `#s=1` (`npm run preview` in `ws5_frontend`) at 1280 × 720, and record video
     (`recordVideo`).
   - Press Next on the timings from `docs/submission/video_script.md` (about 30 seconds in total), then save to
     `share/submission/story.webm`.
   - If `ffmpeg` exists, also write an mp4:
     `ffmpeg -y -i story.webm -c:v libx264 -preset veryfast -crf 23 story.mp4`.
4. Check: the video is 28-32 seconds long (`ffprobe` if available; otherwise state "duration not measured"), and the
   PDF has at most 7 pages (or the guide's limit).
5. Run the checks, mark the card done, `split`, push and open the PR. `share/` is git-ignored, so list the asset paths
   and sizes in the PR, and tell Sheikh where they are.

## Acceptance
- [ ] `share/submission/slides.pdf` and `story.webm` (or `.mp4`) exist and are within the guide's limits.
- [ ] `RULES_CHECK.md` is updated from the 2026 guides, or says they weren't published yet.

## Stop and ask if
- The guide requires something we can't produce, such as live voice-over or a specific template.
