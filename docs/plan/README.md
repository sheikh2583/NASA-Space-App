# FireSense win plan: operating manual

Goal: win NASA Space Apps 2026 (event 14-15 Nov, Bangladesh) with the MODIS + VIIRS burning-activity calendar.

This folder is the plan. The **coding agent** does everything it can, following the loop in section 3 exactly,
always under the **strict no-training policy in `AGENTS.md`**. The agent never runs training, model fitting, CUDA
probes, readiness checks, blanket pytest, smoke or QA.

**Sheikh** does only these things:
- the two full training runs (`scripts/train.ps1 -Pack` / `scripts/train.sh --pack`), each with its human-only
  checks;
- confirming the Render service and putting the FIRMS key into its environment;
- submitting on the Space Apps site;
- the event days;
- committing and pushing.

The other team members are dormant for now. One tool answers "what next?": `python scripts/plan.py next`.

**Hosting** is one free Render Docker service (`docs/guides/deployment.md`). It builds the UI and serves the live FastAPI from one
origin, with data from a pinned GitHub Release (`deployment/runtime.json`). Every push to `main` rebuilds it, and it
never trains. GitHub Pages is legacy and manual-only. `snapshot.json` and CHECK-SNAP keep that fallback working.

| File | What it is |
|---|---|
| `STATUS.md` | The board: one row per card, in work order. Only the Status and Note columns are edited, by hand or with `plan.py set`. Statuses: todo, doing, review, done, blocked, cut. |
| `tasks/<ID>_<slug>.md` | One card per piece of work. |
| `team.yaml` | People, commit authors, path ownership. |
| `AGENT_PROMPT.md` | The text to paste into the agentic IDE. |
| `../specs/` | Specs for changes to scientific outputs (I1 season profile, I8 coverage). |

Card kinds:
- **T (agent):** the coding agent does it end to end. This includes rules checks, FIRMS truth checks, outage
  verification, downloads with tokens from `.env`, Render data releases via `gh`, the device review, slides and the
  video. Retired cards (T11, T39) stay on the board as `cut`.
- **H (Sheikh):**
  - H01: confirm the Render service and add the FIRMS key there;
  - H02 and H03: full training runs, plus the batched human-only checks;
  - H04: submit;
  - H05: event days.

**Decisions** that change scientific outputs are written by the agent with the documented defaults (T05 for outages,
T14 for season flags). Sheikh's commit of that card is the sign-off.

## 1. What the judges score, and how this plan answers it

| Criterion | Our answer | Cards |
|---|---|---|
| Influence | Punjab and Bangladesh crop-residue smoke; a printable brief in English and Bangla; any region by name; live season status during judging week | T08, T11, T19, T22 |
| Creativity | Season timing measured as a trend; the overpass blind-spot test; guided story mode | T07, T20, T23 |
| Validity | Verified outage handling and retraining; interval report by stratum; independent burned-area check; FIRMS truth checks | T31, T32, T05, T06, T40, T13, T24 |
| Relevance | A calendar for any named division or state, live on Render; when burning happens; whether it is unusual | T07, T15, T16, T17, T18 |
| Presentation | Story mode, a 30-second video, 7 slides, a complete Bangla UI | T23, T34, T29, T35 |

Awards in reach: Best Use of Data, Best Use of Science, Local Impact, Best Storytelling.

## 2. Measured facts this plan builds on (4 Nov 2026)

**Training run.** Copied from the files named; never retype these from memory.
- `docs/results/training-results.md`: "Current selected harmonization: **B1**, with selection CCC 0.8855 versus XGBoost CUDA
  0.8696 across Terra+Aqua and Terra-only holdouts. All five scientific QA groups passed."
- `docs/results/cuda-results.md`: "Nominal 90% interval coverage is 91.6% weekly and 93.7% monthly."

**Season profile, from the snapshot on `main`** (`python -m ws4_outlook.season_profile --area pb|bd`; re-measured on
4 Nov after the CUDA run, with the same results). These are the demo areas, before the outage fix.

| Area and season | Typical window (p10-p90) | Timing trend since 2012 | Amount trend since 2012 |
|---|---|---|---|
| Punjab paddy | 21 Oct-12 Nov | 4.3 days per decade **later** (CI 1.0 to 6.6; 14 seasons) | 58% fewer per decade (CI 25 to 91%) |
| Punjab wheat | 1-18 May | no clear shift | no clear change |
| Bangladesh dry season | 26 Dec-2 Apr | no clear shift | 26% fewer per decade (CI 1 to 51%) |

