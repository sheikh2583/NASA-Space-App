# Phase prompts: Shammo (Team Member 5). Detailed sub-prompts: prompts/ws5_shammo.md

## PHASE 1: Kickoff (H0-3)
```
GOAL: Scaffold started; fixtures contain the fields the UI needs.
STEPS:
1. Tell Sattyam which fields the heatmap and chart need.
2. Start P5.1: React + Vite, i18n from the first commit, Noto Sans Bengali, API base URL from VITE_API_BASE_URL.
3. When the mock URL arrives at H3, connect to it.
DELIVER: scaffold running on the mock.
DONE WHEN: toggling the language changes every visible string.
IF BLOCKED: build against the fixture files directly.
MANUAL (you do these yourself; the agent cannot):
- Set up your AI tool project with docs/AI_PREAMBLE.md pasted in; install Node LTS and the editor you will use
- Pick the map and chart libraries with Sattyam so the fixtures match
```

## PHASE 2: Data (H3-8)
```
GOAL: Demo link and en.json key list at H8.
STEPS:
1. Finish P5.1; deploy to the static host.
2. Post the demo link in the channel; send the en.json key list to Samiul.
3. Start P5.2 (map drawing and the data call).
DELIVER: demo link; key list.
DONE WHEN: no hard-coded strings (grep passes).
IF BLOCKED: share a screenshot and fix the host later.
MANUAL (you do these yourself; the agent cannot):
- Open the demo link on your phone and on a desktop browser and look at it
```

## PHASE 3: Floor (H8-24)
```
GOAL: Floor UI on live data at H16; floor gate at H24.
STEPS:
1. Run P5.2 (draw tool, loading, empty, oversized, error states, static fallback).
2. Run P5.3 (calendar heatmap) and P5.4 (series chart with band).
3. Ask Sattyam for the live URL and fallback pattern at H16; switch the base URL; post the demo link.
4. At H24 run the floor with Samiul and fix every item on his bug list.
DELIVER: floor UI.
DONE WHEN: the app works on live data with only the base URL changed; the seam at 2012 is visible.
IF BLOCKED: keep working on the mock; tell Sheikh.
MANUAL (you do these yourself; the agent cannot):
- Try drawing an area with a finger on your phone
- Check the colours with a colour-blindness simulator or a teammate
```

## PHASE 4: Core (H24-30)
```
GOAL: bands, source badges and drift icons on v1 data.
STEPS:
1. Confirm the live API serves v1; check that bands update.
2. Run P5.9 (where map layer and current-status card).
3. Start P5.5 (critical periods panel).
4. Fix items on Samiul's H30 bug list.
DELIVER: UI on v1 data.
DONE WHEN: Samiul's H30 run passes.
MANUAL (you do these yourself; the agent cannot):
- Look at the app next to Samiul's bug list and decide the order of fixes
```

## PHASE 5: Scale-up (H30-36)
```
GOAL: all panels; feature freeze at H36.
STEPS:
1. Run P5.5 (critical periods, drivers, outlook). Ask Monazir about driver wording and Samin about the status wording.
2. Run P5.6 (comparison, validation page, method panel) and P5.7 (export, error boundaries).
3. Tag the freeze build at H36.
DELIVER: all panels.
DONE WHEN: a missing validation piece does not break the page.
IF BLOCKED: cut comparison first, then the validation page.
MANUAL (you do these yourself; the agent cannot):
- Check Bangla text on a real phone: numerals, line breaks, long strings
```

## PHASE 6: Polish (H36-42)
```
GOAL: Bangla, mobile and bug fixes.
STEPS:
1. Run P5.8: complete bn.json with Samiul's reviewed text (H42); check numerals and long strings.
2. Make every panel usable at phone width.
3. Fix every item on Samiul's H36 and H42 bug lists.
DELIVER: polished build.
DONE WHEN: Samiul's H42 run has no severity-1 bugs.
IF BLOCKED: ship English only with i18n intact.
MANUAL (you do these yourself; the agent cannot):
- Take clean screenshots of the final screens for the slides and give them to Samiul
```

## PHASE 7: Ship (H42-48)
```
GOAL: Final build deployed at H44.
STEPS:
1. Deploy with Sattyam; confirm the final URL works from a different device.
2. Rehearse the demo path with Samiul.
DELIVER: final build.
DONE WHEN: the demo path passes on the hosted build and on the fallback.
MANUAL (you do these yourself; the agent cannot):
- Open the final URL on another device and network; rehearse the demo path with Samiul
```
