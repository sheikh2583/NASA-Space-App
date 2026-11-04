# GitHub-linked hosted demo

Repository: https://github.com/sheikh2583/NASA-Space-App

Expected Pages URL after deployment: https://sheikh2583.github.io/NASA-Space-App/

On 4 November 2026, repository Pages was enabled with `build_type=workflow` using the existing local Git credential helper. No separate hosting provider or deployment secret is needed for the snapshot site.

The `Deploy live demo` GitHub Actions workflow (`.github/workflows/pages.yml`) runs on every push to `main` and can also be dispatched manually. It installs locked npm dependencies, runs frontend tests and translation checks, builds the app, uploads the Pages artifact, and publishes it. Failed checks prevent that revision from replacing the deployed site.

## What is hosted

The first deployment is a static real-data demo with exactly the Bangladesh and Punjab example areas. `ws5_frontend/public/demo/snapshot.json` is an explicitly published, approximately 645 KB export from the completed real-data run. It includes weekly summaries, periods, associated drivers, outlooks, and validation records. It contains no API keys, raw CSVs, local model files, or private account data.

The app displays the snapshot date and limits. Custom drawing, alternate date/resolution queries, spatial cell layers, and CSV exports require a running backend and are disabled or omitted in snapshot mode. Calendar and series browsing, comparison, Validation, Method, English/Bangla, and printing remain available. A hosted UI update is separate from a data refresh: pushing code does not download NASA data or retrain a model.

## One-time repository setup

1. Open repository **Settings > Pages**.
2. Set **Build and deployment > Source** to **GitHub Actions**.
3. Open **Actions > Deploy live demo** and run it, or push a commit to `main`.
4. Wait for both build and deploy jobs to pass. Open the URL recorded in the `github-pages` environment.

The maintainer can alternatively run `python scripts/github_pages.py --enable` from an authenticated Git checkout. It uses the existing Git credential helper without displaying its contents. This requires repository administration access. `python scripts/github_pages.py` reports Pages and the latest deployment runs.

Reference: [GitHub custom Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Verify each push

Open the repository Actions tab, select `Deploy live demo`, and match its commit SHA to your pushed revision. The site also publishes `version.json` with the deployed commit. The old site remains usable while a new artifact builds. Reload after a successful deployment; the snapshot JSON is cached only for the current browser session, so reload to see a refreshed dataset.

For a local production-equivalent build on PowerShell:

```powershell
$env:VITE_DEMO_MODE = 'snapshot'
$env:VITE_DATA_MODE = 'real'
cd ws5_frontend
npm test
npm run check:strings
npm run build
npm run preview -- --host 127.0.0.1
```

On Linux: `VITE_DEMO_MODE=snapshot VITE_DATA_MODE=real npm run build` inside `ws5_frontend/`.

## Refresh the public data

1. Complete local training and QA against real NASA inputs.
2. Run `python scripts/export_hosted_demo.py` from the environment.
3. Review the generated snapshot and its data-through date. The current export uses the fixed 2 November 2026 record; extending it requires updating configured dates and reviewing satellite windows.
4. Run frontend tests/build in snapshot mode and commit `ws5_frontend/public/demo/snapshot.json` with the relevant documentation.
5. Push to `main`. The next successful Pages workflow publishes the new snapshot.

Keep raw data and `.env` ignored. The small, public JSON snapshot is a deliberate exception to the policy excluding large generated scientific artifacts from Git.

## Full live backend later

GitHub Pages serves static files and cannot run FastAPI. To enable arbitrary AOIs, deploy the API container separately, supply its processed runtime artifacts, and build the frontend without `VITE_DEMO_MODE=snapshot`, with `VITE_API_BASE_URL` set to that public HTTPS service. Do not point a hosted browser app at `localhost`.

The existing API Dockerfile expects processed files in its build context. GitHub checkout does not contain those files, so connecting a Docker host directly to this repository is insufficient. A follow-up backend deployment needs versioned artifact storage/download, validation of required files, health checks that load data, memory sizing, and a GitHub-linked deployment configuration. No backend hosting account or paid resource is created by this Pages workflow.
