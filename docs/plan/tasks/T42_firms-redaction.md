---
id: T42
title: Redact FIRMS credentials at every error boundary
kind: agent
owner: Monazir
authors: ["Monazir"]
phase: P1
size: M
needs: ["T00"]
requires: []
branch: ws1/T42-firms-redaction
touches: ["ws3_anomaly/ingest/firms.py"]
creates: ["ws3_anomaly/tests/test_firms_redaction.py"]
checks: ["CHECK-PLAN", "python -m pytest -q ws3_anomaly/tests/test_firms_redaction.py"]
human_checks: [CHECK-QA]
---
## Goal
Prevent API credentials from appearing in exceptions, logs, returned gaps or CLI output.

## Context
ws3_anomaly/ingest/firms.py; ws3_anomaly/tests/test_ingest.py.

## Steps
Add a reusable redactor for literal and URL-encoded keys. Sanitize HTTP bodies and request exceptions before storing or raising; do not retain an unsafe exception chain. Sanitize again at the download boundary, including errors from CSV parsing or file handling. Validate retries>=1. Add fake sessions for ConnectionError, non-200 bodies and exhausted retries; assert caplog, gaps and formatted tracebacks contain no dummy key. No real credentials or requests.

## Acceptance
Dummy credentials absent from every error surface; valid CSV and cache/resume behavior retained. T18 must reuse the helper.

## Stop and ask if
Any diagnostic would require printing a real request URL or credential.

