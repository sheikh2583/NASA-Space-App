# Deployment: one Render service for the UI and the API

Updated 4 November 2026. The repository is prepared for a single **Free Docker Web Service**. Its root Dockerfile builds the React frontend, downloads existing validated runtime data, and starts FastAPI serving everything on one origin. No training, GPU, FIRMS key, database, persistent disk, or separate frontend service is required.

## What gets deployed

| File | Role |
|---|---|
| [`Dockerfile`](../../Dockerfile) | Builds the frontend in live mode, installs only the serving dependencies (`requirements-api.txt`), downloads the pinned data, and starts one API worker |
| [`render.yaml`](../../render.yaml) | Blueprint: Free plan, Singapore, branch `main`, health check `/health`, auto-deploy on commit |
| [`deployment/runtime.json`](../../deployment/runtime.json) | URL and SHA256 of the versioned runtime-data ZIP on a GitHub Release |

Routes: `/` serves the UI; `/health`, `/docs`, `/aoi/*`, `/export` and `/meta/validation` serve the API; `/version.json` reports the deployed Git SHA. Code pushes rebuild the UI and API together with the same pinned data. Nothing is trained, and no new NASA data is fetched. The record ends on **2 November 2026**.

## Fill in the New Web Service form

Connect `sheikh2583/NASA-Space-App`, then use:

| Field | Value |
|---|---|
| Name | `firesense` (or another available name) |
| Language / Runtime | **Docker**, replacing the auto-detected Python 3 selection |
| Branch | `main` |
| Region | Singapore |
| Root Directory | Empty |
| Dockerfile Path | `./Dockerfile` |
| Docker Build Context | Repository root (`.`), if shown |
| Compute / Instance Type | **Free — $0/month**; the paid plan is often preselected |
| Docker Command | Empty; use the Dockerfile command |
| Environment Variables | None required for this deployment |
| Health Check Path | `/health` (under Advanced or service Settings) |
| Auto-Deploy | On Commit |

Do not use the older Python build/start commands from the API-only instructions. Switching to Docker removes those fields. Click **Deploy web service** once these files are on `main`. Render's first Docker build must download Python/npm packages and the runtime archive; wait for its build and deployment logs to finish.

Alternatively use **New → Blueprint**, connect the repository, and review `render.yaml`. It specifies the same Free Docker service. Use the existing service's Settings for later changes rather than creating duplicate services.

