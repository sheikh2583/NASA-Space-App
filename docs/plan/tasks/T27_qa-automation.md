---
id: "T27"
title: "Current-interface QA: strings, payload budgets and sourced numbers"
kind: "agent"
owner: "Shammo"
authors: ["Shammo","Sheikh"]
phase: "P3"
size: "S"
needs: ["T58","T60","T22"]
requires: []
branch: "ws1/T27-qa-automation"
touches: ["ws5_frontend/package.json"]
creates: ["ws5_frontend/src/i18n/i18n.test.ts","ws5_frontend/scripts/check-budget.mjs","scripts/tests/test_numbers_in_ui.py"]
checks: ["CHECK-PLAN","python -m pytest -q scripts/tests/test_numbers_in_ui.py","CHECK-WEB","npm --prefix ws5_frontend run check:budget"]
---
## Goal
Catch presentation regressions in the delivered English/live interface (Q04/Q05).

## Steps
1. Read current i18n/build/component conventions. Test used English keys, nonempty required text and interpolation placeholders; unused Bangla parity is not a delivered-language criterion.
2. Add post-build gzip budget reporting: entry <=120 KB and individual chunk <=150 KB as existing internal targets. Measure catalog/evidence payloads separately; retired snapshot size is irrelevant.
3. Add a narrowly scoped scientific-literal check with explicit reviewed exceptions for geometry/layout/version/algorithm constants. Do not exempt entire lines containing CSS when scientific copy is present.
4. Test the checker itself with genuine sourced/runtime scientific text and hardcoded-score failures.
5. Run web checks/build/budget and record actual sizes. Improve loading/lazy boundaries if needed; no automatic budget inflation.
6. Document where checks actually ran. There is no general CI test workflow today; do not claim CI coverage from a local pass.

## Acceptance
- [ ] Current used strings/interpolations, scientific literal checks and payload table are verified.
- [ ] Budgets pass or a specific unresolved issue is retained; no obsolete language/snapshot work.
- [ ] No test assertion is removed to obtain green output.

## Stop and ask if
An implementation needs a new dependency or a budget change requires scope/architecture review.
