# I8: verified satellite coverage and outage handling (spec, 4 Nov 2026)

Status: **proposal**. The registry (`common/outages.yaml`) and the read-only audit (`ws2_platform/coverage.py`, 13
tests) are in the code. Nothing in the pipeline reads them yet, so `data/processed/` and the hosted snapshot are unchanged. Sections 4
and 5 need Sheikh's sign-off and an entry in `docs/project/contract-changes.md` before anything changes scientific outputs.

## 1. The problem, measured against the current code

- `ws2_platform/sensors.py` treats a satellite as operating on **every** day between its first and last detection,
  minus `common.regions.OUTAGES`. That list has one entry (Terra, 26-27 Mar 2026). Gaps inside the record are not
  visible.
- NASA MODAPS lists many Suomi NPP outages
  ([table](https://modaps.modaps.eosdis.nasa.gov/services/production/outages_suomi_npp.html), from 14 Nov 2011, last
  updated 15 Aug 2026). One is the GPS anomaly of **2 Nov 22:12 to 6 Nov 17:30 UTC 2024**, at the peak of Punjab's
  burning season. Our archive has SNPP detections again on 7-9 Nov (docs/agents/claude-review.md).
- The current pipeline treats those outage days as operating. As a result:
  - SNPP shows observed zeros or undercounts.
  - Weeks that contain outage days count as full SNPP+MODIS overlap weeks, so they are in the B1 ratio fit and the
    model training rows (`ws1_harmonize/model.py`, `baselines.py`), and in the NOAA-20 ratio fit.
  - This likely biases the PB November ratio downward. Every modeled pre-2012 November in Punjab uses that ratio. The
    size of the bias is unmeasured (see acceptance criterion A6).
- Two inferences are not allowed:
  - Detections on a day do not prove full coverage. An outage can remove one pass or part of the region.
  - Zero detections do not prove an outage. There may simply be no fire.
  So the registry must come from operational sources, and our data is used only to check it.

## 2. Registry contract (`common/outages.yaml`)

One entry per UTC interval. Each entry has these fields:

| Field | Meaning |
|---|---|
| `id` | Unique id |
| `sat` | One of the values in `common.regions.SATS` |
| `start_utc` | Start time, inclusive, ISO-8601 ending in `Z` |
| `end_utc` | End time, exclusive. A granule listed as "inclusive" ends 6 minutes after its start |
| `source` | Where the entry comes from |
| `source_url` | Link to the source. Required unless `verification` is `documented` |
| `products` | Affected products. MODAPS gives none, so this reads `unspecified` |
| `verification` | One of the values in the table below |
| `note` | Free text |

`verification` takes one of these values:

| Value | Meaning |
|---|---|
| `documented` | In a NASA notice already cited in docs/science/decisions.md |
| `table_and_data` | In the source table and consistent with our archive |
| `transcribed` | Copied, but a person has not checked it against the source page |
| `rejected` | Kept for the record, but ignored by the audit |

`load_registry()` refuses an entry that is missing a field, has an unknown satellite or a time that isn't UTC, ends
before it starts, or reuses an id. Overlapping entries for the same satellite are merged before use.

What it contains today:
- The Terra event (documented).
- The Nov 2024 GPS event (`table_and_data`).
- 24 multi-hour SNPP entries for 2024-2026, all `transcribed` (copied from a page summary on 4 Nov).
- Entries before 2024 are **not** in it yet.

## 3. From UTC intervals to our days: local solar dates and passes

Our day is the local solar date (decision 23), so one UTC outage covers different local days in Bangladesh (about
UTC+6) and Punjab (about UTC+5). The audit works per demo region, local day and pass (D = day, N = night):

1. **Pass window.** The span of local solar hours when that satellite's detections occur over the region. It is
   measured from our detections: the 0.5-99.5% quantiles, with the night pass centred on midnight. Where there are
   fewer than 50 detections, it falls back to D 11:30-15:30 and N 23:30-03:30.
2. **UTC window.** For local day L the pass can occur between L + start - lon_max/15 h and L + end - lon_min/15 h. The
   region's whole longitude range is covered, so the window is conservative.
3. **Overlap fraction.** The share of that UTC window inside the merged outage: 0 to 1, per pass.

Worked example: the Nov 2024 GPS event with the default windows (unit test `test_gps_outage_maps_to_local_days_and_passes`).

| Local day | PB day | PB night | BD day | BD night |
|---|---|---|---|---|
| 2 Nov | 0 | 0 | 0 | 0 |
| 3 Nov | 1.00 | 0.26 | 1.00 | 0.18 |
| 4 Nov | 1.00 | 1.00 | 1.00 | 1.00 |
| 5 Nov | 1.00 | 1.00 | 1.00 | 1.00 |
| 6 Nov | 1.00 | 0.83 | 1.00 | 0.88 |
| 7 Nov | 0 | 0 | 0 | 0 |

So the outage removes the **day pass on local 3-6 Nov** in both regions. That is consistent with the archive having
SNPP data on 7-9 Nov. Measured windows will move the night fractions somewhat. On local 3 Nov the night pass is only
partly affected, so the partial-day policy (section 4) decides that day.

## 4. Proposed pipeline change (needs sign-off)

**Option A (recommended now; additive).**
- `sensor_days` keeps its key `(date, sat)`.
- A satellite is non-operating on a local day if the policy excludes that day in **any** demo region. The two regions
  differ by about one hour, so this over-excludes at most the edge days.
- `note` carries the event ids and their verification status.
- A new provenance file `data/processed/coverage_days.parquet` holds the audit's `affected_days` table: sat, region,
  date, overlap_D, overlap_N, event_ids, verification.
- `parquet_schemas.json` gains that table. No existing column changes.

**Option B (later; breaking).** `sensor_days` keyed by `(date, sat, region)`. Use it only if Option A's
over-exclusion turns out to matter.

**Partial-day policy (provisional).** Exclude a day when any pass overlap is at least **0.25**. That drops days where
a quarter of a pass window is lost, and ignores single 6-minute granule blips. On the current registry with default
windows, 133 region-days have some overlap:

| Threshold | Region-days excluded |
|---|---|
| Any overlap | 133 |
| 0.25 | 115 |
| 0.5 | 109 |
| 1.0 | 92 |

Pick the final threshold from the real-data audit (`would_flip_*.csv`), not from these defaults.

**Filling excluded SNPP days.**
- From 1 Apr 2018, when NOAA-20 is operating: use NOAA-20 adjusted to SNPP terms (`source = adjusted_from_noaa20`).
  That is the same ratio already used after the 2 Nov 2026 cutoff. It needs a change to `common.series.day_sources`
  and `ws1_harmonize/write_harmonized.py`; today they use NOAA-20 only after the cutoff.
- Before 2018: modeled MODIS, which is the current behaviour.
- Both cases get wider intervals. They are never shown as observed.

**Which applies.** Only `documented` and `table_and_data` entries change outputs. `transcribed` entries stay in the
audit until a person checks them.

**Versioning.** Bump `method_version` (for example `v1-b1-cov1`) and record the registry's git hash in
`method.json`. Keep the 4 Nov 2026 run (`docs/results/training-results.md`) as the comparison baseline.

## 5. Acceptance criteria

Each criterion is marked measured (M) or person-checked (H). Expected-failure tests do not count.

| # | Criterion | Type |
|---|---|---|
| A1 | `load_registry()` passes and every `transcribed` entry has been checked against the MODAPS page: set to `table_and_data` or `rejected`, with the checker named in `note` | H |
| A2 | Real-data run of `python -m ws2_platform.coverage`: pass windows `measured` (not default) for every satellite and region with data; zero contradictions for `documented`/`table_and_data` entries; every other contradiction explained in the PR | M |
| A3 | Nov 2024: SNPP day-pass detections in PB and BD on local 4-5 Nov = 0; NOAA-20 day-pass detections on those days > 0; SNPP present on 7-9 Nov | M |
| A4 | `candidate_gaps.csv` reviewed for each region's burning months (PB Apr-May and Oct-Nov, BD Feb-Apr), 2012-2026. Each candidate is added to the registry with a source, or listed as a reviewed real zero in `ws6_validation/coverage_review.md`. Candidates are never excluded automatically | H |
| A5 | Before wiring: the `would_flip` count at the chosen threshold, and the number of SNPP+MODIS and SNPP+NOAA-20 overlap weeks that leave the fit, are written in the PR | M |
| A6 | After wiring, Sheikh's full training run (H02; agents never train) reports: the selection metrics for B1 and the learned candidate on every holdout; 90% band coverage, weekly and monthly; PB and BD November B1 ratios and the NOAA-20 ratio, before and after. The method choice is re-made from these numbers, not assumed | M |
| A7 | PB 2024 ISO weeks 44-45: excluded days show `adjusted_from_noaa20` and the weekly total no longer drops below the NOAA-20-implied value; `modeled_share` / source mix visible in the API and snapshot | M |
| A8 | All five QA groups pass; `test_rows_on_non_operating_days_are_documented` passes with the event ids in `note`; a new test covers the NOAA-20 fill before the cutoff, a region with no detections (default windows) and an empty registry | M |
| A9 | New runtime release published (`scripts/release_runtime.py`), Render rebuilt and `scripts/check_render.py` passes (`/health` `data_through`, `/version.json` commit), legacy snapshot re-exported, and the method page (en and bn) says how outages are handled | M + H |

## 6. Work left, in order (plan cards in `docs/plan/tasks/`)

1. **T32, agent:** check the registry against the MODAPS table (A1) and add the multi-hour entries from 2012-2023.
2. **T05, agent, on the laptop with data:**
   - run the audit and review the candidate gaps for the burning months (A4);
   - write `docs/specs/I8_AUDIT_RESULTS.md` with the counts, the lost overlap weeks and the recommended threshold (A5);
   - record the decision in `docs/science/decisions.md`. Sheikh's merge of that PR is the sign-off.
3. **T06, agent:**
   - `sensors.py` applies verified outages, through `coverage.py`, and writes `coverage_days.parquet`;
   - `day_sources` gains the NOAA-20 fill;
   - new tests.
4. **H02, Sheikh:** the full training run.
5. **T40, agent:** before → after report (A6), the A7 check, and the republished snapshot (A9).

Owners: Sattyam (`ws2_platform/`: sensors, coverage), Samin (`common/`: registry, series), Sheikh (`ws1_harmonize/`
and the training run), Samiul (A4 review file, method text).
