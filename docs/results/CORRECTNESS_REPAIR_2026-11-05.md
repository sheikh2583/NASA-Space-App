# Correctness repair evidence — 5 November 2026

T42-T48 code repairs are committed. T49 integrates saved outputs and the new runtime release.
No harmonization learner, interval calibration or forecast learner was fitted during these repairs.
The discarded T41 experiment is not included.

| Finding | Disposition |
|---|---|
| FIRMS credentials | Error-boundary redaction; 11 offline regressions, plus 7 existing ingest tests |
| Pipeline ordering | Cells precede sensors; sensors resume rebuilds cells; 3 planning-only tests, no pipeline run |
| Forecast leakage | Forward-season fold construction, frozen training climatology and target embargo; 4 pure regressions |
| Conditional coverage | NOT scientifically resolved: nominal bands retained, conditional failures exposed, T13 stays review |
| Area-size diagnostics | Unique contributing cells counted; drawn size retained; one-cell/edge/empty-group regressions |
| Runtime report | New bundles require detailed report; exact old format still accepted; 6 transport regressions |
| Forecast alerts | Watch promotes correctly; absent genuine forecast bounds disables batch alerts; 8 pure regressions |
| Record dates | Live health/static metadata drives defaults and exporter; record end distinguished from season complete-week cutoff |

## Verification

Focused non-fitting regression run: 60 passed across ingestion, pipeline planning, forecast data,
alerts, outlook status, interval diagnostics and transport/export tests.
Season/record-date integration follow-up: 11 passed. Frontend: 37 passed; string lint and live/
snapshot production builds passed. The later wording-only change also passed frontend tests/lint.
QA before the API cutoff integration: all five groups passed (7 data, 17 contract, 4 end-to-end,
20 common tests plus the seam-rate check). Follow-up QA/deployment evidence will be recorded below.

Saved outputs were backed up under ignored results/runs/correctness-repair-* before regeneration.
The non-fitting interval_report and outlook_status stages regenerated diagnostics/current status.
All 11 regions have forecast status no_demonstrated_skill, pending corrected forecast validation,
with forecast alerts off. No replacement forecast scores are claimed.

Interval-table SHA256 before and after:
2a5e18dd319e663ab65f7b78f914f121f0acf41f74aa31b634aada84d6626e4b.

Corrected detailed report: 60 rows, acceptance_status=stop_condition. Existing season failures
remain, and positive-activity diagnostics make further failures explicit:

| Group | n | Coverage |
|---|---:|---:|
| Weekly Terra+Aqua / positive activity | 1100 | 0.732727 |
| Weekly Terra only / positive activity | 1095 | 0.471233 |
| Weekly Terra only / season q2 | 1065 | 0.774648 |
| Monthly Terra only / positive activity | 1718 | 0.569267 |
| Monthly Terra only / contributing cells 11-50 | 1097 | 0.743847 |
| Monthly Terra only / season q1 | 1035 | 0.729469 |
| Monthly Terra only / season q2 | 1045 | 0.761722 |

Source: data/processed/validation/intervals_by_stratum.json regenerated from saved OOF predictions.
These are held-out diagnostics, not ground truth for pre-2012 or independent-draw confidence estimates.
No bands were widened. T46 repairs reporting, not the scientific undercoverage.

## Runtime and deployment

New immutable runtime-20261105-render-v2 was uploaded and downloaded back for checksum verification:
d5f85f9242436a693841712a782557850be1e531fb5c23b1720f31fad4311eed.
It contains validation/intervals_by_stratum.json and explicit pending forecast evidence.
The uploaded runtime preceded discovery of the API season cutoff integration; that integration
changes API computation/metadata, not files in the runtime archive.

The exporter initially refused a season/record-date mismatch. The API now preserves the
complete-week data_through and adds record_data_through for the full record, documented in
OpenAPI/schema/contract log. It excludes partial weeks that could extend beyond the actual
record. The exporter checks the explicit record end.
Snapshot export then completed for all 13 saved areas, through 2026-11-03.

Live revision/report verification is pending the repair push and Render rebuild. Do not
interpret this report as evidence that the code is already serving live.
