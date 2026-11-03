# H0 verification list (first 90 minutes)

These close the gaps in docs/KNOWN_GAPS.md. Record each result as one line in docs/DECISIONS.md (what you found, what we do).

| ID | Who | Check | Pass | If it fails |
|---|---|---|---|---|
| H0-01 | Sheikh | Read the official challenge page and rules; ask organizers about hours, deadline, hardware, AI-use disclosure, licence, pre-event files, team size, submission format | answers written down and shared | shift TIMELINE.md; adjust the plan to the rules |
| H0-02 | Monazir | Run prompt P3.1: archive route, API limits, SNPP near-real-time, source-type and confidence fields | one-day pull for MODIS and VIIRS works; limits noted in NOTES.md | use the area API in small windows; use NOAA-20 for the current season; drop wider South Asia |
| H0-03 | Sattyam | Find the land-cover product, its format and the cropland classes; try one tile | a 0.05 degree product loads in under 90 minutes | skip cropland_frac; use the region-season rule |
| H0-04 | Sattyam | Download geoBoundaries ADM1 for Bangladesh, India, Pakistan, Nepal; check ids and licence | admin1 ids load | pick another boundary source |
| H0-05 | Monazir | Fetch one week of CHIRPS and one POWER point or region; note limits and fields | both return values | cut the drivers panel to what loads |
| H0-06 | Everyone | Create your venv, install requirements, run a one-line import check (pandas, pyarrow, duckdb, lightgbm; Sattyam also shapely, geopandas, fastapi) | imports succeed | install with conda or drop geopandas; tell Sheikh |
| H0-07 | Sattyam | Read the free-tier limits of the chosen hosts; deploy hello-world | URL works; limits recorded | switch host; rely on the static fallback |
| H0-08 | Sheikh, Sattyam | After the first slice: count rows, zero fraction at 0.05, 0.1 and 0.25 degrees, memory and runtime of gridding | 0.1 degree is workable | change grid in DECISIONS.md before H8 (needs everyone's agreement) |
| H0-09 | Sheikh | Read NASA and FIRMS notices on Terra, Aqua and SNPP status | status understood | adjust the story and limitations |
| H0-10 | Everyone | Accept the invitation, sign in, clone, run `bash scripts/git/setup.sh <your-github-username>` and `bash scripts/git/status.sh`; confirm shared drive access and the channel | status shows your name, prefix and folder; hello-world PR merged | fix before G0 |

Design review at H12 (Sheikh and Samin, 20 minutes): re-read the harmonization, conformal and drift design against what the data showed, and decide what claims we can make.
