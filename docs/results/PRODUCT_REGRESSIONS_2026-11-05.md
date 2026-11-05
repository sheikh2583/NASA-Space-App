# Product regressions — T50

Five reviewed implementation defects were repaired without fitting or scientific-artifact edits.

- Month completeness uses the intersection of the month, requested start/end and record end.
  Tiny-API regression: 15-31 Dec 2016 = 17 days/incomplete; 1-31 Dec = 31 days/complete;
  15-20 Dec = 6 days/incomplete; record-clipped 31 Dec = 1 day; full leap February = 29 days.
- The display uses actual ISO weeks 1-53. Folded weeks 1-52 remain available for climatology.
  Rendered observations for 21 and 28 Dec 2015 have different x positions on the same year row,
  and the week-53 cell lies within the SVG bounds. Counts are unchanged.
- Network failures, non-200 responses and invalid JSON reset the snapshot download promise.
  Each regression performs a failed download, a successful retry and a cache hit: exactly two fetches.
- Band help and chart labels say nominal 90%, disclose conditional undercoverage and point to Validation.
- Snapshot success tests use each exported request's dates, rather than the fallback config date.
  Altered-date and unsupported-resolution rejection tests remain and use otherwise valid saved requests.

Validation: 5 new tiny-API cases plus 3 existing partial-period regressions pass (8 total).
All 42 frontend tests pass; string lint and both live/snapshot production builds pass.
The 11 snapshot/area tests were rerun after tightening the negative requests to use valid saved dates.
Previous web success before regenerating the snapshot did not establish compatibility with the new export.
These tests exercise the actual checked-in snapshot containing requests through 3 Nov 2026.

Interval undercoverage remains scientifically unresolved and acceptance_status remains stop_condition.
Forecast performance remains numerically unvalidated and forecast alerts stay disabled.
No runtime release or recalibration is needed for these code/UI/test changes.
Live deployment must be verified against the new commit; a successful local build is not evidence of deployment.
