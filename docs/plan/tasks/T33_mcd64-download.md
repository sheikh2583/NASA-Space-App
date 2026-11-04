---
id: T33
title: Download MODIS burned-area tiles (MCD64A1) with the Earthdata token
kind: agent
owner: Sheikh
authors: [Sheikh]
phase: P2
size: S
needs: [T00]
requires: [secret:EARTHDATA_TOKEN]
branch: ws1/T33-mcd64-download
touches: [data/MANIFEST.md]
creates: [tools/get_mcd64a1.py, scripts/tests/test_get_mcd64a1.py]
checks: [CHECK-PLAN, "python -m pytest -q scripts/tests/test_get_mcd64a1.py"]
---
## Goal
Get the independent burned-area product, so T24 can check our season totals and timing against it.
- This needs an Earthdata bearer token in `.env` as `EARTHDATA_TOKEN`. Generate it under the Earthdata profile's
  "Generate Token" page, using the same Earthdata account as for MCD12C1.
- If the token is missing, `plan.py next` skips this card. Sheikh can then cut T33 and T24, which are 3rd in the cut
  order.

## Steps
1. **`tools/get_mcd64a1.py`.** Standard library plus `requests`, which is already a dependency.
   - Find files with NASA CMR search:
     `https://cmr.earthdata.nasa.gov/search/granules.json?short_name=MCD64A1&version=061&temporal=<start>,<end>&bounding_box=<w,s,e,n>&page_size=200`.
   - Take each granule's `.hdf` link.
   - Download with the header `Authorization: Bearer <token>` into `data/raw/mcd64a1/`. Skip files that already
     exist; write to a `.part` file and rename it when complete.
   - The token is read from the environment or `.env`. **It is never printed or logged**; strip it from any error
     text.

   Requests:

   | Area | Bounding box | Months | Years | Expected tiles |
   |---|---|---|---|---|
   | Punjab demo | 74.6, 29.8, 76.4, 31.2 | Apr-Jun and Sep-Dec | 2012-2025 | h24v05, h24v06 |
   | Bangladesh demo | 89.5, 23.0, 90.5, 24.0 | Nov-May | 2012-2025 | h26v06 |

   Print the tiles found; they should match the table.
2. **Tests** (`scripts/tests/test_get_mcd64a1.py`), with no network: the CMR JSON parser on a small fixture; month
   windows are generated correctly (including Nov-May across the year end); the token is redacted from error text.
3. Run `python tools/get_mcd64a1.py`. Append one line to `data/MANIFEST.md`: product, tiles, months, file count,
   date. **Never commit `data/raw/`.**
4. Run the checks, mark the card done, `split`, push and open the PR. Paste the file count and tiles into the PR.

## Acceptance
- [ ] The `.hdf` files are in `data/raw/mcd64a1/`, the tiles match the table, and a MANIFEST line is added.
- [ ] No token appears in output or files.

## Stop and ask if
- CMR returns no granules for a request, or downloads fail with 401 twice. The token may be expired; Sheikh
  regenerates it.
