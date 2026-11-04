# Sheikh's guide: from the zip to a submitted project

Every command here can be copied as it is. Run them from the repo folder (`nasa-modis-viirs/`) unless a block says
otherwise. Linux/macOS commands use bash; Windows commands use PowerShell (the git scripts need Git Bash).

Contents: 1 What you have · 2 Accounts · 3 Datasets · 4 Setup · 5 Real-data run and ML training · 6 Checking results ·
7 Deploying · 8 GitHub and the team · 9 Manual workflows by person · 10 Event runbook · 11 Troubleshooting

---

## 1. What you have
- The team repository with its git history: starter kit, kit-review fixes, then one commit per workstream, authored as
  its owner and stating that it was written with Claude at your direction.
- Working code for all six workstreams, tested on **synthetic** data (70 Python tests, 3 web tests, contract check on
  every output, checked in a browser). No real fire data has been used yet.
- `docs/ONBOARDING.md`: status, project structure and the prioritized gap list (owners, P0/P1/P2).

---

## 2. Accounts (do these first; most are free and instant)
| Account | Who | Why | Where |
|---|---|---|---|
| GitHub | everyone | repo, pull requests | https://github.com |
| NASA Earthdata Login | everyone | FIRMS archive, MCD12C1 land cover | https://urs.earthdata.nasa.gov |
| FIRMS MAP_KEY (one per person: limits are per key) | everyone who downloads | FIRMS area API | https://firms.modaps.eosdis.nasa.gov/api/map_key/ |
| Hugging Face (Spaces) or Render | Sattyam | API hosting (Docker) | https://huggingface.co/spaces · https://render.com |
| Netlify, Cloudflare Pages or GitHub Pages | Shammo, Sattyam | web app and static fallback | any static host |
| Space Apps team registration | Sheikh | submission | https://www.spaceappschallenge.org |

FIRMS API limit: 5,000 transactions per 10 minutes per MAP_KEY; larger day ranges count as several transactions.

---

## 3. Datasets
| # | Dataset | Used for | Source | Access | Format | Put it in | Owner |
|---|---|---|---|---|---|---|---|
| 1 | FIRMS MODIS C6.1 active fires (Terra, Aqua), 1 Nov 2000 → | model inputs before and after 2012 | FIRMS country yearly CSV or archive download | Earthdata Login or email code | CSV | `data/raw/firms/` | Monazir |
| 2 | FIRMS VIIRS S-NPP 375 m, 20 Jan 2012 → 2 Nov 2026 | observed reference series | same | same | CSV | `data/raw/firms/` | Monazir |
| 3 | FIRMS VIIRS NOAA-20 375 m, 1 Apr 2018 → | values after the SNPP cutoff; SNPP/NOAA-20 ratio | same + area API for recent weeks | MAP_KEY for the API | CSV | `data/raw/firms/` | Monazir |
| 4 | FIRMS VIIRS NOAA-21 375 m, 1 Mar 2023 → | optional second VIIRS | same | same | CSV | `data/raw/firms/` | Monazir |
| 5 | geoBoundaries ADM1, Bangladesh (BGD) and India (IND) | regions (admin1) | geoBoundaries API | none | GeoJSON | `data/raw/boundaries/` | Sattyam |
| 6 | MODIS MCD12C1 v061 land cover, yearly, 0.05° | cropland fraction (agricultural tag), strata | LP DAAC (Earthdata Search) | Earthdata Login | HDF4 | `data/raw/landcover/` | Sattyam |
| 7 | NASA POWER daily (T2M, PRECTOTCORR, GWETTOP) | driver associations, forecast | POWER API | none | JSON → cached Parquet | `data/interim/monazir/` (automatic) | Monazir |
| 8 | CHIRPS daily rainfall (optional, instead of POWER rain) | drivers | CHC UCSB | none | GeoTIFF | `data/raw/chirps/` | Monazir |
| 9 | MODIS/VIIRS burned area (stretch, validation only) | comparison with burned area | UMD sftp (FIRMS archive page lists it) | login in the product user guide | HDF/GeoTIFF | `data/raw/burned/` | Samin |
| 10 | OpenAQ PM2.5 (stretch) | consistency check | https://openaq.org | free API key | JSON | `data/raw/openaq/` | Samiul |

