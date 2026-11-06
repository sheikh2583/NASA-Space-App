# I13: scientific acceptance and remediation protocol

Planning specification, 6 November 2026. T53 audits the actual data/splits and freezes the run appendix before T55/T56 fitting. Until that audit, this is a proposed design, not evidence that statistical prerequisites hold. [Training authorization](../project/training-authorization.md) permits agent execution.

## 1. Estimand and scope

Estimate satellite active-fire detections on the SNPP VIIRS reference scale. Preserve observed SNPP, NOAA-20 adjustment and MODIS reconstruction as separate source classes. Neither agreement with SNPP nor an interval against SNPP establishes detection of every actual fire.

Scientific acceptance names source combinations, era, resolution, target, sampling/query domain and artifact versions. It is never an unqualified global boolean. Observed-source degenerate bounds describe absence of added harmonization error, not zero physical observation uncertainty.

## 2. Freeze before fitting

The T53 run appendix must contain:

- Input filters, source/product identifiers, cutoff and baseline/member hashes; exact source commit/patch and environment.
- Actual roles and counts for fit, calibration, method selection, development evaluation and proposed confirmation, by spatial block and period. Document all earlier inspected outcomes.
- Whole-week targets and calendar-month daily allocation, including overlap/completeness requirements; no legacy Monday-month target in new production evidence.
- Actual named-AOI sizes/shapes and the subset where uncertainty can be evaluated honestly.
- Primary metric/group list, sampling seed, uncertainty/dependence method, sparse-support rule and candidate budget.
- A bounded resource plan: one pipeline per output tree, verified backups, available GPU/disk, initial readiness/quick/full commands and recorded wall times. No paid cloud job is assumed.

Do not create an untouched confirmation set by relabeling already inspected holdouts. If no uninspected evidence exists, report development validation and that limitation. Additional fits do not manufacture independent data.

## 3. Reference comparisons

Retain B1 and the current frozen interval table as the reproducible baseline. Retain the existing learned candidate for a corrected comparison; no extra model family is required. Every required spatial, temporal, backward and drift-era holdout must be reported by its actual code-defined name and for both MODIS input combinations.

Evaluate count agreement, bias and error, not only a selection average. CCC is agreement, not classification accuracy. Keep selection/test-use distinctions visible. Do not force the GPU candidate to win. A material regression triggers diagnosis and a recorded decision, not silent exclusion of a difficult holdout.

## 4. Diagnosis before a repair

T54 produces an immutable diagnostic report using existing OOF/grid/sensor artifacts. Analyze zeros/positive activity, positive truth at zero prediction, under/over misses, magnitude, season, land cover, input combination, actual area size, missingness and geography/time support. Include width and interval score, not coverage alone.

Count contributing cell IDs separately from drawn rectangle size. Record unique blocks/periods and overlap among sampled rectangles. Do not use naive independent-binomial uncertainty for repeated correlated draws.

Test calendar allocation across leap days and month/year boundaries; verify daily SNPP truth sums to weekly OOF truth. Full named-area evaluation needs coherent out-of-sample predictions across its complete cell set. Partial holdout-block coverage cannot silently stand in for a complete administrative AOI.

## 5. Candidate budget and leakage controls

After diagnosis, register at most two interval repair candidates in the run appendix before evaluation. Prefer a minimal mechanism supported by the failure analysis, such as explicit MODIS-combination/predicted-magnitude conditioning, an appropriate zero-sensitive score, or documented sparse-group fallbacks. Record the exact choice, score, strata and fitting data.

Deployment strata may use only information available at prediction time. Truth-positive and truth-magnitude groups remain mandatory diagnostics, not a deployable oracle grouping. Never recalibrate on inspected test outcomes or widen intervals repeatedly until a favorable test score appears.

Preserve fit/calibration/evaluation roles, deterministic seeds and finite-sample quantile semantics where applicable. For dependence or nonexchangeability, explain the limitation rather than citing a guarantee the implementation does not possess. [Conditional-coverage research](https://arxiv.org/abs/2305.12616) distinguishes restricted targets from universal finite-sample guarantees.

If both candidates fail, record the failure, retain a limited/unsupported interval disposition and propose a new preregistration only when there is a specific new hypothesis. Do not run an unbounded search against a known test set.

## 6. Review criteria

These are internal scientific quality criteria, not NASA judging thresholds.

| Item | Rule |
|---|---|
| Target | Production report explicitly says `calendar_month_daily_allocation` for months and matches served aggregation |
| Severe failure | Preserve the existing stop rule: any reported group with at least 500 draws and coverage below 0.80 is a stop condition |
| Primary groups | Week/month × Terra-only/Terra+Aqua, positive activity, zero prediction with positive truth, size/support classes, seasons; audit sparse groups rather than hiding them |
| Nominal goal | 0.90 with empirical coverage and justified dependence-aware uncertainty; absence of an 0.80 stop does not prove 0.90 calibration |
| Tolerance | Proposed primary-group empirical deviation tolerance: 5 percentage points. T53 freezes the exact rule and support requirements before fitting; this is not a distribution-free conditional guarantee |
| Width/usefulness | Compare width and interval score on identical eligible samples against the frozen baseline; justify the tradeoff, including near-zero cases. Infinite/vacuous bands do not pass |
| Support | Explicit counts, unique units and sparse-fallback frequency. T53 records adequate support rules from the inventory before candidate fitting; unsupported groups cannot receive accepted status |
| Completeness | No missing mandatory report, nonfinite metric, incompatible hash or unexplained excluded holdout |
| Historical applicability | Pre-2012 reconstruction is overlap-era extrapolation; no claim pre-2012 SNPP truth exists |

Accepted status requires the target/provenance/support checks and the registered empirical criteria to pass for the declared scope. A tolerance screen alone does not establish calibrated probability or make all AOIs supported. Publish the actual coverage, width, dependence assumptions and remaining uncertainty.

## 7. Status contract

Use explicit states: `accepted_for_scope`, `limited`, `stop_condition`, `insufficient_support`, `missing`, `incompatible`. Exact wire enums/schema are finalized in T57. Keep engineering readiness and delivery verification separate.

The gate recomputes stop rows from metrics and compares declared status/hashes/target. Legacy `reported` does not automatically mean accepted; legacy evidence cannot acquire a new producer revision merely through packaging.

The API/UI/brief/CSV/story must carry limitations consistently. Derived categorical conclusions that rely on unsupported modeled bands are qualified or withheld. A missing interval is not a reliable zero-width interval.

## 8. Promotion

Preserve all trial outputs, source patches, configuration and logs outside Git. T56 writes the full comparison/disposition. T59 independently assesses corrected outlook evaluation; absence of skill is an acceptable disclosed outcome and keeps forecast alerts off.

T28 may publish an accepted scoped release or an explicitly limited research demo with visible limitations. It cannot call failing science accepted because engineering tests pass. The final subjective assessment must retain a deduction for central unresolved evidence gaps.
