# S01: harmonization and aggregate-interval scientific run

Execution owner: coding agent, authorized by Sheikh on 6 November 2026. This is a run specification, **not a record of an executed run**. T53 freezes its measured inventory/appendix; T52 provides the explicit scientific command lane; T56 executes it.

## Question

Do corrected context/targets and a diagnosis-led interval repair improve the relevant held-out results over preserved B1/current intervals without hiding positive-activity failures or exceeding the evaluated AOI domain?

## Inputs and protected baseline

- Real FIRMS input inventory, retained cells/boundaries, gridded counts, sensor-day/outage metadata and weather inputs.
- Existing selected parameters, OOF predictions, interval table and all validation pieces.
- Source commit plus uncommitted patch, package/device versions and relevant spec/contract versions.

Record hashes, sizes, cutoff and location in an ignored `results/runs/<run-id>/` dossier. Verify baseline copies in `data/runs/<run-id>/baseline/` before a runner replaces shared output paths. Raw inputs are read-only. Use one scientific pipeline per output tree; keep Render on its pinned runtime during experiments.

## Required preregistration appendix, frozen by T53

Record exact split identifiers and already-inspected outcomes; confirmation availability; candidate definitions/parameters (maximum two interval repairs); metric/group/support rules; random seeds; named-AOI evaluation strategy; fit/calibration/selection boundaries; command order; resources and stop/resume rules. Every item needs a value or a named unresolved blocker before execution. No fabricated hashes, GPU capacity or support counts in the planning document.

## Command sequence

Run only after T52/T53/T55/T57 prerequisites are complete. Use the project virtual environment. T52's planned `python scripts/plan.py checks T56 --scientific --run` executes only the declared scientific lane; that flag is not available until T52 implements it.

1. Read the setup/readiness and runner paths; record available GPU/disk and verify the baseline. Readiness fits are authorized but count as fitting activity.
2. `python scripts/workflow.py prepare --gpu-id 0 --threads 8` after confirming those device/thread settings in the appendix.
3. `python scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8 --quick` as an implementation check. Stop on corruption, target inconsistency or invalid device placement. A known scientific stop row is a diagnostic outcome, not justification to suppress it.
4. `python scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8` for the complete comparison. Preserve the baseline and each trial; record the full actual holdout list and both input combinations.
5. `python scripts/workflow.py validate` and full reviewed suite execution in the scientific lane. Capture exit codes plus scientific statuses and detailed metrics; five green engineering groups are insufficient.
6. Reconcile generated reports, calibration target, prediction/table hashes and provenance. Compare baseline/candidates on identical eligible samples; publish every attempted disposition.

These commands use current entry points, not a promise they already expose every future candidate option. T55 must implement the frozen configuration mechanism without manual parameter edits between reported trials. Optional smoke/benchmark commands run only if they verify an unresolved concern; they are not extra fits for appearance.

## Evaluation and stop rules

Apply [I13](../../specs/I13_SCIENTIFIC_ACCEPTANCE.md). Never use inspected test outcomes as calibration labels. Preserve severe stop conditions and report sparse support. No numerical result is a completion target: B1 may remain selected, a simpler interval method may fail, and a limited demo may remain the honest release disposition.

Pause execution on baseline-backup failure, input mutation, wrong compute placement, nonfinite/corrupt output or a failed prerequisite. Fix a reproducible implementation defect in scope; resource/authentication problems require a concrete report. Do not repeat an identical fit without a new change, transient-failure rationale or declared reproducibility check.

## Output dossier

`execution.json`, input/member hashes, configuration, fit/device log, source patch, stage/command logs, all holdout tables, detailed interval report, block-aware uncertainty/support audit, forecast disposition and promotion decision stay together outside Git. T56 creates a concise sourced Markdown report in `docs/results/SCIENTIFIC_REMEDIATION.md`; raw models/OOF/calibration outputs are never committed.

Record whether the run is full, quick or resumed. A resumed run can validate a scoped change but its duration is not a fresh full-run benchmark. Code/training completion and scientific acceptance are separate outcomes.
