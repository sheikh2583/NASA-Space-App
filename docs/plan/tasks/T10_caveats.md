---
id: T10
title: Caveats and "how we checked" on the method page (en, bn draft)
kind: agent
owner: Samiul
authors: [Samiul]
phase: P1
size: S
needs: [T31]
requires: []
branch: ws1/T10-caveats
touches: [docs/method_en.md, docs/method_bn.md]
creates: []
checks: [CHECK-PLAN, CHECK-WEB, CHECK-SNAP]
---
## Goal
Say plainly what the numbers can and can't tell you, and how we checked them. Validity is a fifth of the score, and
honest limits read as strength.

## Context
- The Method page renders `docs/method_<lang>.md` (copied into `public/` by `ws5_frontend/scripts/copy-method.mjs`)
  with a tiny renderer (`renderMd` in `src/components/Pages.tsx`).
- It supports **only**: `# ` and `## ` headings, `- ` list items, `**bold**` and plain paragraphs. No links, tables,
  `###` or numbered lists, so write URLs as plain text.
- T31 has produced `ws6_validation/truth_checks.md`.

## Steps
1. Append to `docs/method_en.md` a section `## What these numbers can and can't tell you`, with these list items
   (keep them short, in plain words):
   - Detections are not area burned. Small, short, cloud-covered or under-canopy fires are missed; a quiet week isn't
     proof that nothing burned.
   - Satellites pass at fixed times: Terra about 10:30, Aqua and Suomi NPP about 13:30, NOAA-20 about 50 minutes
     from Suomi NPP. NASA has reported Punjab burning moving later in the day, so falling counts can partly mean
     fires burned while no satellite was looking. Source: science.nasa.gov/?p=1160169
   - Every year is shown as if seen by VIIRS on Suomi NPP. Before 2012 values are estimated from MODIS and carry wider
     bands.
   - Suomi NPP fire data ended on 2 November 2026; later weeks use NOAA-20 scaled to the same standard. Terra and
     Aqua are ending their missions.
   - Season timing ("usually from … to …") counts when 10% and 90% of a season's detections had happened. It isn't
     the date fields were set alight.
   - Weather links are associations, not causes.
   - This is not an alert service; for emergencies use national services and FIRMS directly.
2. Append `## How we checked`. Write one list item per truth check from `ws6_validation/truth_checks.md` (T31), in
   the form "check: FIRMS value, our value, verdict". Then add one item each for:
   - held-out agreement: "Lin's CCC 0.9417 for the chosen method on six held-out tests (4 Nov 2026 run)";
   - band coverage: "91.6% weekly, 93.7% monthly for nominal 90% bands".
   Copy the numbers exactly from `docs/TRAINING_RESULTS.md`; if T40 has added a newer section, use that one.
3. Translate both sections into Bangla at the end of `docs/method_bn.md`, in the same structure. Add a first line
   inside the section, in Bangla: "**Translation drafted with AI assistance.**" Keep it there unless a fluent
   reviewer checks the text.
4. Run the checks. Open the Method page in the snapshot build (`npm run preview`) in both languages and check every
   bullet renders as a list item, with no raw `#` or `*`.
5. Mark the card done, `split`, push and open the PR.

## Acceptance
- [ ] Both sections appear on the Method page in en and bn, using only supported Markdown.
- [ ] Every number matches `docs/TRAINING_RESULTS.md` and `ws6_validation/truth_checks.md`.

## Stop and ask if
- `ws6_validation/truth_checks.md` is missing (T31 not merged).
