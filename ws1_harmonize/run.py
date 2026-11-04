"""Harmonization steps (Sheikh). Run in order; each writes to data/interim or data/processed.

  python -m ws1_harmonize.run panel       # data/interim/sheikh/panel.parquet
  python -m ws1_harmonize.run v0          # harmonized.parquet v0 (B1) + interval_table.json v0  (H14)
  python -m ws1_harmonize.run model       # metrics table, predictions_oof.parquet, saved LightGBM   (H24)
  python -m ws1_harmonize.run v1          # harmonized.parquet v1 (needs Samin's interval_table v1 and drift_flags) (H30)
  python -m ws1_harmonize.run validation  # validation/harmonization.json                            (H34)
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import os
import pickle
import sys

import numpy as np
import pandas as pd

from ws1_harmonize import baselines, evaluate, model, panel as panelmod, write_harmonized as wh

P = "data/processed"
I = "data/interim/sheikh"


def _load():
    grid = pd.read_parquet(f"{P}/grid_daily.parquet")
    grid["date"] = pd.to_datetime(grid["date"]).dt.date
    cells = pd.read_parquet(f"{P}/cells.parquet")
    sd = pd.read_parquet(f"{P}/sensor_days.parquet")
    return grid, cells, sd


def _panel():
    return pd.read_parquet(f"{I}/panel.parquet")


def step_panel():
    os.makedirs(I, exist_ok=True)
    grid, cells, sd = _load()
    p = panelmod.build_panel(grid, cells, sd)
    p.to_parquet(f"{I}/panel.parquet", index=False)
    print(f"panel: {len(p)} rows, {p['cell_id'].nunique()} cells, {p['week_start'].nunique()} weeks")


def step_v0():
    grid, cells, sd = _load()
    p = _panel()
    params = baselines.fit(p)
    with open(f"{I}/b1_params.pkl", "wb") as f:
        pickle.dump(params, f)
    pred = baselines.predict_b1(params, p)
    qs = baselines.ratio_quantiles(p, pred)
    table = baselines.interval_table_v0(qs)
    with open(f"{P}/interval_table.json", "w") as f:
        json.dump(table, f, indent=1)
    h = wh.assemble(p, pred, baselines.predict_b0_frp(params, p), grid, cells, sd,
                    lambda a, m: baselines.n20_ratio(params, a, m), table, "b1")
    wh.write(h, f"{P}/harmonized.parquet")
    print(f"B0 ratios {params['b0']}; NOAA-20 ratio {params['b0_n20']:.3f}; overlap weeks {params['n_overlap_weeks']}")
    print(f"harmonized v0: {len(h)} rows; sources {h['source'].value_counts().to_dict()}; interval entries {len(table['entries'])}")


def step_model():
    p = _panel()
    if os.path.exists(f"{I}/metrics.csv") and "--reuse-metrics" in sys.argv:
        table = pd.read_csv(f"{I}/metrics.csv")
    else:
        table = evaluate.evaluate(p, quick="--quick" in sys.argv)
        table.to_csv(f"{I}/metrics.csv", index=False)
    print(table.round(3).to_string(index=False))
    choice = evaluate.select_method(table)
    with open(f"{I}/method.json", "w") as f:
        json.dump(choice, f, indent=1)
    print("method chosen:", choice)
    oof, m0 = evaluate.oof(p, choice["method"])
    from tools.verify_files import write_parquet_contract
    write_parquet_contract(oof, f"{P}/predictions_oof.parquet", "predictions_oof")
    full = model.fit(p)  # final model on all overlap rows
    model.save(full, f"{I}/lgbm")
    print(f"predictions_oof: {len(oof)} rows; splits {oof['split'].value_counts().to_dict()}")


def step_v1():
    grid, cells, sd = _load()
    p = _panel()
    with open(f"{I}/b1_params.pkl", "rb") as f:
        params = pickle.load(f)
    choice = json.load(open(f"{I}/method.json"))
    if choice["method"] == "lgbm":
        m = model.load(f"{I}/lgbm")
        pc, pf = model.predict(m, p)
    else:
        pc, pf = baselines.predict_b1(params, p), baselines.predict_b0_frp(params, p)
    version = "v1-" + choice["method"]
    with open(f"{P}/interval_table.json") as f:
        table = json.load(f)
    drift = pd.read_parquet(f"{P}/drift_flags.parquet") if os.path.exists(f"{P}/drift_flags.parquet") else None
    h = wh.assemble(p, pc, pf, grid, cells, sd, lambda a, mo: baselines.n20_ratio(params, a, mo), table, version, drift)
    wh.write(h, f"{P}/harmonized.parquet")
    yr = pd.to_datetime(h["date"]).dt.year
    seam = h.assign(year=yr).groupby("year")["source"].apply(lambda s: round((s == "modeled_from_modis").mean(), 3))
    print(f"harmonized v1: {len(h)} rows; table {table['version']}; drift flags {int(h['drift_flag'].sum())}")
    print("modeled share by year (seam check):", seam.loc[[2010, 2011, 2012, 2013]].to_dict())


def step_validation():
    t = pd.read_csv(f"{I}/metrics.csv")
    choice = json.load(open(f"{I}/method.json"))
    real_data = any("synthetic_" not in os.path.basename(path)
                    for path in glob.glob("data/raw/firms/*.csv*"))
    piece = {
        "schema_version": "1.0", "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "producer": "harmonization",
        "metrics": {"method_chosen": choice, "region_week": t.replace({np.nan: None}).to_dict(orient="records"),
                    "note": "region-week sums of SNPP-equivalent detections on test rows; spearman and lins_ccc closer to 1 is better"},
        "limitations": [
            "Values before 20 Jan 2012 are modeled from MODIS; they are estimates with intervals, not observations.",
            "Nov 2000 - Jul 2002 uses Terra alone; its error is reported separately (terra_only rows).",
            "After 2 Nov 2026 values are NOAA-20 detections scaled to SNPP terms by a region x month ratio.",
            "Terra and Aqua drifted off their designed orbits; the drift-era row shows how far the model degrades after 2021.",
            "Cell-level intervals are indicative only and are never summed; AOI intervals come from interval_table.json.",
            f"The learned model was {'kept' if choice['method'] == 'lgbm' else 'not used: the per-region ratio (B1) agreed better with held-out observations'}; see method_chosen.",
            ("These metrics were computed on downloaded FIRMS observations."
             if real_data else "These metrics use synthetic development data and do not establish real-world accuracy."),
        ]}
    os.makedirs(f"{P}/validation", exist_ok=True)
    with open(f"{P}/validation/harmonization.json", "w") as f:
        json.dump(piece, f, indent=1)
    print("validation/harmonization.json written")


if __name__ == "__main__":
    {"panel": step_panel, "v0": step_v0, "model": step_model, "v1": step_v1, "validation": step_validation}[sys.argv[1]]()
