---
id: "T57"
title: "Enforce artifact provenance and scoped scientific acceptance"
kind: "agent"
owner: "Sheikh"
authors: ["Sheikh","Samin","Samiul","Sattyam"]
phase: "P1"
size: "L"
needs: ["T52","T53"]
requires: []
branch: "ws1/T57-provenance-acceptance"
touches: ["scripts/runtime_bundle.py","scripts/release_runtime.py","scripts/check_render.py","ws6_validation/qa.py","ws4_outlook/run.py","ws2_platform/api/app.py","ws2_platform/api/query.py","contracts/openapi.yaml","contracts/json_schemas/validation_piece.schema.json","docs/project/contract-changes.md","tools/verify_files.py"]
creates: ["common/acceptance.py","common/tests/test_scoped_acceptance.py","contracts/json_schemas/runtime_evidence.schema.json","scripts/tests/test_scientific_release_gate.py","ws2_platform/tests/test_evidence_metadata.py"]
checks: ["CHECK-PLAN","python -m pytest -q common/tests/test_scoped_acceptance.py scripts/tests/test_scientific_release_gate.py ws2_platform/tests/test_evidence_metadata.py"]
---
## Goal
Separate engineering readiness, scientific support and live delivery with verifiable source/artifact identity.

## Steps
1. Read I13, S01/S02 and all touched packaging/QA/API/contract paths. Define versioned runtime evidence: producer/serving revision, targets, input/parameter/OOF/table/report hashes, scope, method/run and dispositions.
2. Implement a pure acceptance evaluator which recomputes stop rows, validates finite metrics/support/target/hash compatibility and does not trust a green QA string. Missing or legacy evidence never becomes accepted automatically.
3. Define exact accepted_for_scope/limited/stop_condition/insufficient_support/missing/incompatible semantics and compatibility rules for older runtimes. Keep outer ZIP checksum outside a self-containing member manifest.
4. Require explicit limited-research-demo disposition for publishing incompatible/unaccepted claims; visible disclosure is part of the contract, not an unchecked force flag.
5. Expose evidence/status in API metadata and propagate accurate producer information from scientific stages. Include required new members in immutable packaging and verification without exposing secrets/models.
6. Test fabricated green QA with failing rows, stale hashes, wrong monthly target, missing/corrupt/nonfinite evidence, legacy layouts, accepted scope and explicitly limited release. Test full checked-in OpenAPI validity.
7. Record the contract change and exact live verification expectations.

## Acceptance
- [ ] One chart can be traced to a compatible run/target/table/report; serving revision can differ honestly from producer revision.
- [ ] Failing/unknown science cannot acquire an accepted badge through packaging.
- [ ] Legacy archive compatibility stays explicit, and new releases carry the required evidence.

## Stop and ask if
Compatibility would require overwriting a released asset or inventing producer provenance. Keep the prior runtime readable with honest unknown/limited status.

