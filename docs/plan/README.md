# FireSense execution plan

Updated 6 November 2026. The goal is a strong, honest submission to the MODIS/VIIRS harmonization challenge. A subjective 9/10 is an ambition, not a guaranteed score or an official judging threshold.

## 1. Source of truth

Read [AGENTS.md](../../AGENTS.md) first. Sheikh explicitly authorizes agent-operated training, calibration, fitting tests, probes and integrated QA. Preserve baselines and use attributable scientific runs; earlier no-training/H03-freeze instructions are superseded.

- [Executable scaffold](../project/hardening-scaffold.md): installed sequence, dependencies, gates, deferred scope and handover.
- [Challenge contract](CHALLENGE_CONTRACT.md): verified core outcomes C01-C06 and internal quality controls Q01-Q05; source-access limits are explicit.
- [STATUS.md](STATUS.md): actual card status and order.
- [tasks/](tasks/): exact file scope, prerequisites, commands and acceptance per card.
- [I13](../specs/I13_SCIENTIFIC_ACCEPTANCE.md): evaluation, leakage/support, conditional uncertainty and promotion.
- [Run specs](runs/): S01 harmonization, S02 outlook and S03 integration/release validation.
- [team.yaml](team.yaml): path ownership and commit authors; ownership does not imply delegated execution.
- [Dated review](../project/review-2026-11-06.md): historical measured evidence and the original rating, not fresh validation of later changes.

The application is English/live FastAPI plus React on one Render service with OSM tiles and a pinned runtime. Pages/snapshot/Bangla delivery is retired. No card may restore those paths merely because an older historical note mentions them.

## 2. Starting point and scope

This scaffold installation is planning work. It changes cards/docs/board, not application code, scientific artifacts or the measured score. T51 is the first new implementation card; T61 provides early user-study preparation.

`next` deliberately reads the committed board. Before the scaffold commit it may show no available card because
T51 is absent from that older board. A dry dependency projection is not execution; do not mark work done or
modify scheduler behavior to hide the pending commit.

Default scope: comparable historical record, regional selection, calendar/season/unusual-period exploration, recent-versus-history comparisons, export/brief, scientific evidence and verified delivery. NRT (T18/T19), speculative blind-spot attribution (T20) and FRP (T25) are deferred/cut with explicit reopening prerequisites.

H02/H03 remain historical completed runs. New numerical validation belongs to T52-T59 and their run specs. H06 supplies real user observations; H04/H05 remain submission/event tasks. The agent does not contact people automatically.

## 3. The loop

**Execution authorization update, 6 November:** Sheikh authorized the agent to auto-commit and push through this PC's configured SSH credentials. This supersedes the earlier manual Git handover. Commit the verified scaffold before ordinary card implementation. Preserve unrelated edits and the local codex/ folder; do not reset a dirty tree to make the loop proceed.

1. Check git status. Start a new card from the attributable committed state; synchronize only when safe for existing edits.
2. Run `python scripts/plan.py next`. `next --all` shows eligible cards. Dependencies count as complete only according to the committed board.
3. Run `python scripts/plan.py show <ID>`. Read the whole card and every named context/source/spec file before editing.
4. Change only its touches/creates plus its STATUS row. If actual code requires additional scope, update the card through the authorized plan workflow before changing unrelated paths.
5. Run `python scripts/plan.py checks <ID> --run` for routine checks. Never weaken/delete a test. If the same check fails twice, report the exact cause and unresolved scope rather than hide the failure.
6. Execute separately declared scientific validation under AGENTS.md, the card and run spec. Required fits are authorized; they are not incidental UI/doc checks.
7. Hand over changed behavior, challenge IDs, commands/results (including failures), source/run identity, dispositions, report paths and a suggested commit message.
8. Use review for incomplete review handovers; done means verified work is committed. Auto-commit only reviewed task paths with the configured identity and push through SSH. In explicitly requested PR flow, use the plan's ws1/<ID>-... branch, folder-owner split/guard and PR. Never force-push or rewrite pushed history.
9. Verify the push and continue with the next eligible card. Do not infer scientific acceptance from a done implementation row or deployment from a successful push.

WAITING ON Sheikh means a genuinely human task such as H06 observations or submission, not renewed training permission. SKIPPED requirements may mean unavailable data/authentication. Report the concrete missing item without printing secrets and continue independent eligible work.

## 4. Routine and scientific lanes

Current `plan.py` supports check/next/show/checks/board/set/split. Routine checks stay non-fitting and scan test files/conftest. Scientific preview/execution uses the explicit `--scientific` selector on show/checks.

T52 implements `python scripts/plan.py checks <ID> --scientific --run`. It executes only that card's declared scientific command list after plan/spec, committed-prerequisite, requirement, writer-lock and baseline checks. It does not rerun routine checks. Without `--run`, `checks --scientific` and `show --scientific` only preview commands and create no run/backup.

For compatibility, scientific commands live in the legacy human_checks field and need an existing relative Markdown scientific_spec with protocol sections. Older routine-only cards may retain legacy lists without a spec; scientific execution of such a card is refused until its protocol is declared. No additional training permission prompt is introduced.

