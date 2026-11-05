"""Held-out interval diagnostics by area size, magnitude, season and input combination."""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import metrics
from common.intervals import apply_interval_many
from ws4_outlook.conformal import LEVEL, _aggregate_samples, month_target

AREA_STRATA = (
    ("1-10", 1, 10),
    ("11-50", 11, 50),
    ("51-100", 51, 100),
    ("101-400", 101, 400),
)
MAGNITUDE_STRATA = ("zero", "q1", "q2", "q3", "q4")
SEASON_STRATA = ("q1", "q2", "q3", "q4")


def _finite(value: float) -> float | None:
    return float(value) if np.isfinite(value) else None


def _row(frame: pd.DataFrame, *, res: str, sat_combo: str, dimension: str, value: str) -> dict:
    n = int(len(frame))
    row = {
        "res": res,
        "sat_combo": sat_combo,
        "dimension": dimension,
        "value": value,
        "stratum": f"{res} | {sat_combo} | {dimension}:{value}",
        "n": n,
        "below_lower": float((frame["y"] < frame["lo"]).mean()) if n else None,
        "above_upper": float((frame["y"] > frame["hi"]).mean()) if n else None,
        "coverage": _finite(metrics.coverage(frame["y"], frame["lo"], frame["hi"])),
        "interval_score": _finite(metrics.interval_score(frame["y"], frame["lo"], frame["hi"], alpha=0.1)),
        "mean_width": _finite(float((frame["hi"] - frame["lo"]).mean()) if n else np.nan),
        "median_relative_width": _finite(
            np.median((frame["hi"] - frame["lo"]) / np.maximum(frame["y"], 1)) if n else np.nan
        ),
    }
    if dimension == "magnitude" and value == "zero":
        row["zero_covered"] = _finite(np.mean((frame["lo"] <= 0) & (frame["hi"] >= 0)) if n else np.nan)
    if n < 30:
        row["note"] = "too few samples"
    return row


def _magnitude_labels(values: pd.Series) -> pd.Series:
    labels = pd.Series("zero", index=values.index, dtype="object")
    positive = values[values > 0]
    if len(positive):
        # Ranking first gives deterministic, similarly sized groups even when many totals are tied.
        ranks = positive.rank(method="first").to_numpy() - 1
        labels.loc[positive.index] = [f"q{min(4, int(rank * 4 / len(positive)) + 1)}" for rank in ranks]
    return labels


def stop_rows(rows):
    return [row for row in rows if row.get("n", 0) >= 500 and
            row.get("coverage") is not None and row["coverage"] < 0.80]


def report(oof: pd.DataFrame, cells: pd.DataFrame, table: dict, n: int = 4000, seed: int = 7,
           daily: pd.DataFrame | None = None) -> dict:
    """Measure the saved interval table on random rectangles from held-out test blocks."""
    rng = np.random.default_rng(seed)
    rows = []
    for res in ("week", "month"):
        for sat_combo in ("terra_aqua", "terra_only"):
            samples = _aggregate_samples(
                oof, cells, "test", n, res, rng, sat_combo=sat_combo, max_side=20, daily=daily
            )
            strata = [(f"landcover:{lc}|season:{season}",) for lc, season in
                      zip(samples["landcover"], samples["season"])]
            samples["lo"], samples["hi"] = apply_interval_many(
                samples["pred"].to_numpy(), strata, res, table
            )
            samples["magnitude_stratum"] = _magnitude_labels(samples["y"])

            rows.append(_row(samples, res=res, sat_combo=sat_combo,
                             dimension="satellite_combination", value=sat_combo))
            rows.append(_row(samples[samples["y"] > 0], res=res, sat_combo=sat_combo,
                             dimension="activity", value="positive"))
            # Positive truth where the model predicts nothing: the band can only cover it through hi_add.
            rows.append(_row(samples[(samples["y"] > 0) & (samples["pred"] <= 0)], res=res, sat_combo=sat_combo,
                             dimension="prediction", value="zero_with_positive_truth"))
            for value, low, high in AREA_STRATA:
                rows.append(_row(samples[samples["n_cells"].between(low, high)], res=res,
                                 sat_combo=sat_combo, dimension="area_size", value=value))
            for value in MAGNITUDE_STRATA:
                rows.append(_row(samples[samples["magnitude_stratum"] == value], res=res,
                                 sat_combo=sat_combo, dimension="magnitude", value=value))
            for value in SEASON_STRATA:
                rows.append(_row(samples[samples["season"] == value], res=res,
                                 sat_combo=sat_combo, dimension="season", value=value))
    failures = stop_rows(rows)
    return {"rows": rows, "nominal": LEVEL, "stop_rows": failures,
            "acceptance_status": "stop_condition" if failures else "reported",
            "area_size_basis": "unique contributing OOF cell IDs, not drawn rectangle size",
            "month_target": month_target(daily)}
