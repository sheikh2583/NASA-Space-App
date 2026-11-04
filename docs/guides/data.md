# Data: what to download and where to put it

Training needs NASA and boundary files on local disk. None of them go into Git. If a teammate already has them, the quickest route is their **input ZIP** (see [teammate training](teammate-training.md)), which skips this page.

## Accounts

| Account | Needed for | Link |
|---|---|---|
| NASA Earthdata Login | FIRMS archive downloads, MCD12C1 land cover | <https://urs.earthdata.nasa.gov> |
| FIRMS MAP_KEY (optional) | Downloading recent weeks through the FIRMS API | <https://firms.modaps.eosdis.nasa.gov/api/map_key/> |

The FIRMS API allows 5,000 transactions per 10 minutes per key. Keep the key in `.env`, never in Git or a `VITE_*` variable.

## Required layout

All paths are relative to the repository root. `bash scripts/setup.sh` / `scripts\setup.ps1` creates the empty folders.

```text
data/
  raw/
    firms/                  FIRMS *.csv or *.csv.gz (extract any downloaded ZIPs)
    boundaries/
      BGD_ADM1.geojson       Bangladesh ADM1 (exact name)
      IND_ADM1.geojson       India ADM1 (exact name)
    landcover/
      MCD12C1*.hdf           original MCD12C1 v061 file name
    power/                   NASA POWER tile cache (created automatically)
  interim/monazir/
    weather_BD.parquet       built by the weather step
    weather_PB.parquet       built by the weather step
```

Readiness (`workflow.py prepare`, run automatically by `scripts/train.*`) checks every item above and tells you what's missing.

## 1. FIRMS active fires

| Product | Period used |
|---|---|
| MODIS C6.1 (Terra and Aqua) | 1 Nov 2000 → |
| VIIRS S-NPP 375 m | 20 Jan 2012 → 2 Nov 2026 (the reference sensor) |
| VIIRS NOAA-20 375 m | 1 Apr 2018 → |
| VIIRS NOAA-21 375 m (optional) | 1 Mar 2023 → |

1. Open the [FIRMS country downloads](https://firms.modaps.eosdis.nasa.gov/country/). For **Bangladesh** and **India**, download every year of MODIS, VIIRS S-NPP and VIIRS NOAA-20 (NOAA-21 optional).
2. Save the CSVs in `data/raw/firms/`. Any file names work, and India is clipped to Punjab–Haryana–Delhi automatically. Extract ZIP files first.
3. Files with `synthetic_` in the name are ignored. Delete them if they're still there.

Alternative: an [archive request](https://firms.modaps.eosdis.nasa.gov/download/) for the two areas. The links arrive by email, and the archive also covers recent months as near-real-time data.

**Recent weeks (optional, needs `FIRMS_MAP_KEY`).** Standard files lag by about five months. Fill the gap through the API. The key must be in the process environment, not just in `.env`:

```bash
export FIRMS_MAP_KEY=xxxx
.venv/bin/python -m ws3_anomaly.ingest.firms --source VIIRS_NOAA20_NRT --bbox 88,20.5,92.7,26.7 --start 2026-06-01 --end 2026-11-02
.venv/bin/python -m ws3_anomaly.ingest.firms --source VIIRS_NOAA20_NRT --bbox 73.5,28,78,32.5 --start 2026-06-01 --end 2026-11-02
```

```powershell
$env:FIRMS_MAP_KEY = 'xxxx'
.venv\Scripts\python -m ws3_anomaly.ingest.firms --source VIIRS_NOAA20_NRT --bbox 88,20.5,92.7,26.7 --start 2026-06-01 --end 2026-11-02
.venv\Scripts\python -m ws3_anomaly.ingest.firms --source VIIRS_NOAA20_NRT --bbox 73.5,28,78,32.5 --start 2026-06-01 --end 2026-11-02
```

Use `--source MODIS_NRT` for MODIS. SNPP near-real-time ended on 2 Nov 2026, so take SNPP from the archive. Overlapping standard and near-real-time rows are de-duplicated (standard wins), and reruns resume. The configured record ends on **2 November 2026**. Extending it means reviewing the sensor windows in `common/regions.py`; changing an end date alone isn't enough.

## 2. Boundaries (geoBoundaries ADM1)

```bash
.venv/bin/python - <<'EOF'
import requests
for iso in ("BGD", "IND"):
    meta = requests.get(f"https://www.geoboundaries.org/api/current/gbOpen/{iso}/ADM1/", timeout=60).json()
    open(f"data/raw/boundaries/{iso}_ADM1.geojson", "wb").write(requests.get(meta["gjDownloadURL"], timeout=300).content)
    print(iso, "licence:", meta.get("boundaryLicense"))
EOF
```

On Windows, save the Python part as `get_boundaries.py` and run `.venv\Scripts\python get_boundaries.py`. Keep the country and ADM IDs as they are.

## 3. Land cover (MODIS MCD12C1 v061)

Sign in to [Earthdata Search](https://search.earthdata.nasa.gov), search **MCD12C1 061**, download the newest yearly `.hdf`, and save it in `data/raw/landcover/` **with its original name** (it starts with `MCD12C1`). Cropland is IGBP class 12 plus half of class 14.

## 4. Weather (NASA POWER)

`scripts/train.*` builds this automatically when the two Parquet files are missing. To build it by hand:

```bash
.venv/bin/python -m ws3_anomaly.loaders.weather --start 2000-11-01 --end 2026-11-03
```

That's about 210 POWER calls (20–40 minutes). No key is needed, and it resumes from the tile cache in `data/raw/power/`. Without it, driver associations report "weather data not loaded".

## Credits

NASA FIRMS (MODIS C6.1, VIIRS 375 m); geoBoundaries (licence in each file's `boundaryLicense`); MODIS MCD12C1 (LP DAAC, DOI 10.5067/MODIS/MCD12C1.061); NASA POWER.

Next: [train](training.md).
