"""cells.parquet: every grid cell in the demo regions with admin1 and land cover.

Admin1: a geoBoundaries ADM1 GeoJSON (shapeID, shapeName) if given, else data/raw/synthetic/admin1.geojson.
Land cover: MODIS MCD12C1 (HDF4, 0.05 degree class percentages, read with pyhdf) if given, else the synthetic
table. If neither exists, cropland_frac stays null and agri tags fall back to the region-season rule (decision 8).

Usage: python -m ws2_platform.cells [--admin1 BGD.geojson IND.geojson] [--mcd12c1 PATH.hdf] [--out data/processed/cells.parquet]
"""
from __future__ import annotations

import argparse
import json
import os

import numpy as np
import pandas as pd
import pyarrow as pa
from shapely import STRtree, points
from shapely.geometry import shape

from common.grid import cell_center, cells_in_bbox
from common.regions import DEMO_REGIONS
from ws2_platform.grid import write

SCHEMA = pa.schema([("cell_id", pa.int32()), ("lat_c", pa.float32()), ("lon_c", pa.float32()),
                    ("landcover_dom", pa.string()), ("cropland_frac", pa.float32()), ("forest_frac", pa.float32()),
                    ("admin1_id", pa.string()), ("admin1_name", pa.string()), ("country", pa.string())])
# IGBP classes in MCD12C1 Land_Cover_Type_1_Percent: 12 croplands, 14 cropland/natural mosaic (half), 1-5 forests.
CROP_CLASSES, MOSAIC_CLASS, FOREST_CLASSES = [12], 14, [1, 2, 3, 4, 5]


def admin1_lookup(cells: pd.DataFrame, geojson_paths) -> pd.DataFrame:
    paths = [geojson_paths] if isinstance(geojson_paths, str) else list(geojson_paths)
    feats = [ft for p in paths for ft in json.load(open(p))["features"]]
    geoms = [shape(ft["geometry"]) for ft in feats]
    tree = STRtree(geoms)
    pts = points(cells["lon_c"].values, cells["lat_c"].values)
    pi, gi = tree.query(pts, predicate="intersects")  # border points match too; first polygon wins
    ids = np.full(len(cells), None, dtype=object)
    names = np.full(len(cells), None, dtype=object)
    groups = np.full(len(cells), None, dtype=object)
    for p, g in zip(pi, gi):
        if ids[p] is not None:
            continue
        props = feats[g]["properties"]
        ids[p], names[p] = props.get("shapeID"), props.get("shapeName")
        groups[p] = props.get("shapeGroup")
    # country = demo region code (BD, PB), not the boundary file's ISO code, so season rules and weather match.
    demo = np.full(len(cells), None, dtype=object)
    for code, meta in DEMO_REGIONS.items():
        x0, y0, x1, y1 = meta["bbox"]
        inside = cells["lon_c"].between(x0, x1).values & cells["lat_c"].between(y0, y1).values
        demo[inside & (demo == None)] = code  # noqa: E711
    return cells.assign(admin1_id=ids, admin1_name=names, country=demo)


def mcd12c1_fractions(path: str, cells: pd.DataFrame) -> pd.DataFrame:
    """Average the 0.05 degree class percentages over the 2x2 sub-cells of each 0.1 degree cell."""
    from pyhdf.SD import SD, SDC
    pct = SD(path, SDC.READ).select("Land_Cover_Type_1_Percent")[:]  # (3600, 7200, 17), row 0 = 90N
    r = ((90 - cells["lat_c"].values) / 0.05).astype(int)
    c = ((cells["lon_c"].values + 180) / 0.05).astype(int)
    sub = np.stack([pct[np.clip(r + dr, 0, 3599), np.clip(c + dc, 0, 7199)] for dr in (-1, 0) for dc in (-1, 0)]).mean(0)
    crop = (sub[:, CROP_CLASSES].sum(1) + 0.5 * sub[:, MOSAIC_CLASS]) / 100
    forest = sub[:, FOREST_CLASSES].sum(1) / 100
    return pd.DataFrame({"cell_id": cells["cell_id"].values, "cropland_frac": crop, "forest_frac": forest})


def build_cells(admin1_path, landcover: pd.DataFrame | None) -> pd.DataFrame:
    ids = np.concatenate([cells_in_bbox(*m["bbox"]) for m in DEMO_REGIONS.values()])
    lat, lon = cell_center(ids)
    cells = pd.DataFrame({"cell_id": ids.astype("int32"), "lat_c": lat, "lon_c": lon}).drop_duplicates("cell_id")
    cells = admin1_lookup(cells, admin1_path)
    if landcover is not None:
        cells = cells.merge(landcover[["cell_id", "cropland_frac", "forest_frac"]], on="cell_id", how="left")
        cells["cropland_frac"] = cells["cropland_frac"].fillna(0.0)
        cells["forest_frac"] = cells["forest_frac"].fillna(0.0)
        cells["landcover_dom"] = np.where(cells["cropland_frac"] >= 0.5, "cropland",
                                          np.where(cells["forest_frac"] >= 0.3, "forest", "mosaic"))
    else:
        cells["cropland_frac"] = np.nan
        cells["forest_frac"] = np.nan
        cells["landcover_dom"] = None
    for c in ("lat_c", "lon_c", "cropland_frac", "forest_frac"):
        cells[c] = cells[c].astype("float32")
    return cells[[f.name for f in SCHEMA]].sort_values("cell_id").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--admin1", nargs="+", default=["data/raw/synthetic/admin1.geojson"])
    ap.add_argument("--mcd12c1", default=None)
    ap.add_argument("--synthetic-landcover", default="data/raw/synthetic/landcover.parquet")
    ap.add_argument("--out", default="data/processed/cells.parquet")
    a = ap.parse_args(argv)
    lc = None
    if a.mcd12c1:
        lat_lon = build_cells(a.admin1, None)
        lc = mcd12c1_fractions(a.mcd12c1, lat_lon)
    elif a.synthetic_landcover != "none" and os.path.exists(a.synthetic_landcover):
        lc = pd.read_parquet(a.synthetic_landcover)
    cells = build_cells(a.admin1, lc)
    write(cells, a.out, SCHEMA)
    print(f"cells: {len(cells)} -> {a.out}; admin1 missing: {int(cells['admin1_id'].isna().sum())}")
    print(cells.groupby(["country", "admin1_id"]).size().to_string())


if __name__ == "__main__":
    main()
