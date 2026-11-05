---
id: T46
title: Correct interval area counts and report every stop-condition failure
kind: agent
owner: Samin
authors: ["Samin", "Sheikh", "Shammo", "Samiul"]
phase: P1
size: M
needs: ["T00"]
requires: []
branch: ws1/T46-interval-diagnostics
touches: ["ws4_outlook/conformal.py", "ws4_outlook/interval_report.py", "ws4_outlook/run.py", "docs/plan/tasks/T13_interval-report.md", "ws5_frontend/src/components/Pages.tsx", "ws5_frontend/src/i18n/en.json", "ws5_frontend/src/i18n/bn.json", "docs/science/method_en.md", "docs/project/contract-changes.md"]
creates: ["ws4_outlook/tests/test_interval_diagnostics.py", "docs/specs/I11_INTERVAL_DIAGNOSTICS.md"]
checks: ["CHECK-PLAN", "python -m pytest -q ws4_outlook/tests/test_interval_diagnostics.py", "CHECK-WEB"]
human_checks: [CHECK-QA]
---
## Goal
Measure contributing cells honestly and surface conditional undercoverage without recalibrating bands.

## Context
ws4_outlook/conformal.py; ws4_outlook/interval_report.py; ws4_outlook/tests/test_interval_report.py; docs/plan/tasks/T13_interval-report.md; ws5_frontend/src/components/Pages.tsx.

## Steps
Write a measurement-only spec/contract note. Keep RNG draws and summed values unchanged. Record n_cells from unique contributing cell IDs for the selected block/period; retain h*w separately as drawn_n_cells. Explain sparse-row versus complete-grid representation rather than claiming unobserved cells were tested. Fix T13 wording that implies Terra-only OOF holdouts are actual pre-2012 truth. Add robust small/empty-group handling and positive-activity/tail diagnostics. Detect ALL n>=500, coverage<0.80 rows regardless of dimension. Add one-cell, block-edge, missing-combination and known-stop-row regression tests with fixed tables only. Publish limitations in the validation UI, qualifying 90% as nominal and pre-2012 values as modeled. Document the three saved season stop rows as historical diagnostics. Never build or change interval calibration tables.

## Acceptance
One contributing cell always reports n_cells=1. Every qualifying stop row is reported; no automatic completion/promotion on failing coverage. Original interval-table hash unchanged. T13 remains under review until Sheikh accepts the diagnostic disposition.

## Stop and ask if
Any proposed fix changes interval bands, silently counts sparse absent cells as observed, or suppresses failing strata.