**Live defects found while checking this plan** (each has a card):

| Defect | Card |
|---|---|
| The Punjab status card says "Normal" for a record-low week (percentile 0); Bangladesh says "High" for 3 detections against a typical 0 | T03 |
| The Validation page said "Built on SYNTHETIC data" under three pieces of the real run. The source is fixed on `main` (`piece()`, `bf800af`); T02 confirms the saved outputs are clean | T02 |
| The last week (2 Nov 2026) holds 1 day of data but is drawn as a full week | T04 |
| Suomi NPP was down on 3-6 Nov 2024; those days count as zeros, also inside the training ratios | T32, T05, T06, H02, T40 |
| The intervals sampler never draws areas over 100 cells, so large-area coverage is unmeasured | T13 |
| The FIRMS downloader can put the API key into error messages and logs | T18, before any server-side use |

Punjab 2026 so far: 455 detections, against a typical 21,656 by the same date. Check this against the FIRMS API before
anyone repeats it (T31).

## 3. The loop (the agent does exactly this)

**Commit flow.** Sheikh commits and pushes to `main` himself; that is the default.
- **Default (Sheikh commits):** the agent works on `main` in the working tree, finishes the card, and hands over: what
  changed, the checks and the commit message to use. Then it **stops** until Sheikh has committed. The next card needs
  a clean tree.
