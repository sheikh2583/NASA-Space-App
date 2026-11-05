"""Samin's steps. Run after Sheikh's `model` step (needs predictions_oof.parquet and the saved model).

  python -m ws4_outlook.run intervals   # interval_table.json v1 + validation/intervals.json      (H30)
  python -m ws4_outlook.run drift       # drift_flags.parquet + validation/drift.json            (H30)
  python -m ws4_outlook.run outlook     # outlook_region.json + validation/outlook_skill.json    (H34)
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import glob

import numpy as np
import pandas as pd

from common.series import weekly_series
from common import compute
from tools.verify_files import write_parquet_contract
from ws1_harmonize import model as lgbm
from ws3_anomaly.loaders.weather import load_weather
from ws4_outlook import alerts, conformal, drift, interval_report, outlook

P, I = "data/processed", "data/interim/sheikh"
NOW = lambda: dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def piece(producer, metrics, limitations):
    os.makedirs(f"{P}/validation", exist_ok=True)
    with open(f"{P}/validation/{producer}.json", "w") as f:
        metrics = {**metrics, "training_backend": compute.backend()}
        real = any("synthetic_" not in os.path.basename(path) for path in glob.glob("data/raw/firms/*.csv*"))
        if real:
            limitations = [text.replace("Built on SYNTHETIC data; rerun on real data before quoting.",
                                         "Computed from downloaded FIRMS observations.") for text in limitations]
        json.dump({"schema_version": "1.0", "generated_at": NOW(), "producer": producer, "metrics": metrics,
                   "limitations": limitations}, f, indent=1)


def step_intervals():
    oof = pd.read_parquet(f"{P}/predictions_oof.parquet")
    cells = pd.read_parquet(f"{P}/cells.parquet")
    table, cov = conformal.build_table(oof, cells)
    with open(f"{P}/interval_table.json", "w") as f:
        json.dump(table, f, indent=1)
    allrow = [r for r in cov["coverage"] if r["landcover"] == "all"]
    print(f"interval_table v1: {len(table['entries'])} entries; test coverage {[(r['res'], r['coverage']) for r in allrow]}")
    piece("intervals", cov, [
        "Calibrated on 2012 onward (where SNPP observations exist); coverage before 2012 is not guaranteed.",
        "Coverage is measured on randomly drawn rectangles in held-out test blocks; very large or unusual areas may differ.",
        "Rows below 90% coverage are reported as they are; the band is then too narrow for that land cover and season.",
        "Built on SYNTHETIC data; rerun on real data before quoting."])


def step_interval_report():
    oof = pd.read_parquet(f"{P}/predictions_oof.parquet")
    cells = pd.read_parquet(f"{P}/cells.parquet")
    with open(f"{P}/interval_table.json") as f:
        table = json.load(f)
    piece("intervals_by_stratum", interval_report.report(oof, cells, table), [
        "Coverage is measured on random rectangles from held-out test blocks only.",
        "Terra-only diagnostics use overlap-era holdouts, not observed truth for pre-2012.",
        "Area-size groups count unique contributing OOF cells; absent cells are not counted as evaluated.",
        "Nominal 90% does not guarantee conditional coverage; every stop-condition row is reported.",
        "Relative interval width is a diagnostic, not an optimization target."])


def step_drift():
    p = pd.read_parquet(f"{I}/panel.parquet")
    choice = json.load(open(f"{I}/method.json"))
    if choice["method"] in {"lgbm", "xgb"}:
        pred, _ = lgbm.predict(lgbm.load(f"{I}/{choice['method']}"), p)
    else:
        import pickle
        from ws1_harmonize import baselines
        pred = baselines.predict_b1(pickle.load(open(f"{I}/b1_params.pkl", "rb")), p)
    a = drift.ratio_flags(p, pred)
    b = drift.applicability_flags(p)
    flags = pd.concat([b[["region_id", "year", "drift_flag", "reason"]], a[a["year"] >= 2012][["region_id", "year", "drift_flag", "reason"]]])
    flags["year"] = flags["year"].astype("int32")
    write_parquet_contract(flags, f"{P}/drift_flags.parquet", "drift_flags")
    print(f"drift_flags: {len(flags)} region-years, flagged {int(flags['drift_flag'].sum())}")
    print(flags[flags["drift_flag"]].groupby("year").size().to_dict())
    piece("drift", {"flagged_region_years": flags[flags["drift_flag"]][["region_id", "year", "reason"]].to_dict(orient="records"),
                    "ratio_z": a[["region_id", "year", "z"]].round(2).to_dict(orient="records"),
                    "applicability_auc": b[["region_id", "year", "auc"]].round(3).replace({np.nan: None}).to_dict(orient="records")}, [
        "Drift after 2012 compares observed SNPP with the model; it cannot be checked after the SNPP cutoff (2 Nov 2026).",
        "Before 2012 there is no observation to compare with; the flag only says the MODIS inputs look unlike the training years.",
        "Built on SYNTHETIC data; rerun on real data before quoting."])


def step_outlook():
    h = pd.read_parquet(f"{P}/harmonized.parquet")
    cells = pd.read_parquet(f"{P}/cells.parquet")
    sd = pd.read_parquet(f"{P}/sensor_days.parquet")
    table = json.load(open(f"{P}/interval_table.json"))
    end = pd.to_datetime(sd["date"]).max()
    as_of = end + pd.Timedelta(days=1)
    regions, skills = {}, []
    for (region, name, country), _ in cells.groupby(["admin1_id", "admin1_name", "country"]):
        w = weekly_series(h, cells, region_ids=[region], sensor_days=sd, table=table, start="2000-11-06", end=end)
        sk, status = outlook.evaluate_forecast(w, load_weather(country))
        al = alerts.no_forecast_bounds()
        o = outlook.outlook(w, as_of=as_of, skill=sk, status=status, alert=al, data_through=end.date().isoformat())
        regions[region] = {"region_name": name, **o}
        skills.append({"region_id": region, **sk, "status": status})
        print(f"{region}: status {status}, skill vs clim {sk['vs_climatology']} CI {sk['ci']}, now {o['current_status']['level']}")
    with open(f"{P}/outlook_region.json", "w") as f:
        json.dump({"schema_version": "1.0", "generated_at": NOW(), "regions": regions}, f, indent=1)
    piece("outlook_skill", {"by_region": skills, "horizon_weeks": "2-4", "loss": "pinball (median)"}, [
        "Skill is measured on forward-season folds with training-only climatology and target-boundary embargoes.",
        "Forecast alerts are off until genuine validated forecast lower-bound percentiles are available.",
        "Where status is no_demonstrated_skill the app shows the current-season position only, not a forecast.",
        "Built on SYNTHETIC data; rerun on real data before quoting."])


def main(command=None):
    command = command or sys.argv[1]
    if command in {'drift', 'outlook'}:
        compute.configure_cuda_training()
    {"intervals": step_intervals, "interval_report": step_interval_report,
     "drift": step_drift, "outlook": step_outlook}[command]()


if __name__ == "__main__":
    main()
