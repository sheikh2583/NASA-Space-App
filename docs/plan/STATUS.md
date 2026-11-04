# Status board

Edit only the Status and Note columns, by hand or with `python scripts/plan.py set <ID> <status> --note "…"`.
Status values: `todo`, `doing`, `review` (PR open), `done` (merged), `blocked` (say why in Note), `cut` (dropped on purpose; counts as finished for cards that need it).
Kinds: `agent` (coding agent) and `human` (Sheikh only: account and token, the two training runs, submitting, event days). The other team members are dormant.
Regenerate the other columns from the cards with `python scripts/plan.py board --fix`. The order of rows is the order of work.

| ID | Kind | Title | Owner | Needs | Status | Note |
|---|---|---|---|---|---|---|
| T00 | agent | Install the plan and set integration permissions | Sheikh | – | todo |  |
| T30 | agent | Check the Space Apps rules and record them with quotes | Sheikh | T00 | todo |  |
| T01 | agent | Licence, references and AI-use statement | Sheikh | T30 | todo |  |
| T31 | agent | Truth checks against FIRMS itself (area API, no viewer) | Samiul | T00 | todo |  |
| T02 | agent | Remove the false "synthetic data" labels from the live validation page | Samin | T00 | todo |  |
| T03 | agent | Lower-than-usual status levels and honest status wording | Samin | T00 | todo |  |
| T04 | agent | Mark incomplete weeks and months | Sattyam | T00 | todo |  |
| T32 | agent | Verify and complete the outage registry from NASA's MODAPS table | Sheikh | T00 | todo |  |
| T05 | agent | Run the coverage audit and record the outage decision | Sheikh | T32 | todo |  |
| T06 | agent | Wire verified outages into sensor_days and fill from NOAA-20 (code and tests) | Sheikh | T05 | todo |  |
| H02 | human | Sheikh: full training run with the outage handling | Sheikh | T06 | todo |  |
| T40 | agent | Report the outage-corrected training run and republish | Sheikh | H02 | todo |  |
| T07 | agent | Season profile in the API, mock server, fixtures and snapshot | Sattyam | T00 | todo |  |
| T08 | agent | Season card and typical-window strip on the calendar (en/bn) | Shammo | T07 | todo |  |
| T09 | agent | Plain-language help, month labels and a phone-first layout | Shammo | T00 | todo |  |
| T10 | agent | Caveats and "how we checked" on the method page (en, bn draft) | Samiul | T31 | todo |  |
| T11 | agent | Region picker with exact administrative regions (API and snapshot) | Sattyam | T07 | todo |  |
| T12 | agent | Shareable links (view, area, period, language in the URL) | Shammo | T00 | todo |  |
| T13 | agent | Interval report by stratum (measurement only) | Samin | T00 | todo |  |
| T14 | agent | Season-level unusual flags (library and spec) | Monazir | T07 | todo |  |
| T15 | agent | Season flags in the season response and on the calendar | Monazir | T14, T08 | todo |  |
| T16 | agent | Hosted API, part 1: data release script, Docker download and hybrid web mode | Sattyam | T07 | todo |  |
| H01 | human | Sheikh: create the Hugging Face Space and token | Sheikh | T16 | todo |  |
| T17 | agent | Hosted API, part 2: publish the data release, deploy the Space, switch Pages to hybrid | Sheikh | H01 | todo |  |
| T18 | agent | Live season feed, part 1: redacted NRT fetcher, live builder and workflow step (off) | Monazir | T03, T04, T07 | todo |  |
| T39 | agent | Add the FIRMS key as a GitHub Actions secret (without printing it) | Sheikh | T18 | todo |  |
| T19 | agent | Live season feed, part 2: switch on the nightly run and verify | Sheikh | T39 | todo |  |
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
| T28 | agent | Validate, export and tag v1.0-event after Sheikh's final training | Sheikh | H03 | todo |  |
| T29 | agent | Draft the submission text, slide content and video script from measured numbers | Samiul | T28 | todo |  |
| T35 | agent | Submission assets (slides page, recorded story video) and a 13 Nov rules re-check | Samiul | T29, T30 | todo |  |
| H04 | human | Sheikh: submit on the Space Apps site | Sheikh | T35 | todo |  |
| H05 | human | Sheikh: event days (14-15 Nov) | Sheikh | H04 | todo |  |
