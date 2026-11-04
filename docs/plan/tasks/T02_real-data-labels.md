---
id: T02
title: Confirm that no validation piece still says "synthetic data" (read-only check)
kind: agent
owner: Samin
authors: [Samin, Sheikh]
phase: P0
size: S
needs: [T00]
requires: [real-data]
branch: ws1/T02-real-data-labels
touches: [docs/project/known-gaps.md]
creates: []
checks: [CHECK-PLAN]
---
## Goal
The old live site said "Built on SYNTHETIC data; rerun on real data before quoting" under drift, intervals and outlook
skill, although the run used real FIRMS data. The source is already fixed on `main`: `ws4_outlook/run.py` `piece()`
swaps that sentence for "Computed from downloaded FIRMS observations." when real FIRMS files exist (commit `bf800af`).
This card only checks the saved outputs and the deployed service. **It changes no data and runs no pipeline step.**

## Steps
1. Read-only check of the saved pieces:
   `python -c "import glob,json;print([p for p in glob.glob('data/processed/validation/*.json') if 'SYNTHETIC' in open(p,encoding='utf-8').read()])"`.
   It must print `[]`.
2. The same check on `ws5_frontend/public/demo/snapshot.json`, the legacy fallback.
3. If `RENDER_URL` is set: fetch `$RENDER_URL/meta/validation` and search it for `SYNTHETIC`.
4. If all three are clean, mark the card done with the note "labels verified clean". Otherwise add a line to
   `docs/project/known-gaps.md` naming the files. The next training run (H02) rewrites them through `piece()`, and T40
   re-checks. Don't edit any data file by hand.
5. Run the checks, mark the card done, and hand over for commit (only if `docs/project/known-gaps.md` changed).

## Acceptance
- [ ] All three checks pasted, each `[]` or listed in `docs/project/known-gaps.md`.

## Stop and ask if
- `piece()` no longer contains the replacement. Then the source fix was lost and needs a new card.
