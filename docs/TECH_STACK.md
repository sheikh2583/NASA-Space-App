# Technology stack

Current implementation, 4 November 2026. See [training](TRAINING.md) for the supported CUDA setup and [hosting](HOSTING.md) for the deployed demo.

Principle: boring, widely documented tools, so AI agents write correct code; free tiers only.
Versions: Python 3.11, Node.js 22.12+ for frontend work, and XGBoost 3.2.0 for training. Install the complete pinned training environment from `requirements-cuda.txt`; frontend packages use `package-lock.json`. UI-only initialization is available without NVIDIA.

| Layer | Choice | Why | Owner |
|---|---|---|---|
| Language (data, ML, API) | Python 3.11 | one language for everything except the web app | all |
| Tables and files | pandas, pyarrow, Parquet files | compact, typed, fast to read; matches contracts/parquet_schemas.json | all |
| Queries over files | DuckDB (SQL on Parquet) | fast AOI aggregation without running a database server | Sattyam, Sheikh |
| Maths | NumPy, SciPy, statsmodels (STL) | baselines, tests, seasonal decomposition | Sheikh, Monazir, Samin |
| ML | XGBoost CUDA, scikit-learn | Poisson/Tweedie harmonization, binary drift tests, quantile forecast fitting; verified CUDA placement | Sheikh, Samin |
| Geometry | shapely 2, geopandas | polygons, cell-in-polygon lookup | Sattyam |
| Contracts | OpenAPI 3, JSON Schema, jsonschema, pyyaml | one source of truth for shapes | Sattyam, Sheikh |
| API | FastAPI, Uvicorn, Pydantic; Docker for deploy | typed, quick to write, easy to test | Sattyam |
| Tests (Python) | pytest, httpx | contract, data and end-to-end tests | all, Samiul |
| Web app | React, Vite, TypeScript, project CSS | versions locked in package-lock.json | Shammo |
| Map | Leaflet, OSM tiles, geoBoundaries ADM1 | country/name/administrative filters and clickable named boundaries | Shammo |
| Charts | D3 (calendar heatmap), Recharts (line with band) | each fits its job | Shammo |
| i18n | i18next + react-i18next; Noto Sans Bengali (bundled with @fontsource) | English/Bangla toggle; font works offline | Shammo |
| Tests (web) | Vitest for logic; real phone for layout | small, quick | Shammo |
| Static hosting | GitHub Pages, Netlify or Cloudflare Pages (free) | web app and the static fallback JSON, on separate sites | Shammo, Sattyam |
| API hosting | Hugging Face Spaces (Docker) or Render free tier | free containers; may sleep, so the fallback exists | Sattyam |
| Source control | GitHub: PRs, CODEOWNERS, branch protection | clear ownership; reviews | Sheikh |
| Large files | shared drive (Google Drive) or a private Kaggle dataset | git stays small | Sheikh |
| Training compute | NVIDIA Windows/Linux, RTX 4070 Laptop or RTX 3090 Desktop | single-device CUDA training; the 3090 timing remains an estimate | Sheikh, Samin |
| Team channel | the team's existing chat (WhatsApp or Discord) | already in use | Sheikh |

## Version notes for AI agents (checked 3 Nov 2026)
- pandas is held below 3 in requirements.txt (pandas 3 changed copy-on-write and string defaults).
- DuckDB 2.0: a relation from `duckdb.sql(...)` has no `fetchone()`; use `.fetchall()`, `.df()` or `con.execute(...).fetchone()`.
- MCD12C1 land cover is HDF4: read it with pyhdf (the rasterio wheel has no HDF4 driver).

## Data sources
- NASA FIRMS: MODIS, VIIRS SNPP (history to 2 Nov 2026) and VIIRS NOAA-20 (overlap and near-real-time) active fires (archive download, area API). Needs a free MAP_KEY.
- geoBoundaries ADM1 (regions); a ready-made 0.05 degree land-cover product such as MODIS MCD12C1 (verify at H0).
- CHIRPS rainfall and NASA POWER (temperature, precipitation, soil wetness) for drivers.
- Stretch: OpenAQ (PM2.5) and MODIS MCD64A1 burned area (needs an Earthdata login).

## What we deliberately do not use
- No database server or message queue is required. Training requires a working NVIDIA CUDA environment; file/geospatial/statistical work still uses host resources.
- No private SaaS that needs a card.
