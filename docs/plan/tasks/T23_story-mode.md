---
id: "T23"
title: "Story mode (90-second guided tour for judges and the video)"
kind: "agent"
owner: "Shammo"
authors: ["Shammo","Samiul"]
phase: "P2"
size: "M"
needs: ["T08","T12","T22","T58","T60"]
requires: []
branch: "ws1/T23-story-mode"
touches: ["ws5_frontend/src/App.tsx","ws5_frontend/src/styles.css","ws5_frontend/src/i18n/en.json","docs/project/demo-script.md"]
creates: ["ws5_frontend/src/components/Story.tsx","ws5_frontend/src/lib/story.ts","ws5_frontend/src/lib/story.test.ts"]
checks: ["CHECK-PLAN","CHECK-WEB"]
---
## Goal
Create a concise evidence-led guided journey for judges and users (C01-C06), without speculative findings.

## Steps
1. Read the challenge contract, claim register, current supported products and T22 brief.
2. Build a small step definition/variable helper and Back/Next/Exit UI: sensor mismatch; reference/source labels; regional calendar; same-cutoff comparison; validation limitations; usable brief.
3. Read all numbers and eligible findings from actual runtime responses. Missing/no-clear-shift/unsupported results get honest fallback text. Do not force a story about later burning or fewer actual fires; T20 is not a dependency.
4. Reuse area selection/share state with cancellation. Support keyboard, focus restoration and reduced motion; avoid changing the selected result behind the user's back after exiting.
5. Test navigation bounds, missing evidence, rejected trends, source labels and state restoration. Observe on phone/desktop and time the complete journey.
6. Update demo-script with a 90-second product target and <=3-minute spoken target, marked internal until T35 verifies format limits. A rehearsed existing-interface demonstration is the documented fallback if this UI is cut.

## Acceptance
- [ ] Actual supported tour completes with clear limitations and exits cleanly.
- [ ] No hardcoded scientific scores, assumed Bangla or snapshot transport.
- [ ] Measured timing/source revision recorded, not a claim of official video limits.

## Stop and ask if
The story needs an unsupported scientific inference or new dependency. Keep the core task and record the limitation.
