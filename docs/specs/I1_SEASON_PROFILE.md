# I1: season profile (spec, 4 Nov 2026)

Status: the library is built and tested (`ws4_outlook/season_profile.py`, 10 tests). The draft contract is
`contracts/json_schemas/season_profile.schema.json` with example `contracts/fixtures/punjab_season_profile.json`.
It isn't yet served by the API, exported to the snapshot or shown in the UI (cards T07, T08). It changes no existing
output.

## 1. Question it answers
"When does burning usually happen here, is this season early, late, big or small, and is the timing shifting?"
This is the plainest reading of the challenge's "when burning happens", and today the app doesn't answer it in words.

## 2. Definitions

**Season window.** A fixed calendar search window per area. Provisional windows, from the observed 2012-2026 monthly
shares in the snapshot:

| Area | Season | Window | Share of observed detections |
|---|---|---|---|
| Punjab (pb) | wheat residue | 1 Apr-30 Jun | Apr 1.9%, May 18.2% |
| Punjab (pb) | paddy residue | 15 Sep-31 Dec | Oct 23.9%, Nov 54.4% |
| Bangladesh (bd) | dry season | 1 Nov-31 May (crosses the year) | Nov-Apr 96% |

A week belongs to the season year whose window contains its midpoint. The season year is the year in which the
window ends.

**Central activity window.** The days on which 10% and 90% of the season's detections had accumulated (p10, p90),
with the median day p50. Each week's value is spread evenly over its 7 days. This is a detection statistic, **not the
physical start or end of burning**, and the UI must say so.

**Timing.** Measured in days since the window start, so leap years don't shift it. Typical dates are shown as
month-day in a non-leap reference year.

**Status of a season year:**
- `partial`: the window hasn't ended by `as_of`.
- `missing`: fewer than 90% of its weeks have values.
- `low_activity`: fewer than 30 detections in total. This is an absolute threshold on purpose: Punjab's small recent
  seasons are still seasons.
- `complete`: otherwise. Only complete seasons enter the typical values and the trends.

**Multiple peaks.** `multi_peak` is true when another local maximum of at least half the main peak lies 3 or more
weeks away from it.

**No look-ahead.** Weeks that end after `as_of` are dropped before anything else. A test checks that changing later
data changes nothing.

## 3. What it reports, per season
- **`typical`:** all complete seasons. Median and quartiles of p10, p50, p90 and peak, plus the median total.
- **`typical_observed_era`:** the same, but only for seasons with less than 50% modeled values (VIIRS era).
- **`timing_trend`:** Theil-Sen slope of p50 against year, in days per decade, with its 95% interval.
  - Observed era only, so the 2012 sensor seam can't create a fake shift.
  - Verdict `later`, `earlier` or `no_clear_shift`; `insufficient_seasons` when there are fewer than 8.
- **`magnitude_trend`:** Theil-Sen of log(total), as percent per decade, with interval and verdict `more`, `fewer` or
  `no_clear_shift`. It is reported **separately** from timing, with the caveat that detections are not burned area.
- **`current`:** the season in progress, compared with past complete seasons **at the same cutoff**:
  - total so far;
  - its percentile;
  - the typical total so far;
  - the typical share of a season done by this date.
- **`years`:** per season year: status, total, coverage, modeled share, p10/p50/p90/peak dates, multi-peak, and
  `interval_sensitivity_days`. The last is the largest timing shift when non-observed weeks are set to their lower,
  then upper, bound. It is a bounding scenario, labelled as such, not a calibrated interval.

## 4. Measured on the public snapshot, 4 Nov 2026
These are the demo AOIs, measured before the I8 correction (`python -m ws4_outlook.season_profile --area pb|bd`).

| Area / season | Typical window (p10-p90), median day | Observed-era timing trend | Observed-era magnitude trend |
|---|---|---|---|
| Punjab paddy | 21 Oct-12 Nov, 2 Nov (25 seasons) | **4.3 days per decade later** (CI 1.0 to 6.6; 14 seasons) | **58% fewer per decade** (CI 25 to 91% fewer) |
| Punjab wheat | 1-18 May, 9 May (26) | no clear shift (-1.4; CI -7.8 to 5.2) | no clear change |
| Bangladesh dry season | 26 Dec-2 Apr, 16 Mar (25) | no clear shift | 26% fewer per decade (CI 1 to 51% fewer) |

Punjab paddy 2026 to 2 Nov: 455 detections against a typical 21,656 by the same date (0th percentile). Check this in
H02 before using it.

Interpretation limits:
- NASA has reported that Punjab burning may have shifted to later in the **day**, after the afternoon polar-orbiter
  passes (https://science.nasa.gov/?p=1160169).
- So part of the fall in detections may be fires burning outside overpass times (T20). The app must not present it
  simply as "less burning".
- The later **seasonal** timing found here is our own measurement. It has not been checked against harvest-date
  records.

## 5. Contract and snapshot (T07)
- API: `POST /aoi/season` takes an `AOIRequest`.
  - Start and end are ignored: the full history up to `as_of` is used, where `as_of = data_end + 1 day`.
  - It returns the profile with the API envelope fields applied last (`schema_version`, `units`, `day_convention`,
    `notes`); the profile's own version moves to `profile_version`.
- Season windows: `area` is the demo code (`pb`, `bd`) of the admin1 region holding most of the selected cells
  (`Store.region_of(sel)["country"]`), for drawn areas too. With no cells, or no windows for that code, the response
  has `seasons: []` and a note.
- Snapshot: `areas.<key>.season` holds the profile computed by `export_hosted_demo.py`. `snapshot.ts` serves
  `/aoi/season` from it.
- The schema version stays `0.1.0-draft` until T08 ships, then becomes `0.1.0`.

## 6. Acceptance
- Library tests (done):
  - known timing recovered;
  - timing and magnitude trends kept separate;
  - observed-era basis;
  - no look-ahead;
  - window crossing the new year;
  - missing, low-activity and multi-peak seasons;
  - schema validation on the real snapshot.
- T07: API test with fixture data. The snapshot contains a valid `season` block for both areas
  (`tools/verify_files.py` validates it).
- T08:
  - The UI shows the typical window band on the calendar and one sentence in en and bn.
  - The definition is available behind a "?" (T09).
  - Works at 390 px width and in snapshot mode.
- Human: Samiul confirms the Bangla wording. Someone outside the team answers "when does burning usually peak in
  Punjab?" correctly within 30 seconds.
