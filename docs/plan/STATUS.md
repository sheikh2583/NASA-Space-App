# Status board

Statuses describe work/evidence, not scientific quality: todo, doing, review, done, blocked, cut.
T51 is the first new implementation card; T61 prepares real-user evidence early. Agent-operated training is authorized.
Scientific runs use declared specs; old H02/H03 are historical. Owners are accountable authors, not spawned agents.
Cut/deferred work is omitted, not passed; T63 must retain its evidence/score limitations.
Use plan.py board --fix for structural columns and plan.py set for status/notes. Sheikh's commit/push flow remains unchanged.

| ID | Kind | Title | Owner | Needs | Status | Note |
|---|---|---|---|---|---|---|
| T00 | agent | Finish the plan install (integration permissions and baseline checks) | Sheikh | – | done | plan installed; agent-safe baseline green (147 tests, web 13, both builds) |
| H01 | human | Sheikh: confirm the Render service, add the FIRMS key there, and note its URL | Sheikh | T00 | done | Sheikh 5 Nov: Render service working; FIRMS key set there; RENDER_URL in .env |
| T30 | agent | Check the Space Apps rules and record them with quotes | Sheikh | T00 | done | rules recorded 4 Nov; FAQ forbids pre-event work on challenges - Sheikh to decide |
| T01 | agent | Licence, references and AI-use statement | Sheikh | T30 | done | Historical licence/references delivered; AI_USE.md was left unfinished. Its creation is explicitly reassigned to T29; this row does not claim the disclosure exists. |
| T31 | agent | Truth checks against FIRMS itself (area API, no viewer) | Samiul | T00 | done | FIRMS vs ours: a 460/455 (-1.1%); outage confirmed; seasons within 0.2% |
| T02 | agent | Confirm that no validation piece still says "synthetic data" (read-only check) | Samin | T00 | done | labels verified clean (validation [], snapshot clean); Render check waits for H01/T17 |
| T03 | agent | Lower-than-usual status levels and honest status wording | Samin | T00 | done | Punjab very_low (pct 0), Bangladesh none; snapshot re-exported |
| T04 | agent | Mark incomplete weeks and months | Sattyam | T00 | done | last week 2026-11-02 partial (2 of 7 days: data runs to 3 Nov) in all 13 areas only |
| T32 | agent | Verify and complete the outage registry from NASA's MODAPS table | Sheikh | T00 | done | 22 confirmed, 2 corrected, 0 rejected, 39 added 2012-2023, 15 missing 2024-2026 added |
| T05 | agent | Run the coverage audit and record the outage decision | Sheikh | T32 | done | threshold 0.25: 105 sensor-days flip; 54/770 SNPP+MODIS and 36/448 SNPP+NOAA20 weeks lost; 1 explained contradiction |
| T06 | agent | Wire verified outages into sensor_days and fill from NOAA-20 (code and tests) | Sheikh | T05 | done | code+tests; dry compute on real data: 105 SNPP sensor-days non-operating (= audit); H02 next |
| T16 | agent | Render data releases: publish a new runtime data version with one command | Sheikh | T00 | done | release_runtime.py + 8 offline tests; dry run proposes runtime-20261104-render-v2; runtime.json unchanged |
| H02 | human | Sheikh: full training run with the outage handling | Sheikh | T06 | done | full run 21:12-21:35 (~23 min); QA 5/5, pytest 211 passed 2 skipped, smoke passed; runtime ZIP 97165177 |
| T40 | agent | Report the outage-corrected training run and publish it to Render | Sheikh | H02, T16 | done | Published checksum-verified runtime-20261104-render-v2 for data through 2026-11-03 and refreshed the legacy snapshot; final guarded checks passed. |
| T17 | agent | Render deploy check: a script that verifies the live service, run once and recorded | Sheikh | H01 | review | Dated 6 Nov review records e97d49f check passing and detailed report served; planning did not rerun live checks. Final identity verification belongs to T28. |
| T07 | agent | Season profile in the API, mock server, fixtures and snapshot | Sattyam | T00 | done | season in API, mock, fixtures and snapshot (13 areas, +2%); PB paddy 21 Oct-12 Nov, BD p50 16 Mar; verify_files validates bd/pb |
| T08 | agent | Season card and typical-window strip on the calendar (en/bn) | Shammo | T07 | done | Season card, current status, trends and accessible calendar bands verified at 390px/1366px in en/bn |
| T09 | agent | Plain-language help, month labels and a phone-first layout | Shammo | T00 | done | Localized help, month labels and mobile collapsibles verified at 360px/390px/1366px |
| T10 | agent | Caveats and "how we checked" on the method page (en, bn draft) | Samiul | T31 | done | Added bilingual caveats, truth-check evidence, sourced validation metrics, and verified rendered Method pages. |
| T11 | agent | Retired: region picker (done on main by the named-area explorer) | Sattyam | T07 | cut | retired 4 Nov: named-area explorer on main (04adbc4, 0c9241d) |
| T12 | agent | Shareable links (view, area, period, language in the URL) | Shammo | T00 | done | English-only UI complete, including an English-only area-search placeholder. |
| T13 | agent | Interval report by stratum (measurement only) | Samin | T00 | review | Reporting implementation exists; scientific stop rows remain. New diagnosis/remediation/acceptance is T54-T58; report presence alone is not acceptance. |
| T42 | agent | Redact FIRMS credentials at every error boundary | Monazir | T00 | done | 11 offline redaction regressions pass; credentials sanitized at error boundaries |
| T43 | agent | Correct clean-run pipeline dependency ordering | Sheikh | T00 | done | 3 planning-only tests pass via explicit session override; named guard flags runner imports; no stages executed |
| T44 | agent | Eliminate forecast feature and target leakage | Samin | T00 | done | 4 pure fold-isolation tests pass; old forecast scores qualified; numerical revalidation pending |
| T45 | agent | Correct alert transitions and disable unsupported forecast alerts | Samin | T44 | done | 8 pure alert tests pass; watch promotes; unsupported batch forecast alerts explicitly off |
| T46 | agent | Correct interval area counts and report every stop-condition failure | Samin | T00 | done | 4 diagnostic tests and 35 web tests pass; all-dimensional stop warnings; bands unchanged; T13 stays review |
| T47 | agent | Include detailed interval diagnostics in runtime releases | Sheikh | T46 | done | 3 new and 3 existing transport tests pass; new bundles require diagnostics; legacy pins remain loadable |
| T48 | agent | Use runtime metadata consistently for record-end dates | Shammo | T00 | done | 6 exporter tests and 37 frontend tests pass; live and snapshot builds pass; metadata drives dates |
| T49 | agent | Verify and publish the reviewed correctness repairs | Sheikh | T42, T43, T44, T45, T46, T47, T48 | review | Dated 6 Nov review records reviewed source live; new scientific provenance/remediation follows T52-T59 and T28. Historical billing/deploy notes are superseded, not a fresh host-cause diagnosis. |
| T18 | agent | Live season feed, part 1: redacted NRT fetcher and a cached /live/season endpoint (off without a key) | Monazir | T03, T04, T07, T51 | cut | Deferred default path: NRT requires distinct pinned/live coverage and revision spec; core historical evidence first. |
| T19 | agent | Live season feed, part 2: verify it on Render and record the result | Sheikh | T18, T17, T51 | cut | Deferred with T18; no fresh-feed or operational claim in default submission. |
| T39 | agent | Retired: FIRMS key as a GitHub Actions secret (the key now lives only in Render, H01) | Sheikh | T18 | cut | retired 4 Nov: FIRMS key lives only in Render (H01) |
| T20 | agent | Overpass blind-spot indicator (are fires moving out of satellite view?) | Monazir | T00, T51 | cut | Deferred: detected-time medians cannot identify missed fires/orbit drift without independent observation-opportunity evidence. |
| T25 | agent | Fire intensity (FRP) view, labelled uncalibrated | Sattyam | T07, T51 | cut | Deferred: uncalibrated sampled FRP does not repair the core harmonization/calendar validity gap. |
| T26 | agent | Add a third region (cut by default; reopen only if ahead on 10 Nov) | Sheikh | T40 | cut | one-person team; reopen if all P0-P1 done by 10 Nov |
| H03 | human | Sheikh: final training run for the release (by 12 Nov) | Sheikh | H02 | done | Historical 5 Nov: H02 run 20261104-211232 accepted as final. The no-more-training freeze was explicitly superseded by Sheikh on 6 Nov; new agent-operated runs use new scientific-run cards/specs (AGENTS.md). |
| T50 | agent | Repair partial-month, calendar and snapshot regressions | Sattyam | T48 | done | 8 API and 42 web tests pass; live/static builds pass; five product regressions repaired |
| T51 | agent | Freeze the baseline and register challenge claims | Sheikh | T00 | done | Protected 29 files / 116187230 bytes with source+copy SHA256 verification; baseline and 22-claim register recorded; CHECK-PLAN passed; science unchanged. |
| T61 | agent | Prepare neutral user tasks and evidence collection | Samiul | T51 | todo | Installed scaffold; implementation and acceptance not yet performed. |
| T52 | agent | Add an explicit scientific validation lane with preserved baselines | Sheikh | T51 | todo | Installed scaffold; implementation and acceptance not yet performed. |
| T53 | agent | Audit and freeze targets, splits and scientific acceptance | Sheikh | T51, T52 | todo | Installed scaffold; implementation and acceptance not yet performed. |
| T54 | agent | Diagnose conditional interval failures and deployment support | Samin | T53 | todo | Installed scaffold; implementation and acceptance not yet performed. |
| T55 | agent | Implement the registered aggregate-interval repair | Samin | T54 | todo | Installed scaffold; implementation and acceptance not yet performed. |
| T57 | agent | Enforce artifact provenance and scoped scientific acceptance | Sheikh | T52, T53 | todo | Installed scaffold; implementation and acceptance not yet performed. |
| T56 | agent | Execute the controlled scientific comparison and record dispositions | Sheikh | T55, T57 | todo | Installed scaffold; implementation and acceptance not yet performed. |
| T58 | agent | Carry scientific support consistently through API, UI and exports | Shammo | T56, T57 | todo | Installed scaffold; implementation and acceptance not yet performed. |
| T59 | agent | Revalidate corrected outlook and enforce honest alert disposition | Samin | T56, T57, T44, T45 | todo | Installed scaffold; implementation and acceptance not yet performed. |
| T60 | agent | Verify the challenge's area-calendar-comparison-export journey | Sattyam | T58, T59 | todo | Installed scaffold; implementation and acceptance not yet performed. |
| T14 | agent | Season-level unusual flags (library and spec) | Monazir | T07, T53, T58 | todo |  |
| T15 | agent | Season flags in the season response and on the calendar | Monazir | T14, T08, T58 | todo |  |
| T21 | agent | Observed hotspot recurrence by eligible season | Sattyam | T07, T53, T58 | todo |  |
| T22 | agent | Evidence-bearing planner brief in English | Shammo | T08, T58, T60 | todo |  |
| H06 | human | Sheikh: observe intended users and provide anonymized task evidence | Sheikh | T61, T60, T22 | todo | Requires actual intended-user observations; no simulated participant evidence. |
| T33 | agent | Download MODIS burned-area tiles (MCD64A1) with the Earthdata token | Sheikh | T51 | todo |  |
| T24 | agent | Corroborating burned-area and timing check with MCD64A1 | Samin | T33, T53, T58 | todo |  |
| T23 | agent | Story mode (90-second guided tour for judges and the video) | Shammo | T08, T12, T22, T58, T60 | todo |  |
| T27 | agent | Current-interface QA: strings, payload budgets and sourced numbers | Shammo | T58, T60, T22 | todo |  |
| T34 | agent | Observed device, keyboard and accessibility review | Samiul | T27, T15, T21, T22, T23, T60, H06 | todo |  |
| T62 | agent | Measure serving capacity and resolve demonstrated bottlenecks | Sattyam | T60 | todo | Installed scaffold; implementation and acceptance not yet performed. |
| T28 | agent | Freeze, publish and verify the evidence-bearing event release | Sheikh | T56, T57, T58, T59, T60, T62, T34, T24, H06, T16 | todo |  |
| T29 | agent | Draft the submission text, slide content and video script from measured numbers | Samiul | T28 | todo |  |
| T35 | agent | Submission assets (slides page, recorded story video) and a 13 Nov rules re-check | Samiul | T29, T30 | todo |  |
| T63 | agent | Reassess readiness against the challenge and final evidence | Samiul | T28, T35, T34, T62, H06, T24 | todo | Installed scaffold; implementation and acceptance not yet performed. |
| H04 | human | Sheikh: submit on the Space Apps site | Sheikh | T35, T63 | todo |  |
| H05 | human | Sheikh: event days (14-15 Nov) | Sheikh | H04 | todo |  |
