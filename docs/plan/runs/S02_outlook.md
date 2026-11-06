# S02: corrected outlook evaluation and alert disposition

Owned by T59; agent execution is authorized. This is a planned specification, not a measured skill report. Reuse attributable compatible S01 outlook outputs when sufficient; do not refit merely to duplicate them.

## Question and scope

Does the corrected forward-season evaluation demonstrate skill against both training-only climatology and persistence on supported regions/horizons? Current-status percentiles and season-to-date context are historical comparisons, not forecast probabilities.

## Before execution

Preserve the current `outlook_region.json` and skill piece. Freeze source/input hashes, horizon/target, region eligibility, rolling-origin folds, training-only transformations/reference values and embargo for complete target windows. Verify no future row enters features, thresholds or reference distributions.

Name previously inspected scores as development evidence. Register the skill metric, uncertainty method and multiplicity handling across regions/horizons before a new run. Do not enable only the most favorable result after searching many slices.

## Commands and artifacts

The declared scientific commands are `python -m ws4_outlook.run outlook` and `python scripts/workflow.py validate`, using the project virtual environment and preserved S01-compatible inputs. The outlook stage can fit learners; it belongs to T59's explicit scientific lane after T52, never an ordinary request/startup path.

Use the stage only if S01 did not already provide compatible complete outputs or a T59 change requires it. Preserve every execution and its reason in the ignored run dossier. Write actual per-region/horizon metrics, baseline results, intervals, eligibility and alert disposition to `docs/results/OUTLOOK_REVALIDATION.md`.

## Acceptance

- Pure boundary tests cover forward fold/reference isolation, incomplete weeks, gaps, cross-year seasons and horizon censoring.
- Report actual skill and uncertainty against both baselines for every required eligible region/horizon. Unsupported/missing/low-support cases are explicit.
- Positive point skill alone does not demonstrate skill. Apply the registered uncertainty rule; a confidence interval including zero retains `no_demonstrated_skill`.
- Alerts require genuinely validated forward bounds and the documented transition contract. A current-status percentile or a historical seasonal range is not a forecast lower bound.
- It is acceptable for all forecast alerts to remain off. That must not hide the core historical calendar/status journey or become a false operational warning claim.

No emergency efficacy or forecast deployment claim follows from a software pass. T28 must serve the exact reviewed skill/alert disposition and hashes.
