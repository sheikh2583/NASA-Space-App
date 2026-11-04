---
id: T39
title: Add the FIRMS key as a GitHub Actions secret (without printing it)
kind: agent
owner: Sheikh
authors: [Sheikh]
phase: P2
size: S
needs: [T18]
requires: [secret:FIRMS_MAP_KEY, gh-auth]
branch: ws1/T39-firms-secret
touches: [docs/guides/deployment.md]
creates: []
checks: [CHECK-PLAN]
---
## Goal
Let the nightly job (T19) fetch near-real-time NOAA-20 data. The key goes from `.env` straight into GitHub's secret
store; it never appears on screen, in a file or in a log.

## Steps
1. Check that `gh auth status` succeeds for sheikh2583, and that the repository is `sheikh2583/NASA-Space-App`:
   `gh repo view --json nameWithOwner`.
2. Set the secret with a short Python one-liner that reads `.env` and pipes the value to `gh` on stdin:
   `python -c "import re,subprocess;v=[l.split('=',1)[1].strip() for l in open('.env') if re.match(r'\s*FIRMS_MAP_KEY\s*=',l)][0];subprocess.run(['gh','secret','set','FIRMS_MAP_KEY','--repo','sheikh2583/NASA-Space-App'],input=v,text=True,check=True)"`
   **Don't echo the value, and don't pass it as a command-line argument.**
3. Create the variable that keeps the feed off until T19: `gh variable set LIVE_FEED --body off --repo sheikh2583/NASA-Space-App`.
4. Check: `gh secret list` shows `FIRMS_MAP_KEY` (names only), and `gh variable list` shows `LIVE_FEED off`.
5. In `docs/guides/deployment.md` ("Nightly live feed"), add how the secret was set and how to rotate it: run the same command
   after changing `.env`.
6. Run the checks, mark the card done, `split`, push and open the PR.

## Acceptance
- [ ] The secret and the variable exist (names shown in the PR, never the value).

## Stop and ask if
- `gh` isn't logged in as sheikh2583, or `gh secret set` is refused because the token lacks admin rights.
