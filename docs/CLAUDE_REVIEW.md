# Review for the original Claude author

Reviewed 4 November 2026 against the repository at functional baseline `a4dc92d` and the local real-data outputs. Input documents were `codex/PROJECT_STATE.md`, `codex/IMPROVEMENT_PLAN.md`, and `codex/scaffold-patches.zip`. No scaffold was applied, and those original files were left unchanged.

## Decision

Keep selected ideas, revise the state/backlog and scientific acceptance criteria, then implement small working changes. Do not apply the ZIP as a completed feature set. All six patches pass a read-only `git apply --check`, but contain stubs and expected-failure tests rather than implemented functionality.

## Replace obsolete state claims

The repository is pushed, real inputs are loaded, full training is complete, and Pages is live. Full-run selection was B1 CCC 0.9417 versus LightGBM 0.9351; held-out coverage was 91.6% weekly and 93.7% monthly for nominal 90% intervals. These are agreement/coverage statistics, not classification accuracy. The UI already has two demo-selection buttons. Use `CLAUDE_HANDOFF.md` and `TRAINING_RESULTS.md` for current facts, rather than synthetic-run scores or old feature estimates.

## Revisions required before implementation

1. **I8 outage registry:** Do not exclude SNPP for all of 2–9 November 2024. The [NASA MODAPS operational table](https://modaps.modaps.eosdis.nasa.gov/services/production/outages_suomi_npp.html) lists a GPS outage spanning parts of 2–6 November. The downloaded archives have SNPP observations on 7–9 November. Record UTC intervals, source, affected product/collection, verification status, and a partial-day policy; reconcile these with local-solar dates. Detection presence alone is not complete coverage proof, and zero detections alone is not outage proof. Current operating-day logic can miss internal gaps; investigate before adding new trend claims.

2. **I2 NRT:** Replace append-only-by-latest-date logic with overlapping re-fetch and reconciliation, explicit standard/NRT provenance, late-arrival/replacement handling, affected-day/week recomputation, frozen model/calibration versions, staging, validation, and atomic publication/rollback. A fresh GitHub Actions checkout has no historical datasets or fitted models: define versioned artifact storage and retrieval first. The real stage name is `anomalies`, not `anomaly`; the current pipeline input glob does not recursively discover `data/raw/firms/nrt/`. Review feature availability at refresh time, including `next_modis_n`. Keep credentials backend-only and redact request URLs from errors/logs.

3. **I5 FRP:** Do not reuse count-interval multipliers as calibrated FRP uncertainty. Validate/calibrate FRP separately, or show explicitly uncalibrated point estimates initially. Define sampled FRP aggregation and units; a sum of observations is not automatically integrated energy or continuous weekly intensity. Audit the current use of a count-derived NOAA-20 adjustment for FRP.

4. **I13 intervals:** Remove the target that bands must be no wider than 2.5 times the value. Require held-out coverage and interval-score assessment by AOI size, magnitude, season, and satellite-input combination; report width as a diagnostic with sensible handling around zero. The current sampler filters to `terra_aqua`, so assess applicability to Terra-only reconstruction explicitly.

5. **I14 seasonal flags:** Do not treat a sum of weekly lower bounds as a calibrated seasonal lower bound. Use season-level calibration or a justified dependence-aware method, and compare partial seasons at equivalent cutoffs.

6. **I1 season profiles:** Call cumulative 10–90% thresholds a central activity window, not physical fire onset/cessation. Define missing/partial/low-activity seasons, leap years, multiple peaks, as-of cutoffs, and uncertainty. Distinguish timing changes from activity magnitude changes; Punjab can have multiple burning seasons.

7. **I3 region picker:** ADM1 corresponds to Bangladesh divisions and Indian states/territories, not districts. Use the correct label or acquire ADM2. Select exact IDs/polygons when reporting administrative totals; a bounding box can include neighboring jurisdictions.

8. **I7 forecast display:** The current UI already withholds forecast alerts without demonstrated skill while retaining season-to-date context. Preserve that distinction rather than hiding the entire outlook panel.

9. **I11 config regions:** Adding a third region currently requires more than YAML: review geometry, clipping, weather, seasons, readiness checks, frontend configuration, and packaging. Include `config/` in the share allowlist if introduced; preserve Punjab/Haryana/Delhi filtering and the SNPP ingestion fix.

10. **I18 experimental scope:** Split viewing-angle correction, multi-VIIRS harmonization, and burned-area cross-check into independent experiments. Resolve the inconsistent proposed pairs (SNPP + NOAA-20 versus NOAA-20 + NOAA-21). Any change to the reference series requires validation and clear versioning, not an untested average. Check paper methods and transferability before adopting published coefficients.

## Revised priorities

| Priority | Items |
|---|---|
| Next | Verified coverage/outage handling I8; explanatory wording I4/I15; carefully specified season profile I1 |
| Small UI improvements | Correctly named ADM1 picker I3; optional Compare collapse I7 |
| Infrastructure design first | NRT refresh I2; separate full FastAPI hosting if arbitrary hosted AOIs are required |
| Validation/contract design first | FRP I5; recurrence I10; GeoJSON I12; interval improvements I13; seasonal flags I14 |
| Reassess on current system | Day-view speed I6; config-driven regions I11 |
| Defer | Global overview I16; geostationary work I17; bundled scientific experiments I18; offline caching I19 |

For recurrence, define valid-observation denominators and modeled versus observed years. For GeoJSON, retain provenance, method version, units, uncertainty semantics, and citation. Benchmark day-view latency on current data rather than reusing old synthetic timings. Do not assume the static host can serve new API endpoints.

## Replace weak acceptance tests

- Replace `None` stores/selections with meaningful data fixtures.
- `test_i13_large_area_band_width` unconditionally raises; implemented code cannot make that test pass. Write a real coverage/score check.
- Expected failures document unfinished work; report them separately from implemented, passing features.
- Cover missing observations, partial seasons, delayed updates, replacement products, network failure, rollback, and no-data cases.
- Test local API and hosted snapshot modes separately. Each new feature needs snapshot support or an explicit disabled state.
- Preserve current deployment and distinguish code pushes from scientific-data refreshes.
- Review actual file ownership/branch guard rules when introducing shared config or new root-level artifacts. Patch authorship does not grant implementation approval or demonstrate teammate review.

## Suggested continuation prompt

Read `CLAUDE.md`, `docs/CLAUDE_HANDOFF.md`, and this review. Update the old state/backlog around the completed real-data baseline and live snapshot site. Propose revised contracts and acceptance criteria for the highest-priority item before changing scientific outputs. Preserve existing data, secrets, the working basemap, and Pages deployment. Do not apply all scaffold patches or treat expected-failure tests as feature completion. Report measured results separately from estimates and remaining human checks.
