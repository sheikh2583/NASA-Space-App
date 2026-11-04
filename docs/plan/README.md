# FireSense win plan: operating manual

Goal: win NASA Space Apps 2026 (event 14-15 Nov, Bangladesh) with the MODIS + VIIRS burning-activity calendar.

This folder is the plan. The **coding agent** does everything it can, following the loop in section 3 exactly.
**Sheikh** does only five things:
- the two full training runs;
- creating the Hugging Face account and token;
- submitting on the Space Apps site;
- the event days.

The other team members are dormant for now. One tool answers "what next?": `python scripts/plan.py next`.

| File | What it is |
|---|---|
| `STATUS.md` | The board: one row per card, in work order. Only the Status and Note columns are edited, by hand or with `plan.py set`. Statuses: todo, doing, review, done, blocked, cut. |
| `tasks/<ID>_<slug>.md` | One card per piece of work. |
| `team.yaml` | People, commit authors, path ownership. |
| `AGENT_PROMPT.md` | The text to paste into the agentic IDE. |
| `../specs/` | Specs for changes to scientific outputs (I1 season profile, I8 coverage). |

Card kinds:
- **T (agent):** the coding agent does it end to end. This includes rules checks, FIRMS truth checks, outage
  verification, downloads with tokens from `.env`, GitHub secrets via `gh`, the QA review, slides and the video.
- **H (Sheikh):** H01 Hugging Face account and token, H02 and H03 full training runs, H04 submit, H05 event days.

**Decisions** that change scientific outputs are written by the agent with the documented defaults (T05 for outages,
T14 for season flags). Sheikh's merge of that pull request is the sign-off.

## 1. What the judges score, and how this plan answers it

| Criterion | Our answer | Cards |
|---|---|---|
| Influence | Punjab and Bangladesh crop-residue smoke; a printable brief in English and Bangla; any region by name; live season status during judging week | T08, T11, T19, T22 |
| Creativity | Season timing measured as a trend; the overpass blind-spot test; guided story mode | T07, T20, T23 |
| Validity | Verified outage handling and retraining; interval report by stratum; independent burned-area check; FIRMS truth checks | T31, T32, T05, T06, T40, T13, T24 |
| Relevance | A calendar for any selected area (hosted API with snapshot fallback); when burning happens; whether it is unusual | T07, T11, T15, T16, T17 |
| Presentation | Story mode, a 30-second video, 7 slides, a complete Bangla UI | T23, T34, T29, T35 |

Awards in reach: Best Use of Data, Best Use of Science, Local Impact, Best Storytelling.

## 2. Measured facts this plan builds on (4 Nov 2026)

**Training run** (`docs/TRAINING_RESULTS.md`):
- B1 selected, with mean held-out CCC 0.9417 against 0.9351 for LightGBM.
- Nominal 90% bands cover 91.6% weekly and 93.7% monthly.

**Season profile, from the public snapshot** (`python -m ws4_outlook.season_profile --area pb|bd`). These are the
demo areas, measured before the outage fix.

| Area and season | Typical window (p10-p90) | Timing trend since 2012 | Amount trend since 2012 |
|---|---|---|---|
| Punjab paddy | 21 Oct-12 Nov | 4.3 days per decade **later** (CI 1.0 to 6.6; 14 seasons) | 58% fewer per decade (CI 25 to 91%) |
| Punjab wheat | 1-18 May | no clear shift | no clear change |
| Bangladesh dry season | 26 Dec-2 Apr | no clear shift | 26% fewer per decade (CI 1 to 51%) |

**Live defects found while checking this plan** (each has a card):

| Defect | Card |
|---|---|
| The Punjab status card says "Normal" for a record-low week (percentile 0); Bangladesh says "High" for 3 detections against a typical 0 | T03 |
| The Validation page says "Built on SYNTHETIC data" under three pieces of the real run | T02 |
| The last week (2 Nov 2026) holds 1 day of data but is drawn as a full week | T04 |
| Suomi NPP was down on 3-6 Nov 2024; those days count as zeros, also inside the training ratios | T32, T05, T06, H02, T40 |
| The intervals sampler never draws areas over 100 cells, so large-area coverage is unmeasured | T13 |
| The FIRMS downloader can put the API key into error messages and logs | T18, before any CI use |

Punjab 2026 so far: 455 detections, against a typical 21,656 by the same date. Check this against the FIRMS API before
anyone repeats it (T31).

