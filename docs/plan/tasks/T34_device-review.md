---
id: T34
title: Automated device, accessibility and Bangla completeness review
kind: agent
owner: Samiul
authors: [Samiul, Shammo]
phase: P3
size: M
needs: [T27, T15, T21, T22, T23, T25, T26]
requires: []
branch: ws1/T34-device-review
touches: [ws5_frontend/src/i18n/bn.json]
creates: [ws6_validation/qa_review.md, ws6_validation/screens]
checks: [CHECK-PLAN, CHECK-WEB, CHECK-SNAP]
---
## Goal
Check what judges see on phones and desktops, and what assistive tools see, without a person. Card-level tests can't
see the whole page.

## Context
- The snapshot build is in `ws5_frontend/dist`. Serve it with `npm run preview -- --port 4173`.
- Use Playwright and Lighthouse through `npx` as tools for this card only. **Don't add them to `package.json`.**
  - `npx --yes playwright@1.48.2 install chromium`
  - `npx --yes playwright@1.48.2 screenshot --viewport-size=390,844 <url> <file>`
  - `npx --yes lighthouse@12.2.1 <url> --only-categories=accessibility,performance --form-factor=mobile --output=json --output-path=<file> --chrome-flags="--headless=new"`

  If a tool can't run on this machine, write "not run: <reason>" in the report, and continue.

## Steps
1. Review what judges will open: the Render URL from `RENDER_URL`, after T17 passes. Otherwise start the local live
   build in the background with `python scripts/workflow.py dev`; it serves the API and UI and trains nothing.
2. **Screenshots** into `ws6_validation/screens/`, PNGs under 300 KB each, at widths 360, 390, 1366 and 1920 px, of:
   - Dhaka (the default) and Punjab;
   - the season card;
   - the area filters (country, name search, Apply);
   - the brief (`#v=brief`);
   - story mode step 1 (`#s=1`);
   - English and Bangla (`#l=bn`).
3. **Overflow check.** For each page at 360 and 390 px, run in Playwright:
   `document.documentElement.scrollWidth > window.innerWidth`. It must be false. List any failures.
4. **Lighthouse** (mobile) on the home page in both languages. Record the Accessibility and Performance scores; targets
   are ≥ 90 and ≥ 80. List the failing audits.
5. **Keyboard.** In Playwright, press Tab 40 times from the top. Every focused element must have a visible outline:
   computed `outline-style` isn't `none`, or `box-shadow` isn't `none`. List failures.
6. **Bangla completeness.**
   - Every `bn.json` value contains Bengali script (Unicode range U+0980-U+09FF), except proper names and numbers.
     List English leftovers and translate them.
   - Set `_review` to "Drafted with AI assistance; completeness checked automatically on <date>; not reviewed by a
     fluent reader."
7. **Fix small issues** in this card (CSS overflow, a missing `aria-label`, a missing translation). Bigger ones:
   describe them in the report and stop.
8. Write `ws6_validation/qa_review.md`: a table of check, device or width, result and fix, plus the Lighthouse
   scores. Run the checks, mark the card done, `split`, push and open the PR.

## Acceptance
- [ ] No horizontal overflow at 360 and 390 px.
- [ ] The Lighthouse scores are recorded, or "not run" with a reason.
- [ ] Every `bn.json` value is in Bangla script, apart from names and numbers.

## Stop and ask if
- Accessibility is under 80, or a fix needs more than CSS and labels.
