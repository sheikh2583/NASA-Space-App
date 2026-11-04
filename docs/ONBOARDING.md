# Onboarding: where the project stands (4 Nov 2026)

Read this first, then your own file in docs/instructions/. Ten minutes. Sheikh's step-by-step guide (datasets,
commands, ML training, deployment, push) is docs/SHEIKH_GUIDE.md.

## 1. The short version
- **Every workstream has working code.** The real-data chain runs end to end: ingest → grid → harmonize → intervals and drift →
  anomalies and drivers → outlook → API → web app. The current smoke run passes all data, contract, end-to-end, and shared-library QA groups.
- **Real inputs are loaded.** FIRMS archives, geoBoundaries ADM1, MCD12C1 land cover, and the NASA POWER weather cache are present locally.
  The 4 Nov smoke run selected B1 by held-out agreement (mean CCC 0.9401 versus LightGBM 0.9219), with 91.6% weekly coverage for nominal 90% bands.
- **What remains:** full (non-quick) training, the manual FIRMS viewer comparison, hosting, device checks, fluent Bangla review,
  video, and submission tasks (section 5).
- The code was written with an AI assistant (Claude) at Sheikh's direction and committed under each workstream owner's name,
  with the AI use stated in every commit message and in each NOTES.md. **Review your own folder before you build on it.**

## 2. Big changes since the starter kit
| Change | Why | Where |
|---|---|---|
| Suomi NPP stopped on 2 Nov 2026; values after that are NOAA-20 adjusted to SNPP terms | FIRMS ended SNPP data | DECISIONS 17 |
| `sensor_days` table: days without a sensor are missing, never zero | outages looked like "no fires" | DECISIONS 18 |
| Grid per satellite; MODIS fitted per satellite combination (Terra-only before Jul 2002) | Terra flew alone 2000-2002 | DECISIONS 19 |
| Series, flags and current status computed live for drawn areas; drivers, drift and forecast per admin1 region | drawn AOIs vs region files | DECISIONS 20 |
| Grid formula rounded and clamped; days are local solar dates | float errors; night passes on the wrong day | DECISIONS 22, 23 |
| openapi.yaml 0.2.0: full schemas for all 8 endpoints | contract tests need them | contracts/ |
| B1 (per-region ratio) chosen over LightGBM by held-out agreement; the choice reruns automatically on real data | RISKS: "ship B1 with honest wording" | ws1_harmonize/NOTES.md |
| Anomaly baseline = same-week climatology (STL optional); severity scaled by the region's typical week | STL absorbed whole unusual seasons | ws3_anomaly/NOTES.md |

## 3. Project structure
```
nasa-modis-viirs/
├── common/              Samin   shared library: grid, regions, series, climatology, intervals, splits, metrics
├── contracts/           Sattyam (openapi, fixtures) / Sheikh (parquet + JSON schemas)
├── data/                not in git: raw/, interim/, processed/ (the file contracts), processed/validation/
├── docs/                plans, decisions, this file; method_en/bn.md and demo_script.md (Samiul)
├── prompts/             the original prompt packs (still the spec for each step)
├── scripts/             setup.sh / setup.ps1, start.*, run_pipeline.py, push_to_github.*, git/ (team git scripts)
├── tools/               synth_firms.py (synthetic inputs), verify_files.py (contract check)
├── ws1_harmonize/       Sheikh  panel, baselines B0/B1, LightGBM, evaluation + OOF, harmonized v0/v1, validation piece
├── ws2_platform/        Sattyam grid, sensor_days, cells; api/ (FastAPI app, mock, fixtures, static fallback); Dockerfile
├── ws3_anomaly/         Monazir ingest/ (FIRMS API + normalize), anomaly scoring, critical periods, drivers, weather loaders
├── ws4_outlook/         Samin   conformal intervals v1, drift flags, outlook + forecast skill, alerts
├── ws5_frontend/        Shammo  React + Vite app: map + where layer, status card, calendar, band chart, panels, EN/BN
└── ws6_validation/      Samiul  contract, data QA and end-to-end tests; qa.py -> validation/qa.json
```

Data flow (each arrow is a file in data/processed/, checked by `python tools/verify_files.py`):
```
FIRMS CSV -> detections -> grid_daily + sensor_days + cells -> (panel) -> harmonized v0 + interval_table v0
          -> predictions_oof -> interval_table v1 + drift_flags -> harmonized v1
          -> anomalies_region_week, critical_periods, drivers_region.json, outlook_region.json, validation/*.json
          -> API (/aoi/*, /meta/validation, /export) + static fallback -> web app
```

