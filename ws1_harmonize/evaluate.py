"""Holdout evaluation of B0, B1 and the learned candidate on region-week sums.

select_method() picks B1 or the CUDA candidate using both satellite-input configurations; the OOF file,
the conformal intervals and harmonized v1 all use the chosen method ("ship B1 with honest wording").

Holdouts: (a) spatial blocks (train blocks -> test blocks), (b) rolling temporal folds, (c) backward
(train 2015-2020, test 2012-2014), plus the drift-era check (train 2015-2020, test 2021 on).
Calibration and test rows are never used for training (the OOF file says which model produced each row).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import compute, metrics, splits
from ws1_harmonize import baselines, model
from ws1_harmonize.baselines import overlap

ROUNDS = 200


def _region_week(panel: pd.DataFrame, pred: np.ndarray, rows: np.ndarray) -> pd.DataFrame:
    p = panel.loc[rows, ["admin1_id", "week_start", "snpp_n"]].assign(pred=pred[rows])
    return p.groupby(["admin1_id", "week_start"])[["snpp_n", "pred"]].sum()


def _score(panel, train_mask, test_mask, label):
    ov = overlap(panel).values
    tr, te = train_mask & ov, test_mask & ov
    params = baselines.fit(panel[tr])
    preds = {"B0": baselines.predict_b0(params, panel), "B1": baselines.predict_b1(params, panel)}
    m = model.fit(panel, tr, rounds=ROUNDS)
    preds[compute.learner_name()], _ = model.predict(m, panel)
    out = []
    for name, pr in preds.items():
        rw = _region_week(panel, pr, te)
        out.append({"holdout": label, "method": name, **metrics.summary(rw["snpp_n"], rw["pred"])})
        # Terra-only inputs on the same test rows (how well Nov 2000 - Jul 2002 is reconstructed)
    pr_t = {"B1": baselines.predict_b1(params, panel.assign(sat_combo="terra_only")),
            compute.learner_name(): model.predict(m, panel, "terra_only")[0]}
    for name, pr in pr_t.items():
        rw = _region_week(panel, pr, te)
        out.append({"holdout": label + " (terra_only inputs)", "method": name, **metrics.summary(rw["snpp_n"], rw["pred"])})
    return out


def evaluate(panel: pd.DataFrame, quick: bool = False) -> pd.DataFrame:
    """quick=True: spatial and backward holdouts only (about 4x faster)."""
    lab = splits.labels_frame(panel["cell_id"].unique()).set_index("cell_id")
    split = panel["cell_id"].map(lab["split"]).values
    buf = panel["cell_id"].map(lab["buffer"]).values
    year = panel["week_start"].dt.year.values
    rows = _score(panel, (split == "train") & ~buf, split == "test", "spatial blocks")
    ov_years = sorted(set(year[overlap(panel).values]))
    for tr_years, te_years in ([] if quick else splits.yearly_folds(ov_years, n_folds=3)):
        rows += _score(panel, np.isin(year, tr_years), np.isin(year, te_years), f"temporal {te_years[0]}-{te_years[-1]}")
    tr, te = splits.backward_holdout(year)
    rows += _score(panel, tr, te, "backward 2015-2020 -> 2012-2014")
    if not quick:
        tr, te = splits.drift_era(year)
        rows += _score(panel, tr, te, "drift era 2015-2020 -> 2021+")
    return pd.DataFrame(rows)


def select_method(table: pd.DataFrame) -> dict:
    candidates = {"B1": "b1", "LightGBM": "lgbm", "XGBoost CUDA": "xgb"}
    t = table[table["method"].isin(candidates)]
    score = t[~t["holdout"].str.contains("terra_only")].groupby("method")["lins_ccc"].mean()
    selection_score = t.groupby("method")["lins_ccc"].mean()
    # Prefer B1 on ties; never select a GPU model merely because CUDA is enabled.
    best_name = max(candidates, key=lambda name: selection_score.get(name, -np.inf))
    best = candidates[best_name]
    return {"method": best, "mean_ccc": {k: round(float(v), 4) for k, v in score.items()},
            "selection_mean_ccc": {k: round(float(v), 4) for k, v in selection_score.items()},
            "compute_backend": compute.backend(), "learned_candidate": compute.learner_name(),
            "rule": "highest mean Lin's CCC across both terra_aqua and terra_only region-week holdouts; both combinations matter for the historical record"}


def oof(panel: pd.DataFrame, method: str = "lgbm"):
    """predictions_oof rows for overlap weeks. Fold 0: model trained on train blocks, applied to calib and test.
    Folds 1-3: train blocks split by block id, each predicted by a model that did not see it."""
    lab = splits.labels_frame(panel["cell_id"].unique()).set_index("cell_id")
    split = panel["cell_id"].map(lab["split"]).values
    buf = panel["cell_id"].map(lab["buffer"]).values
    block = panel["cell_id"].map(lab["block_id"]).values
    ov = overlap(panel).values
    train = (split == "train") & ~buf
    frames = []

    def fit_any(mask):
        if method == "b1":
            return baselines.fit(panel[mask & ov])
        return model.fit(panel, mask, rounds=ROUNDS)

    def predict_any(m, mask, combo):
        if method == "b1":
            sub_ = panel[mask].assign(sat_combo=combo)
            return baselines.predict_b1(m, sub_), baselines.predict_b0_frp(m, sub_)
        # Full-panel feature context, then the held-out rows (same context as the final prediction).
        return model.predict(m, panel, combo, rows=mask)

    def emit(mask, m, fold):
        for combo in ("terra_aqua", "terra_only"):
            pc, pf = predict_any(m, mask, combo)
            frames.append(pd.DataFrame({
                "cell_id": panel.loc[mask, "cell_id"].values, "date": panel.loc[mask, "week_start"].dt.date.values,
                "y_true_count": panel.loc[mask, "snpp_n"].values, "y_pred_count": pc,
                "y_true_frp": panel.loc[mask, "snpp_frp"].values, "y_pred_frp": pf,
                "fold": fold, "block_id": block[mask], "split": split[mask], "sat_combo": combo}))

    m0 = fit_any(train)
    emit(ov & (split != "train"), m0, 0)
    tb = np.unique(block[train])
    groups = np.array_split(np.random.default_rng(3).permutation(tb), 3)
    for k, g in enumerate(groups, start=1):
        held = np.isin(block, g)
        mk = fit_any(train & ~held)
        emit(ov & train & held, mk, k)
    out = pd.concat(frames, ignore_index=True)
    for c in ("y_true_count", "y_pred_count", "y_true_frp", "y_pred_frp"):
        out[c] = out[c].astype("float32")
    out["fold"] = out["fold"].astype("int32")
    out["cell_id"] = out["cell_id"].astype("int32")
    return out, m0