Data credits for the submission: NASA FIRMS (MODIS C6.1, VIIRS 375 m), geoBoundaries (licence in each file's
`boundaryLicense`), MODIS MCD12C1 (LP DAAC, DOI 10.5067/MODIS/MCD12C1.061), NASA POWER, CHIRPS if used.

### 3.1 FIRMS history (fastest route: country yearly files)
1. Open https://firms.modaps.eosdis.nasa.gov/country/ (linked from the archive page).
2. For **Bangladesh** and **India**, download every year for **MODIS**, **VIIRS S-NPP** and **VIIRS NOAA-20**
   (NOAA-21 optional). These are standard-product files; recent months may be missing (standard data lags about 5 months).
3. Save the CSVs in `data/raw/firms/`. Any file names work; the ingest step reads every CSV there and keeps only the
   demo-region boxes (`--clip demo`), so the India files are cut to Punjab–Haryana–Delhi automatically.
4. Delete the synthetic files so they are not mixed in:
```bash
rm -f data/raw/firms/synthetic_*.csv.gz
```
```powershell
Remove-Item data\raw\firms\synthetic_*.csv.gz -ErrorAction SilentlyContinue
```

Alternative (slower): the archive request at https://firms.modaps.eosdis.nasa.gov/download/ (draw the two boxes, pick
each source and the full date range, CSV). Links arrive by email. The archive also covers recent months as near-real-time data.

### 3.2 FIRMS recent weeks (gap between the last standard file and today) via the API
```bash
cp -n .env.example .env            # then put your key in .env: FIRMS_MAP_KEY=xxxx
export $(grep -v '^#' .env | xargs)
. .venv/bin/activate
# NOAA-20 near-real-time, both demo regions, from the day after your last standard file to today:
python -m ws3_anomaly.ingest.firms --source VIIRS_NOAA20_NRT --bbox 88,20.5,92.7,26.7 --start 2026-06-01 --end 2026-11-14
python -m ws3_anomaly.ingest.firms --source VIIRS_NOAA20_NRT --bbox 73.5,28,78,32.5   --start 2026-06-01 --end 2026-11-14
python -m ws3_anomaly.ingest.firms --source MODIS_NRT        --bbox 88,20.5,92.7,26.7 --start 2026-06-01 --end 2026-11-14
python -m ws3_anomaly.ingest.firms --source MODIS_NRT        --bbox 73.5,28,78,32.5   --start 2026-06-01 --end 2026-11-14
```
```powershell
Copy-Item .env.example .env -ErrorAction SilentlyContinue   # then edit .env: FIRMS_MAP_KEY=xxxx
$env:FIRMS_MAP_KEY = "xxxx"
.venv\Scripts\python -m ws3_anomaly.ingest.firms --source VIIRS_NOAA20_NRT --bbox 88,20.5,92.7,26.7 --start 2026-06-01 --end 2026-11-14
.venv\Scripts\python -m ws3_anomaly.ingest.firms --source VIIRS_NOAA20_NRT --bbox 73.5,28,78,32.5 --start 2026-06-01 --end 2026-11-14
```
SNPP near-real-time ended on 2 Nov 2026 (the script refuses `VIIRS_SNPP_NRT`); take SNPP up to 2 Nov from the archive.
Overlapping standard and NRT rows are de-duplicated at ingest (standard wins). Windows are cached, so a rerun resumes.

