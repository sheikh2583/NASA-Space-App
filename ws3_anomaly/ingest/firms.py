"""NASA FIRMS downloads: area API in day windows, with retry, resume and a raw-file cache.

Sources (decision 7, 17): MODIS_SP / MODIS_NRT, VIIRS_SNPP_SP (history to 2 Nov 2026),
VIIRS_NOAA20_SP / VIIRS_NOAA20_NRT, VIIRS_NOAA21_NRT. The MAP_KEY comes from the FIRMS_MAP_KEY environment
variable, never from code. Limits (day window, transactions per 10 minutes) are confirmed at H0-02; the
defaults below are conservative.

Usage: python -m ws3_anomaly.ingest.firms --source VIIRS_NOAA20_NRT --bbox 88,20.5,92.7,26.7 \
           --start 2026-11-01 --end 2026-11-10 --out data/raw/firms
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import logging
import os
import re
import time
from urllib.parse import quote, quote_plus

import pandas as pd
import requests

API = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{source}/{bbox}/{days}/{date}"
SOURCES = ("MODIS_SP", "MODIS_NRT", "VIIRS_SNPP_SP", "VIIRS_SNPP_NRT", "VIIRS_NOAA20_SP", "VIIRS_NOAA20_NRT",
           "VIIRS_NOAA21_NRT")
RETIRED = {"VIIRS_SNPP_NRT": "SNPP near-real-time ended on 2 Nov 2026; use VIIRS_NOAA20_NRT (decision 17)"}
MAX_DAYS = 10
log = logging.getLogger("firms")


def _redact(text, key):
    """Remove the credential in URL, escaped-body and ordinary exception representations."""
    text = str(text)
    if not key:
        return text
    variants = {str(key), quote(str(key), safe=""), quote_plus(str(key)),
                repr(str(key))[1:-1]}
    for value in sorted(variants, key=len, reverse=True):
        text = re.sub(re.escape(value), lambda match: "***", text, flags=re.IGNORECASE)
    return text


def windows(start: dt.date, end: dt.date, size: int = MAX_DAYS):
    """(first_day, n_days) windows covering [start, end]."""
    d = start
    while d <= end:
        n = min(size, (end - d).days + 1)
        yield d, n
        d += dt.timedelta(days=n)


def url(key: str, source: str, bbox, first: dt.date, n_days: int) -> str:
    b = ",".join(f"{v:g}" for v in bbox)
    return API.format(key=key, source=source, bbox=b, days=n_days, date=first.isoformat())


def fetch_window(session, key, source, bbox, first, n_days, retries=4, pause=2.0) -> pd.DataFrame:
    """One API call with exponential back-off. An 'Invalid' or HTML body raises; an empty CSV is a valid zero."""
    if not isinstance(retries, int) or retries < 1:
        raise ValueError("retries must be a positive integer")
    last = "FIRMS request failed"
    for attempt in range(retries):
        try:
            r = session.get(url(key, source, bbox, first, n_days), timeout=120)
            if r.status_code == 200 and r.text.lstrip().startswith(("latitude", "country_id")):
                return pd.read_csv(io.StringIO(r.text))
            # Redact BEFORE truncation/repr so a partial or escaped key cannot survive.
            last = f"HTTP {r.status_code}: {_redact(r.text, key)[:200]!r}"
        except requests.RequestException as e:
            last = _redact(e, key)
        except Exception as e:
            # Parsing failures must also lose their original exception context.
            last = _redact(e, key)
            break
        if attempt + 1 < retries:
            time.sleep(pause * 2 ** attempt)
    # Raise outside the handler: no original URL-bearing exception is retained as context.
    raise RuntimeError(_redact(last, key)) from None


def download(source, bbox, start, end, out_dir, key=None, session=None, pause_between=1.0):
    """Download [start, end] in windows; each window is cached as its own CSV so a rerun resumes."""
    if source in RETIRED:
        raise ValueError(RETIRED[source])
    key = key or os.environ.get("FIRMS_MAP_KEY")
    if not key:
        raise RuntimeError("Set FIRMS_MAP_KEY in your .env (each person registers their own key).")
    session = session or requests.Session()
    directory_error = None
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as e:
        directory_error = _redact(e, key)
    if directory_error is not None:
        raise RuntimeError(directory_error) from None
    gaps, paths = [], []
    for first, n in windows(start, end):
        path = os.path.join(out_dir, f"{source}_{'_'.join(f'{v:g}' for v in bbox)}_{first}_{n}.csv")
        if not os.path.exists(path):
            try:
                df = fetch_window(session, key, source, bbox, first, n)
                df.to_csv(path + ".part", index=False)
                os.replace(path + ".part", path)
            except Exception as e:  # logged and listed; the rest continues
                message = _redact(e, key)
                log.warning("gap %s %s+%d: %s", _redact(source, key), first, n, message)
                gaps.append((first.isoformat(), n, message))
                continue
            time.sleep(pause_between)
        paths.append(path)
    return paths, gaps


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, choices=SOURCES)
    ap.add_argument("--bbox", required=True, help="min_lon,min_lat,max_lon,max_lat")
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--out", default="data/raw/firms")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO)
    bbox = [float(v) for v in a.bbox.split(",")]
    paths, gaps = download(a.source, bbox, dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end), a.out)
    print(f"{len(paths)} windows cached; {len(gaps)} gaps")
    for g in gaps:
        print("GAP", *g)


if __name__ == "__main__":
    main()
