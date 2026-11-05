---
id: T09
title: Plain-language help, month labels and a phone-first layout
kind: agent
owner: Shammo
authors: [Shammo]
phase: P1
size: M
needs: [T00]
requires: []
branch: ws1/T09-help-layer
touches: [ws5_frontend/src/App.tsx, ws5_frontend/src/components/Panels.tsx, ws5_frontend/src/components/Calendar.tsx,
          ws5_frontend/src/components/SeriesChart.tsx, ws5_frontend/src/styles.css, ws5_frontend/src/i18n/en.json,
          ws5_frontend/src/i18n/bn.json]
creates: [ws5_frontend/src/components/Help.tsx, ws5_frontend/src/components/Help.test.tsx,
          ws5_frontend/src/lib/months.ts, ws5_frontend/src/lib/months.test.ts]
checks: ["CHECK-PLAN", "CHECK-WEB"]
---
## Goal
Judges and planners aren't remote-sensing experts. Every term on screen gets a one-tap plain explanation, the
calendar shows months instead of week numbers, and the page reads well on a phone.

## Context
- `Calendar.tsx` labels week columns 1, 14, 27 and 40. Columns are ISO weeks; `CELL + GAP = 12` px; `LEFT = 34`.
- `Panels.tsx` has `StatusCard`, `PeriodsPanel`, `DriversPanel` and `OutlookPanel`, each with an `h2`.
- `check:strings` scans `src/components/*` for visible English outside `t()`.
- Component tests run in node through `src/test/render.tsx`; event handlers don't run there. Put logic in plain
  functions and test those.

## Steps
1. **`lib/months.ts`.** `monthColumns(): { month: number; col: number }[]` returns, for months 1-12,
   `col = weekOfYear("2023-MM-04")` (the 4th always falls in the month's first full ISO week; January gives 1).
   `months.test.ts` checks January → 1, July → 27 and December → 49.
2. **Calendar month labels.** Replace the week-number labels with month initials at `monthColumns()`. The text is
   `t("months.short." + month)`. Add `months.short.1`…`months.short.12` to en ("J", "F", "M", …) and bn (Bangla
   month initials).
3. **`Help.tsx`.** `<HelpButton topic="…" />` renders a button labelled "?" (`aria-label={t("help.open", { topic: t("help.topic_" + topic) })}`)
   and a `<div role="dialog" id=… hidden={!open}>` holding `t("help." + topic)` and a close button.
   - Logic in a pure reducer `helpReducer(state, action)` (`open`, `close`, `toggle`, `escape`) exported from
     `Help.tsx`.
   - Escape closes it; clicking outside closes it (use a `useEffect` with a document listener).
   - `Help.test.tsx`: the reducer transitions; `renderHtml` shows `aria-expanded="false"` and the help text is
     inside a `hidden` element.
4. **Place help buttons** next to these headings:

   | Topic | Where |
   |---|---|
   | `status` | StatusCard |
   | `calendar` | the calendar card in `App.tsx` |
   | `bands` | the chart card |
   | `severity` | PeriodsPanel |
   | `drivers` | DriversPanel |
   | `outlook` | OutlookPanel |
   | `sources` | the calendar legend |

5. **Help text** (en here; Bangla drafts in bn; T34 checks they are complete). Each is 35 words at most, in plain
   words:
   - `help.status`: "How this week compares with the same week in past years. 'Much lower' or 'much higher' means
     the week ranks in the bottom or top tenth."
   - `help.calendar`: "Each square is one week; darker means more fires detected by satellites. Rows are years. Rings
     mark unusual weeks."
   - `help.bands`: "The shaded band is the likely range of the true weekly count (90% of the time). Before 2012
     values are estimated from older satellites, so the band is wider."
   - `help.severity`: "How many typical weeks' worth of extra burning a period had."
   - `help.drivers`: "Weather that tended to come before or with burning. These are associations, not proof of cause."
   - `help.outlook`: "Where this season stands compared with past seasons at the same date. Forecasts are shown only
     where they proved accurate on past seasons."
   - `help.sources`: "Observed: Suomi NPP satellite. Adjusted: NOAA-20 satellite scaled to the same standard. Modeled:
     estimated from older MODIS satellites (before 2012)."
   - Add `help.open`, `help.close` and `help.topic_*` names.
6. **Phone layout.**
   - Below 640 px, wrap `DriversPanel` and the Compare card in `<details>`, with `<summary>` set to the card title.
   - Keep `OutlookPanel` open. Its season-to-date sentence stays visible; don't hide the outlook.
   - Use a `useMediaQuery("(max-width: 640px)")` hook: `window.matchMedia` with a listener, and no matching in node.
7. Run the checks. Run `npm run preview` on the snapshot build and check 390 px width in the browser's device mode.
   Take screenshots for the PR.
8. Mark the card done, `split`, push and open the PR.

## Acceptance
- [ ] `months.test.ts` and `Help.test.tsx` pass, and `check:strings` passes.
- [ ] Every topic in the step 4 table has a working "?" in the snapshot build, in en and bn; screenshots in the PR.
- [ ] The calendar shows month initials, not week numbers.

## Stop and ask if
- Adding the help buttons makes any card overflow at 360 px width.
