---
id: T23
title: Story mode (90-second guided tour for judges and the video)
kind: agent
owner: Shammo
authors: [Shammo, Samiul]
phase: P2
size: M
needs: [T08, T12, T20]
requires: []
branch: ws1/T23-story-mode
touches: [ws5_frontend/src/App.tsx, ws5_frontend/src/styles.css, ws5_frontend/src/i18n/en.json,
          ws5_frontend/src/i18n/bn.json, docs/project/demo-script.md]
creates: [ws5_frontend/src/components/Story.tsx, ws5_frontend/src/lib/story.ts, ws5_frontend/src/lib/story.test.ts]
checks: [CHECK-PLAN, CHECK-WEB, CHECK-SNAP]
---
## Goal
Presentation is a fifth of the score, and Best Storytelling is an award. A guided tour, driven entirely by our own
data, makes the case in 90 seconds and doubles as the video script.

## Story: "Punjab: fewer fires, later fires, or fires we can't see?"
Step text lives in i18n (`story.s1`…`story.s7`, en and bn). **Every number is read from data at runtime** (season
profile, blind-spot piece) and passed in by interpolation; no number is typed into the text.

In the Area column, `pb` and `bd` mean the catalog areas Punjab and Dhaka (`ws5_frontend/public/demo/areas.json`).
Look up their ids at runtime by name; don't hard-code them.

| Step | Area | Highlight | Content |
|---|---|---|---|
| 1 | pb | calendar | The smoke season: the Oct-Nov band every year since 2000. |
| 2 | pb | chart seam | One record from three satellite eras: MODIS modeled before 2012, VIIRS observed, NOAA-20 adjusted after 2 Nov 2026; bands are wider before 2012. |
| 3 | pb | season card, amount | Fewer detections: magnitude trend `pct_per_decade` with its interval. |
| 4 | pb | season card, timing | Later in the season: timing trend `days_per_decade` with its interval. |
| 5 | pb | validation blind-spot block | Or out of view? The T20 verdict sentence, as it is. |
| 6 | bd | season card | Bangladesh is different: dry-season peak (`typical.p50`) and its own trends. |
| 7 | – | brief button and area filters | Use it: open the planner brief, or pick your division or state. |

When a trend verdict is `no_clear_shift`, the step says so instead. The story adapts to the data; it doesn't force
the claim.

## Steps
1. **`lib/story.ts`.**
   - `STEPS: StoryStep[]`, with `{ key, area, view, highlight }`.
   - `storyVars(step, profilePb, profileBd, blindspot)` returns the interpolation values, or `null` when a needed
     value is missing (that step then shows its fallback text `story.sN_fallback`).
   - `next(i)` and `prev(i)` are clamped.
   - Tests (`story.test.ts`):
     - 7 steps;
     - clamping;
     - `storyVars` for step 4 reads `days_per_decade` and `ci` from a profile object;
     - a `no_clear_shift` verdict selects the fallback text.
2. **`components/Story.tsx`.**
   - A side panel (a bottom sheet under 640 px) with step dots, Back, Next and Exit. Keyboard: ← → and Escape.
   - Applying a step uses the same setters as `App.tsx` (`pickArea` with an option from the area catalog, `setView`). Highlight with a CSS outline on
     elements carrying `data-story="<highlight>"`; add those attributes to the existing cards.
   - Respect `prefers-reduced-motion`.
3. **Start.**
   - A top-bar button "Take the 90-second tour" (`t("story.start")`).
   - `#s=1` in the URL opens it (T12's `s` field).
4. **`docs/project/demo-script.md`** (Samiul). Rewrite the live demo to follow the 7 steps, with what to say at each one, in
   under 3 minutes.
5. Run the checks. Walk through the tour in the snapshot build at 390 px and on desktop, in both languages, and time
   it. Paste the time into the PR.
6. Mark the card done, `split`, push and open the PR.

## Acceptance
- [ ] `story.test.ts` passes. The tour runs end to end in snapshot mode in under 2 minutes; time measured.
- [ ] No measured number is typed into a `story.*` string: no decimals or percentages. This prints `[]`:
  `python -c "import json,re;e=json.load(open('ws5_frontend/src/i18n/en.json'));print([k for k,v in e.items() if k.startswith('story.') and re.search(r'\d+\.\d+|\d+\s*%', v)])"`

## Stop and ask if
- T20's verdict is `confounded_by_orbit_drift` or `inconclusive`. Step 5 must then say that plainly; confirm the
  wording with Samiul.
