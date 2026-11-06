---
id: "T34"
title: "Observed device, keyboard and accessibility review"
kind: "agent"
owner: "Samiul"
authors: ["Samiul","Shammo","Sheikh"]
phase: "P3"
size: "M"
needs: ["T27","T15","T21","T22","T23","T60","H06"]
requires: []
branch: "ws1/T34-device-review"
touches: ["ws5_frontend/src/styles.css","ws5_frontend/src/App.tsx","ws5_frontend/src/components/AreaFilters.tsx","ws5_frontend/src/components/MapView.tsx","ws5_frontend/src/components/Calendar.tsx","ws5_frontend/src/components/SeasonCard.tsx","ws5_frontend/src/components/Brief.tsx","ws5_frontend/src/components/Story.tsx","ws5_frontend/src/i18n/en.json","ws6_validation/USER_STUDY.md"]
creates: ["ws6_validation/qa_review.md"]
checks: ["CHECK-PLAN","CHECK-WEB"]
---
## Goal
Observe the actual supported user journey on devices and with keyboard/assistive access; unit tests are insufficient (Q04).

## Steps
1. Read current app/brief/tour, T60 findings and anonymized H06 observations. Use available browser/automation tooling and required skills; do not assume old npx versions remain appropriate or install dependencies silently.
2. Review English local-production/live UI at 360, 390, 768 and 1366 px; use a real phone where available. Record browser/OS/viewport and generated screenshots outside Git.
3. Complete selection, calendar interpretation, comparison, brief/export, no-data and error journeys. Require no page overflow, clipped critical labels or inaccessible controls.
4. Check full keyboard flow, focus restoration, meaningful labels/errors, textual calendar/chart alternatives, map-independent selection, source distinctions beyond color and reduced motion.
5. Record automated accessibility/performance audits if available (internal targets >=90/>=80). They supplement manual task checks and do not certify WCAG conformance. Missing tooling stays not run with a reason.
6. Fix in-scope critical issues and participant confusion, then rerun affected checks/tasks. Ask Sheikh to supply a fresh follow-up observation through H06 when needed; never simulate participants.
7. Write qa_review.md with pass/fail/not-run, evidence paths, severity and unresolved limitations.

## Acceptance
- [ ] No critical source/date confusion, inaccessible core task or small-screen overflow remains.
- [ ] Actual observed evidence is distinct from automated/static results.
- [ ] Unavailable real-phone/assistive/user evidence remains explicit in the final score.

## Stop and ask if
A fix changes scientific meaning, requires new dependencies or unavailable assistive tooling. Record the concrete limitation rather than claiming coverage.
