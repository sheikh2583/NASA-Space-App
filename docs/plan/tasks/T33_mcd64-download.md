---
id: "T33"
title: "Download MODIS burned-area tiles (MCD64A1) with the Earthdata token"
kind: "agent"
owner: "Sheikh"
authors: ["Sheikh"]
phase: "P2"
size: "S"
needs: ["T51"]
requires: ["secret:EARTHDATA_TOKEN","network"]
branch: "ws1/T33-mcd64-download"
touches: ["data/MANIFEST.md"]
creates: ["tools/get_mcd64a1.py","scripts/tests/test_get_mcd64a1.py"]
checks: ["CHECK-PLAN","python -m pytest -q scripts/tests/test_get_mcd64a1.py"]
---
## Goal
Acquire a predeclared MCD64A1 corroboration sample for T24; it shares MODIS inputs and is not independent ground truth.

## Steps
1. Read the challenge contract, T24, NASA product/CMR documentation and existing credential-redaction code before downloading.
2. Declare collection, AOIs/season windows, years and storage/network budget before looking for favorable agreement. Verify tile coverage from actual geospatial metadata; old guessed tile tables are not acceptance truth.
3. Implement resumable standard-library/installed-requests acquisition with CMR pagination, exact collection filtering, .part staging, validated existing-file reuse and recorded metadata/checksums.
4. Read the token internally; redact headers, URLs and errors, including redirects. Never forward bearer authorization to an untrusted redirect host or print credentials.
5. Test pagination, crossing-year date windows, partial/corrupt files, expired authentication and redaction with fake network responses. No network in unit checks.
6. Download only the declared sample into data/raw/mcd64a1 and append a sourced manifest entry. Keep raw products outside Git; report missing/unmapped sample rather than substituting favorable years.

## Acceptance
- [ ] Actual complete inventory, collection/extent and integrity evidence exist for T24.
- [ ] No token in output; no raw products committed.
- [ ] Missing data/authentication has an explicit disposition.

## Stop and ask if
Credentials are missing/expired, data rights are unclear or the declared disk/network budget is exceeded. Do not disclose tokens or expand the sample silently.
