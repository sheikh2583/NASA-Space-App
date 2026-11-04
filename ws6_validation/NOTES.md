# NOTES (ws6_validation)

## Decisions and assumptions
- tests/: contract (every endpoint vs openapi.yaml), data QA, end-to-end demo path, static fallback presence.
  API tests use API_BASE_URL if set, else the app in-process on data/processed.
- qa.py writes validation/qa.json: test results, flag rates before/after 2012 (decision 21), planted-anomaly recovery.
- docs/science/method_en.md (under 250 words), method_bn.md (AI draft, needs review), demo-script.md (3-minute path + 8 slides).

## Known issues
- Manual: FIRMS web-viewer comparison on real data, phone checks, Bangla review, video, submission forms.

## AI assistance log (where AI tools helped)
- 2026-11-03: everything in this folder was written with Claude (AI assistant) at Sheikh's direction before the event, on synthetic data, and assigned to this workstream's owner. Review it before relying on it; rerun on real data.
