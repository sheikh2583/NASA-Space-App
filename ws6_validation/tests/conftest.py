"""Shared fixtures for Samiul's tests.

API tests run against API_BASE_URL when it is set (mock or live), otherwise in-process against the FastAPI app
on data/processed. Data tests skip when data/processed is missing (CI has no data).
"""
import json
import os

import pytest
import yaml

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(ROOT, "data", "processed")
FIX = os.path.join(ROOT, "contracts", "fixtures")


@pytest.fixture(scope="session")
def spec():
    with open(os.path.join(ROOT, "contracts", "openapi.yaml")) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def client():
    base = os.environ.get("API_BASE_URL")
    if base:
        import httpx

        class Remote:
            def __init__(self):
                self.c = httpx.Client(base_url=base.rstrip("/"), timeout=60)

            def post(self, path, json=None):
                return self.c.post(path, json=json)

            def get(self, path):
                return self.c.get(path)
        return Remote()
    if not os.path.exists(os.path.join(DATA, "harmonized.parquet")):
        pytest.skip("no API_BASE_URL and no data/processed: nothing to test against")
    from fastapi.testclient import TestClient
    from ws2_platform.api.app import app
    return TestClient(app)


@pytest.fixture(scope="session")
def fixture_request():
    def load(name):
        with open(os.path.join(FIX, name)) as f:
            return json.load(f)
    return load


def need_data(*names):
    missing = [n for n in names if not os.path.exists(os.path.join(DATA, n))]
    return pytest.mark.skipif(bool(missing), reason=f"data/processed missing {missing}")
