"""Mock API (prompt P2.2): serves contracts/fixtures/ with the real endpoint paths, no data needed.
Picks the Punjab fixture when the request has a geometry, otherwise the Bangladesh one.

Run: uvicorn ws2_platform.api.mock_server:app --port 8001
"""
from __future__ import annotations

import json
import os

from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

FIX = os.environ.get("FIXTURES_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "contracts", "fixtures"))
app = FastAPI(title="MODIS-VIIRS mock API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def fx(name):
    with open(os.path.join(FIX, name)) as f:
        return json.load(f)


def which(body: dict) -> str:
    if body.get("bbox") and (body["bbox"][2] - body["bbox"][0]) * (body["bbox"][3] - body["bbox"][1]) * 100 > 6000:
        return "oversized"
    if body.get("bbox") == [0, 0, 0.5, 0.5]:
        return "empty"
    return "punjab" if body.get("geometry") else "bangladesh"


@app.get("/health")
def health():
    return {"status": "ok", "mock": True}


def _aoi(kind):
    def handler(body: dict = Body(...)):
        w = which(body)
        if w == "oversized":
            return JSONResponse(status_code=422, content={"detail": "area too large (mock)"})
        if w == "empty" and kind == "summary":
            r = fx("bangladesh_summary.json")
            return {**r, "aoi": {"n_cells": 0, "area_km2": 0.0}, "series": [], "notes": ["No grid cells in this area."]}
        return fx(f"{w}_{kind}.json")
    return handler


for kind in ("summary", "cells", "critical-periods", "drivers", "outlook"):
    app.post(f"/aoi/{kind}")(_aoi(kind))


@app.post("/aoi/compare")
def compare(body: dict = Body(...)):
    return fx("compare.json")


@app.get("/meta/validation")
def validation():
    return fx("meta_validation.json")


@app.post("/export")
def export(body: dict = Body(...)):
    s = fx("bangladesh_summary.json")["series"]
    rows = ["t,value,lo,hi,source,modeled_share,drift_flag"] + [
        f"{p['t']},{p['value']},{p['lo']},{p['hi']},{p['source']},{p['modeled_share']},{p['drift_flag']}" for p in s]
    return Response("\n".join(rows) + "\n", media_type="text/csv")