### 3.3 Admin1 boundaries (geoBoundaries)
```bash
mkdir -p data/raw/boundaries
. .venv/bin/activate
python - <<'EOF'
import json, requests
for iso in ("BGD", "IND"):
    meta = requests.get(f"https://www.geoboundaries.org/api/current/gbOpen/{iso}/ADM1/", timeout=60).json()
    gj = requests.get(meta["gjDownloadURL"], timeout=300).content
    open(f"data/raw/boundaries/{iso}_ADM1.geojson", "wb").write(gj)
    print(iso, "licence:", meta.get("boundaryLicense"), "->", f"data/raw/boundaries/{iso}_ADM1.geojson")
EOF
```
(Windows: save the Python part as `get_boundaries.py` and run `.venv\Scripts\python get_boundaries.py`.)

### 3.4 Land cover (MCD12C1 v061)
1. Sign in at https://search.earthdata.nasa.gov, search **MCD12C1 061**, pick the newest year, download the `.hdf` file.
2. Save it as `data/raw/landcover/MCD12C1.A2024001.061.<...>.hdf` (keep the original name; it starts with `MCD12C1`).
3. The cells step reads `Land_Cover_Type_1_Percent` with pyhdf; cropland = IGBP class 12 plus half of class 14.

### 3.5 Weather (NASA POWER), cached once
```bash
. .venv/bin/activate && python -m ws3_anomaly.loaders.weather --start 2000-11-01 --end 2026-11-14
```
This calls POWER once per 0.5° tile (about 210 calls; 20-40 minutes). Cached JSON goes to `data/raw/power/`, weekly
anomalies to `data/interim/monazir/weather_BD.parquet` and `weather_PB.parquet`. Without this cache, drivers report
"weather data not loaded" in real mode (synthetic weather is never used with real fires).

---

## 4. Setup (once per laptop)
```bash
# Linux / macOS: Python 3.11, Node 22 LTS and git must be installed
cd nasa-modis-viirs
bash scripts/setup.sh --ui-only        # initialize mock/UI development
bash scripts/start.sh --mock            # look at the app on fixtures: http://localhost:5173
```
```powershell
# Windows PowerShell
cd nasa-modis-viirs
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 -UiOnly
powershell -ExecutionPolicy Bypass -File scripts\start.ps1 -Mock
```
Setup does not train or download data. Follow [TRAINING.md](TRAINING.md) to initialize CUDA and train on real inputs.

---

## 5. Real-data CUDA training

Use the current [CUDA training guide](TRAINING.md) for initialization, readiness, quick/full runs, monitoring, recovery, and publishing. The former CPU timings and commands in this section are obsolete and have been removed.

The supported setup installs the complete environment from `requirements-cuda.txt`; setup no longer launches any pipeline. Select menu 1 for CUDA setup, 12 for GPU verification, 2 for readiness, and 4/5 for quick/full training. For dataset-free UI development use `-UiOnly` or `--ui-only`, then `python scripts/workflow.py dev --mock --open`.

The GPU candidate is XGBoost CUDA (Poisson counts, Tweedie FRP). B1 remains a scientific comparator and can win. Selection now averages both Terra+Aqua and Terra-only holdouts. Model artifacts and evidence are explained in [CUDA operations](CUDA_PIPELINE.md); the two GPU timing ranges are in [GPU estimates](GPU_TRAINING_TIMES.md).

### 5.3 Design review after the first real run (Sheikh + Samin, 20 minutes; H12 in the plan)
| Look at | File | Good sign | If not |
|---|---|---|---|
| Method chosen and its margin | validation/harmonization.json | CCC above 0.8 on the backward holdout | say "ratio-based estimate" and keep B1 |
| Terra-only rows | same, `(terra_only inputs)` rows | bias within ±20% | widen the 2000-2002 caveat in the method text |
| Interval coverage | validation/intervals.json | 0.88-0.95 overall | rerun intervals; report the gap per land cover |
| Drift flags | validation/drift.json | flags after 2021 (Terra/Aqua drift), few before | read the reasons; mention them in limitations |
| Seam | `qa.json` → seam_flag_rates | similar flag rates before and after 2012 | keep FLAG_RULE = "value" (decision 21) |
| Forecast skill | validation/outlook_skill.json | CI above 0 | the app already hides the forecast when it has no skill |
| Manual count | FIRMS map, one day, one area | matches detections.parquet (count by UTC acq_date) | check the ingest filters |

