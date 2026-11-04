# Hosting operations

The current deployment target is **one Free Render Docker Web Service** serving React and the live FastAPI on the same origin. Use **[the Render deployment guide](RENDER.md)** for the exact form fields, health checks, data updates, and troubleshooting. The first Render deployment still needs to be completed and verified in the user's account.

- Root [Dockerfile](../Dockerfile): builds the frontend in live mode, installs only serving dependencies, downloads validated existing data, and starts one API worker.
- [render.yaml](../render.yaml): Free plan, Singapore, `main`, `/health`, automatic deployment on commits.
- [deployment/runtime.json](../deployment/runtime.json): public versioned runtime archive and SHA256. Raw data, trained models, secrets, and logs remain outside Git.
- `/` serves the UI; `/health`, `/docs`, `/aoi/*`, `/export`, and `/meta/validation` serve the API. `/version.json` reports the Render Git SHA.
- Code pushes rebuild the UI/API together using the same pinned existing data. No training or NASA acquisition occurs.

No FIRMS key, CUDA dependency, database, persistent disk, or separate frontend host is required for serving. Existing results end on **2 November 2026**. A live API permits dynamic queries within the loaded coverage; it does not itself produce newer observations.

## Free-tier operation

Render Free sleeps after 15 idle minutes and takes time to wake. The whole app wakes together. The plan has 512 MB RAM and shared workspace allowances; inspect Render metrics and logs for resource exhaustion. No paid upgrade is configured automatically. [Render free limits](https://render.com/docs/free).

Local serving and artifact checks passed without training; the actual Docker build and Render capacity remain unverified until deployment. See [RENDER.md](RENDER.md) for the exact verification performed and operational limitations.

## Legacy Pages snapshot

The previous site remains at [GitHub Pages](https://sheikh2583.github.io/NASA-Space-App/). It serves saved products, with fixed dates/resolution and no live CSV/cell requests. It has not been deleted.

`.github/workflows/pages.yml` is now **manual-only**; pushes no longer update Pages. Use the new Render URL as primary after confirming health, revision, date/resolution changes, cell layers, and CSV export. The old API-only Dockerfile under `ws2_platform/` is retained for local builds with processed artifacts; it is not the Render entrypoint.

The OpenStreetMap basemap and geoBoundaries ADM1 selection remain unchanged. Basemap access does not use FIRMS_MAP_KEY. Observe the [OSM tile policy](https://operations.osmfoundation.org/policies/tiles/); do not bulk-prefetch tiles.
