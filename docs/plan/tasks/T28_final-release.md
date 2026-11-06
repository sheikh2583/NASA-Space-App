---
id: "T28"
title: "Freeze, publish and verify the evidence-bearing event release"
kind: "agent"
owner: "Sheikh"
authors: ["Sheikh","Shammo","Samiul"]
phase: "P3"
size: "M"
needs: ["T56","T57","T58","T59","T60","T62","T34","T24","H06","T16"]
requires: ["real-data","gh-auth"]
branch: "ws1/T28-final-release"
touches: ["docs/results/training-results.md","docs/project/claim-register.md","docs/guides/deployment.md","docs/project/submission-checklist.md","ws5_frontend/public/demo/areas.json","deployment/runtime.json"]
creates: ["docs/results/RELEASE_DOSSIER.md"]
checks: ["CHECK-PLAN","CHECK-FILES","CHECK-WEB"]
human_checks: ["CHECK-PY","CHECK-QA"]
scientific_spec: "docs/plan/runs/S03_release-validation.md"
---
## Goal
Release one reproducible code/runtime/evidence combination with truthful scientific disposition (Q01/Q04/Q05).

## Steps
1. Read the challenge contract, claim register, S01/S02 reports, I13/T57 evidence gate, device/user/capacity reports and corroboration disposition.
2. Record the release source/patch, producer revisions, runtime identity/member hashes, targets, scientific scope, all known failures and fresh verification. Reuse compatible completed scientific evidence; full suites/QA use the explicit scientific lane when needed.
3. Require an accepted scoped result or explicit limited-research-demo release disposition with visible limitations. Green engineering checks cannot certify failed bands or forecast skill.
4. Package a new immutable runtime release; inspect/verify record end, diagnostics/provenance and compatibility. Never replace an existing asset. Keep raw models/data/logs and backups outside Git.
5. Use the catalog exporter only if relevant cells/catalog changed. No snapshot export. Update sourced results/dossier and prepare the exact commit/manifest for Sheikh's normal commit/push flow.
6. After the intended commit is pushed, run check_render.py against that commit and inspect served target/status/runtime/hash contents. Observe the complete supported journey; record date/browser. No deploy claim from a push/build.
7. Tag only when Sheikh names the final commit. Rehearse rollback with a previous compatible pair and local live runtime plus recording contingency; do not advertise offline snapshot mode.

## Acceptance
- [ ] Actual live commit/runtime/record end/diagnostics match the release dossier.
- [ ] All scientific and deferred/missing user/corroboration evidence is visible.
- [ ] Rollback/contingency and attribution are documented; no undisclosed re-fit or publication.

## Stop and ask if
Required release credentials/authority are absent, an asset would be overwritten, or live identity fails. Report actual host evidence; do not invent a deployment cause.
