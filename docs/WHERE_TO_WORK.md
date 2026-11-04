# Where to do what

| Thing | Where it lives | Who may write |
|---|---|---|
| Code | your own folder in the GitHub repo (branch, then pull request) | folder owner |
| Raw downloads (FIRMS, boundaries, land cover, weather) | data/raw/ in the shared drive (not git) | Monazir (FIRMS, weather), Sattyam (boundaries, land cover) |
| Working files | data/interim/<your-name>/ on your laptop or the shared drive | you |
| Final data files | data/processed/ (shared drive), one writer per file (docs/FILE_OWNERSHIP.md) | the file's owner |
| Notebooks | ws*/notebooks/ in the repo; export to .py before committing; never commit outputs | folder owner |
| Secrets (keys) | your local .env only | you |
| API (live) | the API host (Sattyam's account) | Sattyam |
| Web app (live) | the static host project for the app | Shammo |
| Static fallback JSON (live) | a separate static site or branch | Sattyam |
| Slides, video, method text | docs/ and the shared drive | Samiul |

## Per person
| Person | Main place | Heavy jobs | Deploy target |
|---|---|---|---|
| Sheikh | NVIDIA training machine, project venv | CUDA harmonization/evaluation through scripts/workflow.py; preserve reports and QA | none (integration) |
| Sattyam | laptop (venv, Docker if available) | gridding and aggregates on laptop | API host; static fallback site |
| Monazir | laptop | downloads and ingestion on laptop; big files straight to the shared drive | none |
| Samin | NVIDIA training machine, project venv | interval calibration plus CUDA drift/forecast fitting | none |
| Shammo | laptop with Node; dev server on port 5173 pointing at the hosted mock | builds locally | web app host |
| Samiul | laptop | tests run against hosted URLs | none |

## Running things
- Training: use `scripts/setup.ps1 -TrainingOnly` or `bash scripts/setup.sh --training-only`, then the CUDA readiness and quick/full commands in [TRAINING.md](TRAINING.md). Public training commands reject CPU mode.
- Web app: `npm install` then `npm run dev`; copy `ws5_frontend/.env.example` to `ws5_frontend/.env` and set `VITE_API_BASE_URL` (hosted mock, then live API) and `VITE_FALLBACK_BASE_URL`.
- API locally: `uvicorn` on port 8000 from ws2_platform/api/; everyone else uses the hosted mock or live API, not Sattyam's laptop.
- Tests: `pytest <your folder>/tests`. Samiul's tests take a base URL (`API_BASE_URL=... pytest ws6_validation/tests`).
