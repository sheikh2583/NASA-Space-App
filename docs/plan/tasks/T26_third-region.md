---
id: T26
title: Add a third region (cut by default; reopen only if ahead on 10 Nov)
kind: agent
owner: Sheikh
authors: [Sheikh, Sattyam, Monazir, Samin, Shammo]
phase: P2
size: L
needs: [T40]
requires: [real-data]
branch: ws1/T26-third-region
touches: [common/regions.py, ws2_platform/cells.py, ws2_platform/api/make_fixtures.py, ws3_anomaly/periods.py,
          ws4_outlook/season_profile.py, ws5_frontend/src/config.ts, ws5_frontend/src/api.ts, ws5_frontend/src/App.tsx,
          ws5_frontend/src/i18n/en.json, ws5_frontend/src/i18n/bn.json, ws5_frontend/public/demo/areas.json,
          scripts/export_area_catalog.py, README.md, docs/results/training-results.md]
creates: []
checks: [CHECK-PLAN, "python -m pytest -q ws4_outlook/tests/test_season_profile.py ws2_platform/tests/test_tiny_api.py", CHECK-FILES, CHECK-WEB]
human_checks: [CHECK-PY, CHECK-QA, CHECK-SMOKE]
---
## Goal
Show that the method transfers by adding one more region end to end, without harming the existing two.
- **The default is western Uttar Pradesh / Indo-Gangetic Plain:** the same rice-wheat system as Punjab, and the India
  FIRMS files are already downloaded.
- This card is `cut` on the board. Sheikh reopens it (`plan.py set T26 todo`) only if every P0 and P1 card is done by
  10 Nov.
- It needs a full training run by Sheikh after the code changes.

## Context: where a region is wired (verified in the code)
- `common/regions.py` `DEMO_REGIONS`: code → name and bbox. It drives cell creation (`ws2_platform/cells.py`), the
  ingest clip (`ws3_anomaly/ingest/normalize.py --clip demo`) and the weather download
  (`ws3_anomaly/loaders/weather.py`).
- `ws2_platform/cells.py` `TARGET_ADMIN_ISOS = {"IND": {"IN-PB", "IN-HR", "IN-DL"}}` filters which Indian ADM1
  boundaries are kept. **Keep these three.**
- `ws3_anomaly/periods.py` `AGRI_MONTHS`: crop-residue months per demo code.
- `ws4_outlook/season_profile.py` `SEASON_WINDOWS`: season windows per lower-case demo code.
- `ws2_platform/api/make_fixtures.py` `AOIS`: the demo AOIs used by the fixtures and by `scripts/export_hosted_demo.py`.
- `ws5_frontend/src/config.ts` `DEMOS`: the web app's demo areas. `snapshot.ts` `areaKey()` matches them.

## Steps
1. **Code.** Add the new code (for example `UP`) to `DEMO_REGIONS`, with a bbox from the geoBoundaries ADM1 shape of
   `IN-UP`, cut to the western half (lon ≤ 80). Add its ISO code to
   `TARGET_ADMIN_ISOS["IND"]`. Add its months to `AGRI_MONTHS`.
2. **Season windows.** Measure the region's monthly shares after the first run (step 4), then set its
   `SEASON_WINDOWS` the same way `docs/specs/I1_SEASON_PROFILE.md` section 2 did. Record the shares in the PR.
3. **Weather.** Run `python -m ws3_anomaly.loaders.weather` so the new region's NASA POWER cache exists. Check how
   it's invoked in `scripts/run_pipeline.py` first.
4. **Stop and ask Sheikh** to run the training with `scripts/train.ps1` (or `scripts/train.sh`). It includes
   readiness, the quick and full CUDA runs and QA, and all of it is human-only (`docs/guides/training.md`). Continue
   when he reports the results.
5. **Compare** with the latest `docs/results/training-results.md` section: the existing regions' held-out CCC and coverage must not
   get worse by more than 0.005 CCC or 1 coverage point. Explain any change.
6. **Demo wiring.** Add a demo AOI (a 1.8° × 1.4° box inside the region, like Punjab's) to `AOIS` and to
   `config.ts` `DEMOS`. Add the i18n names (`map.demo_<code>`) and the button in `App.tsx`'s map bar. Re-export the
   snapshot.
7. **Docs.** Add a section to `docs/results/training-results.md` and a line to `README.md` scope.
8. Run the checks, mark the card done, `split`, push and open the PR.

## Acceptance
- [ ] The third area works in the snapshot build: calendar, season card, status.
- [ ] Existing regions' metrics are within tolerance; numbers are in the PR.

## Stop and ask if
- Cells or detections double, or memory runs out during training.
- The existing regions' metrics move beyond tolerance.
