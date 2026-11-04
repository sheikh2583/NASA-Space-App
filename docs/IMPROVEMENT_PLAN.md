# Improvement plan, revised (4 Nov 2026)

> **Execution order and step-by-step cards now live in `docs/plan/`** (README, STATUS, and the cards in tasks/: T00-T40 for the coding agent, H01-H05 for Sheikh only). This file keeps the per-item requirements those cards implement.

This plan replaces the 3 Nov plan and its `scaffold-patches.zip`. That plan was written before the real-data run, and
its scaffold was not applied. It was revised from `docs/CLAUDE_REVIEW.md`.

Current facts are in `docs/CLAUDE_HANDOFF.md` and `docs/TRAINING_RESULTS.md`:
- **Data and training:** real data through 2 Nov 2026. The full training run selected B1 (held-out CCC 0.9417 against
  0.9351 for LightGBM).
- **Interval coverage:** 91.6% weekly and 93.7% monthly for nominal 90% bands.
- **Hosting:** live static snapshot on GitHub Pages; FastAPI runs locally only.

Rules for every item:
- **Before any change to scientific outputs:** write a spec with contracts and acceptance criteria, and get Sheikh's
  sign-off. Then re-run full training and report the measured results separately from estimates.
- **Snapshot site:** every user-facing feature works in the static snapshot or shows an explicit "needs the live
  API" state. The static host cannot serve new endpoints.
- **Expected-failure tests:** these record unfinished work and are reported apart from passing features. Tests use
  real fixtures, never `None` stores.

## Priorities

| Priority | Item | State | Next step |
|---|---|---|---|
| **Next** | **I8 verified coverage and outages** | Registry and read-only audit done; spec written | Sheikh runs the audit locally; a person checks the transcribed entries ([spec](specs/I8_COVERAGE.md)) |
| Next | I4 plain-language help, I15 caveats | Not started | Wording only; en and bn; no scientific change |
| Next | I1 season profile | Not started | Spec first (below) |
| Small UI | I3 region picker (ADM1) | Two demo buttons exist | Label as division (BD) / state or territory (IN); select exact IDs, not a bounding box |
| Small UI | I7 Compare collapse | Forecast alerts already withheld without skill | Only fold Compare; keep the season-to-date context |
| Infrastructure first | I2 near-real-time refresh | Not started | Design artifact storage, reconciliation and rollback before code |
| Infrastructure first | Full FastAPI hosting | Not started | Versioned artifacts, health check that loads data, memory sizing |
| Validation first | I5 FRP, I10 recurrence, I12 GeoJSON, I13 intervals, I14 season flags | Not started | Contract and validation design per item (below) |
| Reassess | I6 day-view speed, I11 config regions | Not started | Benchmark on current data; list the real steps for a third region |
| Defer | I16 global, I17 geostationary, I18 experiments, I19 offline | Not started | After the event |

## What each item must satisfy (revised from the review)

**I8 coverage and outages.** See `docs/specs/I8_COVERAGE.md`.
- The registry holds UTC intervals with source, products and verification status.
- Outages map to local solar days per region and pass.
- The partial-day threshold is chosen from measured audit counts.
- The NOAA-20 fill from 2018 is versioned.
- Full retraining reports CCC, coverage and the ratios before and after.

**I4 / I15 wording.**
- Help next to Status, Severity, Calendar and bands; month labels on the week axis.
- The caveats cover these points:
  - detections are not burned area;
  - pre-2012 values are modeled;
  - overpass timing and late-afternoon burning;
  - the sensor changes (the SNPP end on 2 Nov 2026, NOAA-20 adjusted);
  - weather is association only;
  - this is not an alert service.
- Done when `check:strings` passes, a fluent reviewer signs off the Bangla, and the page works at phone width in
  both demo areas.

**I1 season profile.**
- Call the 10-90% cumulative span the "central activity window", not onset or end of burning.
- Define the edge cases: missing, partial and low-activity seasons; leap years; as-of cutoffs with no later data.
- Support more than one season per year: Punjab has Apr-May and Oct-Nov.
- Report timing shifts apart from changes in amount, with uncertainty, and mark seasons that rely on modeled years.
- Snapshot mode needs a precomputed profile in `snapshot.json`.

**I3 region picker.**
- ADM1 means Bangladesh divisions and Indian states or territories, not districts. Use ADM2 only if it is acquired
  and validated.
- Administrative totals select exact admin IDs or polygons; a bounding box takes in neighbouring areas.
- Snapshot mode is limited to the exported areas.

**I2 near-real-time refresh.**
- Fetching:
  - re-fetch an overlapping window on each run;
  - when a standard-product row replaces an NRT row, track provenance and handle late arrivals;
  - recompute only the affected days and weeks.
- Models: freeze the model and calibration versions.
- Publishing:
  - stage the new outputs and validate them;
  - publish atomically, with rollback.
- Before writing any code:
  - Storage: define versioned artifacts. A fresh GitHub Actions checkout has no data or models.
  - Stage names: the real stage is `anomalies`.
  - File discovery: the pipeline glob must include `data/raw/firms/nrt/`.
  - Features: check which ones exist at refresh time (`next_modis_n`).
- Keep credentials backend-only; strip request URLs from logs.

**I5 FRP.**
- No count-interval multipliers as FRP uncertainty: calibrate FRP separately, or show it explicitly as uncalibrated.
- Define the aggregation and units: a sum of sampled FRP is not energy or continuous intensity.
- Audit the current count-derived NOAA-20 adjustment applied to FRP.

**I10 recurrence.** Denominator = years with valid observations for those weeks (per I8). Show modeled and observed
years apart.

**I12 GeoJSON export.** Carry provenance, method version, units, interval meaning and citation. API mode only, unless
it is added to the snapshot.

**I13 intervals.**
- No width target.
- Report held-out coverage and interval score by AOI size, magnitude, season and satellite combination.
- Report width only as a diagnostic, with handling near zero.
- The sampler uses `terra_aqua` only, so check the Terra-only years explicitly.

**I14 season flags.**
- Use a calibrated season-level bound, or a dependence-aware method.
- Don't sum weekly lower bounds.
- Compare a partial season at the same cutoff in past years.

**I6 day view.** Benchmark on the current real data before changing anything.

**I11 config regions.**
- A third region needs more than YAML:
  - geometry and clipping;
  - weather;
  - season months;
  - readiness checks, frontend config and packaging.
- Add `config/` to `scripts/share_zip.py` if it is introduced.
- Keep the Punjab/Haryana/Delhi filter and the SNPP ingestion fix.

**I18 experiments.**
- Split into three independent experiments:
  - viewing-angle correction;
  - multi-VIIRS harmonization (state which pair);
  - burned-area cross-check.
- Any change to the reference series is validated and versioned. Check published coefficients transfer to these
  regions before use.

## Measured versus estimated

Report every result with how it was obtained:
- **measured** in a named run (date, command, commit);
- **unit-tested** on a fixture;
- **estimated**;
- **person-checked**.
