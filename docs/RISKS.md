# Risks

| Risk | Early sign | Response |
|---|---|---|
| FIRMS access or limits slow ingestion | first slice not ready by H4 | archive route, parallel API windows, Bangladesh first |
| Free-tier API sleeps or fails | slow first request | static JSON fallback from H16 |
| Learned model does not beat B1 | H24 metrics table | ship B1 with honest wording; keep calibrated intervals |
| Coverage poor on shifted periods | drift flags, coverage gap | widen intervals, mark extrapolated, say so plainly |
| Contract mismatch between mock and live API | contract test fails | fix at the source; log in CONTRACT_CHANGES.md |
| Overclaimed drivers | causal wording found | lint test; association wording; Monazir wording review |
| Forecast shows no skill | CI includes zero | say no_demonstrated_skill; cut alerts |
| Modeled/observed seam creates false anomalies | flags cluster at 2012 | seam check; depends_on_modeled_history mark |
| Fatigue after H30 | merge errors rise | sleep shifts; freeze at H36; no new features after |
| Late translation | Bangla keys incomplete at H30 | keys exported at H8; method text by H38; English first |
| Deployment surprises | no hello-world by H4 | deploy early and at every gate |
