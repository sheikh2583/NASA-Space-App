# Status board

Edit only the Status and Note columns, by hand or with `python scripts/plan.py set <ID> <status> --note "…"`.
Status values: `todo`, `doing`, `review` (handed over or PR open), `done` (committed on main), `blocked` (say why in Note), `cut` (dropped on purpose; counts as finished for cards that need it).
Kinds: `agent` (coding agent, never trains) and `human` (Sheikh only: Render service and key, the two training runs with the human-only checks, submitting, event days). The other team members are dormant.
Regenerate the other columns from the cards with `python scripts/plan.py board --fix`. The order of rows is the order of work.

| ID | Kind | Title | Owner | Needs | Status | Note |
|---|---|---|---|---|---|---|
| T00 | agent | Finish the plan install (integration permissions and baseline checks) | Sheikh | – | done | plan installed; agent-safe baseline green (147 tests, web 13, both builds) |
| H01 | human | Sheikh: confirm the Render service, add the FIRMS key there, and note its URL | Sheikh | T00 | todo |  |
| T30 | agent | Check the Space Apps rules and record them with quotes | Sheikh | T00 | done | rules recorded 4 Nov; FAQ forbids pre-event work on challenges - Sheikh to decide |
| T01 | agent | Licence, references and AI-use statement | Sheikh | T30 | todo |  |
| T31 | agent | Truth checks against FIRMS itself (area API, no viewer) | Samiul | T00 | done | FIRMS vs ours: a 460/455 (-1.1%); outage confirmed; seasons within 0.2% |
| T02 | agent | Confirm that no validation piece still says "synthetic data" (read-only check) | Samin | T00 | done | labels verified clean (validation [], snapshot clean); Render check waits for H01/T17 |
| T03 | agent | Lower-than-usual status levels and honest status wording | Samin | T00 | done | Punjab very_low (pct 0), Bangladesh none; snapshot re-exported |
| T04 | agent | Mark incomplete weeks and months | Sattyam | T00 | done | last week 2026-11-02 partial (2 of 7 days: data runs to 3 Nov) in all 13 areas only |
| T32 | agent | Verify and complete the outage registry from NASA's MODAPS table | Sheikh | T00 | done | 22 confirmed, 2 corrected, 0 rejected, 39 added 2012-2023, 15 missing 2024-2026 added |
| T05 | agent | Run the coverage audit and record the outage decision | Sheikh | T32 | todo |  |
| T06 | agent | Wire verified outages into sensor_days and fill from NOAA-20 (code and tests) | Sheikh | T05 | todo |  |
| T16 | agent | Render data releases: publish a new runtime data version with one command | Sheikh | T00 | todo |  |
| H02 | human | Sheikh: full training run with the outage handling | Sheikh | T06 | todo |  |
| T40 | agent | Report the outage-corrected training run and publish it to Render | Sheikh | H02, T16 | todo |  |
| T17 | agent | Render deploy check: a script that verifies the live service, run once and recorded | Sheikh | H01 | todo |  |
| T07 | agent | Season profile in the API, mock server, fixtures and snapshot | Sattyam | T00 | todo |  |
| T08 | agent | Season card and typical-window strip on the calendar (en/bn) | Shammo | T07 | todo |  |
| T09 | agent | Plain-language help, month labels and a phone-first layout | Shammo | T00 | todo |  |
| T10 | agent | Caveats and "how we checked" on the method page (en, bn draft) | Samiul | T31 | todo |  |
| T11 | agent | Retired: region picker (done on main by the named-area explorer) | Sattyam | T07 | cut | retired 4 Nov: named-area explorer on main (04adbc4, 0c9241d) |
| T12 | agent | Shareable links (view, area, period, language in the URL) | Shammo | T00 | todo |  |
| T13 | agent | Interval report by stratum (measurement only) | Samin | T00 | todo |  |
| T14 | agent | Season-level unusual flags (library and spec) | Monazir | T07 | todo |  |
| T15 | agent | Season flags in the season response and on the calendar | Monazir | T14, T08 | todo |  |
| T18 | agent | Live season feed, part 1: redacted NRT fetcher and a cached /live/season endpoint (off without a key) | Monazir | T03, T04, T07 | todo |  |
| T19 | agent | Live season feed, part 2: verify it on Render and record the result | Sheikh | T18, T17 | todo |  |
| T39 | agent | Retired: FIRMS key as a GitHub Actions secret (the key now lives only in Render, H01) | Sheikh | T18 | cut | retired 4 Nov: FIRMS key lives only in Render (H01) |
| T20 | agent | Overpass blind-spot indicator (are fires moving out of satellite view?) | Monazir | T00 | todo |  |
| T21 | agent | Recurrence map (how often each place burns in a season) | Sattyam | T07 | todo |  |
| T22 | agent | Planner brief (one printable page, en/bn) | Shammo | T08, T21 | todo |  |
| T23 | agent | Story mode (90-second guided tour for judges and the video) | Shammo | T08, T12, T20 | todo |  |
| T33 | agent | Download MODIS burned-area tiles (MCD64A1) with the Earthdata token | Sheikh | T00 | todo |  |
| T24 | agent | Independent check against MODIS burned area (MCD64A1) | Samin | T33 | todo |  |
| T25 | agent | Fire intensity (FRP) view, labelled uncalibrated | Sattyam | T07 | todo |  |
| T26 | agent | Add a third region (cut by default; reopen only if ahead on 10 Nov) | Sheikh | T40 | cut | one-person team; reopen if all P0-P1 done by 10 Nov |
| T27 | agent | Automated QA sweep before the freeze (i18n parity, budgets, hard-coded numbers) | Shammo | T08, T09, T11, T12 | todo |  |
| T34 | agent | Automated device, accessibility and Bangla completeness review | Samiul | T27, T15, T21, T22, T23, T25, T26 | todo |  |
| H03 | human | Sheikh: final training run for the release (by 12 Nov) | Sheikh | T34 | todo |  |
| T28 | agent | Validate, export and tag v1.0-event after Sheikh's final training | Sheikh | H03, T16 | todo |  |
| T29 | agent | Draft the submission text, slide content and video script from measured numbers | Samiul | T28 | todo |  |
| T35 | agent | Submission assets (slides page, recorded story video) and a 13 Nov rules re-check | Samiul | T29, T30 | todo |  |
| H04 | human | Sheikh: submit on the Space Apps site | Sheikh | T35 | todo |  |
| H05 | human | Sheikh: event days (14-15 Nov) | Sheikh | H04 | todo |  |
