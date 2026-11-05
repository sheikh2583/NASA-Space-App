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

Monthly target: the served monthly value sums days into calendar months, so monthly samples are built the same way
(daily_oof): SNPP daily detections as truth, and each held-out weekly estimate split over its days with the rule
write_harmonized uses for the served table. Only calendar months fully covered by overlap weeks are sampled. Without
daily rows (tiny tests) the legacy target, whole weeks grouped by their Monday's month, is used and labelled.
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


CALENDAR_MONTH = "calendar_month_daily_allocation"
LEGACY_MONTH = "legacy_whole_weeks_by_monday_month"


def month_target(daily: pd.DataFrame | None) -> str:
    return CALENDAR_MONTH if daily is not None else LEGACY_MONTH


def daily_oof(oof: pd.DataFrame, grid: pd.DataFrame, splits=("calib", "test")) -> pd.DataFrame:
    """Held-out weekly OOF rows -> cell-day rows (cell_id, date, y_true_count, y_pred_count, block_id, split, sat_combo).

    Truth is the SNPP daily detection count. The weekly prediction is split over its days in proportion to MODIS
    daily detections (Terra only for terra_only), else booked on the Monday: write_harmonized.disaggregate, the
    rule behind the served table. Raises if daily SNPP truth does not add up to the weekly OOF truth."""
    from ws1_harmonize.panel import week_start
    from ws1_harmonize.write_harmonized import disaggregate

    o = oof[oof["split"].isin(splits)].copy()
    o["week_start"] = pd.to_datetime(o["date"])
    keys = o[o["sat_combo"] == o["sat_combo"].iloc[0]][["cell_id", "week_start", "y_true_count", "block_id", "split"]] \
        if len(o) else o[["cell_id", "week_start", "y_true_count", "block_id", "split"]]
    g = grid[grid["cell_id"].isin(keys["cell_id"].unique())][["cell_id", "date", "sat", "n_det"]].copy()
    g["date"] = pd.to_datetime(g["date"])
    snpp = g[g["sat"] == "SNPP"].assign(week_start=lambda x: week_start(x["date"]).values)
    snpp = snpp.merge(keys[["cell_id", "week_start"]], on=["cell_id", "week_start"])
    weekly = snpp.groupby(["cell_id", "week_start"])["n_det"].sum()
    check = keys.set_index(["cell_id", "week_start"])["y_true_count"].astype("float64")
    diff = (weekly.reindex(check.index).fillna(0) - check).abs()
    if (diff > 1e-6).any():
        raise ValueError(f"Daily SNPP truth disagrees with weekly OOF truth for {int((diff > 1e-6).sum())} cell-weeks")
    truth = snpp.groupby(["cell_id", "date"])["n_det"].sum().rename("y_true_count").reset_index()
    frames = []
    for combo, rows in o.groupby("sat_combo"):
        panel = rows[["cell_id", "week_start"]].assign(sat_combo=combo).reset_index(drop=True)
        pred = rows["y_pred_count"].to_numpy("float64")
        d = disaggregate(panel, pred, np.zeros_like(pred), g)
        d = d.rename(columns={"modeled_count": "y_pred_count"})[["cell_id", "date", "y_pred_count"]]
        d["date"] = pd.to_datetime(d["date"])
        d = d.merge(truth, on=["cell_id", "date"], how="outer").fillna({"y_pred_count": 0.0, "y_true_count": 0.0})
        frames.append(d.assign(sat_combo=combo))
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(
        columns=["cell_id", "date", "y_pred_count", "y_true_count", "sat_combo"])
    labels = keys.drop_duplicates("cell_id").set_index("cell_id")
    out["block_id"] = out["cell_id"].map(labels["block_id"])
    out["split"] = out["cell_id"].map(labels["split"])
    return out


def _complete_months(week_starts) -> list:
    """Calendar months whose every day lies in one of the given (overlap) weeks."""
    weeks = pd.to_datetime(pd.Series(pd.unique(week_starts)))
    if weeks.empty:
        return []
    days = pd.DatetimeIndex(np.unique(np.concatenate([(weeks + pd.Timedelta(days=k)).values for k in range(7)])))
    months = days.to_period("M")
    counts = pd.Series(1, index=months).groupby(level=0).sum()
    return [m.start_time for m, c in counts.items() if c == m.days_in_month]


def _calendar_month_samples(d: pd.DataFrame, daily: pd.DataFrame, cells: pd.DataFrame, split: str, n: int, rng, *,
                            sat_combo: str, max_side: int) -> pd.DataFrame:
    block_cells = {b: np.sort(g["cell_id"].unique()) for b, g in d.groupby("block_id")}
    blocks = list(block_cells)
    periods = _complete_months(d["date"])
    dd = daily[(daily["split"] == split) & (daily["sat_combo"] == sat_combo)].copy()
    dd["period"] = pd.to_datetime(dd["date"]).dt.to_period("M").dt.start_time
    sums = dd[dd["period"].isin(periods)].groupby(["period", "cell_id"])[["y_true_count", "y_pred_count"]].sum()
    lc_of = cells.set_index("cell_id")["landcover_dom"]
    rows = []
    for _ in range(n if blocks and periods else 0):
        ids = block_cells[blocks[rng.integers(len(blocks))]]
        c0 = ids[rng.integers(len(ids))]
        h, w = rng.integers(1, max_side + 1, 2)
        i0, j0 = divmod(int(c0), N_COLS)
        sel = np.intersect1d(ids, [(i0 + a) * N_COLS + (j0 + b) for a in range(h) for b in range(w)])
        t = periods[rng.integers(len(periods))]
        if not sel.size:
            continue
        v = sums.reindex(pd.MultiIndex.from_product([[t], sel])).fillna(0.0)
        lcs = lc_of.reindex(sel).dropna()
        lc = lcs.mode().iloc[0] if len(lcs) else "unknown"
        rows.append((t, lc, float(v["y_true_count"].sum()), float(v["y_pred_count"].sum()), int(sel.size), int(h * w)))
    return pd.DataFrame(rows, columns=["period", "landcover", "y", "pred", "n_cells", "drawn_n_cells"])


def _aggregate_samples(oof: pd.DataFrame, cells: pd.DataFrame, split: str, n: int, res: str, rng, *,
                       sat_combo: str = "terra_aqua", max_side: int = 10, daily: pd.DataFrame | None = None) -> pd.DataFrame:
    d = oof[(oof["split"] == split) & (oof["sat_combo"] == sat_combo)].copy()
    d["date"] = pd.to_datetime(d["date"])
    if res == "month" and daily is not None:
        out = _calendar_month_samples(d, daily, cells, split, n, rng, sat_combo=sat_combo, max_side=max_side)
        out["season"] = pd.to_datetime(out["period"]).dt.month.map(season_label)
        out["score"] = np.abs(np.log((out["y"] + 1) / (out["pred"] + 1)))
        return out
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


def build_table(oof: pd.DataFrame, cells: pd.DataFrame, n_samples: int = 6000, seed: int = 1,
                daily: pd.DataFrame | None = None) -> tuple[dict, dict]:
    rng = np.random.default_rng(seed)
    entries, cover_rows = [], []
    for res in ("week", "month"):
        cal = _aggregate_samples(oof, cells, "calib", n_samples, res, rng, daily=daily)
        test = _aggregate_samples(oof, cells, "test", n_samples // 2, res, rng, daily=daily)
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
    return ({"version": "v1-conformal", "level": LEVEL, "entries": entries},
            {"coverage": cover_rows, "nominal": LEVEL, "month_target": month_target(daily)})
