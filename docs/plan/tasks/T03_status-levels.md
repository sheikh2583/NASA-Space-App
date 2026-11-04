---
id: T03
title: Lower-than-usual status levels and honest status wording
kind: agent
owner: Samin
authors: [Samin, Sheikh, Sattyam, Shammo]
phase: P0
size: S
needs: [T00]
requires: [real-data]
branch: ws1/T03-status-levels
touches: [ws4_outlook/outlook.py, ws4_outlook/tests/test_outlook.py, contracts/openapi.yaml,
          contracts/json_schemas/outlook_region.schema.json, docs/CONTRACT_CHANGES.md, ws5_frontend/src/types.ts,
          ws5_frontend/src/components/Panels.tsx, ws5_frontend/src/styles.css, ws5_frontend/src/i18n/en.json,
          ws5_frontend/src/i18n/bn.json, ws5_frontend/public/demo/snapshot.json]
creates: [ws5_frontend/src/components/Panels.test.tsx]
checks: [CHECK-PLAN, CHECK-PY, CHECK-WEB, CHECK-SNAP, CHECK-FILES]
---
## Goal
Two wrong status cards are live today (measured on 4 Nov from the snapshot):
- **Punjab:** the week of 26 Oct 2026 has 305 detections, against a typical 13,019 for that week. It ranks at
  percentile 0, yet the card says "Normal" and "Higher than 0% of the same week in past years".
- **Bangladesh:** the same week has 3 detections, against a typical 0. It ranks at percentile 98, so the card says
  "High" ("much higher than usual") for 3 fires.

Add `low` and `very_low` levels, ignore differences too small to matter, and make every wording state the rank
plainly.

## Context
- `ws4_outlook/outlook.py` `current_status()`:
  - `level` is `high` when the percentile of the week's lower bound ≥ 90; `watch` when the percentile of its value
    ≥ 80; otherwise `none`.
  - `percentile_of` uses mid-ranks, so a zero week among zero weeks scores 50.
- In `contracts/openapi.yaml`, `CurrentStatus.level` refers to the shared `AlertLevel` enum (`none`, `watch`,
  `high`), which forecast alerts use too.
- `contracts/json_schemas/outlook_region.schema.json` repeats the enum under `current_status.level`.
- The UI shows `t("status.level_" + level)` plus `status.percentile`. It never shows the server's `message`.

## Steps
1. **Contract.**
   - In `contracts/openapi.yaml`, add a schema `StatusLevel` (string; enum `very_low`, `low`, `none`, `watch`,
     `high`) and point `CurrentStatus.level` at it. Leave `AlertLevel` and `alert.level` unchanged.
   - In `outlook_region.schema.json`, add `very_low` and `low` to `current_status.level`'s enum only.
   - Don't change `SCHEMA_VERSION`; additive enum values follow the "adding is fine" rule.
   - Append a dated line to `docs/CONTRACT_CHANGES.md` ("CurrentStatus.level gains very_low and low; AlertLevel
     unchanged").
2. **Logic** (`ws4_outlook/outlook.py`). Add the constants `LOW, VERY_LOW, MIN_CHANGE = 25.0, 10.0, 10.0`. Then:
   - `hi_pct` = the percentile of the week's upper bound `hi`, or of the value if `hi` is missing. This mirrors
     `lo_pct`.
   - `typical` = the median of the same week in past years (`same`).
   - The level is the first rule that matches:

     | Level | Rule |
     |---|---|
     | `none` | `abs(value - typical) < MIN_CHANGE`: fewer than 10 detections from typical never counts as unusual, either way |
     | `high` | `lo_pct >= HIGH` |
     | `watch` | `pct >= WATCH` |
     | `very_low` | `hi_pct <= VERY_LOW` |
     | `low` | `pct <= LOW` |
     | `none` | otherwise |

   - Messages: `LEVEL_WORDS` gains `"low": "lower than usual"` and `"very_low": "much lower than usual"`. Change
     `"none"` to `"within the usual range"`. The message becomes:
     `f"Burning in the week of {week_txt} was {LEVEL_WORDS[level]} for this time of year (percentile {pct:.0f} of the same week in {n} past years)."`
     where `n = int(same.notna().sum())`.
   - When the level is `none` because of the `MIN_CHANGE` rule and `typical < MIN_CHANGE`, use instead:
     `f"Little or no burning in the week of {week_txt}, as usual for this time of year."`

3. **Tests** in `ws4_outlook/tests/test_outlook.py`:
   - A last week far below every past year (past values around 100, last 5) gives `very_low`, and the message
     contains "much lower".
   - Past values 0-1 with the last week at 3 (the Bangladesh case) give `none` and "Little or no burning".
   - Past values around 2 with the last week at 0 give `none`.
   - A median week gives `none`.
   - The existing `high` and `watch` tests still pass; their differences are well over 10.
4. **UI:**
   - `types.ts`: `export type StatusLevel = Level | "low" | "very_low";` and use it in `CurrentStatus.level`.
   - `styles.css`: add `--low: #2f6f9f;` and `--very-low: #1d4f7a;` in `:root`, and
     `.level.low { background: var(--low); }` and `.level.very_low { background: var(--very-low); }`.
   - i18n: add `status.level_low` / `status.level_very_low` in en ("Lower than usual" / "Much lower than usual")
     and bn ("স্বাভাবিকের চেয়ে কম" / "স্বাভাবিকের চেয়ে অনেক কম").
   - Change `status.level_none` to "Usual" (bn "স্বাভাবিক").
   - Change `status.percentile` to "Percentile {{p}} of the same week in past years". In bn, write that sentence in
     Bangla. Avoid English ordinals like "1th".
5. **Component test** `ws5_frontend/src/components/Panels.test.tsx`. Use `renderHtml` and `textOf` from
   `src/test/render.tsx`.
   - Render `StatusCard` with a hand-made `OutlookResponse` whose `current_status.level` is `very_low` and
     `week_percentile` is 0. The English text contains "Much lower than usual" and "Percentile 0".
   - The Bangla render doesn't contain those English words.
6. **Republish.** Run `python scripts/export_hosted_demo.py` and check that Punjab's `outlook.current_status.level`
   is now `very_low` or `low`. Paste the value into the PR.
7. Run the checks, mark the card done, then `split` (four authors), push and open the PR.

## Acceptance
- [ ] The new and existing outlook tests pass.
- [ ] The tiny-API contract tests pass (`ws2_platform/tests/test_tiny_api.py`), so the OpenAPI change is valid.
- [ ] `Panels.test.tsx` passes in both languages.
- [ ] Snapshot after re-export: Punjab is `very_low` and Bangladesh is `none`; both values are pasted in the PR.
- [ ] CHECK-FILES passes, so `outlook_region.json` still validates.

## Stop and ask if
- After this change, any demo area shows `high`, `watch`, `low` or `very_low` for a difference under 10 detections.
- The snapshot export fails.