References: [Render Docker builds](https://render.com/docs/docker), [Blueprint settings](https://render.com/docs/blueprint-spec).

## Verify the deployed service

Use the exact `onrender.com` URL assigned by Render:

1. Open `/health`. It must report `status: ok`, a nonzero cell count, and `data_through: 2026-11-02`.
2. Open `/version.json`. Its `commit` should match the deployment's Git SHA, and `mode` should be `live-api`.
3. Open `/`. It should display the explorer with no saved-snapshot limitation banner.
4. Select Dhaka, change the date range and resolution, inspect cell layers, and download CSV.
5. Open `/docs` for the live API contract UI. Browser Network requests must go to this same Render host rather than `localhost` or the previous Pages site.

The API uses existing processed observations/reconstructions. Serving a live API does not extend data coverage beyond 2 November or acquire new FIRMS observations.

## Data delivery and updates

`deployment/runtime.json` pins a public GitHub Release ZIP and its SHA256. The Docker build downloads it, verifies integrity, checks saved real-data provenance and passing QA, and installs only the allowlisted runtime files. The data becomes part of the container image, so it remains available after Render sleeps/restarts. Raw downloads, trained models, secrets, and local run directories are excluded.

Normal code pushes automatically rebuild the same service with the same pinned scientific data. They never train or refresh NASA data. The API runtime requirements exclude CUDA and learner packages; the reference forecast learner is imported only by its human-run fitting path.

To publish a new data version after **human-run** scientific validation:

```sh
python scripts/runtime_bundle.py pack
```

This packages existing outputs only. Upload `share/firesense-runtime.zip` to a **new versioned GitHub Release**, update its URL and printed SHA256 in `deployment/runtime.json`, then commit/push the manifest. Do not replace an asset under an existing pinned URL. Keep raw/processed data out of Git. The download helper refuses a bad checksum, synthetic/failed saved QA, unexpected files, or overwriting a populated data directory.

## Free-tier behavior

Free Render web services sleep after 15 minutes without requests and can take about a minute to wake. The UI and API wake together. This deployment requests Free compute explicitly; workspace bandwidth/build allowances and free instance hours still apply. Read [Render's current limits](https://render.com/docs/free).

While a sleeping service wakes, the web app says "Waking the server, this can take up to a minute…" after 3 seconds and offers **Try again** after 90 seconds, so a cold start never looks like a broken page.

### Keep-warm switch (optional)

`.github/workflows/keep-warm.yml` calls `<RENDER_URL>/health` every 10 minutes, so judges never meet a cold start. It runs only while two repository variables are set: `KEEP_WARM` is `on`, and `RENDER_URL` is the service URL. Run these once, with the [GitHub CLI](https://cli.github.com/) signed in (`gh auth login`):

```bash
gh variable set RENDER_URL --body "https://<service>.onrender.com" --repo sheikh2583/NASA-Space-App
```

```bash
gh variable set KEEP_WARM --body "on" --repo sheikh2583/NASA-Space-App
```

**Switch it off** with `gh variable set KEEP_WARM --body "off" --repo sheikh2583/NASA-Space-App`, or in GitHub under Settings → Secrets and variables → Actions → Variables.

Cost: Render grants each workspace 750 free instance hours a month, and one service awake all month uses at most 744 (31 × 24). So keep it on only if this is the workspace's **only** always-on free service; otherwise the hours run out and Render suspends the free services until the next month. Scheduled GitHub Actions can be delayed by a few minutes, and the ping is a tiny inbound request. GitHub disables scheduled workflows in a public repository after 60 days without activity.

The free instance provides 512 MB RAM. The local Windows serving check reached approximately 430 MiB peak for the sampled Dhaka requests; this is not a Linux/container capacity benchmark. One worker and single-threaded numeric libraries reduce resource use. Monitor Render's memory and logs for out-of-memory restarts, especially with simultaneous users or broad areas. No paid upgrade is selected automatically.

## Troubleshooting

| Failure | Check |
|---|---|
| Python build/start fields still visible | Select **Docker**, not Python 3; use root `Dockerfile`. |
| Runtime download fails | Read the Docker build log; the public release URL must remain available and match the manifest SHA256. |
| `/health` fails or data files are missing | Ensure the Docker build completed its runtime download; no training command should be part of deployment. |
| Page is blank or requests go to localhost | Deploy the latest root Dockerfile; it overrides local frontend settings with same-origin live mode. |
| Snapshot banner still visible | Verify you opened the new Render URL and its deployed revision, rather than the previous GitHub Pages URL. |
| Process killed / memory limit | Inspect Render metrics/logs; Free capacity has not been load-tested on Render. |
| Changes do not appear | Verify repository, branch, Auto-Deploy, deployment SHA, and `/version.json`; use Manual Deploy → Deploy latest commit if needed. |

GitHub Pages is retained as an optional manually dispatched legacy snapshot workflow. It no longer auto-deploys on pushes. The previous site is not deleted; use Render as the primary URL after verifying its deployment.

## Verification performed

The combined frontend passed 12 frontend tests, translation checks and its production build. Artifact integrity/routing tests passed without scientific fitting. A local read-only check served `/`, assets/catalog, `/health`, `/version.json`, `/docs`, live summary/periods/drivers/outlook/cells, changed day/month queries, and CSV export. Training-library imports were blocked during that check. The published runtime ZIP was downloaded and checksum-verified independently.

A Docker engine is unavailable in the current Windows environment, so a native Docker build and the actual Render deployment must still be verified in Render's logs. No model training or fitting probes were run for this migration.

## Check the container locally (optional)

On any machine with Docker:

```bash
docker build -t firesense .
docker run --rm -p 10000:10000 firesense
```

Open `http://localhost:10000/`, `/health` and `/docs`. This builds and serves the existing artifacts only.

## Legacy GitHub Pages snapshot

The previous static site is still at [sheikh2583.github.io/NASA-Space-App](https://sheikh2583.github.io/NASA-Space-App/). It serves saved results for fixed dates and resolutions, with no live CSV export or cell requests. `.github/workflows/pages.yml` is **manual-only**: pushes no longer update it. Refresh it only on purpose with `scripts/export_hosted_demo.py`. The API-only `ws2_platform/Dockerfile` is kept for local builds that already have processed files. It is not the Render entrypoint.

The basemap is OpenStreetMap and never uses `FIRMS_MAP_KEY`. Follow the [OSM tile policy](https://operations.osmfoundation.org/policies/tiles/), and don't bulk-prefetch tiles.
