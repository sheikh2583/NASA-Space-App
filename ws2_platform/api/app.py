"""FastAPI service implementing contracts/openapi.yaml 0.2.0 (prompts P2.6, P2.8, P2.9).

Run:  DATA_DIR=data/processed uvicorn ws2_platform.api.app:app --port 8000
"""
from __future__ import annotations

import datetime as dt
import glob
import io
import json
import math
import os
from collections import OrderedDict
from typing import Literal, Optional

import numpy as np
import pandas as pd
from fastapi import Body, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field, model_validator

from ws2_platform.api.query import AOIError, Store
from ws3_anomaly.anomaly import score_series
from ws3_anomaly.periods import find_periods
from ws4_outlook import outlook as outlook_mod

SCHEMA_VERSION = "0.2.0"
DAY_CONVENTION = "local_solar_date"
EXPECTED_PIECES = ["harmonization", "intervals", "drift", "outlook_skill", "qa"]
SEAMS = ["2012-01-20", "2026-11-02"]

app = FastAPI(title="MODIS-VIIRS Harmonization API", version=SCHEMA_VERSION)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
_store: Store | None = None
_cache: "OrderedDict[str, dict]" = OrderedDict()


def store() -> Store:
    global _store
    if _store is None:
        _store = Store(os.environ.get("DATA_DIR", "data/processed"))
    return _store


class AOIRequest(BaseModel):
    geometry: Optional[dict] = None
    bbox: Optional[list[float]] = Field(default=None, min_length=4, max_length=4)
    start: dt.date
    end: dt.date
    res: Literal["day", "week", "month"] = "week"

    @model_validator(mode="after")
    def _one_area(self):
        if (self.geometry is None) == (self.bbox is None):
            raise ValueError("give exactly one of geometry or bbox")
        if self.start > self.end:
            raise ValueError("start must not be after end")
        return self


class CompareRequest(BaseModel):
    a: AOIRequest
    b: AOIRequest


class ExportRequest(AOIRequest):
    view: Literal["summary", "cells", "critical_periods"]


def envelope(res="week", notes=None) -> dict:
    return {"schema_version": SCHEMA_VERSION, "units": f"SNPP-equivalent detections per {res}",
            "day_convention": DAY_CONVENTION, "notes": notes or []}


def _num(x, nd=2):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), nd)


