# Codex handoff, 5 Nov 2026: finish the remaining work

Written by Claude after two external audits were reviewed with Sheikh. Pick up from here. Work top to bottom.

## 0. Read first, and the rules that never bend

1. `AGENTS.md` in full. **No training or fitting, ever** (no `workflow.py` train/all/smoke/test/prepare/gpu-check/
   validate, no `python -m <package>.run`, no blanket pytest, no CUDA probes). **There will be no more training:**
   H03 is done (see section 1). Pipeline stages that fit nothing (`python -m ws3_anomaly.batch`) are still
   Sheikh's to run; give him the one-line command.
2. `CLAUDE.md`, `docs/plan/README.md` section 3 (the loop) and section 4 (rules).
3. For each card: `python scripts/plan.py show <ID>`, read every file it names, then edit.
4. Checks: `python scripts/plan.py checks <ID> --run`. Never weaken, skip or delete a test.
5. Never print, log or commit `FIRMS_MAP_KEY`, `EARTHDATA_TOKEN`, `RENDER_URL` values or `.env`. Never commit `data/`,
   `dist/`, `node_modules/`, `share/`, `codex/`.
6. Science wording: observed VIIRS / adjusted NOAA-20 / modeled MODIS stay distinct; weather is "associated with";
   season timing is a "central activity window"; detections are not burned area.

## 1. Decisions Sheikh made on 5 Nov (these override older card text)

| Topic | Decision |
|---|---|
| Language | **English-only.** Bangla was removed on purpose (commits `5d64738`, `7b4c6ff`). Remove every Bangla/bilingual claim. T22 and T34 become English-only. Keep `bn.json` and the Bengali font only if removing them breaks tests; never advertise them. |
| Licence | Apache-2.0, "the FireSense team". **Done** (T01, `c03cfae`, `a81f1dc`). |
| AI-use statement | **Do not write `docs/AI_USE.md`.** The team writes it (several AIs were used). |
| Pre-event rule | Sheikh is handling it. Don't raise it. |
| Render | Working. `RENDER_URL` is in `.env`. **H01 is done.** |
| Training | **H03 is done: the H02 run (`results/runs/20261104-211232-599349`) is the final training.** No more training runs. Every remaining card must work from the saved outputs in `data/processed/`. Science-code changes that need recomputation use non-fitting stages only (e.g. `ws3_anomaly.batch`), which Sheikh runs. |
| Cards | **Implement every remaining card. Cut nothing.** Reopen T26 (third region). |
| T33/T24 | `EARTHDATA_TOKEN` is now in `.env` (5 Nov). Go ahead. |
| Commits | Commit **and push** to `main` after each card or work package, one commit per folder owner (authors in `docs/plan/team.yaml`; `plan.py split --card <ID> -m "<ID>: …"` prints the commands). Add your tool's AI co-author trailer. Never force-push. Every push rebuilds Render. |

## 2. Work packages before the cards (not on the board; Sheikh asked for them directly)

### W1. Stale claims sweep (one commit, "docs: remove stale claims")
Fix each line below. Find more with:
`git ls-files -z | grep -z -v -e "^data/" -e public/demo -e contracts/fixtures -e docs/archive -e bn.json | xargs -0 grep -n -i -E "bilingual|bangla([^d]|$)|en/bn|draw any|any area|any region|draw an area"`

| File | Change |
|---|---|
| `README.md:3`, `:42` | Drop "bilingual (English / Bangla)"; say "English web app". |
| `docs/project/demo-script.md:10` | "Pick one of 11 calibrated areas in Bangladesh and Punjab–Haryana–Delhi." (no "draw any area") |
| `docs/project/demo-script.md:17` | Replace the বাংলা toggle step with the share link or the CSV export. |
| `ws5_frontend/README.md:3`, `ws5_frontend/index.html:6` | No "draw an area", no "any area you draw", no Bangla. |
| `docs/science/pipeline.md:5,48,51` | "for the named supported areas", not "any area a user draws"; drop Bangla/English. |
| `docs/plan/README.md:48,52` | Brief in English only; "a complete Bangla UI" → "a phone-ready English UI"; "any region by name" → "11 named regions". |
| `docs/project/tech-stack.md:22`, `qa-checklist.md:31`, `known-gaps.md:30` | English-only. |
| `docs/README.md:19` | Keep the method_bn link only if the file stays; label it "draft, not shown in the app". |
| `docs/science/area-selection.md:14` | Only if search still accepts Bangla names; otherwise remove. Check `ws5_frontend/src/lib` search code first. |

