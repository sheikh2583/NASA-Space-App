"""Model features: MODIS-derived or static only. Never a VIIRS-derived column, never the year."""
from __future__ import annotations

import numpy as np
import pandas as pd

from common.grid import N_COLS

FORBIDDEN_PREFIXES = ("snpp_", "n20_", "n21_")
FORBIDDEN = {"year", "week_start", "cell_id"}

FEATURES = [
    "terra_n", "aqua_n", "modis_n", "modis_hi", "modis_frp", "modis_frp_max", "modis_frp_mean",
    "modis_day", "modis_night", "terra_scan", "aqua_scan",
    "nb_modis_n", "prev_modis_n", "next_modis_n",
    "doy_sin", "doy_cos", "lat_coarse", "lon_coarse", "cropland_frac", "forest_frac", "combo_terra_aqua",
]


def _neighbour_sum(p: pd.DataFrame, col: str) -> np.ndarray:
    """Sum of col over the 3x3 neighbourhood (same week), excluding the cell itself."""
    key = p.set_index(["cell_id", "week_start"])[col]
    total = np.zeros(len(p))
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if di == dj == 0:
                continue
            nb = pd.MultiIndex.from_arrays([p["cell_id"].values + di * N_COLS + dj, p["week_start"].values])
            total += key.reindex(nb).fillna(0).values
    return total


def build_features(panel: pd.DataFrame, combo: str | None = None) -> pd.DataFrame:
    """Feature frame aligned with panel rows. combo='terra_only' zeroes Aqua inputs (used for Nov 2000 - Jul 2002
    and to teach the model Terra-only inputs on overlap years)."""
    p = panel.sort_values(["cell_id", "week_start"])
    combo_s = pd.Series(combo, index=p.index) if combo else p["sat_combo"]
    aqua_on = (combo_s == "terra_aqua").astype("float32").values
    f = pd.DataFrame(index=p.index)
    f["terra_n"] = p["terra_n"]
    f["aqua_n"] = p["aqua_n"] * aqua_on
    f["modis_n"] = f["terra_n"] + f["aqua_n"]
    f["modis_hi"] = p["terra_hi"] + p["aqua_hi"] * aqua_on
    f["modis_frp"] = p["terra_frp"] + p["aqua_frp"] * aqua_on
    f["modis_frp_max"] = np.maximum(p["terra_frp_max"], p["aqua_frp_max"] * aqua_on)
    f["modis_frp_mean"] = np.where(f["modis_n"] > 0, f["modis_frp"] / f["modis_n"].clip(lower=1), 0)
    f["modis_day"] = p["terra_n_day"] + p["aqua_n_day"] * aqua_on
    f["modis_night"] = p["terra_n_night"] + p["aqua_n_night"] * aqua_on
    f["terra_scan"] = p["terra_scan_w"]
    f["aqua_scan"] = np.where(aqua_on > 0, p["aqua_scan_w"], np.nan)
    tmp = p[["cell_id", "week_start"]].assign(m=f["modis_n"].values)
    f["nb_modis_n"] = _neighbour_sum(tmp, "m")
    f["prev_modis_n"] = tmp.groupby("cell_id")["m"].shift(1).fillna(0).values
    f["next_modis_n"] = tmp.groupby("cell_id")["m"].shift(-1).fillna(0).values
    doy = p["week_start"].dt.dayofyear.values
    f["doy_sin"], f["doy_cos"] = np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25)
    f["lat_coarse"], f["lon_coarse"] = np.round(p["lat_c"], 0), np.round(p["lon_c"], 0)
    f["cropland_frac"], f["forest_frac"] = p["cropland_frac"], p["forest_frac"]
    f["combo_terra_aqua"] = aqua_on
    f = f[FEATURES].astype("float32")
    return f.reindex(panel.index)


def check_features(cols) -> None:
    bad = [c for c in cols if c in FORBIDDEN or c.startswith(FORBIDDEN_PREFIXES)]
    if bad:
        raise ValueError(f"forbidden feature columns: {bad}")
