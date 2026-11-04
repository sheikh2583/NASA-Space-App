---
id: T14
title: Season-level unusual flags (library and spec)
kind: agent
owner: Monazir
authors: [Monazir, Sheikh]
phase: P1
size: M
needs: [T07]
requires: []
branch: ws1/T14-season-flags
touches: [docs/specs/I1_SEASON_PROFILE.md, docs/CONTRACT_CHANGES.md]
creates: [ws3_anomaly/season_flags.py, ws3_anomaly/tests/test_season_flags.py]
checks: [CHECK-PLAN, CHECK-PY]
---
## Goal
Weekly flags catch spikes, but a whole season that runs high or low is flagged only at its edges. Build a season-level
flag with an honest uncertainty label. This card is library and spec, plus the default decision; Sheikh's merge is the
sign-off. T15 then puts the flags in the API and UI.

## Method (from the review; don't sum weekly lower bounds as if they were calibrated)
- **Input:** one season from `ws4_outlook.season_profile` (`years[]` with `season_year`, `status`, `total`,
  `modeled_share`). The function also takes the weekly series, so it can build bounds.
- **Reference:** past `complete` seasons only. A minimum of 8, else the verdict is `insufficient`.
- **Verdict:** `high` above the reference 90th percentile, `low` below the 10th, otherwise `normal`.
- **Two bases**, both reported:
  - `all`: every past complete season;
  - `last10`: the 10 most recent. Punjab totals are falling, so "versus the last 10 years" is the fairer context.
- **Confidence:**
  - `observed` when the season's `modeled_share < 0.05`.
  - Otherwise recompute the verdict with the season total at a lower and an upper bound: the sum of weekly `lo` and
    `hi` over the non-observed weeks only, plus the observed weeks' values.
  - `confident` if both bounds give the same verdict as the value, else `uncertain`. Label it "range-based, not
    calibrated".
- **Partial seasons:** use `current.to_date_total` against past seasons' totals at the same cutoff
  (`season_profile._cum_at`). Never compare with full-season totals.

## Steps
1. **`ws3_anomaly/season_flags.py`.**
   ```python
   season_flags(weekly: pd.DataFrame, season: Season, as_of, basis="both") -> list[dict]
   ```
   Each item has `season_year`, `verdict`, `basis`, `percentile`, `confidence` and `modeled_share`. Partial seasons
   carry `partial: True` and use the same-cutoff comparison. Reuse `season_profile.season_years`; don't
   re-implement it.
2. **Tests** (`ws3_anomaly/tests/test_season_flags.py`), on synthetic weekly series with noise and a fixed seed, as
   in `ws4_outlook/tests/test_season_profile.py`:
   - a planted 1.9× season is `high` on both bases;
   - a planted 0.3× season is `low`;
   - at most 3 flags in 24 noise-only seasons;
   - a partial season is compared at the same cutoff: an ordinary season cut at its median day is `normal`;
   - a season with 100% modeled weeks and wide bands is `uncertain`;
   - with fewer than 8 past seasons the verdict is `insufficient`.
3. **Spec.** Add a section `## 7. Season flags (proposed)` to `docs/specs/I1_SEASON_PROFILE.md` covering the method
   above, the test results and the proposed API field `years[].flag = {verdict, basis, percentile, confidence}`.
4. **Default decision.** Add "Decision (<date>, approved on merge)" to the spec section:
   - the UI shows the `last10` basis, with `all` in the tooltip;
   - `uncertain` flags are shown greyed out, with a note.

   Append a line to `docs/CONTRACT_CHANGES.md` approving `years[].flag` in the season response.
5. Run the checks, mark the card done, `split` (Monazir: `ws3_anomaly/`; Sheikh: the spec and contract files), push and
   open the PR. Its title starts with "T14 (decision)".

## Acceptance
- [ ] All six tests pass.
- [ ] The spec section exists, with the measured test outcomes.

## Stop and ask if
- The noise-only test produces more than 3 flags with the 10th/90th percentile rule.
