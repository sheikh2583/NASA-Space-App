# I10: forward-season forecast validation

Decision 26, 5 Nov 2026: replace globally prepared leave-one-season-out features with
forward-season folds. This changes forecast validation only, not harmonization/model selection.
Historical saved forecast-skill figures are leakage-affected and cannot validate this repair.

An issue row represents a completed week; targets are the sum of counts at calendar weeks
+2, +3 and +4. Reindex to the seven-day calendar; missing weeks stay missing, never zero.
Training uses seasons strictly earlier than the evaluation season. Its climatology uses
only those training observations. Evaluation features use that frozen climatology plus
observations already available at issue time. Training targets must end before evaluation
starts. Evaluation targets must end inside the evaluation season. Embargo boundary rows.
The last-four-week feature includes only the issue week and its preceding three weeks.

Externally normalized weather anomalies have no fold-local provenance guarantee, so corrected
forecast validation uses fire-history features only until weather normalization is audited.
No forecast fitting is performed by pure fold-construction tests.

Retain median pinball skill against climatology and persistence, with seasonal bootstrap
resampling. Empty folds and zero-loss reference denominators cannot establish demonstrated skill.
Future saved scores require a fresh forward-season run and scientific QA. Existing saved outputs
remain historical; serving current status remains distinct from a validated forecast.
