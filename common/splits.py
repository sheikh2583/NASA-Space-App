"""Spatial blocks, split labels and temporal folds shared by harmonization and calibration."""
from __future__ import annotations

import numpy as np
import pandas as pd

from common.grid import N_COLS

BLOCK_DEG = 2.0
CELLS_PER_BLOCK = int(BLOCK_DEG / 0.1)  # 20
BACKWARD_TRAIN = (2015, 2020)
BACKWARD_TEST = (2012, 2014)
DRIFT_TEST_FROM = 2021


def block_id(cell_id) -> np.ndarray:
    """Deterministic 2x2 degree block id from the block's corner."""
    i, j = np.divmod(np.asarray(cell_id, dtype="int64"), N_COLS)
    return ((i // CELLS_PER_BLOCK) * (N_COLS // CELLS_PER_BLOCK) + (j // CELLS_PER_BLOCK)).astype("int32")


def split_label(cell_id) -> np.ndarray:
    """block_id % 5 == 0 -> calib, == 1 -> test, else train."""
    b = block_id(cell_id)
    return np.where(b % 5 == 0, "calib", np.where(b % 5 == 1, "test", "train"))


def in_buffer(cell_id) -> np.ndarray:
    """True for train cells within one cell of a calib or test block (dropped from training)."""
    cid = np.asarray(cell_id, dtype="int64")
    lab = split_label(cid)
    out = np.zeros(cid.size, dtype=bool)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if di == dj == 0:
                continue
            nb = cid + di * N_COLS + dj
            out |= split_label(nb) != "train"
    return out & (lab == "train")


def yearly_folds(years, n_folds: int = 5):
    """Rolling-origin folds: train on years before each test year group."""
    ys = np.array(sorted(set(int(y) for y in years)))
    groups = np.array_split(ys[len(ys) // 2:], n_folds)
    return [(ys[ys < g.min()].tolist(), g.tolist()) for g in groups if g.size]


def backward_holdout(years):
    ys = np.asarray(years)
    train = (ys >= BACKWARD_TRAIN[0]) & (ys <= BACKWARD_TRAIN[1])
    test = (ys >= BACKWARD_TEST[0]) & (ys <= BACKWARD_TEST[1])
    return train, test


def drift_era(years):
    ys = np.asarray(years)
    return (ys >= BACKWARD_TRAIN[0]) & (ys <= BACKWARD_TRAIN[1]), ys >= DRIFT_TEST_FROM


def labels_frame(cell_ids) -> pd.DataFrame:
    cid = np.asarray(cell_ids)
    return pd.DataFrame({"cell_id": cid, "block_id": block_id(cid), "split": split_label(cid), "buffer": in_buffer(cid)})
