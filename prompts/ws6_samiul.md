# Prompt pack: Samiul (Team Member 6), QA, validation content and pitch
Folders: ws6_validation/ and docs/

## P6.1 QA checklist and test scaffolds (H0-4)  HANDOFF
Prompt: "Using docs/QA_CHECKLIST.md as the starting point, create ws6_validation/tests/ with pytest scaffolds: test_contract.py (validates every endpoint of a given base URL against contracts/openapi.yaml), test_data_qa.py (checks on grid_daily.parquet and detections.parquet), test_e2e.py (posts a Bangladesh AOI and a Punjab AOI). Include a README on how to run them against the mock and the live API."
Output: test scaffolds + README. HANDOFF: to everyone.
Test: contract test runs against the mock once Sattyam delivers it (H3).

## P6.2 Contract tests (H3-10)
Prompt: "Complete test_contract.py: for each path in openapi.yaml send a sample request, check status, check the JSON validates against the response schema, check schema_version, units, day_convention and source are present, and check that the empty-AOI and oversized-AOI cases return the documented responses."
Output: passing contract tests on the mock.
Test: running it against a deliberately broken response fails with a clear message.

## P6.3 Data QA (H6-10)  HANDOFF
Inputs: detections.parquet (H6); grid_daily.parquet and cells.parquet (H8).
Prompt: "Complete test_data_qa.py and write a data QA report in markdown: no duplicate (cell_id, sensor, date) keys; dates inside the range; counts and FRP non-negative; grid sums equal detection rows; confidence values in the allowed set; admin1 and land-cover fields filled. Add the manual check: pick one day and one AOI and compare the count with the FIRMS web viewer; record the result."
Output: data QA report. HANDOFF: to Sattyam, Monazir.
Test: every failed check lists the offending rows or files.

## P6.4 End-to-end runs (H12-24, then H30, H36, H42)  HANDOFF at each gate
Prompt: "Complete test_e2e.py: for a Bangladesh AOI and a Punjab-Haryana-Delhi AOI, call the live API and check non-empty series, source flags, flagged weeks, intervals present, the 2012 seam, and that the static fallback works when the API URL is wrong. Produce a markdown bug list with owner, severity and the exact failing request."
Output: end-to-end report and bug list at H24, H30, H36, H42. HANDOFF: to everyone.
Test: every bug has an owner and a reproduction step.

## P6.5 Validation-page content (H30-34)  HANDOFF
Inputs: validation pieces from Sheikh and Samin; method notes from Sheikh.
Prompt: "Write validation/qa.json per contracts/json_schemas/validation_piece.schema.json (QA results, test counts, known limitations). Then read all validation pieces and draft a plain-language summary of three lines for the validation page: what was checked, how well it held up, where it is weak."
Output: qa.json + summary. HANDOFF: to Sattyam, Shammo.
Test: every number in the summary appears in a piece.

## P6.6 Method text (H34-38)  HANDOFF
Inputs: docs/method_notes_sheikh.md (H34).
Prompt: "Write docs/method_en.md under 250 words in plain language: what we did, which values are modeled and which observed, how uncertainty is shown, what a flag means, and the limits (extrapolation before 2012, associations only, outlook may show no skill). Then prepare a Bangla version for review by a fluent teammate and mark every line that needs checking."
Output: method_en.md (H38); reviewed Bangla (H42). HANDOFF: to Shammo.
Test: a non-team reader can explain the method back in two sentences.

## P6.7 Slides, demo script, video (H12 draft, H40 final, H44 video)
Prompt: "Draft an 8-slide outline and a 3-minute demo script: the MODIS-to-VIIRS problem; our approach; the live app (Bangladesh, then Punjab in October-November); uncertainty and validation; limitations; what next; team. Name the three audiences (early-warning and emergency staff, scientists, land managers) and show one scenario for each: current status now, historical pattern and seam, agricultural burn season. State plainly that the demo covers South Asia. Include a backup path that uses the static fallback. Later, turn the outline into slides and a recording plan with timings."
Output: slides, script, video.
Test: every number on a slide traces to a file or a validation piece; the demo path runs in under three minutes.

## P6.8 Submission checklist (H44-46)
Prompt: "Walk docs/SUBMISSION_CHECKLIST.md item by item against the organizers' current rules, mark each done or blocked, and list what Sheikh must do to submit."
Output: completed checklist.
Test: nothing is left unchecked at H46.

## P6.9 Stretch: PM2.5 consistency check (H32-38, only if on time)
Prompt: "Using a public PM2.5 source (for example OpenAQ), deseasonalize PM2.5 and regional burning anomalies and compute lagged correlations with block-permutation p-values. Write validation/pm25.json with wording 'consistent with' and 'not evidence of', and a limitations list stating PM2.5 has many other sources and is not ground truth for fire. Monazir reviews the wording."
Output: pm25.json.
Test: no causal language; Monazir signs off.
