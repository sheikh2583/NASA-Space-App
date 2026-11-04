---
id: T16
title: "Hosted API, part 1: data release script, Docker download and hybrid web mode"
kind: agent
owner: Sattyam
authors: [Sattyam, Sheikh, Shammo]
phase: P2
size: L
needs: [T07]
requires: []
branch: ws1/T16-hosted-api-code
touches: [ws2_platform/Dockerfile, ws2_platform/api/app.py, ws5_frontend/src/api.ts, ws5_frontend/src/snapshot.ts,
          ws5_frontend/src/App.tsx, ws5_frontend/src/i18n/en.json, ws5_frontend/src/i18n/bn.json, docs/guides/deployment.md]
creates: [scripts/release_data.py, scripts/tests/test_release_data.py, ws2_platform/fetch_data.py,
          ws2_platform/tests/test_fetch_data.py, ws5_frontend/src/mode.ts, ws5_frontend/src/mode.test.ts]
checks: [CHECK-PLAN, CHECK-PY, CHECK-WEB, CHECK-SNAP]
---
## Goal
Let judges draw **any** area inside the processed regions on the public site, while the snapshot stays as an
automatic fallback. This card writes and tests the code; Sheikh creates the account and token (H01), and T17 deploys.

## Context
- `ws2_platform/Dockerfile` copies the API's runtime files from `data/processed/`:
  - `cells.parquet`, `harmonized.parquet` and `sensor_days.parquet`;
  - `interval_table.json`, `drivers_region.json` and `outlook_region.json`;
  - `validation/`.

  Its comment says they are all under 10 MB. A GitHub checkout has no `data/`, so the image must download a
  versioned data release.
- `/health` already loads the Store and returns `method_version`, `data_through` and `cells`. If loading fails, it
  currently errors with a 500.
- `src/api.ts` `call()` uses the snapshot when `STATIC_DEMO` (`VITE_DEMO_MODE === "snapshot"`). It also has an older
  region fallback (`VITE_FALLBACK_BASE_URL`); leave that alone.
- Hugging Face Spaces (Docker):
  - the free CPU Basic tier has 2 vCPU and 16 GB RAM, and sleeps when unused;
  - the app URL is `https://<owner>-<space-name>.hf.space`;
  - the README front matter needs `sdk: docker` and `app_port: 7860`.

## Steps
1. **`scripts/release_data.py`** (Sheikh).
   - `pack(processed="data/processed", out_dir="share")` refuses unless `data/processed/validation/qa.json` has every
     check `pass`.
   - It writes `firesense-data-<method_version>-<YYYYMMDD>.tar.gz` with exactly the runtime files listed above (the
     same list as the Dockerfile).
   - It also writes `manifest.json`: for each file its name, size and sha256, plus `method_version` (from
     `harmonized.parquet`), `data_through` (max `sensor_days.date`), the git commit, and the tarball's sha256.
   - With `--publish`, it prints the exact command and doesn't run it:
     `gh release create data-<method_version>-<YYYYMMDD> <tar> manifest.json --title … --notes "Derived from NASA FIRMS (see docs/REFERENCES.md)"`.
   - `scripts/tests/test_release_data.py`, using `ws2_platform/tests/tiny_data.make_tiny_processed`:
     - the tarball contains exactly the file list;
     - the manifest hashes match;
     - a failing `qa.json` refuses to pack.
2. **`ws2_platform/fetch_data.py`** (Sattyam). Standard library only.
   - `fetch(url, sha256, dest="data/processed")` downloads to a temporary file, verifies the sha256, extracts with
     `tarfile` (rejecting absolute paths and `..`), and checks that every manifest file exists.
   - On a mismatch it raises `ValueError("checksum mismatch")`.
   - `python -m ws2_platform.fetch_data URL SHA256`.
   - Tests use a `file://` URL to a tarball made in `tmp_path`: it extracts; a wrong sha fails; a `../evil` member is
     rejected.
3. **Dockerfile.**
   - Add `ARG DATA_URL` and `ARG DATA_SHA256`.
   - Replace the `COPY data/processed/...` lines with
     `RUN python -m ws2_platform.fetch_data "$DATA_URL" "$DATA_SHA256"`.
   - Keep a commented "local build" alternative showing the old COPY lines.
   - Keep `HEALTHCHECK` and `CMD`.
4. **`/health`.** Wrap the body in try/except: on failure return
   `JSONResponse(status_code=503, content={"status": "unavailable", "detail": "data not loaded"})`. Never return a
   stack trace or a file path. Add a test with `tiny_api` that `/health` is 200 with `status == "ok"`.
5. **Hybrid web mode** (Shammo).
   - **New `src/mode.ts`:** `export type Mode = "api" | "snapshot"`. `resolveMode(env, probe: () => Promise<boolean>): Promise<Mode>`
     works like this:
     - `VITE_DEMO_MODE === "snapshot"` → `"snapshot"`;
     - `VITE_DEMO_MODE === "hybrid"` → `"api"` if `await probe()` is true within 4 seconds, else `"snapshot"`;
     - otherwise → `"api"`.
     Cache the result for the session.
   - The probe is `fetch(BASE + "/health")` with an AbortController and a 4-second timeout, and it requires
     `status === "ok"`.
   - `api.ts`: `call()` asks the cached mode; `snapshot` uses `snapshotCall`.
   - `App.tsx` treats drawing and custom dates as allowed only in `api` mode (today it checks `STATIC_DEMO`). In
     hybrid mode, when it falls back, it shows the banner `t("hosting.api_unavailable")`: "Live service unavailable:
     showing the saved demo areas."
   - **`mode.test.ts`:**
     - snapshot env → snapshot;
     - hybrid with a probe that resolves true → api;
     - hybrid with a probe that rejects → snapshot;
     - hybrid with a probe that never resolves → snapshot after the timeout (use fake timers:
       `vi.useFakeTimers()`).
6. **`docs/guides/deployment.md`.** Add a "Hosted API (Hugging Face Space)" section covering: cutting a data release
   (`release_data.py`), building with `DATA_URL` and `DATA_SHA256`, the Space README header, rollback (point
   `DATA_URL` at the previous release and restart), and `/health`.
7. Run the checks, mark the card done, `split` (Sattyam, Sheikh, Shammo), push and open the PR.

## Acceptance
- [ ] The release, fetch and mode tests pass in CI.
- [ ] `docker build` isn't run here (no data in CI). It runs in T17.
- [ ] The default Pages build (snapshot mode) behaves exactly as before.

## Stop and ask if
- The runtime files on the laptop total more than 200 MB. Check: `python -c "import os;print(sum(os.path.getsize(os.path.join(r,f)) for r,_,fs in os.walk('data/processed') for f in fs)/1e6)"`.
