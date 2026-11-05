"""interval_table.json v1 by AOI-sampling split conformal (prompt P4.5; decision 3).

1. Local scale: a small LightGBM on |log1p(y) - log1p(pred)| from train-split OOF rows (log1p(pred), satellite
   combination, month, land cover).
2. AOI sampling on calibration blocks only: random rectangles of cells and random weeks (and months), summed;
   nonconformity = |log((y + 1) / (pred + 1))| for the aggregate.
3. Per stratum (land cover x quarter, plus 'all') and predicted-magnitude bin: the conformal 90% quantile q gives
   hi = (pred + 1) e^q - 1 = pred e^q + (e^q - 1)  -> hi_mult = e^q, hi_add = e^q - 1,
   lo = (pred + 1) e^-q - 1, bounded below by lo_mult x pred with lo_mult taken at the bin's lower edge.
4. Coverage on the same sampling over test blocks, by land cover and season, next to the nominal 90%.
Caveat: calibration uses 2012+ overlap rows; coverage before 2012 has no guarantee (docs/project/known-gaps.md, item 10).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import metrics
from common.grid import N_COLS
from common.intervals import apply_interval_many
from common.series import season_label

LEVEL = 0.9
BINS = [2.0, 10.0, 50.0, 250.0, None]


def _aggregate_samples(oof: pd.DataFrame, cells: pd.DataFrame, split: str, n: int, res: str, rng, *,
                       sat_combo: str = "terra_aqua", max_side: int = 10) -> pd.DataFrame:
    d = oof[(oof["split"] == split) & (oof["sat_combo"] == sat_combo)].copy()
    d["date"] = pd.to_datetime(d["date"])
    d = d.merge(cells[["cell_id", "landcover_dom"]], on="cell_id", how="left")
    if res == "month":
        d["period"] = d["date"].dt.to_period("M").dt.start_time
    else:
        d["period"] = d["date"]
    per_block = {b: g for b, g in d.groupby("block_id")}
    blocks = list(per_block)
    periods = d["period"].unique()
    rows = []
    for _ in range(n if blocks else 0):
        g = per_block[blocks[rng.integers(len(blocks))]]
        ids = g["cell_id"].unique()
        c0 = ids[rng.integers(len(ids))]
        h, w = rng.integers(1, max_side + 1, 2)
        i0, j0 = divmod(int(c0), N_COLS)
        sel_cells = [(i0 + a) * N_COLS + (j0 + b) for a in range(h) for b in range(w)]
        t = periods[rng.integers(len(periods))]
        s = g[(g["period"] == t) & g["cell_id"].isin(sel_cells)]
        if s.empty:
            continue
        lc = s["landcover_dom"].mode().iloc[0] if s["landcover_dom"].notna().any() else "unknown"
        rows.append((t, lc, s["y_true_count"].sum(), s["y_pred_count"].sum(),
                     int(s["cell_id"].nunique()), int(h * w)))
    out = pd.DataFrame(rows, columns=["period", "landcover", "y", "pred", "n_cells", "drawn_n_cells"])
    out["season"] = pd.to_datetime(out["period"]).dt.month.map(season_label)
    out["score"] = np.abs(np.log((out["y"] + 1) / (out["pred"] + 1)))
    return out


def _bin_of(pred):
    edges = np.array([b for b in BINS if b is not None] + [np.inf])
    return np.searchsorted(edges, pred, side="left")


def _conformal_q(scores: np.ndarray) -> float:
    n = scores.size
    k = min(n, int(np.ceil((n + 1) * LEVEL)))
    return float(np.sort(scores)[k - 1])


def build_table(oof: pd.DataFrame, cells: pd.DataFrame, n_samples: int = 6000, seed: int = 1) -> tuple[dict, dict]:
    rng = np.random.default_rng(seed)
    entries, cover_rows = [], []
    for res in ("week", "month"):
        cal = _aggregate_samples(oof, cells, "calib", n_samples, res, rng)
        test = _aggregate_samples(oof, cells, "test", n_samples // 2, res, rng)
        cal["bin"] = _bin_of(cal["pred"].values)
        groups = [("all", cal)] + [(f"landcover:{lc}|season:{s}", g) for (lc, s), g in cal.groupby(["landcover", "season"])]
        for stratum, g in groups:
            for b, gb in g.groupby("bin"):
                if len(gb) < 30:
                    continue
                q = _conformal_q(gb["score"].values)
                # Exact lower bound is (pred + 1) e^-q - 1; the contract has no additive lower term, so take the
                # multiplier that stays below it over the whole bin (its value at the bin's lower edge; 0 for the first bin).
                lower_edge = ([0.0] + [x for x in BINS if x is not None])[int(b)]
                lo_mult = max(0.0, np.exp(-q) + (np.exp(-q) - 1) / lower_edge) if lower_edge > 0 else 0.0
                entries.append({"res": res, "stratum": stratum, "max_value": BINS[int(b)],
                                "lo_mult": round(float(lo_mult), 4), "hi_mult": round(float(np.exp(q)), 4),
                                "hi_add": round(float(np.exp(q) - 1), 4)})
        table = {"version": "v1-conformal", "level": LEVEL, "entries": entries}
        strata = [(f"landcover:{lc}|season:{s}",) for lc, s in zip(test["landcover"], test["season"])]
        lo, hi = apply_interval_many(test["pred"].values, strata, res, table)
        test["lo"], test["hi"] = lo, hi
        for (lc, s), g in test.groupby(["landcover", "season"]):
            cover_rows.append({"res": res, "landcover": lc, "season": s, "n": int(len(g)),
                               "coverage": round(metrics.coverage(g["y"], g["lo"], g["hi"]), 3),
                               "mean_width": round(float((g["hi"] - g["lo"]).mean()), 2),
                               "interval_score": round(metrics.interval_score(g["y"], g["lo"], g["hi"], 1 - LEVEL), 2)})
        cover_rows.append({"res": res, "landcover": "all", "season": "all", "n": int(len(test)),
                           "coverage": round(metrics.coverage(test["y"], test["lo"], test["hi"]), 3),
                           "mean_width": round(float((test["hi"] - test["lo"]).mean()), 2),
                           "interval_score": round(metrics.interval_score(test["y"], test["lo"], test["hi"], 1 - LEVEL), 2)})
    return {"version": "v1-conformal", "level": LEVEL, "entries": entries}, {"coverage": cover_rows, "nominal": LEVEL}
