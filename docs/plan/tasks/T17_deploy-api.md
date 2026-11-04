---
id: T17
title: "Render deploy check: a script that verifies the live service, run once and recorded"
kind: agent
owner: Sheikh
authors: [Sheikh]
phase: P1
size: S
needs: [H01]
requires: [env:RENDER_URL, network]
branch: ws1/T17-render-check
touches: [docs/guides/deployment.md]
creates: [scripts/check_render.py, scripts/tests/test_check_render.py]
checks: [CHECK-PLAN, "python -m pytest -q scripts/tests/test_check_render.py"]
---
## Goal
`docs/guides/deployment.md` says not to claim the service is live without checking the assigned URL. Turn its five-point
"Verify the deployed service" list into a script the agent can run after every deploy (T19, T28, T40, H05), and record
the first measured result.

## Context
- Routes (`ws2_platform/api/app.py`): `GET /health` returns `status`, `method_version`, `data_through` and `cells`;
  `GET /version.json` returns the deployed `commit` and `mode`; POST routes are under `/aoi/*`; the UI is served at `/`
  (`ws2_platform/api/frontend.py`).
- `deployment/runtime.json` holds `data_through`, the date the deployed data should report.
- `contracts/fixtures/bangladesh_request.json` is a valid small request body.
- Free Render services sleep after 15 minutes; the first request can take about a minute.

## Steps
1. **`scripts/check_render.py`** (standard library only: `urllib.request`, `json`; `encoding="utf-8"` everywhere):
   - URL from `--url`, else `RENDER_URL` from the environment or `.env`.
   - `--commit` defaults to `git rev-parse HEAD`.
   - First request: retry up to 6 times, 15 s apart, to let the service wake.
   - Checks, each printed as `PASS`/`FAIL` with the measured value:
     - `/health`: `status == "ok"`, `cells > 0`, `data_through` equals `deployment/runtime.json`;
     - `/version.json`: `commit` equals `--commit`, and `mode == "live-api"`;
     - `/`: HTML containing `<div id="root">`;
     - `POST /aoi/summary` with `contracts/fixtures/bangladesh_request.json`: status 200 and a non-empty series, with
       the elapsed seconds;
     - `/docs`: status 200.
   - Exit code 0 only if all checks pass. It prints nothing from `.env` except `RENDER_URL`.
2. **`scripts/tests/test_check_render.py`**: replace the HTTP function with a fake. Cover all-pass, a wrong commit, a
   `data_through` mismatch, and a service that wakes on the third try. No network.
3. Run `python scripts/check_render.py --commit "$(git rev-parse origin/main)"`. Paste the output into
   `docs/guides/deployment.md` as "Verification, <date> (measured, scripts/check_render.py)". If `version.json` lags because
   Render is still building, wait 5 minutes and run it once more.
4. Run the checks, mark the card done, and hand over for commit.

## Acceptance
- [ ] The tests pass without network.
- [ ] One real run against the Render URL is recorded, all PASS, or each FAIL explained.

## Stop and ask if
- `/health` never answers after the retries. Sheikh checks the Render logs; the agent can't read them.
