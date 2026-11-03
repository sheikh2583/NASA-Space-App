# Prompt pack: Shammo (Team Member 5), web app
Folder: ws5_frontend/ (React + Vite)

## P5.1 Scaffold and i18n (H3-8)  HANDOFF
Inputs: openapi.yaml, fixtures, mock server URL (Sattyam, H3).
Prompt: "Scaffold a React + Vite app in ws5_frontend/ with i18n from the first commit: src/i18n/en.json and bn.json, a language toggle, Noto Sans Bengali, all UI text from the dictionaries. API base URL from VITE_API_BASE_URL (default the mock). Deploy to the static host and give me a demo link. Export a flat list of all en.json keys."
Output: running scaffold, demo link, en.json key list. HANDOFF: to Samiul (keys) and everyone (link) by H8.
Test: toggling language changes every visible string; no hard-coded strings (grep).

## P5.2 AOI drawing and data call (H6-12)
Prompt: "Add a Leaflet map with a draw tool (rectangle and polygon). On draw, POST the GeoJSON to /aoi/summary with start, end and res. Show loading, empty-AOI, oversized-AOI (422 message) and API-error states. If the API fails, fall back to the static JSON (URL pattern from Sattyam)."
Output: draw-to-data flow on the mock.
Test: all four states appear correctly; fallback works with the API off.

## P5.3 Calendar heatmap (H10-16)
Prompt: "Build a calendar heatmap component: years as rows, weeks as columns, colour = value, colour-blind-safe palette, markers on flagged weeks, a badge per point for source (observed, modeled, mixed) and a warning icon when drift_flag is true. Hover shows the week, value, interval and source. Build against the fixtures."
Output: heatmap component.
Test: the 2012 seam is visible; flagged weeks are marked; keyboard focusable.

## P5.4 Series chart with uncertainty band (H12-16)  HANDOFF at H16
Prompt: "Add a line chart under the heatmap with a lo-hi band, modeled periods shaded differently from observed, and a tooltip with value, interval and source. Hovering a flagged week highlights its period in the list. Switch the base URL to the live API."
Output: floor UI on live data. HANDOFF: demo link to everyone at H16.
Test: works on live data with only the base URL changed.

## P5.5 Result panels (H16-30)
Prompt: "Add panels: critical periods (ranked, with agri tag and a note when depends_on_modeled_history), drivers (wording 'associated with', strength, evidence label, caveats), outlook (season-to-date percentile, expected range, skill status, alert). Each reads its endpoint and shows loading and error states."
Output: three panels.
Test: sparse AOI shows an insufficient-data message; status no_demonstrated_skill is shown in plain words.

## P5.6 Comparison, validation page, method panel (H24-36)
Inputs: /meta/validation (H34); docs/method_en.md (H38).
Prompt: "Add AOI comparison (two areas on the same axes via /aoi/compare), a validation page that renders /meta/validation pieces (tables for baselines and coverage, drift notes, limitations), and a method panel that renders docs/method_en.md."
Output: comparison, validation page, method panel. Feature freeze at H36.
Test: pieces missing from the endpoint do not break the page.

## P5.7 Export and robustness (H30-36)
Prompt: "Add CSV export via /export, a print stylesheet for a one-page summary, and error boundaries so one failing panel does not blank the page."
Output: export + print view.
Test: CSV opens with correct columns; print view fits one page.

## P5.8 Bangla, mobile, polish (H36-44)
Inputs: reviewed Bangla text (Samiul, H42).
Prompt: "Complete bn.json using the reviewed text, check rendering of Bengali numerals and long strings, make every panel usable at phone width, fix every item in Samiul's bug list, and tag the final build."
Output: final build deployed (with Sattyam) by H44.
Test: Samiul's final run-through passes on the hosted build.

## P5.9 Where map layer and current-status card (H16-30)
Inputs: /aoi/cells and /aoi/outlook (Sattyam, fixtures first).
Prompt: "Add a 'where' layer to the map: shade each cell returned by /aoi/cells by burning activity for the selected period, with a legend and a modeled-share hatch or badge. Make the period selectable by clicking a week or a critical period in the calendar and by a simple range control. Add a current-status card from /aoi/outlook current_status: level (none, watch, high), the week percentile, the data-through date and the one-line message, in plain words for emergency responders and land managers. Both must work on the fixtures first, then the live API."
Output: where map layer and status card. HANDOFF: demo link at H30.
Test: selecting a flagged week recolours the map; the status card shows the data-through date; no causal wording.
