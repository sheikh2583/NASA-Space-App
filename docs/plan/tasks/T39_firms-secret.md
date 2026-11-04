---
id: T39
title: "Retired: FIRMS key as a GitHub Actions secret (the key now lives only in Render, H01)"
kind: agent
owner: Sheikh
authors: [Sheikh]
phase: P2
size: S
needs: [T18]
requires: []
branch: ws1/T39-firms-secret
touches: [docs/plan/STATUS.md]
creates: []
checks: [CHECK-PLAN]
---
## Goal
Retired on 4 Nov 2026; its status is `cut`. Nothing to do.

## Context
This card put the key into GitHub Actions for a nightly Pages job. Pages is now legacy and manual-only. The live feed
runs inside the Render service (T18), which reads the key from its own environment (H01, step 2). A copy of the key in
GitHub would only add a second place it could leak.

## Steps
1. None. If `plan.py next` ever offers this card, its status was reset: run `python scripts/plan.py set T39 cut`.

## Acceptance
- [ ] Status is `cut`.

## Stop and ask if
- Sheikh wants a nightly GitHub job again. That needs a new card.
