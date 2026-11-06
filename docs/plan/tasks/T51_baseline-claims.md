---
id: "T51"
title: "Freeze the baseline and register challenge claims"
kind: "agent"
owner: "Sheikh"
authors: ["Sheikh"]
phase: "P1"
size: "S"
needs: ["T00"]
requires: []
branch: "ws1/T51-baseline-claims"
touches: ["docs/plan/CHALLENGE_CONTRACT.md","docs/project/review-2026-11-06.md","docs/project/architecture.md","docs/project/hardening-scaffold.md"]
creates: ["docs/project/claim-register.md","docs/results/BASELINE_2026-11-06.md"]
checks: ["CHECK-PLAN"]
---
## Goal
Create the auditable starting point for the revised plan, mapped to C01-C06 and Q01-Q05 in the challenge contract.

## Context
Read AGENTS.md, docs/plan/CHALLENGE_CONTRACT.md, docs/project/hardening-scaffold.md, the dated review and architecture. The full challenge/resource and current submission sheets were unavailable; preserve that distinction.

## Steps
1. Record actual HEAD/tree state, existing run IDs, artifact timestamps/hashes, saved interval target/status and forecast disposition. Read existing evidence; do not fit or overwrite it.
2. Create BASELINE_2026-11-06.md with command/source/date for observations and clear historical labels for prior tests/live checks. Avoid logging URLs carrying keys, .env values or raw data.
3. Create claim-register.md with claim ID, challenge outcome, audience, exact artifact/target/run, evidence state, UI/export locations, permitted wording and prohibited inference.
4. Register failed conditional uncertainty, unsupported AOI sizes, legacy monthly reports and changed-code provenance as unresolved. Retain B1 eligibility and all holdouts.
5. Confirm scope: regional historical explorer; English/live API/OSM. Optional NRT/FRP/blind-spot cards remain deferred unless explicitly reopened.
6. Run CHECK-PLAN and hand over attributable documentation through the existing commit flow.

## Acceptance
- [ ] Every intended headline claim has provenance and a disposition; none gains validation from a documentation edit.
- [ ] Baseline inputs/outputs can be identified and recovered before subsequent scientific runs.
- [ ] Unknown challenge/submission details remain verification items, not invented mandates.

## Stop and ask if
Existing inputs/artifacts are unavailable, another process is mutating them, or protected user edits would be overwritten. Report exact missing evidence; do not fabricate measurements.