## 3. The loop (the agent does exactly this)

0. If `docs/plan/` doesn't exist yet, do card T00 first. Its steps are in `AGENT_PROMPT.md`.
1. `git switch main && git pull --ff-only`.
2. `python scripts/plan.py next`. Possible outputs:

   | Output | What to do |
   |---|---|
   | `NEXT <ID>` | Work on that card. |
   | `WAITING ON Sheikh` | Tell Sheikh what his card needs: one line, with the file path. Carry on with any `NEXT` card. |
   | `SKIPPED <ID>: needs …` (data, a secret in `.env`, `gh` login, a token) | Tell Sheikh once what is missing; carry on. |
   | `IN FLIGHT <ID>` | A branch for that card exists here and isn't merged yet; cards that need it wait. |
   | No `NEXT` card | Stop. Report what is waiting and on whom. |

3. `python scripts/plan.py show <ID>`. Read the whole card, then every file it names under Context and Steps,
   **before editing anything**.
4. `git switch -c <branch from the card>`.
5. Do the Steps in order:
   - Change only the paths in the card's `touches` and `creates`, plus `docs/plan/STATUS.md` for your own row.
   - If another file must change, stop and ask.
6. `python scripts/plan.py checks <ID> --run`. Every check must pass.
   - Never weaken, skip or delete a test to make it pass.
   - If a check fails twice for the same reason, stop and report the error.
7. `python scripts/plan.py set <ID> done --note "<one line>"`. The row reads `done` once the PR is merged; until then
   `next` shows the card as in flight.
8. `python scripts/plan.py split --card <ID> -m "<ID>: <summary>" --run`. This makes one commit per owner, with each
   owner's `--author`.
9. `python scripts/git/guard.py --range origin/main...HEAD --user sheikh2583 --branch <branch>` must print
   `guard: ok`.
10. `git push -u origin <branch>`, then open a PR titled `<ID>: <title>`. Write the description in four groups:
    - **Measured:** command, date, numbers;
    - **Unit-tested:** test names;
    - **Estimated;**
    - **Needs Sheikh** (only if something is left for him).

    Sheikh reviews and merges. The other team members are dormant; commits still carry the folder owner's name.
11. Go back to step 1.

**Merge conflicts.** Rebase on `main`.
- `STATUS.md`: keep both rows' changes.
- Generated files (`ws5_frontend/public/demo/*.json`, `contracts/fixtures/*.json`): take `main`'s version, re-run
  the command that generates them on the rebased branch, and commit.

## 4. Rules that never bend

- **Data and secrets.** Never commit `data/`, `.env`, models, logs, `node_modules`, `dist` or `share/`. Never print,
  log or commit a key or token: `FIRMS_MAP_KEY` and `HF_TOKEN` live only in `.env`, the shell or Actions secrets.
- **Three kinds of values.** Keep observed VIIRS, adjusted NOAA-20 and modeled MODIS distinct, in data, API and UI.
- **Wording.**
  - Weather is "associated with", never "caused".
  - The season window is a "central activity window", never the start or end of burning.
  - Detections are not burned area.
- **Changing scientific outputs** (numbers in `data/processed/`, the selected method, the bands) needs a spec, a
  contract line and a decision recorded in a pull request Sheikh merges (T05, T14). Retraining is Sheikh's manual
  step (H02, H03); the agent then re-reports the metrics on all six holdouts (T40, T28).
- **Snapshot mode.** Every user feature works on the static site, or shows a clear "needs the live service" state.
- **Tests.**
  - API tests use `tiny_api` / `tiny_request` (`ws2_platform/tests/conftest.py`).
  - Component tests use `renderHtml` / `textOf` (`ws5_frontend/src/test/render.tsx`).
  - Don't add test libraries or other dependencies without Sheikh's OK in the PR.
- **Text.** All UI text goes in `src/i18n/en.json` and `bn.json`, and `npm run check:strings` must pass. Bangla
  drafts are marked for review (H05).
- **Measured numbers** come from data at runtime, or are copied from `docs/TRAINING_RESULTS.md` with their source.
  Never type or round them by memory.
- **Basemap.** OpenStreetMap only. Never restore unauthenticated CARTO URLs.
- **Git.**
  - Never push to `main`, never force-push, never rewrite a merged commit.
  - The PR user is always sheikh2583, so branches start with `ws1/`.
  - Commit authors are the folder owners (`team.yaml`), and each owner reviews their part in the PR.

