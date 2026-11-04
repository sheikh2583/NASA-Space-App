---
id: T17
title: "Hosted API, part 2: publish the data release, deploy the Space, switch Pages to hybrid"
kind: agent
owner: Sheikh
authors: [Sheikh, Sattyam]
phase: P2
size: M
needs: [H01]
requires: [real-data, hf-token]
branch: ws1/T17-deploy-api
touches: [.github/workflows/pages.yml, docs/HOSTING.md]
creates: [ws2_platform/space/README.md, ws2_platform/space/Dockerfile]
checks: [CHECK-PLAN, CHECK-SNAP]
---
## Goal
Put the API online with the reviewed data, and make the public site use it when it's up and the snapshot when it
isn't.

## Steps
1. `python scripts/release_data.py`. Paste the printed `gh release create …` command into the PR, then run it (the
   GitHub CLI must be logged in as sheikh2583). Write down the asset URL and the tarball sha256 from `manifest.json`.
2. Create `ws2_platform/space/README.md` with front matter:
   ```
   ---
   title: FireSense API
   sdk: docker
   app_port: 7860
   ---
   ```
   Add one paragraph pointing to the GitHub repository.
3. Create `ws2_platform/space/Dockerfile`:
   - `FROM python:3.11-slim`.
   - `RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*`. The
     slim image has no git.
   - `RUN git clone --depth 1 --branch main https://github.com/sheikh2583/NASA-Space-App /app`, then
     `WORKDIR /app`.
   - `RUN pip install --no-cache-dir -r requirements.lock.txt`.
   - `RUN python -m ws2_platform.fetch_data <asset URL> <sha256>`, using the values from step 1.
   - `ENV DATA_DIR=/app/data/processed PORT=7860`, and the `EXPOSE`, `HEALTHCHECK` and `CMD` lines from
     `ws2_platform/Dockerfile`.
4. If `huggingface-cli` is missing, run `python -m pip install huggingface_hub` into the virtual environment. It's a
   deployment tool for this card only; don't add it to `requirements*.txt`. Then upload to the Space:
   `huggingface-cli upload <account>/firesense-api ws2_platform/space . --repo-type space`. The token comes from `HF_TOKEN`;
   never print it.
5. Wait for the build, which takes a few minutes. Then `curl https://<account>-firesense-api.hf.space/health` must
   return `status: ok`, plus the `method_version` and `data_through` of the release. Paste the response into the PR.
6. **Measure.** Post the Punjab demo request to `/aoi/summary` five times; record the median time (the first call
   may be slow).
7. **Pages.** In `.github/workflows/pages.yml`, set the build env to `VITE_DEMO_MODE: hybrid` and
   `VITE_API_BASE_URL: https://<account>-firesense-api.hf.space`. The URL is public, not a secret.
8. Update `docs/HOSTING.md` with the real Space id, the release tag and the rollback steps.
9. Run the checks, mark the card done, `split`, push and open the PR. After merge, check on the live site:
   - drawing a box in Punjab returns a calendar;
   - pausing the Space in its settings shows the "Live service unavailable" banner and the snapshot.

## Acceptance
- [ ] `/health` on the Space reports the release's method version (response pasted in the PR).
- [ ] The median summary time is recorded as measured.
- [ ] After merge, both paths (API up and API down) are checked on the live site; screenshots in the PR or a comment.

## Stop and ask if
- The Space build fails twice.
- `/health` returns 503.
- The median summary time is over 5 seconds.