- **Pull-request flow (only when Sheikh asks for it):** a branch `ws1/<ID>-…`, `plan.py split` (one commit per folder
  owner, with that owner's `--author`), the ownership guard, a push of the branch, and a PR that Sheikh merges.
- In both: never force-push, and never push to `main` yourself.

Where a card says "`split`, push and open the PR", or "paste … into the PR", it means the finish step of the flow in
use. In the default flow, that is the hand-over.

1. `git status --short` must print nothing. Then `git switch main && git pull --ff-only`.
2. `python scripts/plan.py next`. Possible outputs:

   | Output | What to do |
   |---|---|
   | `NEXT <ID>` | Work on that card. |
   | `WAITING ON Sheikh` | Tell Sheikh what his card needs: one line, with the file path. Carry on with any `NEXT` card. |
   | `SKIPPED <ID>: needs …` (data, a secret or `RENDER_URL` in `.env`, `gh` login) | Tell Sheikh once what is missing; carry on. |
   | `IN FLIGHT <ID>` | A `ws1/` branch for that card exists here and isn't merged yet; cards that need it wait. |
   | No `NEXT` card | Stop. Report what is waiting and on whom. |

3. `python scripts/plan.py show <ID>`. Read the whole card, then every file it names under Context and Steps,
   **before editing anything**.
4. Pull-request flow only: `git switch -c <branch from the card>`.
5. Do the Steps in order:
   - Change only the paths in the card's `touches` and `creates`, plus `docs/plan/STATUS.md` for your own row.
   - If another file must change, stop and ask.
   - A step that is a pipeline stage (`python -m <package>.run …`, `ws2_platform.sensors`), `workflow.py validate`,
     or any training is **Sheikh's**, even when an older card says "on the laptop, run …". Don't run it; list it
     under "Needs Sheikh". Standalone analyses that only read saved outputs and write a new file are agent work
     (`ws2_platform.coverage`, `ws3_anomaly.blindspot`, `ws6_validation.mcd64`, `ws6_validation.truth_checks`,
     `export_hosted_demo.py`, `export_area_catalog.py`, `release_runtime.py`).
6. `python scripts/plan.py checks <ID> --run`. It runs only the card's agent-safe `checks` and refuses anything else.
   Every one must pass.
   - Never weaken, skip or delete a test to make it pass.
   - If a check fails twice for the same reason, stop and report the error.
   - It ends by printing the card's `human_checks` as "Sheikh runs: …". Put those under "Needs Sheikh". Sheikh runs
     them in a batch with his next training run (H02, H03), unless he asks for them sooner.
7. `python scripts/plan.py set <ID> done --note "<one line>"`. A card counts as done once that row is committed on
   `main`.
8. Finish the card:
   - **Default:** hand over in four groups:
     - **Measured:** command, date, numbers;
     - **Unit-tested:** test names;
     - **Estimated;**
     - **Needs Sheikh:** human checks, anything else.

     Add the suggested commit message `<ID>: <summary>`, then stop.
   - **Pull-request flow:**
     - `python scripts/plan.py split --card <ID> -m "<ID>: <summary>" --run`;
     - `python scripts/git/guard.py --range origin/main...HEAD --user sheikh2583 --branch <branch>` must print
       `guard: ok`;
     - `git push -u origin <branch>`, then open a PR titled `<ID>: <title>` with the same four groups.
9. When Sheikh says it's committed, go back to step 1.

**Merge conflicts** (pull-request flow). Rebase on `main`.
- `STATUS.md`: keep both rows' changes.
- Generated files (`ws5_frontend/public/demo/*.json`, `contracts/fixtures/*.json`): take `main`'s version, re-run the
  command that generates them on the rebased branch, and commit.

## 4. Rules that never bend

- **No training by agents** (`AGENTS.md`). This rule comes first and overrides any card.
  - No `workflow.py` train, all, smoke, test, prepare, gpu-check or validate.
  - No pipeline stages, CUDA probes or blanket pytest.
  - No test that fits a learner.

  `plan.py check` and `plan.py checks --run` enforce this for card checks (section 6).
- **Data and secrets.** Never commit `data/`, `.env`, models, logs, `node_modules`, `dist` or `share/`. Never print,
  log or commit a key or token. `FIRMS_MAP_KEY` lives only in `.env` and in Render's environment; `EARTHDATA_TOKEN`
  only in `.env`.
- **Three kinds of values.** Keep observed VIIRS, adjusted NOAA-20 and modeled MODIS distinct, in data, API and UI.
- **Wording.**
  - Weather is "associated with", never "caused".
  - The season window is a "central activity window", never the start or end of burning.
  - Detections are not burned area.
- **Changing scientific outputs** (numbers in `data/processed/`, the selected method, the bands) needs, in order:
  - a spec;
  - a contract line;
  - a decision recorded in a card that Sheikh commits (T05, T14).

  All training, quick or full, is Sheikh's manual step (H02, H03, with `scripts/train.ps1` / `train.sh`). The agent
  then re-reports the metrics on every holdout, from the saved outputs (T40, T28).
- **Hosting.** Render serves the live UI and API. Every user feature works there. In the legacy snapshot build it
  works too, or shows a clear "needs the live service" state. New data reaches Render only through a new runtime
  release (`scripts/release_runtime.py`, T16), never by replacing an existing release asset.
- **Tests.**
  - API tests use `tiny_api` / `tiny_request` (`ws2_platform/tests/conftest.py`).
  - Component tests use `renderHtml` / `textOf` (`ws5_frontend/src/test/render.tsx`).
  - New Python tests must fit nothing, so that `checks --run` accepts them. It scans each test file and its
    `conftest.py` first.
  - Don't add test libraries or other dependencies without Sheikh's OK.
- **Text.** All UI text goes in `src/i18n/en.json` and `bn.json`, and `npm run check:strings` must pass. Bangla
  drafts are marked for review (H05).
- **Measured numbers** come from data at runtime, or are copied from `docs/results/training-results.md` with their source.
  Never type or round them by memory.
- **Basemap.** OpenStreetMap only. Never restore unauthenticated CARTO URLs.
- **Git.**
  - Sheikh commits and pushes to `main`. The agent never pushes to `main`, never force-pushes, and never rewrites a
    pushed commit.
  - In the pull-request flow, the PR user is sheikh2583, so branches start with `ws1/`. Commit authors are the folder
    owners (`team.yaml`).

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
requires: [real-data]        # real-data | secret:<NAME> | env:RENDER_URL | gh-auth | earthdata-files | network
branch: ws1/T07-season-api   # agent cards
touches: [...]               # existing paths the card may edit (or paths created by a card it needs)
creates: [...]               # new paths; must not exist before the card runs
checks: [CHECK-PLAN, "python -m pytest -q <reviewed test files>", ...]   # agent-safe only (section 6)
human_checks: [CHECK-PY]     # optional: printed for Sheikh, never run by the agent
---
## Goal / ## Context (optional) / ## Steps / ## Acceptance / ## Stop and ask if     (agent cards)
## Goal / ## Steps / ## Done when                                                  (human cards)
```

`python scripts/plan.py check` enforces all of this: links, cycles, phases, owners, branches, paths, and the board
columns. CI runs it through the tests.

## 6. Named checks

`python scripts/plan.py checks <ID> --run` runs a card's `checks` with the right interpreter and environment, on
Windows too.

**Agent-safe.** These may appear in `checks`:

| Name | Command |
|---|---|
| CHECK-PLAN | `python scripts/plan.py check` |
| CHECK-TESTS | `python -m pytest -q` on the reviewed non-fitting test files (`SAFE_TESTS` in `scripts/plan.py`) |
| CHECK-WEB | `npm test`, `npm run check:strings`, `npm run build` (in `ws5_frontend`), with the Render image's settings (`VITE_API_BASE_URL=/`, `VITE_DEMO_MODE=live`, `VITE_DATA_MODE=real`) |
| CHECK-SNAP | `npm run build` with `VITE_DEMO_MODE=snapshot` and `VITE_DATA_MODE=real` (the legacy Pages fallback) |
| CHECK-FILES | `python tools/verify_files.py --all` (reads every contracted file in `data/processed`; skips when there is no data) |
| CHECK-GUARD | the ownership guard for the current branch (pull-request flow) |

A literal command in `checks` must also be agent-safe:
- `python -m pytest -q <files>` naming files only (no folders, no `-k`), each either in `SAFE_TESTS` or created by
  this card or a card it needs;
- `npm`, `npx` and `git` commands;
- `python` scripts and modules other than pipeline stages (`*.run`), `ws1_harmonize`, `ws6_validation.qa`,
  `run_pipeline.py`, `prepare_training.py`, `smoke.py`, `teammate.py`, `bootstrap.py` and `results.py`;
- `workflow.py build`, `share` or `dev`.

Before running pytest, `checks --run` scans each test file, and every `conftest.py` it loads, for fitting code. If it
finds any, it refuses, and Sheikh must review the file.

**Human-only.** These go in `human_checks`. Sheikh runs them, batched, in H02 and H03:

| Name | Command | Why it is human-only |
|---|---|---|
| CHECK-PY | `python -m pytest -q` | the whole suite includes tests that fit learners (`ws1_harmonize/tests`) and CUDA entry-point tests |
| CHECK-SMOKE | `python scripts/workflow.py smoke` | runs a training workflow |
| CHECK-QA | `python scripts/workflow.py validate` | runs whole test folders and rewrites `data/processed/validation/qa.json` |

To review a new test file and make it reusable by every card, add it to `SAFE_TESTS` in `scripts/plan.py`, with
Sheikh's OK.

## 7. Timeline, freeze and cut order

| Dates | Phase | Exit gate |
|---|---|---|
| 4-6 Nov | P0 Truth | T00-T05 and T30-T32 committed: rules, licence, truth checks, wording, label check, partial weeks, outage registry, audit and decision. **H01:** Sheikh confirms Render and adds the FIRMS key |
| 6-9 Nov | P1 Core | T06 code, then **H02: Sheikh trains**, then T40 reports and publishes to Render (with T16's release tool). T17 verifies Render. T07-T15: season profile and card, help, caveats, links, interval report, season flags (T11 retired) |
| 8-12 Nov | P2 Differentiators | Live feed on Render (T18, T19; T39 retired); blind spot (T20); recurrence (T21); brief (T22); story (T23); burned area (T33, T24); FRP (T25) |
| **12 Nov, 20:00 Dhaka** | **Feature freeze** | T27 automated QA, T34 device review, then **H03: Sheikh's final training and human checks**, then T28 publishes and tags v1.0-event |
| 13 Nov | P3 Present | T29 drafts; T35 slides and video, plus the 2026 guide re-check; then **H04: Sheikh submits** |
| 14-15 Nov | P4 Event | **H05**: fixes only; submit by 18:00 on day 2 |

**Cut order** if late. Sheikh runs `python scripts/plan.py set <ID> cut`, and a cut card counts as finished:

| Order | Cut |
|---|---|
| 1 | T26 third region (already cut by default) |
| 2 | T25 FRP |
| 3 | T33 and T24 burned area |
| 4 | T22 brief |
| 5 | T21 recurrence |
| 6 | T19 and T18 live feed (Render keeps serving the pinned record) |
| 7 | T15 season flags UI |

**Never cut:** T00-T08, T10, T16, T17, T27, T28, T30-T32, T34, T35, T40 and the H cards. **Already cut:** T11, T39.

**Critical path:** T00 → T32 → T05 → T06 → H02 → T40 → … → T34 → H03 → T28 → T29 → T35 → H04.
- Commit T32, T05 and T06 quickly, so that the first training run (H02) can happen by 7 Nov. T16 must be committed
  before T40.
- The final training (H03) must finish by 12 Nov, 20:00.
