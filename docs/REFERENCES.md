# References

Every external resource FireSense uses, with what we use it for. The code is Apache-2.0 (see [LICENSE](../LICENSE)).
Data products stay under their providers' terms.

## NASA data

- **NASA FIRMS active fires: MODIS Collection 6.1 (Terra, Aqua), VIIRS 375 m (Suomi NPP, NOAA-20, NOAA-21), archive
  and near-real-time.** The fire detections that the whole record is built from. Archive downloads, country files and
  the area API. <https://firms.modaps.eosdis.nasa.gov/>
  - Archive download: <https://firms.modaps.eosdis.nasa.gov/download/>
  - Country downloads: <https://firms.modaps.eosdis.nasa.gov/country/>
  - API key registration: <https://firms.modaps.eosdis.nasa.gov/api/map_key/>
  - Fire alert notes (MODIS 1 km vs VIIRS 375 m, missed detections): <https://firms.modaps.eosdis.nasa.gov/alerts/notes.php>
- **MODAPS Suomi NPP outage table.** Verifies the satellite outage registry (`common/outages.yaml`), so missing
  acquisitions are not counted as zero fires.
  <https://modaps.modaps.eosdis.nasa.gov/services/production/outages_suomi_npp.html>
- **MODIS MCD12C1 Collection 6.1 land cover (LP DAAC, via Earthdata).** Cropland fraction per cell (IGBP class 12
  plus half of class 14), used for landcover strata and the cropland-associated share.
  <https://search.earthdata.nasa.gov> (sign-in: <https://urs.earthdata.nasa.gov>)
- **NASA POWER daily weather (temperature, precipitation, topsoil wetness).** Weather associations on the drivers
  panel. <https://power.larc.nasa.gov/>

## Other data

- **CHIRPS 2.0 daily rainfall (Climate Hazards Center, UC Santa Barbara).** An optional alternative rainfall source
  supported by `ws3_anomaly/loaders/weather.py`; the current release uses NASA POWER.
  <https://www.chc.ucsb.edu/data/chirps>

## Boundaries and maps

- **geoBoundaries ADM1, Bangladesh (BGD-ADM1-32408957, CC0 1.0).** Division boundaries for the named-area explorer.
  <https://www.geoboundaries.org/api/current/gbOpen/BGD/ADM1/>
- **geoBoundaries ADM1, India (IND-ADM1-1811400), from DataMeet India / Election Commission of India, CC BY 2.5 IN.**
  Punjab, Haryana and Delhi boundaries. <https://www.geoboundaries.org/api/current/gbOpen/IND/ADM1/> ·
  <https://github.com/datameet/maps> · licence: <https://creativecommons.org/licenses/by/2.5/in/>
- **OpenStreetMap tiles.** The basemap. Attribution shown on the map: "© OpenStreetMap contributors".
  <https://www.openstreetmap.org/copyright> · tile policy: <https://operations.osmfoundation.org/policies/tiles/>

## Software

Python packages (`requirements.txt`; licences from the installed package metadata):

- pandas: tables and time series (BSD-3-Clause)
- pyarrow: Parquet files (Apache-2.0)
- duckdb: installed with the environment; checked by the setup scripts (MIT)
- numpy: arrays (BSD-3-Clause)
- scipy: statistics and permutation tests (BSD-3-Clause)
- scikit-learn: cross-validation and AUC scores for the sensor-drift check (BSD-3-Clause)
- lightgbm: harmonization candidate model, drift classifier and outlook quantiles (MIT)
- statsmodels: STL seasonal decomposition for anomalies (BSD-3-Clause)
- shapely: geometry (BSD-3-Clause)
- geopandas: boundary files and clipping (BSD-3-Clause)
- pyhdf: reading MCD12C1 HDF4 files (MIT)
- rasterio: raster reading (BSD-3-Clause)
- xarray: gridded data (Apache-2.0)
- rioxarray: raster support for xarray (Apache-2.0)
- netCDF4: NetCDF files (MIT)
- requests: HTTP downloads from FIRMS and POWER (Apache-2.0)
- fastapi: the API (MIT)
- uvicorn: the API server (BSD-3-Clause)
- pydantic: request and response models (MIT)
- pyyaml: configuration files (MIT)
- jsonschema: data-contract checks (MIT)
- openapi-spec-validator: API spec checks (Apache-2.0)
- openapi-schema-validator: API response checks (BSD-3-Clause)
- pytest: tests (MIT)
- httpx: API test client (BSD-3-Clause)
- xgboost (`requirements-cuda.txt`): the GPU candidate model compared against B1 (Apache-2.0)

Web app packages (`ws5_frontend/package.json` "dependencies"):

- react, react-dom: the user interface (MIT)
- leaflet: the map (BSD-2-Clause)
- recharts: charts (MIT)
- d3-scale, d3-scale-chromatic: calendar colour scales (ISC)
- i18next, react-i18next: interface text (MIT)
- @fontsource/ibm-plex-sans: the interface font (OFL-1.1)

## Papers and articles

- NASA Science, crop-residue burning in Punjab (background on the Punjab paddy season):
  <https://science.nasa.gov/?p=1160169>
