"""Drift flags per admin1 region and year (prompt P4.6).

2012 onward: ratio of observed SNPP to the model's prediction, summed per region-year, standardized against
2012-2020 and run through a CUSUM; |z| > 2 or CUSUM > 4 flags the year ("sensor relationship changed").
Before 2012: a classifier two-sample test (LightGBM, cross-validated AUC) between that year's MODIS features
and the 2012-2020 features; AUC > 0.75 flags the year as outside what the model was trained on.
"""
from __future__ import annotations

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from common import compute

from ws1_harmonize.features import build_features

REF_YEARS = (2012, 2020)
Z_MAX, CUSUM_H, CUSUM_K, AUC_MAX = 2.0, 4.0, 0.5, 0.75
TEST_FEATURES = ["modis_frp_mean", "terra_scan", "modis_day", "modis_night", "modis_hi", "modis_n"]


def ratio_flags(panel: pd.DataFrame, pred: np.ndarray) -> pd.DataFrame:
    p = panel.assign(pred=pred, year=panel["week_start"].dt.year)
    p = p[(p["snpp_days"] == 7) & (p["terra_days"] > 0)]
    ry = p.groupby(["admin1_id", "year"])[["snpp_n", "pred"]].sum()
    ry["log_ratio"] = np.log((ry["snpp_n"] + 1) / (ry["pred"] + 1))
    rows = []
    for region, g in ry.reset_index().groupby("admin1_id"):
        ref = g[(g["year"] >= REF_YEARS[0]) & (g["year"] <= REF_YEARS[1])]["log_ratio"]
        mu, sd = ref.mean(), max(ref.std(ddof=1), 0.02)
        s_hi = s_lo = 0.0
        for _, r in g.sort_values("year").iterrows():
            z = (r["log_ratio"] - mu) / sd
            s_hi, s_lo = max(0.0, s_hi + z - CUSUM_K), max(0.0, s_lo - z - CUSUM_K)
            flag = abs(z) > Z_MAX or s_hi > CUSUM_H or s_lo > CUSUM_H
            reason = (f"observed/predicted ratio z={z:+.1f}, CUSUM {max(s_hi, s_lo):.1f}" if flag else "")
            rows.append((region, int(r["year"]), bool(flag), reason, float(z)))
    return pd.DataFrame(rows, columns=["region_id", "year", "drift_flag", "reason", "z"])


def applicability_flags(panel: pd.DataFrame, years=range(2001, 2012)) -> pd.DataFrame:
    f = build_features(panel)[TEST_FEATURES].fillna(0)
    active = panel["modis_n"] > 0
    yr = panel["week_start"].dt.year
    ref = f[active & (yr >= REF_YEARS[0]) & (yr <= REF_YEARS[1])]
    rows = []
    for region in panel["admin1_id"].dropna().unique():
        in_r = panel["admin1_id"] == region
        ref_r = ref[in_r.loc[ref.index]]
        for y in years:
            cur = f[active & in_r & (yr == y)]
            if len(cur) < 50 or len(ref_r) < 50:
                rows.append((region, y, False, "too few MODIS weeks to test", np.nan))
                continue
            refs = ref_r.sample(min(len(ref_r), 3 * len(cur)), random_state=y)
            X = pd.concat([cur, refs])
            lab = np.r_[np.ones(len(cur)), np.zeros(len(refs))]
            if compute.backend() == "cuda":
                aucs = []
                for train, test in StratifiedKFold(n_splits=3).split(X, lab):
                    clf = compute.train_cuda(X.iloc[train], lab[train], objective="binary:logistic", rounds=60,
                                             purpose="drift-classifier", max_leaves=15)
                    aucs.append(roc_auc_score(lab[test], compute.predict_cuda(clf, X.iloc[test])))
                auc = float(np.mean(aucs))
            else:
                clf = lgb.LGBMClassifier(n_estimators=60, num_leaves=15, verbose=-1, n_jobs=compute.threads())
                auc = float(np.mean(cross_val_score(clf, X, lab, cv=3, scoring="roc_auc")))
            flag = auc > AUC_MAX
            rows.append((region, y, flag, f"MODIS inputs differ from 2012-2020 (AUC {auc:.2f})" if flag else "", auc))
    return pd.DataFrame(rows, columns=["region_id", "year", "drift_flag", "reason", "auc"])