@app.exception_handler(AOIError)
async def aoi_error(_: Request, exc: AOIError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


def _cached(key: str, fn):
    if key in _cache:
        _cache.move_to_end(key)
        return _cache[key]
    val = fn()
    _cache[key] = val
    if len(_cache) > 256:
        _cache.popitem(last=False)
    return val


def _key(name, req: BaseModel) -> str:
    return name + ":" + req.model_dump_json()


def _scored(s: Store, sel, agri: bool = False):
    sc = s._memo("scored", sel, lambda: score_series(s.full_history(sel)))
    if agri:
        sc = sc.assign(agri_value=s.full_agri(sel).values[: len(sc)])
    return sc


def build_summary(req: AOIRequest) -> dict:
    s = store()
    sel = s.select(req.geometry, req.bbox)
    notes = ["Values before 20 Jan 2012 are modeled from MODIS; values after 2 Nov 2026 are NOAA-20 adjusted to SNPP terms."]
    if sel.empty:
        return {**envelope(req.res, notes + ["No grid cells in this area."]), "aoi": {"n_cells": 0, "area_km2": 0.0},
                "res": req.res, "seams": SEAMS, "series": []}
    end = min(pd.Timestamp(req.end), s.data_end)
    flags = {}
    if req.res == "week":
        hist = s.full_history(sel)
        ser = hist[(hist["week_start"] >= pd.Timestamp(req.start) - pd.Timedelta(days=6)) & (hist["week_start"] <= end)]
        sc = _scored(s, sel).set_index("week_start")
        flags = sc[["flag", "score", "exceeds_lower_bound", "depends_on_modeled_history"]].to_dict("index")
    else:
        ser = s.series(sel, req.start, end, req.res)
        notes.append("Unusual-week flags are computed for weekly resolution only.")
    if req.res == "day":
        notes.append("Day points carry no interval; modeled weeks without MODIS detections are booked on Mondays.")
    pts = []
    for _, r in ser.iterrows():
        f = flags.get(r["week_start"])
        pt = {"t": r["week_start"].date().isoformat(), "value": _num(r["value"]), "lo": _num(r["lo"]), "hi": _num(r["hi"]),
              "source": r["source"] or "modeled_from_modis", "modeled_share": round(float(r["modeled_share"]), 3),
              "drift_flag": bool(r["drift_flag"])}
        if f is not None:
            pt["anomaly"] = {"flag": bool(f["flag"]), "score": _num(f["score"], 2) or 0.0,
                             "exceeds_lower_bound": bool(f["exceeds_lower_bound"]),
                             "depends_on_modeled_history": bool(f["depends_on_modeled_history"])}
        pts.append(pt)
    lat = np.deg2rad(sel["lat_c"].values)
    area = float(np.sum((0.1 * 111.32) ** 2 * np.cos(lat)))
    return {**envelope(req.res, notes), "aoi": {"n_cells": int(len(sel)), "area_km2": round(area, 1)},
            "res": req.res, "seams": SEAMS, "series": pts}


@app.get("/health")
def health():
    s = store()
    return {"status": "ok", "method_version": s.version, "data_through": s.data_end.date().isoformat(), "cells": int(len(s.cells))}


@app.post("/aoi/summary")
def aoi_summary(req: AOIRequest):
    return _cached(_key("summary", req), lambda: build_summary(req))


@app.post("/aoi/cells")
def aoi_cells(req: AOIRequest):
    def run():
        s = store()
        sel = s.select(req.geometry, req.bbox)
        t = s.cell_totals(sel, req.start, req.end)
        cells = [{"cell_id": int(r.cell_id), "lat_c": round(float(r.lat_c), 3), "lon_c": round(float(r.lon_c), 3),
                  "value": round(float(r.value), 2), "modeled_share": round(float(r.modeled_share), 3)} for r in t.itertuples()]
        return {**envelope("period"), "period": {"start": req.start.isoformat(), "end": req.end.isoformat()}, "cells": cells}
    return _cached(_key("cells", req), run)


@app.post("/aoi/critical-periods")
def aoi_periods(req: AOIRequest):
    def run():
        s = store()
        sel = s.select(req.geometry, req.bbox)
        if sel.empty:
            return {**envelope(), "periods": []}
        reg = s.region_of(sel)
        ps = find_periods(_scored(s, sel, agri=True), reg["country"] if reg else None)
        ps = [p for p in ps if p["end"] >= req.start.isoformat() and p["start"] <= req.end.isoformat()]
        for r, p in enumerate(ps, start=1):
            p["rank"] = r
        return {**envelope(notes=["Periods are ranked by severity: weeks of typical burning above normal."]), "periods": ps}
    return _cached(_key("periods", req), run)


@app.post("/aoi/drivers")
def aoi_drivers(req: AOIRequest):
    s = store()
    sel = s.select(req.geometry, req.bbox)
    reg = s.region_of(sel)
    if reg is None or reg["region_id"] not in s.drivers:
        return {**envelope(), "region": reg and {k: reg[k] for k in ("region_id", "region_name")} or {"region_id": "", "region_name": ""},
                "status": "insufficient_data", "items": [], "caveats": ["No driver analysis is available for this area."]}
    d = s.drivers[reg["region_id"]]
    return {**envelope(notes=[f"Drivers are computed for {reg['region_name']}, the region covering most of this area."]),
            "region": {"region_id": reg["region_id"], "region_name": reg["region_name"]},
            "status": d.get("status", "ok"), "items": d["items"], "caveats": d["caveats"]}


@app.post("/aoi/outlook")
def aoi_outlook(req: AOIRequest):
    def run():
        s = store()
        sel = s.select(req.geometry, req.bbox)
        reg = s.region_of(sel)
        hist = s.full_history(sel)
        as_of = s.data_end + pd.Timedelta(days=1)
        live = outlook_mod.outlook(hist, as_of=as_of, data_through=s.data_end.date().isoformat())
        ro = s.outlooks.get(reg["region_id"], {}) if reg else {}
        return {**envelope(notes=["Current status is computed for the drawn area; skill and alerts come from its main region."]),
                "region": {"region_id": reg["region_id"], "region_name": reg["region_name"]} if reg else {"region_id": "", "region_name": ""},
                "as_of": live["as_of"], "current_status": live["current_status"],
                "season_to_date_percentile": live["season_to_date_percentile"], "expected_range": live["expected_range"],
                "skill": ro.get("skill", {"n_seasons": 0}), "status": ro.get("status", "no_demonstrated_skill"),
                "alert": ro.get("alert", {"level": "none", "rule": "Forecast alerts are off."})}
    return _cached(_key("outlook", req), run)


@app.post("/aoi/compare")
def aoi_compare(req: CompareRequest):
    a, b = req.a, req.b
    start, end = min(a.start, b.start), max(a.end, b.end)
    a2, b2 = a.model_copy(update={"start": start, "end": end, "res": a.res}), b.model_copy(update={"start": start, "end": end, "res": a.res})
    return {**envelope(a.res), "a": aoi_summary(a2), "b": aoi_summary(b2)}


@app.get("/meta/validation")
def meta_validation():
    d = os.path.join(store().data_dir, "validation")
    pieces = {}
    for p in sorted(glob.glob(os.path.join(d, "*.json"))):
        try:
            v = json.load(open(p))
            pieces[v.get("producer", os.path.basename(p)[:-5])] = v
        except Exception:  # a broken piece must not break the page
            continue
    return {**envelope(), "pieces": pieces, "missing": [x for x in EXPECTED_PIECES if x not in pieces]}


@app.post("/export")
def export(req: ExportRequest):
    if req.view == "summary":
        rows = build_summary(req)["series"]
        df = pd.DataFrame([{**{k: v for k, v in r.items() if k != "anomaly"}, "anomaly_flag": (r.get("anomaly") or {}).get("flag", False)}
                           for r in rows])
    elif req.view == "cells":
        df = pd.DataFrame(aoi_cells(req)["cells"])
    else:
        df = pd.DataFrame(aoi_periods(req)["periods"])
    buf = io.StringIO()
    df.to_csv(buf, index=False)  # header row first, so spreadsheets open it directly; units are in the file name
    return Response(buf.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="burning_{req.view}_{req.start}_{req.end}_snpp-equivalent-detections.csv"'})