---

## 6. Checking results
```bash
. .venv/bin/activate
python -m pytest -q                                   # all tests (data and API tests use data/processed)
python tools/verify_files.py data/processed/*.parquet data/processed/*.json data/processed/validation/*.json
python -m ws6_validation.qa                           # writes validation/qa.json and prints the summary
API_BASE_URL=http://localhost:8000 python -m pytest -q ws6_validation/tests   # against a running API
cd ws5_frontend && npm run check:strings && npm test && npm run build
```
Remove the "synthetic data" banner only after a real run: delete the `app.synthetic` text in
`ws5_frontend/src/i18n/en.json` and `bn.json` (Shammo), and the "SYNTHETIC" lines in the validation limitations.

---

## 7. Deploying
### 7.1 API on Hugging Face Spaces (Docker), Sattyam
```bash
# after a pipeline run; needs git and a Hugging Face account (huggingface.co/new-space -> SDK: Docker)
git clone https://huggingface.co/spaces/<you>/fire-calendar-api space && cd space
rsync -a --exclude .git --exclude node_modules --exclude .venv ../nasa-modis-viirs/{common,ws1_harmonize,ws2_platform,ws3_anomaly,ws4_outlook,tools,contracts,requirements.lock.txt} .
mkdir -p data/processed/validation
cp ../nasa-modis-viirs/data/processed/{cells.parquet,harmonized.parquet,sensor_days.parquet,interval_table.json,drivers_region.json,outlook_region.json} data/processed/
cp ../nasa-modis-viirs/data/processed/validation/*.json data/processed/validation/
cp ws2_platform/Dockerfile Dockerfile
printf -- '---\ntitle: Fire Calendar API\nsdk: docker\napp_port: 7860\n---\n' > README.md
git add -A && git commit -m "API with data" && git push
# then: https://<you>-fire-calendar-api.hf.space/health
```
Free Spaces sleep when idle: open `/health` a few minutes before the demo. Render works the same way with the Dockerfile.

### 7.2 Static fallback and web app, Sattyam and Shammo
```bash
. .venv/bin/activate && python -m ws2_platform.api.static_export --out ws2_platform/static_fallback
# deploy ws2_platform/static_fallback/ as its own static site (Netlify drag-and-drop works), note its URL
cd ws5_frontend
VITE_API_BASE_URL=https://<you>-fire-calendar-api.hf.space VITE_FALLBACK_BASE_URL=https://<fallback-site> npm run build
# deploy ws5_frontend/dist/ to Netlify / Cloudflare Pages / GitHub Pages
```
Test the fallback: break the API URL in the browser's devtools (or stop the Space) and reload; the app says it is
showing saved data.

---

## 8. GitHub and the team
### 8.1 Push (you, once). Repo must be empty; the script never force-pushes.
```bash
gh auth login                       # or sign in through Git Credential Manager
bash scripts/push_to_github.sh      # shows the 8 commits and asks before pushing
bash scripts/git/setup.sh sheikh2583
bash scripts/git/invite_collaborators.sh
bash scripts/git/protect_main.sh    # PRs + guard check on main, merged branches auto-deleted
```
```powershell
gh auth login
powershell -ExecutionPolicy Bypass -File scripts\push_to_github.ps1
# then the three scripts/git/*.sh lines above in Git Bash
```
Before pushing: read the Space Apps terms on pre-event work (gap R1), add a LICENSE (gap R2), and get each teammate's OK
for commits in their name (gap R5).

### 8.2 Every teammate, once
```bash
git clone https://github.com/sheikh2583/NASA-Space-App nasa-space-apps && cd nasa-space-apps
bash scripts/setup.sh --no-pipeline
bash scripts/git/setup.sh <their-github-username>
```
Daily loop: `bash scripts/git/start.sh <topic>` → work in your folder → `bash scripts/git/save.sh "message"` →
`bash scripts/git/ship.sh` (rebases, tests, pushes, opens the PR). After the merge: `bash scripts/git/cleanup.sh`.

