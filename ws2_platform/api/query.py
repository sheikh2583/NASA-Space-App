"""AOI query layer: drawn polygon or bbox -> cells -> series and products (prompt P2.5; decision 20)."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from shapely import STRtree, points
from shapely.geometry import shape

from common.series import OBSERVED, weekly_series

MAX_CELLS = int(os.environ.get("AOI_MAX_CELLS", "6000"))
HISTORY_START = "2000-11-06"


class AOIError(ValueError):
    """Invalid or too large AOI (HTTP 422)."""


@dataclass
class Store:
    data_dir: str
    cells: pd.DataFrame = field(init=False)
    harmonized: pd.DataFrame = field(init=False)
    sensor_days: pd.DataFrame = field(init=False)
    table: dict = field(init=False)
    drivers: dict = field(init=False)
    outlooks: dict = field(init=False)

    def __post_init__(self):
        d = self.data_dir
        self.cells = pd.read_parquet(f"{d}/cells.parquet")
        h = pd.read_parquet(f"{d}/harmonized.parquet")
        h["date"] = pd.to_datetime(h["date"])
        self.harmonized = h.merge(self.cells[["cell_id", "cropland_frac"]], on="cell_id", how="left")
        self.sensor_days = pd.read_parquet(f"{d}/sensor_days.parquet")
        self.table = json.load(open(f"{d}/interval_table.json"))
        self.drivers = self._regions(f"{d}/drivers_region.json")
        self.outlooks = self._regions(f"{d}/outlook_region.json")
        self.tree = STRtree(points(self.cells["lon_c"].values, self.cells["lat_c"].values))
        self.data_end = pd.to_datetime(self.sensor_days["date"]).max()
        self.version = h["method_version"].iloc[0] if len(h) else "none"

    @staticmethod
    def _regions(path):
        return json.load(open(path))["regions"] if os.path.exists(path) else {}

    # -------------------------------------------------------------- selection
    def select(self, geometry=None, bbox=None) -> pd.DataFrame:
        if geometry is not None:
            try:
                geom = shape(geometry)
            except Exception as e:  # noqa: BLE001
                raise AOIError(f"geometry is not valid GeoJSON: {e}")
            if not geom.is_valid or geom.area == 0:
                raise AOIError("geometry must be a valid, non-empty polygon")
            self._check_size(geom.area * 100)
            idx = self.tree.query(geom, predicate="intersects")
            sel = self.cells.iloc[np.sort(idx)]
        elif bbox is not None:
            x0, y0, x1, y1 = bbox
            if x0 >= x1 or y0 >= y1:
                raise AOIError("bbox must be [min_lon, min_lat, max_lon, max_lat]")
            self._check_size((x1 - x0) * (y1 - y0) * 100)
            c = self.cells
            sel = c[(c["lon_c"] >= x0) & (c["lon_c"] <= x1) & (c["lat_c"] >= y0) & (c["lat_c"] <= y1)]
        else:
            raise AOIError("give exactly one of geometry or bbox")
        return sel

    @staticmethod
    def _check_size(n_cells_est: float):
        """Grid cells are 0.1 x 0.1 degree, so area in square degrees x 100 = number of cells drawn."""
        if n_cells_est > MAX_CELLS:
            raise AOIError(f"area too large: about {n_cells_est:,.0f} grid cells (limit {MAX_CELLS:,}, roughly "
                           f"{MAX_CELLS * 110:,} km2). Draw a smaller area.")

    def region_of(self, sel: pd.DataFrame) -> dict | None:
        if sel.empty or sel["admin1_id"].isna().all():
            return None
        rid = sel["admin1_id"].mode().iloc[0]
        name = sel.loc[sel["admin1_id"] == rid, "admin1_name"].iloc[0]
        return {"region_id": rid, "region_name": name, "country": sel.loc[sel["admin1_id"] == rid, "country"].iloc[0]}

    # -------------------------------------------------------------- series
    def series(self, sel, start, end, res="week", with_intervals=True) -> pd.DataFrame:
        return weekly_series(self.harmonized, self.cells, cell_ids=sel["cell_id"].values, res=res, start=start, end=end,
                             sensor_days=self.sensor_days, table=self.table if with_intervals else None)

    def agri_series(self, sel, start, end) -> pd.Series:
        h = self.harmonized.assign(value_count=self.harmonized["value_count"] * self.harmonized["cropland_frac"].fillna(0))
        return weekly_series(h, self.cells, cell_ids=sel["cell_id"].values, start=start, end=end,
                             sensor_days=self.sensor_days)["value"]

    def _memo(self, kind, sel, fn):
        key = (kind, hash(sel["cell_id"].values.tobytes()))
        cache = self.__dict__.setdefault("_memo_cache", {})
        if key not in cache:
            if len(cache) > 64:
                cache.pop(next(iter(cache)))
            cache[key] = fn()
        return cache[key]

    def full_history(self, sel) -> pd.DataFrame:
        """Weekly series from the start of the record, cached per cell set (shared by summary, periods, outlook)."""
        return self._memo("hist", sel, lambda: self.series(sel, HISTORY_START, self.data_end, "week"))

    def full_agri(self, sel) -> pd.Series:
        return self._memo("agri", sel, lambda: self.agri_series(sel, HISTORY_START, self.data_end))

    def cell_totals(self, sel, start, end) -> pd.DataFrame:
        h = self.harmonized
        m = h["cell_id"].isin(sel["cell_id"].values) & (h["date"] >= pd.Timestamp(start)) & (h["date"] <= pd.Timestamp(end))
        x = h.loc[m, ["cell_id", "value_count", "source"]]
        x = x.assign(nonobs=np.where(x["source"] == OBSERVED, 0.0, x["value_count"]))
        g = x.groupby("cell_id")[["value_count", "nonobs"]].sum()
        g = g[g["value_count"] > 0]
        g["modeled_share"] = (g["nonobs"] / g["value_count"]).clip(0, 1)
        out = g.join(self.cells.set_index("cell_id")[["lat_c", "lon_c"]]).reset_index()
        return out.rename(columns={"value_count": "value"})
