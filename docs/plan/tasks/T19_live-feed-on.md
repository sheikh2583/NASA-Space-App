---
id: T19
title: "Live season feed, part 2: switch on the nightly run and verify"
kind: agent
owner: Sheikh
authors: [Sheikh]
phase: P2
size: S
needs: [T39]
requires: [secret:FIRMS_MAP_KEY, gh-auth]
branch: ws1/T19-live-feed-on
touches: [.github/workflows/pages.yml, docs/guides/deployment.md]
creates: []
checks: [CHECK-PLAN, CHECK-SNAP]
---
## Goal
Turn the nightly near-real-time update on, and prove it works and leaks nothing.

## Steps
1. **Local dry run first.** Run `python -m ws3_anomaly.ingest.live --inputs ws5_frontend/public/demo/live_inputs.json --out <scratch folder>/live.json`.
   It takes the key from `.env` or the environment; never print it.
   - Check: `status` is `ok`, `data_through` is yesterday or today, and Punjab's days have plausible values. Paste the
     status and the last 5 days into the PR.
   - Search the output file for the key's first 6 characters; there must be no match.
2. In `pages.yml`, uncomment the schedule (`cron: "41 1 * * *"`) so that it is a real trigger. Leave the `if:` guard
   as it is.
3. Set the repository variable with `gh variable set LIVE_FEED --body on`. Then run the workflow:
   `gh workflow run pages.yml`, and follow it with `gh run watch`.
4. In the run log, search for `api/area` and for the key's first 6 characters; both must have no match. Then open the
   live site: the status card shows "Data through <date>".
5. Update `docs/guides/deployment.md` with the date the feed was switched on and how to switch it off (`LIVE_FEED=off`).
6. Run the checks, mark the card done, `split`, push and open the PR.

## Acceptance
- [ ] A manual run succeeds; the site shows yesterday's or today's data.
- [ ] The log contains no key and no API URL (searched; result pasted).

## Stop and ask if
- The status is `failed` or `suspect` in the local dry run.
- Any log line contains `api/area`.