Each owned run writes `results/runs/scientific-<timestamp>/scientific.json`, copied source/patch identity, raw input hashes, command logs and a fit log. Outputs are backed up under `data/runs/<run-id>/baseline` and checksummed before commands. An exclusive `results/.scientific-writer.lock` prevents a second cooperating writer; authenticated child workflows reuse it. Raw/source mutations or a changed protected backup reject successful completion; generated contract-fixture JSON is recorded separately. Direct workflow/pipeline CLIs use the same protection before fitting readiness probes. Low-level stage/library calls belong inside the declared lane.

An interrupted process may leave a lock. Inspect its PID/receipt and confirm no writer remains before deliberate recovery; never delete an active lock automatically. Failure reports/backups remain for diagnosis. A passed command batch still requires separate scientific-acceptance inspection.

| Lane | Examples | Execution conditions |
|---|---|---|
| Routine | CHECK-PLAN, reviewed pure pytest, CHECK-WEB, CHECK-FILES | Read execution paths; no fitting/probe/hidden stage |
| Scientific | Full pytest, CUDA readiness, training, calibration, outlook, integrated QA | Declared run spec, preserved baseline, source/input/config record, output identity and honest evaluation |
| Human evidence/action | Participant contact/observation, organizer decisions, submission | Sheikh's actual action/evidence; no agent simulation |

Named checks and literal-command eligibility remain defined in scripts/plan.py. CHECK-PY, CHECK-SMOKE and CHECK-QA remain outside the ordinary lane. Smoke is not an automatic extra fit; run it only for a declared unresolved integration concern.

## 5. Card format

```yaml
---
id: T56
title: ...
kind: agent
owner: Sheikh
authors: [Sheikh, Samin]
phase: P1
size: L
needs: [T55, T57]
requires: [real-data]
branch: ws1/T56-scientific-comparison
touches: [...]
creates: [...]
checks: [CHECK-PLAN, CHECK-FILES]
human_checks: ["python scripts/workflow.py train --backend cuda", CHECK-QA]
scientific_spec: docs/plan/runs/S01_harmonization.md
---
```

Agent bodies contain Goal, Steps, Acceptance, Stop and ask if; Context is recommended. Human cards use Goal, Steps, Done when. The actual T56 contains its complete commands/spec, not the abbreviated example.

Scope paths must exist or be created by an ancestor; creates paths are unique and absent for todo cards. Authors include every path owner. Phase dependencies point only to the same/earlier phase. Preserve schema compatibility, branch and owner rules.

`python scripts/plan.py check` validates card/board/path/cycle structure. It does not execute fits or certify scientific results. `board --fix` regenerates structural columns while keeping statuses/notes. No general CI test workflow currently exists; record checks where actually run.

## 6. Scientific and release gates

- Freeze hypotheses, roles, targets and acceptance criteria before candidate fitting. Keep inspected tests distinct from uninspected confirmation.
- Preserve baseline/raw inputs and one-writer execution. Record source/patch, configuration, seeds, hardware, commands, hashes, attempted failures and every required holdout/combo.
- Diagnose conditional failures before selecting at most two registered interval repairs. Do not tune on a test set or force the learned candidate to beat B1.
- Preserve the existing severe-failure rule and report positive activity/zero prediction, width, score, support and dependence. Overall coverage is insufficient.
- New monthly evidence must match served calendar-month daily allocation. Unsupported AOIs/groups are not accepted by extrapolation.
- Separate engineering pass, scientific support and observed live delivery. A work card can finish with an honest limited/failure disposition; that is not a passed science gate.
- Publish only a new immutable runtime asset. After the intended commit is pushed, check_render.py plus served runtime/target/hash/status inspection and the browser journey establish delivery. Never infer the host cause from a mismatch alone.

Exact criteria and candidate limits are in I13 and the frozen run appendix. Unknown resources/rules stay verification items. Any changed scientific output needs the card/spec/contract decision through Sheikh's normal commit/review flow.

## 7. Product, evidence and safety conventions

Keep observed VIIRS, adjusted NOAA-20 and modeled MODIS distinct. Detections are not burned area or distinct fires. Weather is association. Season timing is a central activity window. Sensitivity scenarios are not calibrated seasonal intervals.

API regressions use tiny_api/tiny_request; component tests use renderHtml/textOf and current fixture data. Add dependencies only with Sheikh's approval. Preserve current English strings and OSM basemap; FIRMS credentials stay server-side.

Never print/log/commit tokens or .env. Keep raw data, models, run outputs/logs, node_modules, dist and share outside Git. Generated screenshots/media stay in ignored output directories; committed reports point to their attributable evidence.

## 8. Capacity, cuts and score

Use gate-based milestones and measure actual scientific-cycle cost. The earlier hour estimates predated training authorization and cannot guarantee the expanded schedule. Current format/deadline checks belong to T35; older internal dates are not a new official deadline.

A cut records deliberate omission and limitations; it does not turn an unperformed user/scientific check into a success. If a dependency is cut, downstream claims must adapt. Final reassessment T63 retains deductions for missing support, central uncertainty failures or absent intended-user evidence.

The best submission is a coherent, evidenced solution to the challenge. More features, models, test counts or completed cards alone do not establish a 9/10.
