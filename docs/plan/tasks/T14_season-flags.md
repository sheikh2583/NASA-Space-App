---
id: "T14"
title: "Season-level unusual flags (library and spec)"
kind: "agent"
owner: "Monazir"
authors: ["Monazir","Sheikh"]
phase: "P2"
size: "M"
needs: ["T07","T53","T58"]
requires: []
branch: "ws1/T14-season-flags"
touches: ["docs/specs/I1_SEASON_PROFILE.md","docs/project/contract-changes.md"]
creates: ["ws3_anomaly/season_flags.py","ws3_anomaly/tests/test_season_flags.py"]
checks: ["CHECK-PLAN","python -m pytest -q ws3_anomaly/tests/test_season_flags.py ws4_outlook/tests/test_season_profile.py"]
---
## Goal
Add descriptive season-level unusual flags with valid same-cutoff references and explicit sensitivity/support semantics (C03/C05).

## Context
Read I1, I13, T53 protocol, T58 support contract and ws4_outlook/season_profile.py. This replaces the unimplemented old confidence/noise-test proposal; no existing executable test is deleted or weakened.

## Steps
1. Reuse season_years, existing windows and cutoff logic. Compare a partial season with eligible previous seasons at the same cutoff; use all-history and recent-ten bases, excluding the target season and requiring at least eight eligible references.
2. Use strict reference 10th/90th-percentile comparisons and report the actual basis, n, percentile and ties policy. Missing/low-activity/coverage-insufficient states remain distinct.
3. Report observed/adjusted/modeled provenance explicitly; low modeled_share does not imply observed SNPP. Define zero-total provenance from availability, not division by zero.
4. Weekly bound sums may be sensitivity scenarios only. Use stable_under_sensitivity/unstable/unsupported semantics, not unqualified calibrated confidence. Unsupported T58 bands cannot certify a robust scientific verdict.
5. Test planted high/low, same-cutoff partial, missing coverage, insufficient history, ties, cross-year windows, adjusted-only data and unsupported bands. Test deterministic quantile boundaries. A 10th/90th rule does not promise <=3 flags in 24 noise seasons; record that correction in I1 instead of selecting a favorable seed.
6. Append the spec decision and exact proposed API flag fields/contract line before T15 integration.

## Acceptance
- [ ] All deterministic regressions pass and no planted-value test substitutes for false-positive validation.
- [ ] Reference count/cutoff/source/support and sensitivity meaning are explicit.
- [ ] No physical onset/end, calibrated seasonal confidence or causal-fire claim.

## Stop and ask if
A useful result requires season-level calibration or a changed scientific estimand beyond I13. Preserve unsupported state until a separate scientific spec/run addresses it.
