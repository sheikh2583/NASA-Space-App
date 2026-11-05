# Correctness repair plan — 5 November 2026

Scope: eight audited findings, implemented as bounded repairs. This document and its task
cards are scaffolding only; no implementation, fitting, artifact generation or deployment
is performed by creating this plan. The discarded T41 calibration experiment stays discarded.
No new dependencies, recalibration, model replacement or invented performance claims.

## Work order and scope

| Order | Card | Finding | Deliverable |
|---|---|---|---|
| 1 | T42 | 1: FIRMS credential leakage | Redactor, safe exception boundaries, fake-request regression tests |
| 2 | T43 | 4: sensors before cells | Dependency order and resume prerequisite guards, static tests |
| 3 | T44 | 2: forecast leakage | Fold-local feature/reference construction, target embargo, historical-claim qualification |
| 4 | T45 | 7: forecast alert mismatch | Watch-to-high transition and disabled alerts when genuine forecast bounds are absent |
| 5 | T46 | 3 and 5: interval reporting | Honest contributing-cell counts, all stop rows, conditional limitations; no band changes |
| 6 | T47 | 6: report omitted from runtime | New-bundle report inclusion with explicit legacy-format compatibility |
| 7 | T48 | 8: record-end disagreement | Metadata-driven live/static dates and exporter consistency |
| 8 | T49 | Release/integration evidence | Saved-output disposition, new runtime release, actual live verification |

Each card lists the files it may change and tests it may create. Implement one card at a time,
following the existing plan loop. The repair rows precede T14 on the board. Existing card scopes
remain unchanged; do not start live-feed work before T42 is committed.

T13 is reopened as review: its stop condition applies to EVERY stratum with n>=500 and
coverage<0.80, not just area-size groups. T46 repairs measurement/reporting and supplies a
documented disposition; it must not improve reported coverage by hiding rows or changing bands.
The three saved qualifying rows are:

| Saved diagnostic | n | Coverage |
|---|---:|---:|
| Week / Terra only / season q2 | 1065 | 0.7746478873239436 |
| Month / Terra only / season q1 | 1035 | 0.7294685990338164 |
| Month / Terra only / season q2 | 1045 | 0.7617224880382775 |

Source: data/processed/validation/intervals_by_stratum.json, inspected 5 Nov 2026.
These are historical held-out diagnostics, not a guarantee for the actual pre-2012 record.
Correcting contributing-cell counts changes area-stratum interpretation, not the band table.

## Validation and release gates

Agent work: inspect paths, implement pure transformations, run individually reviewed non-fitting
tests through plan.py checks, frontend builds/lints, static checks and approved read-only
diagnostics. No blanket pytest, readiness/CUDA probes, integrated pipeline or forecast fitting.
New Python tests must import no fitting fixtures and call no fitting functions.

Human-only work: pipeline stages, workflow validation and any forecast re-fitting/re-evaluation.
This plan does not grant an exception to AGENTS.md or assume a new training run.
If forecast fitting is deferred, retain explicit unvalidated status and disable unsupported alerts;
historical scores cannot establish correctness of the repaired forecast.

Scientific behavior changes need each card's specification/contract note/decision and Sheikh's
review. Saved scientific artifacts remain untouched during code implementation.
Before publication, capture input/output hashes and rerun the diagnostics on approved saved
outputs. A passing code test does not mean old scientific claims are validated.

Release compatibility: accept only the specifically enumerated old/new runtime layouts.
Require the report in newly packed releases. Keep the current pinned release bootable during
rollout. Publish new artifacts under a new immutable release, then verify live health,
validation pieces and record dates. No replacement of existing assets.

## Definition of finished

All eight findings have a code/test disposition and evidence; T13's stop-condition breach is
explicitly resolved as a reporting/acceptance decision rather than silently marked done.
No credential exposure, clean-run dependency defect, unsupported forecast alert or misleading
date/coverage claim remains. Deferred human numerical validation is labelled as deferred.
T49 records the actual deployed state; a code push alone is not deployment evidence.
