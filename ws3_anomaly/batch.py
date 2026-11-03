"""Precompute per-region products (Monazir): anomalies_region_week.parquet, critical_periods.parquet,
drivers_region.json. Usage: python -m ws3_anomaly.batch [--skip-drivers]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os

import numpy as np
import pandas as pd

from common.series import weekly_series
from tools.verify_files import write_parquet_contract
from ws3_anomaly.anomaly import score_series
from ws3_anomaly.drivers import driver_associations
from ws3_anomaly.loaders.weather import load_weather
from ws3_anomaly.periods import find_periods

P = "data/processed"


def region_series(h, cells, sd, table, region, end):
    s = weekly_series(h, cells, region_ids=[region], sensor_days=sd, table=table, start="2000-11-06", end=end)
    agri = weekly_series(h.assign(value_count=h["value_count"] * h["cropland_frac"].fillna(0)), cells, region_ids=[region],
                         sensor_days=sd, start="2000-11-06", end=end)
    s["agri_value"] = agri["value"].values
    return s


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-drivers", action="store_true")
    a = ap.parse_args(argv)
    h = pd.read_parquet(f"{P}/harmonized.parquet")
    cells = pd.read_parquet(f"{P}/cells.parquet")
    sd = pd.read_parquet(f"{P}/sensor_days.parquet")
    h = h.merge(cells[["cell_id", "cropland_frac"]], on="cell_id", how="left")
    table = json.load(open(f"{P}/interval_table.json"))
    end = pd.to_datetime(sd["date"]).max()
    anomalies, periods, drivers = [], [], {}
    for (region, name, country), _ in cells.groupby(["admin1_id", "admin1_name", "country"]):
        s = region_series(h, cells, sd, table, region, end)
        sc = score_series(s)
        anomalies.append(pd.DataFrame({
            "region_id": region, "week_start": sc["week_start"].dt.date, "value": sc["value"], "baseline": sc["baseline"],
            "score": sc["score"], "flag": sc["flag"], "exceeds_lower_bound": sc["exceeds_lower_bound"],
            "severity": np.clip(sc["value"] - sc["baseline"], 0, None) / np.maximum(sc["baseline"], 1.0),
            "depends_on_modeled_history": sc["depends_on_modeled_history"]}))
        ps = find_periods(sc, country)
        for p in ps:
            periods.append({"region_id": region, "period_id": p["rank"], **{k: p[k] for k in (
                "severity", "rank", "peak_value", "agri_tag", "n_weeks", "depends_on_modeled_history")},
                "start": dt.date.fromisoformat(p["start"]), "end": dt.date.fromisoformat(p["end"]),
                "agri_share": np.nan if p["agri_share"] is None else p["agri_share"]})
        if not a.skip_drivers:
            drivers[region] = driver_associations(s, load_weather(country), name)
        print(f"{region:6} flagged weeks {int(sc['flag'].sum()):3}  periods {len(ps):3}  top {ps[0]['start'] if ps else '-'}")
    an = pd.concat(anomalies, ignore_index=True)
    for c in ("value", "baseline", "score", "severity"):
        an[c] = an[c].astype("float32")
    write_parquet_contract(an, f"{P}/anomalies_region_week.parquet", "anomalies_region_week")
    cp = pd.DataFrame(periods)
    cp = cp.astype({"period_id": "int32", "rank": "int32", "n_weeks": "int32", "severity": "float32",
                    "peak_value": "float32", "agri_share": "float32"})
    write_parquet_contract(cp, f"{P}/critical_periods.parquet", "critical_periods")
    if drivers:
        with open(f"{P}/drivers_region.json", "w") as f:
            json.dump({"schema_version": "1.0", "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                       "regions": drivers}, f, indent=1)
    print(f"anomalies {len(an)} rows; critical periods {len(cp)}; drivers {len(drivers)} regions")


if __name__ == "__main__":
    main()
