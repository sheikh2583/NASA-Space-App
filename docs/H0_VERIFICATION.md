# H0 verification list (first 90 minutes)

These close the gaps in docs/KNOWN_GAPS.md. Record each result as one line in docs/DECISIONS.md (what you found, what we do).

| ID | Who | Check | Pass | If it fails |
|---|---|---|---|---|
| H0-01 | Sheikh | Read the official challenge page and rules; ask organizers about hours, deadline, hardware, AI-use disclosure, licence, pre-event files, team size, submission format | answers written down and shared | shift TIMELINE.md; adjust the plan to the rules |
| H0-02 | Monazir | Run prompt P3.1: archive route, API limits, NOAA-20 standard product start date and VIIRS_NOAA20_NRT, source-type and confidence fields | one-day pull for MODIS, SNPP (history) and NOAA-20 works; NOAA-20 first date and limits noted in NOTES.md | use the area API in small windows; drop wider South Asia; if the SNPP/NOAA-20 overlap is under 2 years, fit one ratio per region instead of per region-month |
| H0-03 | Sattyam | Find the land-cover product, its format and the cropland classes; try one tile | a 0.05 degree product loads in under 90 minutes | skip cropland_frac; use the region-season rule |
| H0-04 | Sattyam | Download geoBoundaries ADM1 for Bangladesh, India, Pakistan, Nepal; check ids and licence | admin1 ids load | pick another boundary source |
| H0-05 | Monazir | Fetch one week of CHIRPS and one POWER point or region; note limits and fields | both return values | cut the drivers panel to what loads |
| H0-06 | Everyone | Use the Windows/Linux CUDA setup in [TRAINING.md](TRAINING.md); run GPU verification and readiness. UI-only contributors use the UI setup. | pinned dependencies and actual CUDA fit/predict pass on training hosts | fix the reported dependency/driver error; do not bypass the GPU check or drop required packages |
| H0-07 | Sattyam | Read the free-tier limits of the chosen hosts; deploy hello-world | URL works; limits recorded | switch host; rely on the static fallback |
| H0-08 | Sheikh, Sattyam | After the first slice: count rows, zero fraction at 0.05, 0.1 and 0.25 degrees, memory and runtime of gridding | 0.1 degree is workable | change grid in DECISIONS.md before H8 (needs everyone's agreement) |
| H0-09 | Sheikh | Re-check NASA and FIRMS notices: SNPP ended 2 Nov 2026 (answered 3 Nov, decision 17); check whether Aqua or Terra have stopped since, and add any new outage window to sensor_days | status understood; sensor_days updated | adjust the story and limitations |
| H0-11 | Sheikh | Read the Space Apps Participant Terms and Conditions now (pre-event work, AI use, licence, public repo); read the Project Submission and Judging guides when they are published on 13 Nov | answers in DECISIONS.md | adjust the plan before H0 |
| H0-10 | Everyone | Accept the invitation, sign in, clone, run `bash scripts/git/setup.sh <your-github-username>` and `bash scripts/git/status.sh`; confirm shared drive access and the channel | status shows your name, prefix and folder; hello-world PR merged | fix before G0 |

Design review at H12 (Sheikh and Samin, 20 minutes): re-read the harmonization, conformal and drift design against what the data showed, and decide what claims we can make.
