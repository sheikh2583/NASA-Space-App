"""Run with FIRESENSE_TEST_CUDA=1 on an NVIDIA machine; skipped on CPU-only CI."""
import os
import numpy as np
import pytest

pytestmark = pytest.mark.skipif(os.environ.get("FIRESENSE_TEST_CUDA") != "1", reason="explicit CUDA integration test")


def test_cuda_harmonization_roundtrip_and_no_target_leakage(monkeypatch, tmp_path):
    from ws1_harmonize.tests.test_harmonize import toy_panel
    from ws1_harmonize import model
    from common import compute
    monkeypatch.setenv("FIRESENSE_BACKEND", "cuda")
    panel = toy_panel(weeks=60)
    fitted = model.fit(panel, rounds=10)
    compute.assert_cuda(fitted["count"])
    count, frp = model.predict(fitted, panel)
    assert np.isfinite(count).all() and (count >= 0).all()
    assert np.isfinite(frp).all() and (frp >= 0).all()
    shuffled = panel.copy()
    for column in [c for c in panel if c.startswith(("snpp_", "n20_"))]:
        shuffled[column] = panel[column].sample(frac=1, random_state=8).values
    assert np.allclose(model.predict(fitted, shuffled)[0], count)
    prefix = str(tmp_path / "cuda")
    model.save(fitted, prefix)
    assert np.allclose(model.predict(model.load(prefix), panel)[0], count)


def test_cuda_classifier_and_quantile_objectives(monkeypatch):
    from common import compute
    monkeypatch.setenv("FIRESENSE_BACKEND", "cuda")
    rng = np.random.default_rng(3)
    X = rng.normal(size=(600, 6)).astype("float32")
    for objective, y, extra in (
        ("binary:logistic", (X[:, 0] > 0).astype(int), {}),
        ("reg:quantileerror", X[:, 0] + rng.normal(size=600), {"quantile_alpha": 0.5}),
    ):
        booster = compute.train_cuda(X, y, objective=objective, rounds=10, purpose="test", **extra)
        assert np.isfinite(compute.predict_cuda(booster, X)).all()
