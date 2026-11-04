import numpy as np
import pandas as pd
import pytest

from common.grid import cells_in_bbox
from ws1_harmonize import baselines, features, model


def toy_panel(seed=0, weeks=120, ratio_ta=2.0):
    rng = np.random.default_rng(seed)
    cids = cells_in_bbox(89.0, 23.0, 89.6, 23.6)
    ws = pd.date_range("2013-01-07", periods=weeks, freq="7D")
    p = pd.MultiIndex.from_product([cids, ws], names=["cell_id", "week_start"]).to_frame(index=False)
    lam = rng.gamma(1.5, 2.0, len(p))
    p["terra_n"] = rng.poisson(0.2 * lam).astype("float32")
    p["aqua_n"] = rng.poisson(0.3 * lam).astype("float32")
    p["snpp_n"] = rng.poisson(lam).astype("float32")
    p["n20_n"] = rng.poisson(0.9 * lam).astype("float32")
    for s in ("terra", "aqua", "snpp", "n20"):
        p[f"{s}_days"] = 7
        for v in ("hi", "frp", "frp_max", "n_day", "n_night"):
            p[f"{s}_{v}"] = (p[f"{s}_n"] * (3.0 if v.startswith("frp") else 0.5)).astype("float32") if s != "n20" or v == "frp" else 0.0
        p[f"{s}_scan_w"] = 1.0
    p["modis_n"] = p["terra_n"] + p["aqua_n"]
    p["snpp_frp"] = p["snpp_n"] * 2.0
    p["sat_combo"] = "terra_aqua"
    p["lat_c"], p["lon_c"] = 23.3, 89.3
    p["admin1_id"] = np.where(p["cell_id"] % 2 == 0, "A", "B")
    p["landcover_dom"], p["cropland_frac"], p["forest_frac"] = "cropland", 0.6, 0.1
    return p


def test_baselines_recover_known_ratios():
    p = toy_panel()
    params = baselines.fit(p)
    assert params["b0"]["terra_aqua"] == pytest.approx(1 / 0.5, rel=0.03)
    assert params["b0"]["terra_only"] == pytest.approx(1 / 0.2, rel=0.06)  # Terra-only sums are small: ~2% sampling error
    assert params["b0_n20"] == pytest.approx(1 / 0.9, rel=0.03)


def test_method_selection_reports_cuda_candidate_and_keeps_better_baseline(monkeypatch):
    from ws1_harmonize.evaluate import select_method
    monkeypatch.setenv("FIRESENSE_BACKEND", "cuda")
    table = pd.DataFrame({"holdout": ["spatial blocks"] * 2, "method": ["B1", "XGBoost CUDA"], "lins_ccc": [0.95, 0.9]})
    assert select_method(table)["method"] == "b1"
    table.loc[1, "lins_ccc"] = 0.99
    assert select_method(table)["method"] == "xgb"


def test_selection_cannot_ignore_failed_terra_only_reconstruction(monkeypatch):
    from ws1_harmonize.evaluate import select_method
    monkeypatch.setenv("FIRESENSE_BACKEND", "cuda")
    table = pd.DataFrame({"holdout": ["spatial blocks", "spatial blocks", "spatial blocks (terra_only inputs)", "spatial blocks (terra_only inputs)"],
                          "method": ["B1", "XGBoost CUDA", "B1", "XGBoost CUDA"],
                          "lins_ccc": [0.9, 0.95, 0.85, 0.3]})
    choice = select_method(table)
    assert choice["mean_ccc"]["XGBoost CUDA"] > choice["mean_ccc"]["B1"]
    assert choice["selection_mean_ccc"]["B1"] > choice["selection_mean_ccc"]["XGBoost CUDA"]
    assert choice["method"] == "b1"


def test_b1_uses_terra_only_ratio_for_terra_only_weeks():
    p = toy_panel()
    params = baselines.fit(p)
    q = p.head(5).assign(sat_combo="terra_only", terra_n=10.0, aqua_n=10.0)
    assert np.allclose(baselines.predict_b1(params, q), 10.0 * np.array(
        [params["b1"]["terra_only"].get((a, m), params["b0"]["terra_only"]) for a, m in zip(q["admin1_id"], q["week_start"].dt.month)]))


def test_forbidden_features_rejected():
    with pytest.raises(ValueError):
        features.check_features(["terra_n", "snpp_n"])
    with pytest.raises(ValueError):
        features.check_features(["year"])
    features.check_features(features.FEATURES)


def test_terra_only_features_zero_aqua():
    p = toy_panel(weeks=10)
    f = features.build_features(p, "terra_only")
    assert (f["aqua_n"] == 0).all() and (f["combo_terra_aqua"] == 0).all()


def test_leakage_shuffling_viirs_columns_changes_nothing():
    p = toy_panel(weeks=60)
    m = model.fit(p, rounds=30)
    a, _ = model.predict(m, p)
    shuffled = p.copy()
    rng = np.random.default_rng(1)
    for c in [c for c in p.columns if c.startswith(("snpp_", "n20_"))]:
        shuffled[c] = rng.permutation(shuffled[c].values)
    b, _ = model.predict(m, shuffled)
    assert np.allclose(a, b)


def test_snpp_outage_day_is_filled_from_noaa20_times_the_ratio():
    """Plan card T06: assemble() fills an SNPP outage day from NOAA-20; no model is fitted here."""
    import datetime as dt
    from ws1_harmonize import write_harmonized as wh
    days = pd.date_range("2024-11-03", "2024-11-05").date
    sd = pd.DataFrame([(d, s, not (s == "SNPP" and d == dt.date(2024, 11, 4))) for d in days for s in ("SNPP", "NOAA20")],
                      columns=["date", "sat", "operating"])
    grid = pd.DataFrame({"cell_id": [1, 1], "date": [dt.date(2024, 11, 4), dt.date(2024, 11, 3)], "sat": ["NOAA20", "SNPP"],
                         "n_det": [10, 3], "frp_sum": [5.0, 1.0]})
    panel = pd.DataFrame({"cell_id": [1], "week_start": [pd.Timestamp("2024-10-28")], "sat_combo": ["terra_aqua"]})
    cells = pd.DataFrame({"cell_id": [1], "admin1_id": ["X"], "landcover_dom": [12]})
    out = wh.assemble(panel, np.array([0.0]), np.array([0.0]), grid, cells, sd,
                      lambda adm, month: np.full(len(adm), 0.8), {"level": 0.9}, "test")
    row = out[out["date"] == dt.date(2024, 11, 4)].iloc[0]
    assert row["source"] == "adjusted_from_noaa20" and row["value_count"] == pytest.approx(10 * 0.8)
