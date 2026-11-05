"""Outlook regressions using fake histories behind the non-fitting tiny TestClient fixture."""
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
import yaml
from openapi_schema_validator import OAS30Validator

from ws2_platform.api import app as api
from ws2_platform.tests.conftest import tiny_request


def fake_history(monkeypatch, history, record_end):
    fake = SimpleNamespace(
        select=lambda *args: pd.DataFrame({"cell_id": [1]}),
        region_of=lambda selected: None,
        full_history=lambda selected: history.copy(),
        data_end=pd.Timestamp(record_end), outlooks={},
    )
    monkeypatch.setattr(api, "_store", fake)
    api._cache.clear()


@pytest.mark.parametrize("values,level", [([], "insufficient_history"), ([30.0], "insufficient_history"),
                                          ([np.nan], "incomplete_coverage")])
def test_short_reference_history_is_http_200_with_nulls_and_valid_contract(tiny_api, monkeypatch, values, level):
    history = pd.DataFrame({"week_start": pd.date_range("2026-10-26", periods=len(values), freq="7D"),
                            "value": values, "source": ["observed_viirs"] * len(values)})
    fake_history(monkeypatch, history, "2026-11-01")
    response = tiny_api.post("/aoi/outlook", json=tiny_request("bd"))
    assert response.status_code == 200
    result = response.json()
    assert result["current_status"]["level"] == level
    assert result["current_status"]["week_percentile"] is None
    assert result["season_to_date_percentile"] is None
    assert result["season_to_date_status"] == level
    assert result["current_status"]["data_through"] == "2026-11-01"
    if values and np.isfinite(values[0]):
        assert result["current_status"]["data_source"] == "observed_viirs"
    json.dumps(result, allow_nan=False)
    spec = yaml.safe_load((Path(__file__).resolve().parents[2] / "contracts/openapi.yaml").read_text(encoding="utf-8"))
    validator = OAS30Validator({"$ref": "#/components/schemas/OutlookResponse", "components": spec["components"]})
    assert not list(validator.iter_errors(result))


def test_api_passes_actual_record_end_and_evaluated_week_source(tiny_api, monkeypatch):
    history = pd.DataFrame({
        "week_start": pd.to_datetime(["2025-10-20", "2026-10-19", "2026-10-26"]),
        "value": [50.0, 50.0, 10000.0],
        "source": ["observed_viirs", "observed_viirs", "adjusted_from_noaa20"],
    })
    fake_history(monkeypatch, history, "2026-10-31")
    response = tiny_api.post("/aoi/outlook", json=tiny_request("bd"))
    assert response.status_code == 200
    result = response.json()
    assert result["as_of"] == "2026-11-01"
    assert result["current_status"]["data_through"] == "2026-10-31"
    assert result["current_status"]["data_source"] == "observed_viirs"
    assert "19 Oct 2026" in result["current_status"]["message"]
    assert "26 Oct 2026" not in result["current_status"]["message"]
