---
id: T32
title: Verify and complete the outage registry from NASA's MODAPS table
kind: agent
owner: Sheikh
authors: [Sheikh, Samin]
phase: P0
size: M
needs: [T00]
requires: [network]
branch: ws1/T32-registry-verify
touches: [common/outages.yaml]
creates: [tools/modaps_outages.py, scripts/tests/test_modaps_outages.py]
checks: [CHECK-PLAN, CHECK-PY]
---
## Goal
Every outage that will change our numbers must match NASA's own table. 24 entries were copied from a page summary
(`verification: transcribed`), and entries before 2024 are missing. Check them against the table and complete them,
automatically.

## Context
- Source: https://modaps.modaps.eosdis.nasa.gov/services/production/outages_suomi_npp.html. The table's columns are
  Year-Day, Date, Start Time (UTC), End Time (UTC) and Comments. It starts in Nov 2011.
- A granule "inclusive" end means end + 6 minutes.
- The registry format and loader are in `common/outages.yaml` and `ws2_platform/coverage.load_registry`.

## Steps
1. **`tools/modaps_outages.py`.** Standard library plus `pandas`.
   - `fetch(url) -> str` returns the HTML. Use `urllib.request`. If the shell can't reach the site, save the page from
     the IDE's web tool to `data/raw/modaps_outages.html` and read it from there.
   - `parse(html) -> DataFrame` with columns `start_utc`, `end_utc` (pandas Timestamps, UTC) and `comment`, one row
     per table row.
     - Multi-day rows ("2024-307 - 2024-311") use the first day for the start and the last day for the end.
     - An end time of "00:00:00" on a multi-day row means the start of that last day. On a single-day row it means
       the end of that day.
   - `compare(registry, table)`: for each registry SNPP entry, the best-matching table row (overlap ≥ 50%) and the
     differences in minutes.
   - `propose(table, min_hours=1.0, years=(2012, 2023))`: new entries for rows of at least one hour.
2. **Tests** (`scripts/tests/test_modaps_outages.py`). Use a small HTML fixture written in the test, containing the
   2024-307 GPS row and two short rows.
   - Parsing gives 2 Nov 22:12 to 6 Nov 17:36 for the GPS row (end + 6 minutes for "inclusive").
   - `compare` finds it.
   - `propose` keeps only rows of at least one hour.
3. **Run.**
   - For each `transcribed` entry, set `verification: table_and_data` and append "checked against MODAPS table
     <date>" to `note` when start and end match within 6 minutes.
   - Correct it when it is further off, recording the old value in `note`.
   - Set `rejected` when there is no match.
   - Append the proposed 2012-2023 entries with `verification: table_and_data`, ids `snpp-YYYY-MM-DD-<word>`, and the
     table comment as `note`.
4. `python -m pytest ws2_platform/tests/test_coverage.py -q` must pass; the loader validates every entry.
5. Run the checks, mark the card done, `split` (Sheikh: the tool and test; Samin: `common/outages.yaml`), push and
   open the PR. Paste counts: confirmed, corrected, rejected, added.

## Acceptance
- [ ] No `transcribed` entries remain.
- [ ] Entries from 2012-2023 are added.
- [ ] The coverage tests pass.

## Stop and ask if
- The page layout differs from the description, so parsing finds fewer than 100 rows.
