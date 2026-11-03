# Technology stack

> Disclaimer: the choices are my recommendations; versions, free-tier limits and installs were not checked (docs/KNOWN_GAPS.md items 6 and 7). Verify at H0 (docs/H0_VERIFICATION.md).

Principle: boring, widely documented tools, so AI agents write correct code; free tiers only.
Versions: Python 3.11 and the current Node LTS. I could not check current release numbers, so at H0 install the current stable
releases, then pin them (`pip freeze > requirements.lock.txt`, commit `package-lock.json`). Everyone installs from the same files.

| Layer | Choice | Why | Owner |
|---|---|---|---|
| Language (data, ML, API) | Python 3.11 | one language for everything except the web app | all |
| Tables and files | pandas, pyarrow, Parquet files | compact, typed, fast to read; matches contracts/parquet_schemas.json | all |
| Queries over files | DuckDB (SQL on Parquet) | fast AOI aggregation without running a database server | Sattyam, Sheikh |
| Maths | NumPy, SciPy, statsmodels (STL) | baselines, tests, seasonal decomposition | Sheikh, Monazir, Samin |
| ML | scikit-learn, LightGBM | gradient boosting (Poisson, Tweedie, quantile), classifier tests | Sheikh, Samin |
| Geometry | shapely 2, geopandas | polygons, cell-in-polygon lookup | Sattyam |
| Contracts | OpenAPI 3, JSON Schema, jsonschema, pyyaml | one source of truth for shapes | Sattyam, Sheikh |
| API | FastAPI, Uvicorn, Pydantic; Docker for deploy | typed, quick to write, easy to test | Sattyam |
| Tests (Python) | pytest, httpx | contract, data and end-to-end tests | all, Samiul |
| Web app | React 18, Vite, TypeScript, Tailwind CSS | fast dev loop, very well known to AI tools | Shammo |
| Map | Leaflet with leaflet-draw (or react-leaflet) | polygon and rectangle drawing, free tiles | Shammo |
| Charts | D3 (calendar heatmap), Recharts (line with band) | each fits its job | Shammo |
| i18n | i18next + react-i18next; Noto Sans Bengali (bundled with @fontsource) | English/Bangla toggle; font works offline | Shammo |
| Tests (web) | Vitest for logic; real phone for layout | small, quick | Shammo |
| Static hosting | GitHub Pages, Netlify or Cloudflare Pages (free) | web app and the static fallback JSON, on separate sites | Shammo, Sattyam |
| API hosting | Hugging Face Spaces (Docker) or Render free tier | free containers; may sleep, so the fallback exists | Sattyam |
| Source control | GitHub: PRs, CODEOWNERS, branch protection | clear ownership; reviews | Sheikh |
| Large files | shared drive (Google Drive) or a private Kaggle dataset | git stays small | Sheikh |
| Notebook compute | laptop first; Kaggle notebooks if training is slow (Colab disconnects) | free, CPU is enough | Sheikh, Samin |
| Team channel | the team's existing chat (WhatsApp or Discord) | already in use | Sheikh |

## Data sources
- NASA FIRMS: MODIS and VIIRS SNPP active fires (archive download, area API, near-real-time). Needs a free MAP_KEY.
- geoBoundaries ADM1 (regions); a ready-made 0.05 degree land-cover product such as MODIS MCD12C1 (verify at H0).
- CHIRPS rainfall and NASA POWER (temperature, precipitation, soil wetness) for drivers.
- Stretch: OpenAQ (PM2.5) and MODIS MCD64A1 burned area (needs an Earthdata login).

## What we deliberately do not use
- No database server, no message queue, no paid cloud, no GPU. Not needed for this scale and each adds ways to break.
- No private SaaS that needs a card.