## 4. Run it on your laptop
| Step | Linux / macOS | Windows (PowerShell) |
|---|---|---|
| Setup + pipeline (about 15-35 min) | `bash scripts/setup.sh --quick` | `powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 -Quick` |
| Start API + app | `bash scripts/start.sh` → http://localhost:5173 | `... -File scripts\start.ps1` |
| App without data (fixtures) | `bash scripts/start.sh --mock` | `... -File scripts\start.ps1 -Mock` |
| All tests | `. .venv/bin/activate && python -m pytest -q` | `.venv\Scripts\python -m pytest -q` |
| One pipeline step | `python scripts/run_pipeline.py --from v1` | same |

Needs Python 3.11, Node 22 LTS and git. Git scripts (scripts/git/) need Git Bash on Windows.

## 5. Gaps to fix (consolidated, 3 Nov 2026)
Priority: **P0** blocks a credible demo · **P1** should be done before the event · **P2** improves it if time allows.
Owner = who fixes it (docs/FILE_OWNERSHIP.md). Tick them off in your own copy or move them to the team channel.

### 5a. Rules, repo and accounts
| # | P | Owner | Gap | Fix |
|---|---|---|---|---|
| R1 | P0 | Sheikh | Space Apps 2026 terms not read; this code was written before the event and the repo is public | Read the Participant Terms now (H0-11); if pre-event code is not allowed, keep the repo private and rebuild at the event from the plan |
| R2 | P0 | Sheikh | No LICENSE file; NASA will not post solutions without licence documentation | Add LICENSE (Apache-2.0 is NASA's default) |
| R3 | P0 | Sheikh | History not on GitHub yet | `scripts/push_to_github.*`, then invite, protect main |
| R4 | P1 | Monazir | GitHub handle `Monajir` unconfirmed (account has no name) | Confirm; fix scripts/team.csv and CODEOWNERS if wrong |
| R5 | P1 | Everyone | Commits are authored in your name but written by an AI | Review your folder; say in the channel if you do not accept a commit, and Sheikh rewrites it before others build on it |
| R6 | P2 | Sheikh | No authentication or rate limit on the public API (KNOWN_GAPS 17) | Fine for a demo; add a request limit on the host if exposed long |

### 5b. Data (all P0: today every number is synthetic)
| # | P | Owner | Gap | Fix |
|---|---|---|---|---|
| D1 | P0 | Monazir | No real FIRMS data | Country yearly CSVs (fastest) or archive requests for MODIS, VIIRS SNPP, VIIRS NOAA-20; `--clip demo` at ingest; `ws3_anomaly/ingest/firms.py` for the last weeks (docs/SHEIKH_GUIDE.md section 3) |
| D2 | done | Monazir | NOAA-20 start date (1 Apr 2018) confirmed on the FIRMS archive page; NOAA-21 corrected to 1 Mar 2023 | none |
| D3 | P0 | Sattyam | Admin1 regions are synthetic quadrants | geoBoundaries ADM1 for BGD and IND (Punjab, Haryana, Delhi); `python -m ws2_platform.cells --admin1 <file>` |
| D4 | P0 | Sattyam | Land cover is synthetic | MCD12C1 (HDF4, Earthdata login); `--mcd12c1 <file>`; check the cropland classes (12, half of 14) |
| D5 | P1 | Monazir | Weather is synthetic; POWER and CHIRPS loaders untested | Run `ws3_anomaly/loaders/weather.py` per region; cache to data/interim/monazir |
| D6 | P1 | Sattyam | sensor_days only knows outages from notices and data edges | Samiul's data QA: look for multi-day zero runs across a whole region; add them to common/regions.OUTAGES |
| D7 | P1 | Monazir | Near-real-time rows have no `type` field, so static sources are kept | Mask known persistent hot spots (gas flares, kilns) from the standard product's type 2 locations |

### 5c. Science (recheck every item on real data)
| # | P | Owner | Gap | Fix |
|---|---|---|---|---|
| S1 | P0 | Sheikh | B1 beat LightGBM on synthetic data (CCC 0.983 vs 0.931): expected, since the generator is a pure ratio | Rerun `ws1_harmonize.run model` on real data; the choice is automatic and recorded in validation/harmonization.json |
| S2 | P1 | Samin | 90% bands are wide for large areas (about 4x the value before 2012 for a 250-cell area): calibration rectangles are at most 10x10 cells | Sample rectangles up to a whole 2x2 degree block and add a size stratum; recheck coverage |
| S3 | P1 | Samin | Held-out coverage is 96% (target 90%): slightly conservative because the lower multiplier is taken at each bin's lower edge | Acceptable; say "at least 90%" in the pitch, or add finer bins |
| S4 | P1 | Monazir | Whole unusual seasons are flagged only at their edges (planted Bangladesh 2021, 1.9x, best rank 6) | Add a season-level flag from the outlook's season-to-date percentile, shown on the calendar's year labels |
| S5 | P1 | Monazir | Flags use the value, not the lower bound (decision 21 outcome: 0 flags before 2012 otherwise) | Keep; the app shows exceeds_lower_bound. Revisit on real data |
| S6 | P1 | Samin | Forecast shows no skill in any region on synthetic data | Expected; the app explains it. Real weather may help; never show alerts without skill |
| S7 | P2 | Monazir | Drivers lack the LightGBM permutation-importance check from P3.8 | Add if time; correlations with block tests are already in |
| S8 | P2 | Sheikh | Only high anomalies are flagged (planted Punjab 2024 low season not flagged) | Product choice for early warning; mention in the method text if asked |

### 5d. App, API and hosting
| # | P | Owner | Gap | Fix |
|---|---|---|---|---|
| A1 | P0 | Sattyam | Nothing deployed | API from ws2_platform/Dockerfile (bake data/processed in); static fallback folder on a static host |
| A2 | P0 | Shammo | Web app not deployed; VITE_ URLs not set on a host | Build with VITE_API_BASE_URL and VITE_FALLBACK_BASE_URL; deploy dist/ |
| A3 | P1 | Shammo | Driver names and caveats come from the API in English, so Bangla mode shows them in English | Add caveat codes to drivers_region.json (Monazir) and translate in bn.json |
| A4 | P1 | Samiul | bn.json and method_bn.md are AI drafts | Fluent review before H42 |
| A5 | P1 | Shammo | Not checked on a real phone, with a colour-blindness simulator, or with a screen reader; map drawing is mouse/touch only | Manual checks; demo buttons give a keyboard path |
| A6 | P2 | Sattyam | First request per area takes about 0.8 s and free hosts sleep | Warm the demo areas after deploy; the static fallback covers sleeps |
| A7 | P2 | Shammo | JavaScript bundle is 908 kB (Leaflet + Recharts) | Lazy-load the chart and validation page |
| A8 | P2 | Sattyam | Static fallback serves admin1 regions only, not drawn areas | Stated in the app's fallback message |

### 5e. Pitch and submission
| # | P | Owner | Gap | Fix |
|---|---|---|---|---|
| P1 | P0 | Samiul | Remove the "synthetic data" banner only when real data is loaded; every slide number from a validation piece | Rerun `python -m ws6_validation.qa` after the real run |
| P2 | P1 | Samiul | Manual FIRMS web-viewer comparison not done | One day, one area, count by UTC acq_date |
| P3 | P1 | Samiul | Video, slides, submission checklist | docs/demo_script.md has the 3-minute path and 8 slides |
| P4 | P1 | Sheikh | Data credits and AI-use disclosure in the submission | NASA FIRMS, geoBoundaries, MCD12C1, CHIRPS, NASA POWER; AI use per NOTES.md |

## 6. Does it meet the challenge?
| Challenge asks for | Built | Status |
|---|---|---|
| Harmonize split MODIS / VIIRS records | one series in SNPP terms; observed / adjusted / modeled labels; per-satellite fitting | done (synthetic) |
| Burning-activity calendar from hot spots | weekly calendar heatmap, years × weeks, seams marked | done |
| Selected area of interest | draw rectangle or polygon, or demo areas; size limit with a clear message | done |
| Historical patterns over two decades | Nov 2000 to now, 90% bands on modeled weeks | done (synthetic) |
| Unusual conditions | flagged weeks (climatology + lower-bound rule), seam check | done |
| Critical periods | ranked periods, select one to map it | done |
| Wildfires vs agricultural burns | agri_share from cropland fraction; season rule fallback | done (synthetic land cover) |
| When and where | calendar + where map per 0.1° cell for any selected week or period | done |
| Early warning, responders, land managers | current-status card with data-through date; outlook; CSV export; print view | done; needs live NRT data |
| Whole planet | pipeline is global; demo loads South Asia only (stated in the app) | partly (by design) |
| Web application | React app + API + static fallback | done locally; not deployed |

## 7. Ground rules (unchanged)
One writer per path (docs/FILE_OWNERSHIP.md). Branch, save, ship with scripts/git/. Never claim causes. Never hide
that a value is modeled. Keys only in .env.
