---
id: T47
title: Include detailed interval diagnostics in runtime releases
kind: agent
owner: Sheikh
authors: ["Sheikh"]
phase: P1
size: M
needs: ["T46"]
requires: []
branch: ws1/T47-runtime-report
touches: ["scripts/runtime_bundle.py", "scripts/tests/test_runtime_bundle.py"]
creates: ["scripts/tests/test_runtime_report.py"]
checks: ["CHECK-PLAN", "python -m pytest -q scripts/tests/test_runtime_report.py"]
human_checks: [CHECK-QA]
---
## Goal
Carry the detailed diagnostic piece through the pinned runtime release process.

## Context
scripts/runtime_bundle.py; scripts/tests/test_runtime_bundle.py; scripts/release_runtime.py; deployment/runtime.json.

## Steps
Extend the exact allowlist to include validation/intervals_by_stratum.json in new bundles. Preserve loading of the explicitly enumerated legacy bundle shape so the current pinned release remains usable; reject arbitrary extras, duplicates, traversal and unsafe paths. New packs must require the report. Add tiny-file pack/unpack tests for old and new formats and missing report rejection. Do not weaken existing transport/security tests or replace an existing release asset.

## Acceptance
New roundtrip bundles contain the report, old pinned archives remain loadable, unsafe extra files remain rejected.

## Stop and ask if
Compatibility would require accepting arbitrary archive contents or replacing a published release asset.

