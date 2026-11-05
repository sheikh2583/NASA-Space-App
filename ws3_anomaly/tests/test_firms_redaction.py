"""Offline credential-boundary regressions; no requests, fitting or scientific outputs."""
import datetime as dt
import traceback
from urllib.parse import quote, quote_plus

import pandas as pd
import pytest
import requests

from ws3_anomaly.ingest import firms

KEY = "dummy/credential +private"
DAY = dt.date(2026, 11, 1)
BBOX = [88, 20, 89, 21]


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(firms.time, "sleep", lambda seconds: None)


class BrokenSession:
    def __init__(self, kind):
        self.kind = kind
        self.calls = 0

    def get(self, url, timeout):
        self.calls += 1
        if self.kind == "connection":
            raise requests.ConnectionError(f"failed {url} also {quote(KEY, safe='')}")
        body = "Invalid " + KEY + " " + quote_plus(KEY)
        return type("Response", (), {"status_code": 403, "text": body})()


def assert_private(text):
    for variant in (KEY, quote(KEY, safe=""), quote_plus(KEY)):
        assert variant not in text


@pytest.mark.parametrize("kind", ["connection", "http"])
def test_fetch_errors_have_no_credential_or_original_context(kind):
    session = BrokenSession(kind)
    with pytest.raises(RuntimeError) as caught:
        firms.fetch_window(session, KEY, "VIIRS_NOAA20_NRT", BBOX, DAY, 1, retries=2)
    assert session.calls == 2
    assert_private(str(caught.value))
    assert_private("".join(traceback.format_exception(caught.value)))
    assert caught.value.__context__ is None
    assert caught.value.__cause__ is None


@pytest.mark.parametrize("kind", ["connection", "http"])
def test_download_logs_and_gaps_are_redacted(kind, caplog, tmp_path):
    paths, gaps = firms.download("VIIRS_NOAA20_NRT", BBOX, DAY, DAY, tmp_path,
                                key=KEY, session=BrokenSession(kind))
    assert paths == [] and len(gaps) == 1
    assert_private(caplog.text)
    assert_private(str(gaps))
    assert "***" in caplog.text


def test_parse_failure_loses_context_and_key(monkeypatch):
    class Session:
        def get(self, url, timeout):
            return type("Response", (), {"status_code": 200, "text": "latitude,longitude\n1,2\n"})()

    def bad_parse(*args, **kwargs):
        raise ValueError("parse failure " + KEY)

    monkeypatch.setattr(pd, "read_csv", bad_parse)
    with pytest.raises(RuntimeError) as caught:
        firms.fetch_window(Session(), KEY, "VIIRS_NOAA20_NRT", BBOX, DAY, 1)
    assert_private("".join(traceback.format_exception(caught.value)))
    assert caught.value.__context__ is None


def test_redacts_before_response_body_truncation():
    class Session:
        def get(self, url, timeout):
            return type("Response", (), {"status_code": 500, "text": "x" * 195 + KEY})()

    with pytest.raises(RuntimeError) as caught:
        firms.fetch_window(Session(), KEY, "VIIRS_NOAA20_NRT", BBOX, DAY, 1, retries=1)
    assert "dummy" not in str(caught.value)


def test_file_failure_and_directory_failure_are_safe(monkeypatch, caplog, tmp_path):
    def bad_window(*args, **kwargs):
        raise OSError("write error " + KEY)

    monkeypatch.setattr(firms, "fetch_window", bad_window)
    _, gaps = firms.download("VIIRS_NOAA20_NRT", BBOX, DAY, DAY, tmp_path, key=KEY)
    assert_private(str(gaps) + caplog.text)

    def bad_directory(*args, **kwargs):
        raise OSError("directory error " + KEY)

    monkeypatch.setattr(firms.os, "makedirs", bad_directory)
    with pytest.raises(RuntimeError) as caught:
        firms.download("VIIRS_NOAA20_NRT", BBOX, DAY, DAY, tmp_path, key=KEY)
    assert_private("".join(traceback.format_exception(caught.value)))


def test_valid_and_empty_csv_cache_are_preserved(tmp_path):
    class Session:
        calls = 0

        def get(self, url, timeout):
            self.calls += 1
            return type("Response", (), {"status_code": 200, "text": "latitude,longitude\n"})()

    session = Session()
    paths, gaps = firms.download("VIIRS_NOAA20_NRT", BBOX, DAY, DAY, tmp_path, key=KEY, session=session)
    assert len(paths) == 1 and not gaps and session.calls == 1
    assert pd.read_csv(paths[0]).empty
    assert firms.download("VIIRS_NOAA20_NRT", BBOX, DAY, DAY, tmp_path,
                          key=KEY, session=session) == (paths, [])
    assert session.calls == 1


@pytest.mark.parametrize("retries", [0, -1, 1.5])
def test_invalid_retry_count_fails_before_request(retries):
    session = BrokenSession("connection")
    with pytest.raises(ValueError, match="positive integer"):
        firms.fetch_window(session, KEY, "VIIRS_NOAA20_NRT", BBOX, DAY, 1, retries=retries)
    assert session.calls == 0
