"""Demo regions, satellites and their operating windows (docs/AI_PREAMBLE.md, decisions 17-19)."""
from __future__ import annotations

import datetime as dt

DEMO_REGIONS = {
    "BD": {"name": "Bangladesh", "bbox": (88.0, 20.5, 92.7, 26.7)},
    "PB": {"name": "Punjab-Haryana-Delhi", "bbox": (73.5, 28.0, 78.0, 32.5)},
}

SATS = ("Terra", "Aqua", "SNPP", "NOAA20", "NOAA21")
SENSOR_OF = {"Terra": "MODIS", "Aqua": "MODIS", "SNPP": "VIIRS", "NOAA20": "VIIRS", "NOAA21": "VIIRS"}

# First and last day of FIRMS data per satellite. None = still operating.
# Standard-product start dates from the FIRMS archive page (checked 3 Nov 2026): MODIS C6.1 1 Nov 2000,
# VIIRS S-NPP 20 Jan 2012, NOAA-20 1 Apr 2018, NOAA-21 1 Mar 2023. Aqua's MODIS fire data start 4 Jul 2002.
WINDOWS = {
    "Terra": (dt.date(2000, 11, 1), None),
    "Aqua": (dt.date(2002, 7, 4), None),
    "SNPP": (dt.date(2012, 1, 20), dt.date(2026, 11, 2)),
    "NOAA20": (dt.date(2018, 4, 1), None),
    "NOAA21": (dt.date(2023, 3, 1), None),
}

SNPP_CUTOFF = dt.date(2026, 11, 2)
AQUA_START = dt.date(2002, 7, 4)

# Known outage windows (local solar days are excluded whole). Source: NASA Earthdata alert, Mar 2026.
OUTAGES = [
    ("Terra", dt.date(2026, 3, 26), dt.date(2026, 3, 27), "MODIS standby; data flagged questionable"),
]

SEASON_START_MONTH = 10  # season = Oct 1 to Sep 30


def sat_combo(date) -> str:
    """MODIS satellite combination for a date: terra_only before Aqua's first day, else terra_aqua (decision 19)."""
    return "terra_only" if date < AQUA_START else "terra_aqua"
