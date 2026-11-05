"""Mock API (prompt P2.2): serves contracts/fixtures/ with the real endpoint paths, no data needed.
Resolves named catalog areas by country, with legacy geometry/bbox fixture selection retained.

Run: uvicorn ws2_platform.api.mock_server:app --port 8001
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from functools import lru_cache

from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

FIX = os.environ.get("FIXTURES_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "contracts", "fixtures"))
app = FastAPI(title="MODIS-VIIRS mock API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def fx(name):
    with open(os.path.join(FIX, name)) as f:
        return json.load(f)


@lru_cache(maxsize=1)
def named_areas():
    path = Path(__file__).resolve().parents[2] / "ws5_frontend/public/demo/areas.json"
    with path.open(encoding="utf-8") as stream:
        return {area["id"]: area for area in json.load(stream)["areas"]}


def which(body: dict) -> str:
    if body.get("area_id") is not None:
        area = named_areas().get(body["area_id"])
        if area is None or body.get("bbox") is not None or body.get("geometry") is not None:
            return "invalid"
        return "bangladesh" if area["country"] == "BD" else "punjab"
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
        if w == "invalid":
            return JSONResponse(status_code=422, content={"detail": "unknown or conflicting named area (mock)"})
        if w == "oversized":
            return JSONResponse(status_code=422, content={"detail": "area too large (mock)"})
        if w == "empty" and kind == "summary":
            r = fx("bangladesh_summary.json")
            return {**r, "aoi": {"n_cells": 0, "area_km2": 0.0}, "series": [], "notes": ["No grid cells in this area."]}
        return fx(f"{w}_{kind}.json")
    return handler


for kind in ("summary", "cells", "critical-periods", "drivers", "outlook", "season"):
    app.post(f"/aoi/{kind}")(_aoi(kind))


@app.post("/aoi/compare")
def compare(body: dict = Body(...)):
    a, b = which(body.get("a", {})), which(body.get("b", {}))
    if a not in {"punjab", "bangladesh"} or b not in {"punjab", "bangladesh"}:
        return JSONResponse(status_code=422, content={"detail": "invalid comparison area (mock)"})
    return {**fx("compare.json"), "a": fx(f"{a}_summary.json"), "b": fx(f"{b}_summary.json")}


@app.get("/meta/validation")
def validation():
    return fx("meta_validation.json")


@app.post("/export")
def export(body: dict = Body(...)):
    area = which(body)
    if area not in {"punjab", "bangladesh"}:
        return JSONResponse(status_code=422, content={"detail": "invalid export area (mock)"})
    s = fx(f"{area}_summary.json")["series"]
    rows = ["t,value,lo,hi,source,modeled_share,drift_flag"] + [
        f"{p['t']},{p['value']},{p['lo']},{p['hi']},{p['source']},{p['modeled_share']},{p['drift_flag']}" for p in s]
    return Response("\n".join(rows) + "\n", media_type="text/csv")
