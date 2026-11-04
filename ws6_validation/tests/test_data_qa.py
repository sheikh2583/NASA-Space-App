"""Data QA on data/processed (prompt P6.3; docs/project/qa-checklist.md). Skips when the data is not present."""
import datetime as dt
import os
import subprocess
import sys

import pandas as pd

from conftest import DATA, ROOT, need_data


def rd(name):
    return pd.read_parquet(os.path.join(DATA, name))


@need_data("grid_daily.parquet", "detections.parquet")
def test_grid_keys_sums_and_ranges():
    g, d = rd("grid_daily.parquet"), rd("detections.parquet")
    assert not g.duplicated(["cell_id", "date", "sat"]).any()
    assert int(g["n_det"].sum()) == len(d)
    assert (g[["n_det", "n_hiconf", "frp_sum"]] >= 0).all().all()
    assert pd.to_datetime(g["date"]).max().date() <= dt.date.today()
    assert pd.to_datetime(d["acq_date"]).min().date() >= dt.date(2000, 11, 1)


@need_data("detections.parquet")
def test_confidence_mapping_and_vegetation_only():
    d = rd("detections.parquet")
    assert set(d.loc[d["sensor"] == "VIIRS", "conf"].unique()) <= {20.0, 60.0, 90.0}
    assert d.loc[d["sensor"] == "MODIS", "conf"].between(0, 100).all()
    assert set(d["source_type"].unique()) <= {0, -1}


@need_data("cells.parquet")
def test_cells_filled():
    c = rd("cells.parquet")
    assert c["admin1_id"].notna().all()
    assert c["cropland_frac"].notna().all(), "land cover missing: agri tags fall back to the season rule"


@need_data("sensor_days.parquet", "grid_daily.parquet")
def test_rows_on_non_operating_days_are_documented():
    g, s = rd("grid_daily.parquet"), rd("sensor_days.parquet")
    m = g.merge(s, on=["date", "sat"], how="left")
    off = m[~m["operating"].fillna(False).astype(bool)]
    assert off["note"].fillna("").str.len().gt(0).all(), "grid rows on non-operating days without a documented reason"
    snpp = s[s["sat"] == "SNPP"].set_index("date")
    assert not snpp.loc[dt.date(2026, 11, 2), "operating"]


@need_data("harmonized.parquet", "sensor_days.parquet")
def test_harmonized_bounds_sources_and_seams():
    h = rd("harmonized.parquet")
    assert (h["lo_count"] <= h["value_count"] + 1e-4).all() and (h["value_count"] <= h["hi_count"] + 1e-4).all()
    assert (h["value_count"] >= 0).all() and h["source"].notna().all()
    h["date"] = pd.to_datetime(h["date"])
    assert (h.loc[h["date"] < "2012-01-19", "source"] == "modeled_from_modis").all()
    # SNPP era: a row may be other than observed SNPP only on a day SNPP was not operating (decision 24: outage days
    # are filled from NOAA-20 from 1 Apr 2018, modeled from MODIS before that).
    era = h[(h["date"] >= "2012-01-21") & (h["date"] < "2026-11-02")]
    other = era[era["source"] != "observed_viirs"]
    if len(other):
        sd = rd("sensor_days.parquet")
        snpp_off = set(pd.to_datetime(sd.loc[(sd["sat"] == "SNPP") & ~sd["operating"].astype(bool), "date"]))
        assert other["date"].isin(snpp_off).all(), "SNPP-era rows that are not observed fall on days SNPP operated"
        n20_era = other[other["date"] >= "2018-04-01"]
        assert (n20_era["source"] != "modeled_from_modis").mean() > 0.95, "NOAA-20 should fill SNPP outages from 2018"
    assert (h.loc[h["date"] >= "2026-11-02", "source"] == "adjusted_from_noaa20").all()
    obs = h[h["source"] == "observed_viirs"]
    assert (obs["lo_count"] == obs["value_count"]).all() and (obs["hi_count"] == obs["value_count"]).all()


@need_data("predictions_oof.parquet")
def test_oof_splits_and_no_leakage_labels():
    o = rd("predictions_oof.parquet")
    assert set(o["split"]) == {"train", "calib", "test"}
    assert (o.loc[o["split"] != "train", "fold"] == 0).all(), "calib and test rows must come from the fold-0 model only"
    assert (o.loc[o["split"] == "train", "fold"] > 0).all()


def test_verify_files_tool_passes_on_all_outputs():
    paths = [os.path.join(DATA, f) for f in sorted(os.listdir(DATA))] if os.path.isdir(DATA) else []
    paths = [p for p in paths if p.endswith((".parquet", ".json"))]
    vdir = os.path.join(DATA, "validation")
    if os.path.isdir(vdir):
        paths += [os.path.join(vdir, f) for f in sorted(os.listdir(vdir)) if f.endswith(".json")]
    if not paths:
        import pytest
        pytest.skip("no data/processed")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "verify_files.py"), *paths], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-2000:]
