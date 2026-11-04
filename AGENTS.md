# Coding-agent policy

Applies to every coding agent working in this repository, including Codex, Claude, other assistants, and delegated agents. Read this before following task templates or workflow instructions elsewhere in the repository.

## Strict no-training rule

**Coding agents must never execute model training or model fitting. Training is human-operated only.** This includes CPU and CUDA, real and synthetic data, quick and full runs, resumed stages, tiny probes, reference learners, and benchmarks.

- Do not execute `workflow.py train`, `workflow.py all`, `run_pipeline.py`, direct model/drift/outlook training stages, or library fitting/training calls.
- Do not execute `gpu-check`, `compute.probe_cuda()`, or readiness commands (`prepare`, `prepare_training.py`): their verification fits models.
- Do not run default or training-only setup scripts: they automatically run fitting probes. UI-only setup or dependency installation without probes is allowed after inspecting its execution path.
- Do not run blanket Python tests, `smoke`, or `workflow.py test`: some tests fit learners. Run only individually reviewed checks that perform no fitting, including fixtures and imported setup code.
- Do not start training indirectly through a launcher, subprocess, notebook, container entrypoint, remote service, scheduled job, CI dispatch, or another agent. Do not use a code push as a way to obtain training execution or metrics.
- Do not create, overwrite, or regenerate trained models, calibration fits, model-selection results, or scientific training outputs as part of coding work.

There is no automatic exception for validation, smoke testing, a small dataset, a fast run, or an available GPU. Earlier training permissions and old task templates do not override this policy. Generic requests to continue, fix, test, initialize, or deploy do not authorize training. Only a direct, explicit change to this policy by the user can change it; do not repeatedly ask for a training exception.

## Permitted coding work

- Edit and review pipeline/model code, requirements, scripts, tests, UI, and documentation without executing fits.
- Inspect existing datasets, saved models, validation metrics, logs, and run reports without modifying scientific artifacts.
- Run static checks, compilation, dependency checks, frontend checks, and individually reviewed tests that do not fit models.
- Serve, query, package, and deploy the API/UI using existing validated processed artifacts, after checking that startup/request/build paths do not train. Hosting does not require retraining.
- Prepare training commands and documentation for a human to run manually. Clearly label them human-only.

If a code change needs numerical validation that requires fitting, finish the permitted implementation and static checks, provide the manual validation commands, and explicitly report that training validation was not run. Never invent new scores or present historical results as validation of changed code.

Preserve unrelated user edits and the local `codex/` proposal folder. Keep credentials, raw downloads, trained models, and generated run artifacts outside Git; never print secrets. See `CLAUDE.md` for scientific and project conventions, subject to this policy.

## Work plan (subject to the no-training rule above)

1. **What to do next** comes from the plan, not from you. Run `python scripts/plan.py next`, then follow
   `docs/plan/README.md` section 3 ("The loop"). Read the card in full (`python scripts/plan.py show <ID>`) and
   every file it names before editing anything.
2. **Scope.** Change only the paths in the card's `touches` and `creates`, plus your own row in
   `docs/plan/STATUS.md`. If anything else must change, or the code differs from what the card says, stop and ask.
3. **Checks.** Never weaken, skip or delete a test.
   - **Don't run `CHECK-PY` (blanket `pytest`) or `CHECK-SMOKE` (`workflow.py smoke`).** Some of those tests fit
     learners.
   - **Don't run `plan.py checks <ID> --run` if the card lists either one.** Run `python scripts/plan.py checks <ID>`
     without `--run` to see the commands, run only the individually reviewed non-fitting ones, and list the rest
     for Sheikh to run.
4. **Commits.** Follow Sheikh's instructions for the task. Sheikh normally commits and pushes himself.
   - When asked to use the plan's commit flow, `python scripts/plan.py split --card <ID> -m "<ID>: …" --run` makes
     one commit per folder owner, with that owner's `--author` (`docs/plan/team.yaml`).
   - Never force-push.
5. **Secrets and data.** Never print, log or commit `FIRMS_MAP_KEY`, `HF_TOKEN` or `.env`. Never commit `data/`,
   models, `dist/`, `node_modules/` or `share/`.
6. **Science.**
   - Keep observed VIIRS, adjusted NOAA-20 and modeled MODIS distinct.
   - Weather is an association, never a cause.
   - Season timing is a "central activity window", not the start or end of burning.
   - Detections are not burned area.
   - Changing scientific outputs needs the card's spec, a contract line, and a decision in a pull request Sheikh
     merges.
   - All training, quick or full, is Sheikh's manual step (H02, H03). Afterwards you re-report the metrics on all
     six holdouts from the saved outputs.
7. **Numbers.** Measured numbers come from data at runtime or from `docs/TRAINING_RESULTS.md`, with their source.
   Never from memory.
8. **Tests.**
   - API tests use `tiny_api` / `tiny_request` (`ws2_platform/tests/conftest.py`), so they run in CI without data.
   - UI component tests use `renderHtml` / `textOf` (`ws5_frontend/src/test/render.tsx`).
   - Don't add dependencies without the lead's OK.
9. **Hosting.**
   - Render serves the UI and the live API (`docs/RENDER.md`).
   - The basemap is OpenStreetMap; never restore CARTO URLs.
   - The FIRMS key never goes to the browser.
