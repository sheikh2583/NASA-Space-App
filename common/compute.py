"""Explicit CPU/CUDA execution, GPU verification, and measured model-fit events."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import time

import numpy as np


def backend() -> str:
    value = os.environ.get("FIRESENSE_BACKEND", "cpu")
    if value not in {"cpu", "cuda"}:
        raise ValueError("FIRESENSE_BACKEND must be cpu or cuda")
    return value


def threads() -> int:
    value = int(os.environ.get("FIRESENSE_THREADS", "2"))
    if value < 1:
        raise ValueError("CPU thread count must be positive")
    return value


def device() -> str:
    index = int(os.environ.get("FIRESENSE_GPU_ID", "0"))
    if index < 0:
        raise ValueError("GPU ID must be nonnegative")
    return f"cuda:{index}"


def learner_name() -> str:
    return "XGBoost CUDA" if backend() == "cuda" else "LightGBM"


def assert_cuda(booster) -> None:
    actual = json.loads(booster.save_config())["learner"]["generic_param"]["device"]
    if actual != device():
        raise RuntimeError(f"CUDA was requested on {device()}, but XGBoost used {actual}; refusing CPU fallback.")


def train_cuda(X, y, *, objective: str, rounds: int, purpose: str, **extra):
    import xgboost as xgb

    started = time.perf_counter()
    params = {"device": device(), "tree_method": "hist", "max_bin": 63,
              "grow_policy": "lossguide", "max_leaves": 31, "max_depth": 6,
              "learning_rate": 0.06, "min_child_weight": 20,
              "subsample": 0.8, "colsample_bytree": 0.85, "reg_lambda": 1.0,
              "nthread": threads(), "seed": 11, "objective": objective, "verbosity": 1, **extra}
    if objective in {"count:poisson", "reg:tweedie"}:
        params["base_score"] = max(float(np.mean(y)), 1e-6)
    matrix = xgb.QuantileDMatrix(X, label=np.asarray(y), max_bin=params["max_bin"], nthread=threads())
    booster = xgb.train(params, matrix, num_boost_round=rounds)
    assert_cuda(booster)
    event = {"purpose": purpose, "device": device(), "library": f"xgboost {xgb.__version__}",
             "objective": objective, "rows": len(X), "features": X.shape[1], "rounds": rounds,
             "seconds": round(time.perf_counter() - started, 4)}
    log = os.environ.get("FIRESENSE_COMPUTE_LOG")
    if log:
        path = Path(log)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event) + "\n")
    if purpose.startswith("harmonize"):
        print("CUDA fit:", json.dumps(event), flush=True)
    return booster


def predict_cuda(booster, X):
    import xgboost as xgb
    # DMatrix prediction avoids mismatched-device inplace_predict fallback.
    booster.set_param({"device": device(), "nthread": threads()})
    result = booster.predict(xgb.DMatrix(X, nthread=threads()))
    assert_cuda(booster)
    return result


def probe_cuda() -> dict:
    """Verify every pipeline objective on CUDA without altering model audit logs."""
    import xgboost as xgb
    build = xgb.build_info()
    if not build.get('USE_CUDA'):
        raise RuntimeError('This XGBoost library has no CUDA support. Install requirements-cuda.txt, not xgboost-cpu.')
    rng = np.random.default_rng(11)
    X = rng.random((512, 6), dtype=np.float32)
    objectives = [
        ('count:poisson', rng.poisson(2, 512), {}),
        ('reg:tweedie', rng.gamma(2, 2, 512), {'tweedie_variance_power': 1.3}),
        ('binary:logistic', (X[:, 0] > 0.5).astype(int), {}),
        ('reg:quantileerror', rng.normal(size=512), {'quantile_alpha': 0.5}),
    ]
    previous_log = os.environ.pop('FIRESENSE_COMPUTE_LOG', None)
    try:
        for objective, y, extra in objectives:
            booster = train_cuda(X, y, objective=objective, rounds=3, purpose='probe', **extra)
            if not np.isfinite(predict_cuda(booster, X)).all():
                raise RuntimeError(f'CUDA probe produced nonfinite predictions for {objective}')
    finally:
        if previous_log is not None:
            os.environ['FIRESENSE_COMPUTE_LOG'] = previous_log
    result = subprocess.run(["nvidia-smi", "--query-gpu=index,name,memory.total,driver_version", "--format=csv,noheader"],
                            capture_output=True, text=True, check=True)
    return {"backend": "cuda", "device": device(), "xgboost": xgb.__version__,
            "cuda_build_version": build.get('CUDA_VERSION'),
            "verified_objectives": [objective for objective, _, _ in objectives],
            "threads": threads(), "gpus": result.stdout.strip().splitlines(), "verified": True}
