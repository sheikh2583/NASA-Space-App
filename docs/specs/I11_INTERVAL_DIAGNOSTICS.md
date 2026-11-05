# I11: measurement-only interval diagnostic correction

Count unique contributing OOF cell IDs per selected block and period as n_cells.
Retain the drawn h*w as drawn_n_cells. Sparse absent cells are not evaluated cells.
No RNG call, row filter, sum, interval lookup or calibration quantile is changed.
The report is descriptive; repeated rectangles are not independent observations.

Nominal 90% is not a promise of conditional coverage. Include positive-activity coverage and
missed upper/lower tails. Every dimension is subject to n>=500 and coverage<0.80 stop reporting.
Empty groups retain n=0, null metrics and insufficient-sample notes.
Terra-only holdouts use overlap-era observations, not ground truth in the pre-2012 record.

Historical saved report, inspected 5 Nov 2026: weekly Terra-only season q2 n=1065 coverage
0.7746478873239436; monthly q1 n=1035 coverage 0.7294685990338164; monthly q2 n=1045 coverage
0.7617224880382775. These trigger review; no bands are changed. T13 stays in review.
