# Shammo (Team Member 5): your instructions
Your job: make the product understandable at a glance.
Folder: ws5_frontend/. Prompt pack: prompts/ws5_shammo.md. Paste docs/AI_PREAMBLE.md first.

## H0 to H8: scaffold on the mock
1. Talk to Sattyam: tell him which fields your heatmap and chart need, so the fixtures include them.
2. Do P5.1. When the mock URL arrives (H3), connect to it.
3. At H8 share a demo link with the team. Post the en.json key list to Samiul.

## H8 to H16: first live UI
4. Do P5.2 to P5.4 against the mock. Talk to Sattyam: ask for the live URL and the static fallback URL pattern at H16.
5. At H16 switch the base URL to the live API and post the demo link.

## H16 to H36: panels
6. At H24 run the floor with Samiul and fix every item in his bug list.
7. Do P5.5 to P5.7 and P5.9 (where map layer and current-status card). Talk to Monazir about the drivers wording, Samin about the outlook status wording, Samiul about the validation page.
8. At H36 tag the feature-freeze build.

## H36 to H44: Bangla, mobile, polish
9. Do P5.8. Talk to Samiul: get the reviewed Bangla text (H42).
10. With Sattyam, deploy the final build at H44.

## Rules and fallbacks
- Never call endpoints that are not in the contract. Never hide that a value is modeled. Never hard-code strings.
- Share a short demo link at H8, H16 and H24 so the team always sees the current state.
- If you fall behind, ship English only (with i18n in place), one area at a time, basic export.

## Manual tasks
Things an AI agent cannot do for you are listed under your name in docs/MANUAL_TASKS.md, and repeated inside each of your phase prompts (prompts/phases/).

## Your workspace, what you may write, how to verify
- Work in: your laptop with Node LTS. Run the dev server (port 5173) with VITE_API_BASE_URL pointing at the hosted mock, later the live API. Branch prefix: ws5/.
- You may write: ws5_frontend/ only, and your own static-host project.
- You must not write: the API, data files, or the fallback site. Read the fallback address from VITE_FALLBACK_BASE_URL.
- Verify before each HANDOFF: npm run build succeeds; a grep finds no hard-coded UI strings; open the app on a phone and a laptop in English and Bangla; check the network tab shows only contract endpoints.
