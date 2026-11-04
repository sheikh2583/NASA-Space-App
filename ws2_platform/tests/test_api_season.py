"""POST /aoi/season on tiny data (plan card T07). Tiny data ends 31 Dec 2016; its paddy season peaks on 2 Nov."""
import json
import os

import jsonschema
import yaml
from openapi_schema_validator import OAS30Validator

from ws2_platform.tests.conftest import tiny_request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _openapi_valid(doc):
    with open(os.path.join(ROOT, "contracts", "openapi.yaml"), encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    v = OAS30Validator({"$ref": "#/components/schemas/SeasonProfileResponse", "components": spec["components"]})
    errors = list(v.iter_errors(doc))
    assert not errors, "; ".join(f"{list(e.path)}: {e.message}" for e in errors[:5])


def _profile_valid(doc):
    with open(os.path.join(ROOT, "contracts", "json_schemas", "season_profile.schema.json"), encoding="utf-8") as f:
        schema = json.load(f)
    profile = {**doc, "schema_version": doc["profile_version"]}   # the envelope's version replaces the profile's
    profile = {k: v for k, v in profile.items() if k in schema.get("properties", profile)}
    jsonschema.validate(profile, schema)


def season(api, area, **kw):
    r = api.post("/aoi/season", json=tiny_request(area, **kw))
    assert r.status_code == 200, r.text[:300]
    return r.json()


def test_punjab_has_wheat_and_paddy_seasons_at_the_right_time(tiny_api):
    doc = season(tiny_api, "pb")
    _openapi_valid(doc)
    _profile_valid(doc)
    by = {s["name"]: s for s in doc["seasons"]}
    assert set(by) == {"wheat_residue", "paddy_residue"}
    assert by["paddy_residue"]["typical"]["p50"]["median_md"] in ("11-01", "11-02", "11-03")
    assert "05-08" <= by["wheat_residue"]["typical"]["p50"]["median_md"] <= "05-10"


def test_bangladesh_has_one_dry_season_peaking_in_march(tiny_api):
    doc = season(tiny_api, "bd")
    _openapi_valid(doc)
    assert [s["name"] for s in doc["seasons"]] == ["dry_season"]
    assert doc["seasons"][0]["typical"]["p50"]["median_md"].startswith("03-")


def test_the_requested_dates_do_not_change_the_profile(tiny_api):
    assert season(tiny_api, "pb") == season(tiny_api, "pb", start="2010-01-01", end="2012-12-31")


def test_an_area_without_cells_returns_no_seasons_and_says_why(tiny_api):
    r = tiny_api.post("/aoi/season", json={"bbox": [0, 0, 0.5, 0.5], "start": "2004-01-01", "end": "2016-12-31", "res": "week"})
    assert r.status_code == 200
    doc = r.json()
    _openapi_valid(doc)
    assert doc["seasons"] == [] and doc["notes"]
