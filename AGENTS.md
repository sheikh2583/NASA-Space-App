# Coding-agent policy

Applies to every coding agent working in this repository, including Codex, Claude, other assistants, and delegated agents. Read this before following task templates or workflow instructions elsewhere in the repository.

## Agent-operated training authorization — 6 November 2026

**Sheikh explicitly replaced the no-training policy:** "I give you full reign on training, update and override, now how about that". Agents may implement, train, fit, recalibrate, evaluate and regenerate scientific artifacts as needed for the project roadmap. This supersedes earlier no-training instructions, human-only execution labels and the H03 no-more-training freeze. Do not ask again for permission already granted here.

The authorization includes quick/full/resumed training, B1 and NOAA-20 ratios, learned candidates, drift/outlook fits, interval calibration, readiness/CUDA probes, setup paths that fit, fitting tests, blanket pytest, smoke and integrated QA. Inspect execution paths and use the project's supported CUDA configuration; authorization does not require changing CPU/CUDA implementation constraints.

Use an explicit scientific-run card or run specification: hypothesis, inputs, fit/calibration/selection/test roles, configuration, acceptance criteria and output locations. Diagnose known failures before choosing a repair. Routine card checks remain non-fitting so ordinary UI/documentation work cannot unexpectedly start training.

- Preserve existing validated outputs and raw inputs. Use fresh run directories or verified backups before a runner replaces shared output paths; run only one scientific pipeline per checkout/output tree at a time.
- Record source revision plus any uncommitted patch, input/artifact hashes, seeds, configuration, environment/device, commands, logs and all relevant holdout results. Keep attempted and failed runs attributable.
- Keep fitting, calibration, selection and evaluation separated. Do not tune on an inspected test set and call it untouched confirmation. Keep B1 eligible; do not force the learned candidate to win.
- A successful CUDA fit or engineering QA result is not scientific acceptance. Preserve stop conditions, disclose conditional failures and keep unsupported forecast alerts off.
- Publication uses a new immutable runtime release only after its evidence is reviewed. Never overwrite an existing release asset or claim a deploy from a push alone.
- This authorizes scientific execution, not secret disclosure, destructive cleanup, unrequested paid/cloud jobs, participant outreach or changes to the established Git flow.

See [the authorization record](docs/project/training-authorization.md) for precedence and integration with the legacy plan runner.

## Permitted coding work

- Edit and review pipeline/model code, requirements, scripts, tests, UI, and documentation.
- Inspect existing datasets, saved models, validation metrics, logs and reports; generate new scientific artifacts through the documented run workflow above.
- Run static checks, compilation, dependency checks, frontend checks, reviewed tests and planned scientific validation, including fitting where needed.
- Serve, query, package, and deploy the API/UI using existing validated processed artifacts, after checking that startup/request/build paths do not train. Hosting does not require retraining.
- Prepare and execute reproducible training and validation commands; distinguish routine checks from scientific runs and genuinely human tasks such as user interviews.

When a code change needs numerical validation, perform the planned fitting/evaluation and report actual results and limitations. If execution is unavailable, state the specific blocker and what was not run. Never invent new scores or present historical results as validation of changed code.

Preserve unrelated user edits and the local `codex/` proposal folder. Keep credentials, raw downloads, trained models, and generated run artifacts outside Git; never print secrets. See `CLAUDE.md` for scientific and project conventions, subject to this policy.

## Work plan

1. **What to do next** comes from the plan, not from you. Run `python scripts/plan.py next`, then follow
   `docs/plan/README.md` section 3 ("The loop"). Read the card in full (`python scripts/plan.py show <ID>`) and
   every file it names before editing anything.
2. **Scope.** Change only the paths in the card's `touches` and `creates`, plus your own row in
   `docs/plan/STATUS.md`. If anything else must change, or the code differs from what the card says, stop and ask.
3. **Checks.** Never weaken, skip or delete a test.
   - A card's `checks` hold only agent-safe checks. `python scripts/plan.py check` rejects anything else, and
     `python scripts/plan.py checks <ID> --run` refuses it again at run time. It also scans each test file, and the
     `conftest.py` files it loads, for fitting code first.
   - Scientific checks (`CHECK-PY`: blanket pytest; `CHECK-SMOKE`; `CHECK-QA`: `workflow.py validate`) remain in
     the legacy `human_checks` field. The helper's "Sheikh runs" label is historical; agents may execute these
     commands as a separate documented scientific run after reviewing side effects and preserving the baseline.
   - A refusal from the routine check runner is not permission to hide fitting in ordinary checks. Review/classify
     the command and record it in the scientific-run spec, or repair the guard/card if its classification is wrong.
     Never weaken a scientific assertion merely to make a command pass.
4. **Commits.** Sheikh explicitly authorized automatic commits and pushes on 6 November 2026: "auto commit push
   using my credentials in the ssh in this pc". Commit verified scaffold/card changes and push through the configured
   local SSH authentication to the existing repository. Use the configured Git identity; do not claim unperformed
   human reviews. This supersedes earlier instructions reserving every commit/push for Sheikh.
   - Preserve unrelated edits, stage only reviewed task paths, verify checks before committing and use normal
     fast-forward pushes. Stop/report a real authentication or remote-history conflict rather than overwrite it.
   - When asked to use the plan's commit flow, `python scripts/plan.py split --card <ID> -m "<ID>: …" --run` makes
     one commit per folder owner, with that owner's `--author` (`docs/plan/team.yaml`).
   - Never force-push.
5. **Secrets and data.** Never print, log or commit `FIRMS_MAP_KEY`, `EARTHDATA_TOKEN` or `.env`. Never commit `data/`,
   models, `dist/`, `node_modules/` or `share/`.
6. **Science.**
   - Keep observed VIIRS, adjusted NOAA-20 and modeled MODIS distinct.
   - Weather is an association, never a cause.
   - Season timing is a "central activity window", not the start or end of burning.
   - Detections are not burned area.
   - Changing scientific outputs needs the card's spec, a contract line, and a decision in a pull request Sheikh
     merges.
   - Agents may execute training, pipeline stages and `workflow.py validate` under the run policy above. H02/H03
     remain historical completed runs; new validation belongs to new scientific-run cards. Re-report metrics on
     every holdout from the new saved outputs, including failed acceptance criteria.
7. **Numbers.** Measured numbers come from data at runtime or from `docs/results/training-results.md`, with their source.
   Never from memory.
8. **Tests.**
   - API tests use `tiny_api` / `tiny_request` (`ws2_platform/tests/conftest.py`), so they run in CI without data.
   - UI component tests use `renderHtml` / `textOf` (`ws5_frontend/src/test/render.tsx`).
   - Don't add dependencies without the lead's OK.
9. **Hosting.**
   - Render serves the UI and the live API (`docs/guides/deployment.md`). New data reaches it only as a new runtime
     release (`scripts/release_runtime.py`, card T16), never by replacing an existing release asset.
   - Don't claim a deploy is live without `python scripts/check_render.py` (card T17).
   - The basemap is OpenStreetMap; never restore CARTO URLs.
   - The FIRMS key never goes to the browser.
