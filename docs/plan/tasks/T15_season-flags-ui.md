---
id: T15
title: Season flags in the season response and on the calendar
kind: agent
owner: Monazir
authors: [Monazir, Sattyam, Sheikh, Shammo]
phase: P1
size: S
needs: [T14, T08]
requires: [real-data]
branch: ws1/T15-season-flags-ui
touches: [ws2_platform/api/app.py, ws2_platform/tests/test_api_season.py, contracts/json_schemas/season_profile.schema.json,
          ws5_frontend/src/types.ts, ws5_frontend/src/components/Calendar.tsx, ws5_frontend/src/components/SeasonCard.tsx,
          ws5_frontend/src/i18n/en.json, ws5_frontend/src/i18n/bn.json, ws5_frontend/public/demo/snapshot.json]
creates: []
checks: [CHECK-PLAN, "python -m pytest -q ws2_platform/tests/test_api_season.py ws2_platform/tests/test_tiny_api.py ws3_anomaly/tests/test_season_flags.py", CHECK-WEB, CHECK-SNAP, CHECK-FILES]
human_checks: [CHECK-PY]
---
## Goal
Show the approved season-level flags (decision in T14) where people look: on the calendar's year labels and in the season card.

## Steps
1. **API.** In `aoi_season` (`ws2_platform/api/app.py`), after building `prof`, add `flag` to each `years[]` item from
   `ws3_anomaly.season_flags.season_flags(...)`, using the bases the T14 decision approved.
2. **Schema.** In `contracts/json_schemas/season_profile.schema.json`, add an optional `flag` object (`verdict`,
   `basis`, `percentile`, `confidence`) to `years.items`.
3. **Tests.** Extend `ws2_platform/tests/test_api_season.py`:
   - every complete season has a `flag` with a valid verdict;
   - in the tiny data no season is flagged `high` (the tiny seasons are similar).
4. **UI.**
   - `Calendar.tsx`: a small marker after a year label when that year's season is flagged. Use ▲ for high and ▼ for
     low, with the text `t("season.flag_high")` or `t("season.flag_low")` in its `<title>`. For a season crossing
     the new year, put it on the row of the year the season ends.
   - Show `uncertain` flags greyed, as the T14 decision says.
   - `SeasonCard.tsx`: one sentence for the current or last season's flag.
   - Add the i18n keys in en and bn.
5. Republish with `python scripts/export_hosted_demo.py`. Run the checks, mark the card done, `split`, push and open
   the PR. List which seasons are flagged in the snapshot.

## Acceptance
- [ ] Flags are in the API and the snapshot, the schema validates, and the markers show in the snapshot build.
- [ ] Flagged seasons are listed in the PR, with their basis and confidence.

## Stop and ask if
- More than a third of past seasons are flagged in any demo area.
