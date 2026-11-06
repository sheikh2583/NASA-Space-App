---
id: "T62"
title: "Measure serving capacity and resolve demonstrated bottlenecks"
kind: "agent"
owner: "Sattyam"
authors: ["Sattyam","Sheikh"]
phase: "P3"
size: "M"
needs: ["T60"]
requires: []
branch: "ws1/T62-capacity-measurement"
touches: ["ws2_platform/api/query.py","ws2_platform/api/app.py","docs/guides/deployment.md"]
creates: ["scripts/measure_api.py","scripts/tests/test_measure_api.py","docs/results/SERVING_CAPACITY.md"]
checks: ["CHECK-PLAN","python -m pytest -q scripts/tests/test_measure_api.py"]
---
## Goal
Establish a measured operating envelope for the current single-service architecture.

## Steps
1. Read request/cache/memory behavior and actual hosting limits. Register a representative small/large-AOI endpoint/request mix and budgets before measuring.
2. Build a bounded read-only measurement utility with sanitized output and no new dependencies. Mock network/time in its unit tests.
3. Measure local concurrency first, then a small authorized live sample: cold/warm/cache conditions, response size, latency, errors and available memory observations. Do not stress production.
4. Initial proposed warm-summary budget: p95 <=3 s over >=20 representative requests, no unhandled errors, memory within the actual service limit with headroom and no unbounded growth after repeated area changes. Report conditions; a small sample is not an SLA.
5. Inspect 256/64 entry caches for actual payload cost. Tune limits or add byte bounds only where measured need justifies it; preserve equality and in-flight semantics.
6. Record every budget pass/fail and mitigation. Cold starts need clear user feedback and contingency, not a fabricated fast-load claim.

## Acceptance
- [ ] Reproducible measurement table, request mix, actual limit and scope of inference.
- [ ] No critical resource leak/unhandled error in the registered sample; failures are resolved or support is narrowed.
- [ ] No speculative database/service migration or test-budget inflation.

## Stop and ask if
Measurement would require a production stress test, paid service or unapproved dependency. Use bounded local evidence and state the limitation.

