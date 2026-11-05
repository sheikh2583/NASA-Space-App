"""Calendar-exact lag and full-panel feature context. Pure feature construction; nothing is fitted."""
import numpy as np
import pandas as pd

from common.grid import N_COLS
from ws1_harmonize.features import build_features
from ws1_harmonize.model import training_frame

CELL = 1000 * N_COLS + 1000
ZERO_COLS = ["aqua_n", "terra_hi", "aqua_hi", "terra_frp", "aqua_frp", "terra_frp_max", "aqua_frp_max",
             "terra_n_day", "aqua_n_day", "terra_n_night", "aqua_n_night", "snpp_frp"]


def panel(rows):
    p = pd.DataFrame(rows, columns=["cell_id", "week_start", "terra_n"])
    p["week_start"] = pd.to_datetime(p["week_start"])
    for c in ZERO_COLS:
        p[c] = 0.0
    p["snpp_n"] = p["terra_n"]
    p = p.assign(terra_scan_w=1.0, aqua_scan_w=1.0, lat_c=30.0, lon_c=75.0, cropland_frac=0.5, forest_frac=0.0,
                 sat_combo="terra_aqua", terra_days=7, aqua_days=7, snpp_days=7)
    return p


def test_lags_are_exact_calendar_weeks_not_next_available_rows():
    # 11 Jan is missing: 4 Jan has no "next week" and 18 Jan has no "previous week".
    f = build_features(panel([(CELL, "2021-01-04", 5.0), (CELL, "2021-01-18", 9.0)]), "terra_aqua")
    assert f["prev_modis_n"].tolist() == [0.0, 0.0]
    assert f["next_modis_n"].tolist() == [0.0, 0.0]


def test_lags_use_adjacent_weeks_when_present_and_keep_row_order():
    p = panel([(CELL, "2021-01-18", 9.0), (CELL, "2021-01-04", 5.0), (CELL, "2021-01-11", 2.0)])
    f = build_features(p, "terra_aqua")
    assert f.loc[1, ["prev_modis_n", "next_modis_n"]].tolist() == [0.0, 2.0]   # 4 Jan
    assert f.loc[2, ["prev_modis_n", "next_modis_n"]].tolist() == [5.0, 9.0]   # 11 Jan
    assert f.loc[0, ["prev_modis_n", "next_modis_n"]].tolist() == [2.0, 0.0]   # 18 Jan


def test_training_rows_keep_full_panel_context_after_overlap_and_split_masks():
    full = panel([(CELL, "2021-01-04", 5.0), (CELL, "2021-01-11", 2.0), (CELL, "2021-01-18", 9.0),
                  (CELL + 1, "2021-01-04", 4.0), (CELL + 1, "2021-01-11", 4.0), (CELL + 1, "2021-01-18", 4.0)])
    full.loc[1, "snpp_days"] = 6                      # 11 Jan of CELL is not a full-overlap week
    mask = (full["cell_id"] == CELL).values           # the neighbour belongs to another split
    X, y, _ = training_frame(full, mask)
    reference = build_features(full, "terra_aqua")[mask & (full["snpp_days"] == 7).values]
    got = X.iloc[:len(reference)].reset_index(drop=True)
    assert got[["prev_modis_n", "next_modis_n", "nb_modis_n"]].values.tolist() == \
        reference[["prev_modis_n", "next_modis_n", "nb_modis_n"]].values.tolist()
    assert got["next_modis_n"].tolist() == [2.0, 0.0]   # 4 Jan still sees 11 Jan; nothing crosses the gap
    assert got["nb_modis_n"].tolist() == [4.0, 4.0]     # neighbour context survives the split mask
    assert y.tolist() == [5.0, 9.0, 5.0, 9.0]