Card text to change to English-only (titles must match STATUS.md, then run `python scripts/plan.py board --fix` and
`python scripts/plan.py check`): **T22** (title "Planner brief (one printable page)", drop the Bangla render/PDF and
"Bangla overflows" stop rule), **T27** (the i18n parity test no longer requires bn keys; keep the hard-coded-string
lint), **T34** (title "Automated device and accessibility review"; drop step 6 Bangla completeness and the `#l=bn`
pass), **T29** (no Bangla in the video). Leave done cards (T08, T10, T12) as history.

### W2. One source for the record-end date
- Today: `ws5_frontend/src/config.ts:4` `RECORD_END = "2026-11-02"`, `deployment/runtime.json` `data_through:
  "2026-11-03"`, `README.md:5` and `ws5_frontend/src/i18n/en.json:3` say 2 November, `docs/guides/deployment.md:44,63,69`
  say 2026-11-02.
- Fix: the UI reads `data_through` from `/health` (live) or from the snapshot (static); keep `RECORD_END` only as a
  fallback. Make `hosting.snapshot` take `{{date}}`. Docs say "the `data_through` in `deployment/runtime.json`".
- Careful: "Suomi NPP data ended on 2 November 2026" (`method_en.md:24`, `data.md:64`) is a **different, correct**
  fact. Don't change it. The partial last week starts 2026-11-02 (T04); that is also correct.
- Done when: `npm test`, `npm run check:strings`, `npm run build` pass and the status card and date picker agree.

### W3. Out-of-date results numbers
- `docs/results/training-results.md:5` still says CCC 0.8855 / 0.8696. Current, from the same file line 17 and
  lines 68-69: **B1 0.8900, XGBoost CUDA 0.8775; 90% band coverage weekly 0.934, monthly 0.924.** Copy, don't retype.
- Same fix in `docs/plan/README.md:59,61`, `docs/plan/IMPROVEMENT_PLAN.md:10,13`, `docs/plan/tasks/T13_interval-report.md:19`.
- `docs/results/cuda-results.md:15,20` are history of the earlier run: add one line pointing at the coverage
  correction instead of editing the table.

### W4. FIRMS key redaction (`ws3_anomaly/ingest/firms.py`)
- The key is in the request URL; `requests` exceptions include the URL; it reaches `log.warning` and the returned
  `gaps` list.
- Fix: a `_redact(text, key)` helper that replaces the key with `***`; use it in `fetch_window` (the
  `RuntimeError` and re-raised `RequestException` message) and in `download` (log line and `gaps`). Raise a new
  `RuntimeError(_redact(str(e), key))` rather than the original exception.
- Test: a fake session whose `get` raises `requests.ConnectionError(f"...{url}...")`; assert the key appears in
  neither the log (caplog) nor `gaps`. Fits nothing, so it's agent-safe. T18 must reuse the helper.

### W5. Scientific wording and statistics (Step 4)
1. **Weather lag p-values: DONE by Claude on 5 Nov.** `ws3_anomaly/drivers.py` now uses a max-over-lags
   block-permutation p-value (`_assoc_over_lags`); decision 25 in `docs/science/decisions.md`; descriptions on
   `evidence` in `contracts/openapi.yaml` and `contracts/json_schemas/drivers_region.schema.json`; tests
   `test_lag_search_p_value_keeps_false_positives_near_nominal` and `test_shift_matches_pandas` in
   `ws3_anomaly/tests/test_anomaly.py`. The saved `drivers_region.json` still has the old p-values until Sheikh
   reruns `ws3_anomaly.batch` and publishes (section 4). Don't touch drivers.py again unless a test fails.
2. **Cropland wording**: `ws5_frontend/src/i18n/en.json:139-140` "Agricultural burning likely (…)" → "{{share}}% of
   detections in cropland areas" / "Cropland-associated (season rule)". Keep the API field names. Update tests that
   assert the old text and any method/caveat text that says "agricultural-likely".
3. **Why B1 was chosen**: add 3-4 sentences to the Method or Validation page source (`docs/science/method_en.md` and
   the matching validation text). Facts, copied from `docs/results/cuda-results.md:9` and `training-results.md`:
   XGBoost scored higher on Terra+Aqua (0.9438 vs 0.9417) and on most single holdouts, but its Terra-only spatial
   CCC was about 0.287 versus B1's 0.848, and the historical seam QA failed; the selection score was then changed to
   cover both input configurations, which B1 wins (0.8900 vs 0.8775). Say plainly that the rule changed after the
   first trial and why. Mark B1's Terra-only holdouts (0.80-0.84) as the lower-quality early record.