## 5. Card format

```
---
id: T07                      # T = agent, H = Sheikh; matches the file name T07_<slug>.md
title: …                     # must equal the Title column in STATUS.md
kind: agent                  # agent | human
owner: Sattyam               # accountable person (team.yaml)
authors: [Sattyam, Sheikh]   # agent cards: one commit each (plan.py split)
phase: P1                    # P0..P4; needs may not point to a later phase
size: M                      # S < 3 h, M 3-8 h, L > 8 h
needs: [T00]                 # cards that must be merged (done) first
requires: [real-data]        # real-data | secret:FIRMS_MAP_KEY | hf-token | earthdata-files | network
branch: ws1/T07-season-api   # agent cards
touches: [...]               # existing paths the card may edit (or paths created by a card it needs)
creates: [...]               # new paths; must not exist before the card runs
checks: [CHECK-PLAN, CHECK-PY, ...]   # named checks (section 6) or a literal python/npm/git command
---
## Goal / ## Context (optional) / ## Steps / ## Acceptance / ## Stop and ask if     (agent cards)
## Goal / ## Steps / ## Done when                                                  (human cards)
```

`python scripts/plan.py check` enforces all of this: links, cycles, phases, owners, branches, paths, and the board
columns. CI runs it through the tests.

## 6. Named checks

`python scripts/plan.py checks <ID> --run` runs these with the right interpreter and environment, on Windows too.

| Name | Command |
|---|---|
| CHECK-PLAN | `python scripts/plan.py check` |
| CHECK-PY | `python -m pytest -q` (the repository's test paths, including `scripts/tests`) |
| CHECK-WEB | `npm test`, `npm run check:strings`, `npm run build` (in `ws5_frontend`) |
| CHECK-SNAP | `npm run build` with `VITE_DEMO_MODE=snapshot` and `VITE_DATA_MODE=real` |
| CHECK-SMOKE | `python scripts/workflow.py smoke` |
| CHECK-QA | `python scripts/workflow.py validate` (real data) |
| CHECK-FILES | `python tools/verify_files.py --all` (every contracted file in `data/processed`; skips when there is no data) |
| CHECK-GUARD | the ownership guard for the current branch (step 9 of the loop) |

## 7. Timeline, freeze and cut order

| Dates | Phase | Exit gate |
|---|---|---|
| 4-6 Nov | P0 Truth | T00-T05, T30-T32 merged (rules, licence, truth checks, wording and label fixes, partial weeks, outage registry, audit and decision) |
| 6-9 Nov | P1 Core | T06 code, then **H02 Sheikh trains**, then T40 report. T07-T15: season profile and card, help, caveats, regions, links, interval report, season flags |
| 8-12 Nov | P2 Differentiators | Hosted API (T16, **H01 account**, T17); live feed (T18, T39, T19); blind spot (T20); recurrence (T21); brief (T22); story (T23); burned area (T33, T24); FRP (T25) |
| **12 Nov, 20:00 Dhaka** | **Feature freeze** | T27 automated QA, T34 device review, then **H03 Sheikh's final training**, then T28 tag v1.0-event |
| 13 Nov | P3 Present | T29 drafts, T35 slides and video plus the 2026 guide re-check, then **H04 Sheikh submits** |
| 14-15 Nov | P4 Event | **H05**: fixes only; submit by 18:00 on day 2 |

**Cut order** if late. Sheikh runs `python scripts/plan.py set <ID> cut`, and a cut card counts as finished:

| Order | Cut |
|---|---|
| 1 | T26 third region (already cut by default) |
| 2 | T25 FRP |
| 3 | T33 and T24 burned area |
| 4 | T22 brief |
| 5 | T21 recurrence |
| 6 | T19 live switch-on |
| 7 | T17 deploy (and H01); the snapshot carries the demo |
| 8 | T15 season flags UI |

**Never cut:** T00-T08, T10, T27, T28, T30-T32, T34, T35, T40 and the H cards.

**Critical path:** T00 → T32 → T05 → T06 → H02 → T40 → … → T34 → H03 → T28 → T29 → T35 → H04.
- Merge T32, T05 and T06 quickly, so that your first training run (H02) can happen by 7 Nov.
- Your final training (H03) must finish by 12 Nov, 20:00.