### 8.3 Sharing data (not in git)
Put `data/raw/` and `data/processed/` in the shared Google Drive folder after the first real run. Teammates copy them
into their own `data/` instead of downloading again, and add a line to `data/MANIFEST.md` for every hand-off.

---

## 9. Manual workflows by person (an AI agent cannot do these)
| Person | Before the event | At the event |
|---|---|---|
| Sheikh | read Space Apps terms; LICENSE; push; invite; protect main; confirm team registration; get teammates' OK on authorship | kickoff; gates and check-ins; H12 design review; merge PRs in dependency order; submit at H46; open every link in a private window |
| Sattyam | hosting accounts; boundaries (3.3); land cover (3.4) | deploy API (7.1) and fallback (7.2); cold-start check; final deploy with rollback noted |
| Monazir | confirm GitHub handle `Monajir`; Earthdata + MAP_KEY; FIRMS files (3.1, 3.2); weather (3.5) | ingest; driver wording review with Shammo; check anomalies on the deployed app |
| Samin | Earthdata login (burned area, stretch) | read coverage and drift after the real run; agree the no-skill wording with Shammo |
| Shammo | check the app on a real phone and with a colour-blindness simulator | deploy the web app; translate driver caveats; screenshots for slides; Bangla rendering on a phone |
| Samiul | find a fluent Bangla reviewer | manual FIRMS count (one day, one area); QA runs at each gate; slides with real numbers; record and upload the video; submission checklist |

---

## 10. Event runbook (48 hours; shift if the venue hours differ)
| Hours | Goal | Commands / actions |
|---|---|---|
| H0-1 | everyone running | each laptop: section 4; Sheikh: kickoff, read decisions 17-23 aloud |
| H0-3 | real data in | Monazir 3.1-3.2 and 3.5; Sattyam 3.3-3.4; put files in the shared drive |
| H3-4 | first real run | Sheikh: `python scripts/run_pipeline.py --quick`; share data/processed |
| H4-6 | design review | section 5.3; decide claims; Samiul manual count |
| H6-8 | deploy | Sattyam 7.1-7.2; Shammo deploys the app; Samiul runs QA against the live URL |
| H8-24 | improve | gap list in ONBOARDING.md section 5 (P1 items), one PR per folder |
| H24-36 | full run + freeze | full CUDA training and scientific QA; redeploy reviewed results; feature freeze at H36 |
| H36-42 | polish | Bangla review; slides; rehearse demo_script.md |
| H42-46 | ship | final deploy; video; submission checklist; submit at H46 |

---

## 11. Troubleshooting
| Problem | Fix |
|---|---|
| `pip install` fails on Windows for the pinned versions | setup falls back to requirements.txt; if `pyhdf` still fails, skip land cover (cropland stays empty, agri tag uses the season rule) |
| UI/reference dependency import error on macOS (`libomp`) | `brew install libomp`; CUDA training requires an NVIDIA Windows/Linux host |
| `Python 3.11 not found` | install from python.org (Windows: tick "Add to PATH"), or `pyenv install 3.11` |
| Out of memory in the model step | stop concurrent runs; inspect GPU/RAM usage and follow [CUDA recovery](TRAINING.md). Transfer to a suitable NVIDIA host with the same inputs if needed; `--quick` reduces evaluation folds, not necessarily peak fit memory |
| `guard: blocked` when committing | you changed a file outside your folder; see docs/WORKING_TOGETHER.md section 7 |
| GitHub says the PR has conflicts in data/MANIFEST.md | run `bash scripts/git/ship.sh` again (it rebases and keeps both lines) |
| FIRMS API returns errors | check https://firms.modaps.eosdis.nasa.gov (outage notices); rerun: cached windows are skipped |
| App shows "The data service did not answer" | API not running or wrong `VITE_API_BASE_URL`; `curl http://localhost:8000/health` |
| Port 8000 or 5173 busy | stop the other process, or `uvicorn ... --port 8010` and set `VITE_API_BASE_URL` to match |
