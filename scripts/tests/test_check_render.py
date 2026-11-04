"""Render deploy check with a fake HTTP function: no network (plan card T17)."""
import json

from scripts import check_render as cr

URL, COMMIT, THROUGH = "https://firesense.example.onrender.com", "abc123", "2026-11-02"


def fake_service(commit=COMMIT, data_through=THROUGH, asleep_for=0):
    calls = {"health": 0}

    def http(method, url, body=None, timeout=90):
        path = url[len(URL):]
        if path == "/health":
            calls["health"] += 1
            if calls["health"] <= asleep_for:
                return 0, "timed out"
            return 200, json.dumps({"status": "ok", "method_version": "v1-B1", "data_through": data_through, "cells": 2532})
        if path == "/version.json":
            return 200, json.dumps({"commit": commit, "mode": "live-api"})
        if path == "/":
            return 200, '<!doctype html><div id="root"></div>'
        if path == "/aoi/summary" and method == "POST" and body:
            return 200, json.dumps({"series": [{"t": "2026-10-26", "value": 1.0}]})
        if path == "/docs":
            return 200, "<html>docs</html>"
        return 404, "not found"
    return http, calls


def run(monkeypatch, **service):
    http, calls = fake_service(**service)
    monkeypatch.setattr(cr, "http", http)
    lines, sleeps = [], []
    ok = cr.check(URL, COMMIT, THROUGH, sleep=sleeps.append, out=lines.append)
    return ok, lines, sleeps, calls


def test_all_checks_pass_on_a_healthy_service(monkeypatch):
    ok, lines, sleeps, _ = run(monkeypatch)
    assert ok and not sleeps
    assert sum(ln.startswith("PASS") for ln in lines) == 8 and not any(ln.startswith("FAIL") for ln in lines)


def test_a_wrong_commit_fails(monkeypatch):
    ok, lines, _, _ = run(monkeypatch, commit="old000")
    assert not ok and any(ln.startswith("FAIL  /version.json commit") and "old000" in ln for ln in lines)


def test_a_data_through_mismatch_fails(monkeypatch):
    ok, lines, _, _ = run(monkeypatch, data_through="2026-10-01")
    assert not ok and any(ln.startswith("FAIL  /health data_through") for ln in lines)


def test_a_sleeping_service_that_wakes_on_the_third_try_passes(monkeypatch):
    ok, lines, sleeps, calls = run(monkeypatch, asleep_for=2)
    assert ok and calls["health"] == 3 and sleeps == [cr.WAKE_PAUSE_S, cr.WAKE_PAUSE_S]


def test_a_service_that_never_wakes_fails_after_six_tries(monkeypatch):
    ok, _, sleeps, calls = run(monkeypatch, asleep_for=99)
    assert not ok and calls["health"] == cr.WAKE_TRIES and len(sleeps) == cr.WAKE_TRIES - 1


def test_render_url_reads_dotenv_and_nothing_else(tmp_path, monkeypatch):
    monkeypatch.delenv("RENDER_URL", raising=False)
    monkeypatch.setattr(cr, "ROOT", tmp_path)
    (tmp_path / ".env").write_text("FIRMS_MAP_KEY=secret\nRENDER_URL=https://x.onrender.com/\n", encoding="utf-8")
    assert cr.render_url(None) == "https://x.onrender.com"
    assert cr.render_url("https://y.onrender.com/") == "https://y.onrender.com"
