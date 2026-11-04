---
id: T27
title: Automated QA sweep before the freeze (i18n parity, budgets, hard-coded numbers)
kind: agent
owner: Shammo
authors: [Shammo, Sheikh]
phase: P3
size: S
needs: [T08, T09, T11, T12]
requires: []
branch: ws1/T27-qa-automation
touches: [ws5_frontend/package.json]
creates: [ws5_frontend/src/i18n/i18n.test.ts, ws5_frontend/scripts/check-budget.mjs, scripts/tests/test_numbers_in_ui.py]
checks: [CHECK-PLAN, CHECK-PY, CHECK-WEB, CHECK-SNAP, "npm --prefix ws5_frontend run check:budget"]
---
## Goal
Before the feature freeze (12 Nov 20:00 Dhaka), catch the mistakes judges notice that machines can find. The automated
device and accessibility review follows in T34.

## Steps
1. **`src/i18n/i18n.test.ts`:**
   - en and bn have exactly the same keys, ignoring `_review`;
   - no value is empty;
   - every `{{placeholder}}` in an en value also appears in its bn value.
2. **`ws5_frontend/scripts/check-budget.mjs`**, run after a build: read `dist/assets/*.js`, gzip each with
   `node:zlib`, and fail if:
   - the entry chunk (`index-*.js`) is over 120 KB gzipped;
   - any single chunk is over 150 KB gzipped;
   - `public/demo/snapshot.json` is over 1 MB.

   Print a table of the sizes. Add `"check:budget": "node scripts/check-budget.mjs"` to `package.json` scripts.
3. **`scripts/tests/test_numbers_in_ui.py`.** Scan `ws5_frontend/src/components/*.tsx` and `src/i18n/en.json` for
   measured-looking literals: decimals like `0.94` or `4.3`, and percentages like `58%`.
   - Allow: CSS and layout numbers inside `style=` or className lines; SVG geometry constants in UPPER_CASE; dates in
     ISO form in `config.ts`.
   - Fail with the file and line otherwise. The rule: measured numbers must come from data, never be typed in.
4. Run `npm run build && npm run check:budget`. If a budget fails, lazy-load the heavy component (as `SeriesChart` and
   `MapView` already are) rather than raising the budget. Raise a budget only with Sheikh's OK in the PR.
5. Run the checks, mark the card done, `split`, push and open the PR. Paste the size table into the PR.

## Acceptance
- [ ] All three checks run in CI: `npm test` covers i18n, and pytest covers numbers. The budget check is in this
  card's checks.
- [ ] The size table is in the PR under Measured.

## Stop and ask if
- The i18n test finds more than 20 missing Bangla keys. That means T08-T12 skipped bn; send them back to their cards.
