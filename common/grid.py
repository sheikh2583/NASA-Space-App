"""Grid convention (docs/DECISIONS.md decision 22) and local solar date (decision 23).

Every workstream uses these functions instead of re-deriving the formulas.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

RES = 0.1
N_ROWS = 1800  # latitude rows, -90..90
N_COLS = 3600  # longitude columns, -180..180


def _index(v, offset: float, n: int):
    """Row or column index: rounded first so float error on grid lines cannot shift a point, clamped at the edge."""
    idx = np.floor(np.round((np.asarray(v, dtype="float64") + offset) * 10, 6)).astype("int64")
    return np.clip(idx, 0, n - 1)


def cell_id(lat, lon):
    """cell_id = i * 3600 + j with i, j from decision 22. Accepts scalars or arrays; returns int32 for arrays."""
    i = _index(lat, 90.0, N_ROWS)
    j = _index(lon, 180.0, N_COLS)
    out = i * N_COLS + j
    return int(out) if np.ndim(out) == 0 else out.astype("int32")


def cell_center(cid):
    """(lat_c, lon_c) of a cell id (scalar or array)."""
    cid = np.asarray(cid, dtype="int64")
    i, j = np.divmod(cid, N_COLS)
    lat = -90.0 + (i + 0.5) * RES
    lon = -180.0 + (j + 0.5) * RES
    return np.round(lat, 4), np.round(lon, 4)


def cells_in_bbox(min_lon, min_lat, max_lon, max_lat) -> np.ndarray:
    """All cell ids whose centres fall inside the bbox."""
    i0, i1 = _index(min_lat, 90.0, N_ROWS), _index(max_lat, 90.0, N_ROWS)
    j0, j1 = _index(min_lon, 180.0, N_COLS), _index(max_lon, 180.0, N_COLS)
    ii, jj = np.meshgrid(np.arange(i0, i1 + 1), np.arange(j0, j1 + 1), indexing="ij")
    cid = (ii * N_COLS + jj).ravel()
    lat, lon = cell_center(cid)
    keep = (lat >= min_lat) & (lat <= max_lat) & (lon >= min_lon) & (lon <= max_lon)
    return cid[keep].astype("int32")


def local_solar_date(acq_date, acq_time, lon) -> pd.Series:
    """Local solar date from UTC date, HHMM time and longitude: UTC + lon/15 hours (decision 23)."""
    d = pd.to_datetime(pd.Series(acq_date)).reset_index(drop=True)
    t = pd.Series(np.asarray(acq_time, dtype="int64"))
    minutes = (t // 100) * 60 + (t % 100)
    offset = pd.Series(np.asarray(lon, dtype="float64")) / 15.0 * 60.0
    ts = d + pd.to_timedelta(minutes + offset, unit="m")
    return ts.dt.normalize().dt.date
