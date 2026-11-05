---
id: T43
title: Correct clean-run pipeline dependency ordering
kind: agent
owner: Sheikh
authors: ["Sheikh"]
phase: P1
size: M
needs: ["T00"]
requires: []
branch: ws1/T43-pipeline-order
touches: ["scripts/run_pipeline.py"]
creates: ["scripts/tests/test_pipeline_order.py"]
checks: ["CHECK-PLAN", "python -m pytest -q scripts/tests/test_pipeline_order.py"]
human_checks: [CHECK-QA]
---
## Goal
Ensure sensors use cells generated for the current inputs.

## Context
scripts/run_pipeline.py; ws2_platform/sensors.py; ws2_platform/cells.py; scripts/tests/test_resume_backend.py.

## Steps
Move cells before sensors and keep grid before both consumers as required by inspected inputs. Review resume semantics: a resume from sensors must require or explicitly rebuild compatible cells; do not silently reuse stale boundaries. Add non-fitting tests that inspect steps() and prerequisite guards only. Never invoke main(), pipeline stages, backend configuration or CUDA probes.

## Acceptance
Declared dependencies are topologically ordered; missing/stale prerequisite behavior is explicit and tested without execution.

## Stop and ask if
A clean-run check would execute pipeline stages or fitting.