### W6. T17: run the Render check (now unblocked: H01 is done)
`python scripts/check_render.py` against `RENDER_URL` from `.env` (read it in code; never echo it). Record the result
on the card, set T17 done (or blocked with the failing line), commit, push. If it passes, keep-warm setup is in
`docs/guides/deployment.md:88-91`.

## 3. Then the cards, in `plan.py next` order

Loop: `git status --short` clean → `git pull --ff-only` → `python scripts/plan.py next` → `show` → do it → `checks
--run` → `set <ID> done --note "…"` → commit per owner → push.

| Card | Notes for this round |
|---|---|
| T13 | Interval report by stratum, measurement only from saved outputs. The card's "over 100 cells" sampler gap is the point; report under-covering strata honestly (e.g. cropland q3 0.890, forest q2 0.883 from the audit; re-read them from `data/processed/validation/intervals.json`). |
| T14, T15 | Season-level flags. T14 records the decision with documented defaults; T15 puts them in the season response and calendar. |
| T18 | NRT fetcher and cached `/live/season`, off without a key. Reuse W4's redaction. SNPP NRT is retired (`firms.py` `RETIRED`); use NOAA-20/21 NRT. |
| T19 | Verify T18 on Render (after T17). |
| T20 | Overpass blind-spot indicator (`ws3_anomaly.blindspot` is agent-safe: reads saved outputs, writes a new file). |
| T21 | Recurrence map. Also give the static snapshot a recurrence layer, so the public fallback shows "where". |
| T22 | Planner brief, **English only**, one printed page. |
| T23 | Story mode, 90 seconds, uses T12 share links. |
| T33, T24 | Only when `EARTHDATA_TOKEN` is in `.env`. MCD64A1 as a qualitative check of seasonality/recurrence; never convert detections to area. |
| T25 | FRP view, labelled uncalibrated across sensors. |
| T26 | **Reopened.** `python scripts/plan.py set T26 todo --note "reopened 5 Nov by Sheikh"`. Prepare the region (catalog, boundaries, ingest config, docs). **Problem to raise with Sheikh before coding:** a new region needs its own B1 ratios, which is a fit, and there is no more training. Ask him whether to (a) run one pipeline pass for the new region himself, or (b) ship it prepared but hidden. Never show it in the UI without harmonized output. |
| T27 | QA sweep, English-only parity (see W1). Snapshot budget: `public/demo/snapshot.json` is 6.97 MB against 1 MB; split per area and lazy-load. |
| T34 | Device and accessibility review at 360/390/1366 px, keyboard, Lighthouse. English only. Also test fast area/view switching for the Leaflet `_leaflet_pos` error (`MapView.tsx` cleanup; `m.stop()` before `m.remove()` if it shows). |
| H03 | **Done** (the H02 run is final). Nothing to wait for. |
| T28 | Do it **last among the code cards** (after T34). Before it, hand Sheikh the single command in section 4 so the drivers (and T14/T15 season flags, if they live in batch outputs) are recomputed, QA'd and published; then report the metrics from the saved outputs and tag `v1.0-event`. |
| T29, T35 | After T28. T29 takes numbers only from the final saved report. T35 includes the 13 Nov rules re-check. |

## 4. Hand-over format after each card

Measured (command, date, numbers) · Unit-tested (test names) · Estimated · Needs Sheikh (human checks, and whether section 5 must be rerun).

## 5. The one command Sheikh runs before T28 (give it to him as one paste, PowerShell)

Recomputes anomalies, critical periods and drivers from the saved outputs (no model fitting), re-runs QA, repacks
the runtime, and publishes it only if every step passes. `--data-through` must equal `data_through` in
`deployment/runtime.json` (2026-11-03 unless new data was added). Backups go in `results\runs\` (ignored by Git), never in
`data\processed\` (a QA test checks every file there).

```powershell
git pull --ff-only; Copy-Item data\processed\drivers_region.json results\runs\drivers_region.before.json -Force; .venv\Scripts\python -m ws3_anomaly.batch; if ($?) { .venv\Scripts\python scripts\workflow.py validate }; if ($?) { .venv\Scripts\python scripts\runtime_bundle.py pack }; if ($?) { .venv\Scripts\python scripts\release_runtime.py --data-through 2026-11-03 --publish }; if ($?) { git add deployment/runtime.json; git commit -m "Publish runtime with recomputed drivers"; git push }
```
