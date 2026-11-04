"""CPU LightGBM / CUDA XGBoost: MODIS inputs -> SNPP-equivalent Poisson count and Tweedie FRP.

Training rows: full overlap weeks (Terra, Aqua and SNPP operating all 7 days). Each row is used twice:
once with Terra + Aqua inputs and once with Aqua zeroed (terra_only), so the model can be applied to
Nov 2000 - Jul 2002 (decision 19).
"""
from __future__ import annotations

import lightgbm as lgb
import json
import numpy as np
import pandas as pd

from ws1_harmonize.baselines import overlap
from ws1_harmonize.features import FEATURES, build_features, check_features
from common import compute

PARAMS = {"learning_rate": 0.06, "num_leaves": 31, "min_data_in_leaf": 200, "feature_fraction": 0.85,
          "bagging_fraction": 0.8, "bagging_freq": 1, "lambda_l2": 1.0, "verbose": -1, "num_threads": 2, "seed": 11}


def training_frame(panel: pd.DataFrame, mask: np.ndarray | None = None):
    ok = overlap(panel).values
    if mask is not None:
        ok &= mask
    p = panel[ok]
    fa = build_features(p, "terra_aqua")
    ft = build_features(p, "terra_only")
    X = pd.concat([fa, ft], ignore_index=True)
    y = np.concatenate([p["snpp_n"].values, p["snpp_n"].values])
    yf = np.concatenate([p["snpp_frp"].values, p["snpp_frp"].values])
    return X, y, yf


def fit(panel: pd.DataFrame, mask: np.ndarray | None = None, rounds: int = 300) -> dict:
    X, y, yf = training_frame(panel, mask)
    check_features(X.columns)
    if compute.backend() == "cuda":
        count = compute.train_cuda(X, y, objective="count:poisson", rounds=rounds, purpose="harmonize-count")
        frp = compute.train_cuda(X, yf, objective="reg:tweedie", rounds=rounds, purpose="harmonize-frp", tweedie_variance_power=1.3)
    else:
        count = lgb.train({**PARAMS, "num_threads": compute.threads(), "objective": "poisson"}, lgb.Dataset(X, y), num_boost_round=rounds)
        frp = lgb.train({**PARAMS, "num_threads": compute.threads(), "objective": "tweedie", "tweedie_variance_power": 1.3}, lgb.Dataset(X, yf),
                        num_boost_round=rounds)
    return {"count": count, "frp": frp, "backend": compute.backend(), "features": list(X.columns), "n_train_rows": int(len(X))}


def predict(models: dict, panel: pd.DataFrame, combo: str | None = None):
    X = build_features(panel, combo)[models["features"]]
    if models.get("backend") == "cuda":
        return compute.predict_cuda(models["count"], X), compute.predict_cuda(models["frp"], X)
    return models["count"].predict(X), models["frp"].predict(X)


def save(models: dict, prefix: str):
    if models.get("backend") == "cuda":
        models["count"].save_model(prefix + "_count.ubj")
        models["frp"].save_model(prefix + "_frp.ubj")
        with open(prefix + "_metadata.json", "w") as stream:
            json.dump({"backend": "cuda", "features": models["features"], "n_train_rows": models["n_train_rows"]}, stream)
        return
    models["count"].save_model(prefix + "_count.txt")
    models["frp"].save_model(prefix + "_frp.txt")


def load(prefix: str) -> dict:
    from pathlib import Path
    if Path(prefix + "_metadata.json").exists():
        import xgboost as xgb
        metadata = json.loads(Path(prefix + "_metadata.json").read_text())
        return {**metadata, "count": xgb.Booster(model_file=prefix + "_count.ubj"),
                "frp": xgb.Booster(model_file=prefix + "_frp.ubj")}
    return {"count": lgb.Booster(model_file=prefix + "_count.txt"), "frp": lgb.Booster(model_file=prefix + "_frp.txt"),
            "features": FEATURES}
