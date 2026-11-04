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
