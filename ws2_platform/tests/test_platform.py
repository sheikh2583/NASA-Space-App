import datetime as dt
import json

import numpy as np
import pandas as pd

from common.grid import cell_id
from ws2_platform import cells as cellsmod
from ws2_platform import grid, sensors


def _det():
    return pd.DataFrame({
        "sensor": ["VIIRS", "VIIRS", "MODIS", "VIIRS"], "sat": ["SNPP", "SNPP", "Aqua", "SNPP"],
        "acq_date": [dt.date(2024, 3, 1)] * 3 + [dt.date(2024, 3, 1)],
        "acq_time": [730, 735, 730, 1930], "lat": [23.70, 23.71, 23.70, 23.70], "lon": [90.05, 90.06, 90.05, 90.05],
        "frp": [1.0, 3.0, 10.0, 2.0], "conf": [90, 60, 85, 20], "daynight": ["D", "D", "D", "N"],
        "scan": [0.4, 0.5, 1.0, 0.4], "track": [0.4] * 4, "source_type": [0] * 4, "product_version": ["2.0SP"] * 4})


def test_grid_sums_keys_and_local_date():
    g = grid.grid_daily(_det())
    assert g["n_det"].sum() == 4
    assert not g.duplicated(["cell_id", "date", "sat"]).any()
    snpp_day = g[(g["sat"] == "SNPP") & (g["date"] == dt.date(2024, 3, 1))].iloc[0]
    assert snpp_day["n_det"] == 2 and snpp_day["n_hiconf"] == 1 and snpp_day["frp_sum"] == 4
    # the 19:30 UTC night detection at lon 90 is the next local solar day
    assert ((g["sat"] == "SNPP") & (g["date"] == dt.date(2024, 3, 2))).sum() == 1
    assert g.iloc[0]["cell_id"] == cell_id(23.70, 90.05) and (cell_id(23.70, 90.05) // 3600) == 1137


def test_sensor_days_marks_snpp_cutoff_and_outages():
    days = pd.date_range("2026-03-20", "2026-11-05").date
    g = pd.DataFrame({"sat": ["SNPP"] * len(days) + ["Terra"] * len(days), "date": list(days) * 2})
    sd = sensors.sensor_days(g)
    snpp = sd[sd["sat"] == "SNPP"].set_index("date")
    assert snpp.loc[dt.date(2026, 11, 1), "operating"] and not snpp.loc[dt.date(2026, 11, 2), "operating"]
    assert "partial" in snpp.loc[dt.date(2026, 11, 2), "note"]
    terra = sd[sd["sat"] == "Terra"].set_index("date")
    assert not terra.loc[dt.date(2026, 3, 26), "operating"]
    kept, n = sensors.drop_non_operating(g, sd)
    assert n == (~sd["operating"] & sd.set_index(["date", "sat"]).index.isin(g.set_index(["date", "sat"]).index)).sum()


def test_cells_admin1_covers_borders(tmp_path):
    fc = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"shapeID": "A", "shapeName": "A", "shapeGroup": "BD"},
         "geometry": {"type": "Polygon", "coordinates": [[[88, 20.5], [90.35, 20.5], [90.35, 26.7], [88, 26.7], [88, 20.5]]]}},
        {"type": "Feature", "properties": {"shapeID": "B", "shapeName": "B", "shapeGroup": "BD"},
         "geometry": {"type": "Polygon", "coordinates": [[[90.35, 20.5], [92.7, 20.5], [92.7, 26.7], [90.35, 26.7], [90.35, 20.5]]]}},
        {"type": "Feature", "properties": {"shapeID": "P", "shapeName": "P", "shapeGroup": "PB"},
         "geometry": {"type": "Polygon", "coordinates": [[[73.5, 28], [78, 28], [78, 32.5], [73.5, 32.5], [73.5, 28]]]}}]}
    p = tmp_path / "a.geojson"
    p.write_text(json.dumps(fc))
    c = cellsmod.build_cells(str(p), None)
    assert c["admin1_id"].notna().all() and c["cropland_frac"].isna().all()
    assert set(c["admin1_id"]) == {"A", "B", "P"}
