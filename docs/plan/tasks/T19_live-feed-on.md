---
id: T19
title: "Live season feed, part 2: verify it on Render and record the result"
kind: agent
owner: Sheikh
authors: [Sheikh]
phase: P2
size: S
needs: [T18, T17]
requires: [env:RENDER_URL, secret:FIRMS_MAP_KEY, network]
branch: ws1/T19-live-feed-on
touches: [docs/guides/deployment.md]
creates: []
checks: [CHECK-PLAN]
---
## Goal
Prove that the live season feed from T18 works on the deployed service, and that it leaks nothing.

## Steps
1. **Local dry run first.** Start the API locally with the key from `.env`: `uvicorn ws2_platform.api.app:app --port 8000`.
   Then call `/live/season?area=<Punjab's id from areas.json>`.
   - Check that `status` is `ok`, `data_through` is yesterday or today, and the days have plausible values.
   - Search the response for the key's first 6 characters, read from `.env` inside a short Python check that prints
     only `found` or `not found`. It must be `not found`.
   - Stop the server.
2. Once Sheikh has committed T18 and Render has rebuilt, run `python scripts/check_render.py` (T17). All checks must
   pass.
3. Call `$RENDER_URL/live/season?area=<Punjab's id>`.
   - If the status is `off`, the key isn't set in Render: stop and point Sheikh to H01, step 2.
   - Otherwise check the same three things as in step 1.
4. Open the site and confirm that the status card shows "Data through <date>".
5. Record the date, the status, `data_through` and the last 5 days for Punjab in `docs/guides/deployment.md`, "Live season feed",
   marked measured.
6. Run the checks, mark the card done, and hand over for commit.

## Acceptance
- [ ] The deployed endpoint returns `ok` with yesterday's or today's data.
- [ ] The key is not in any response (`not found`, pasted).

## Stop and ask if
- The status is `failed` or `suspect`.
- The service runs out of memory on the free tier. Sheikh checks the Render metrics.
