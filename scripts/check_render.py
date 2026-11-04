"""Verify the live Render service after a deploy (plan card T17).

    python scripts/check_render.py                              # URL from RENDER_URL (environment or .env)
    python scripts/check_render.py --url https://x.onrender.com --commit <sha>

Checks /health (status, cells, data_through = deployment/runtime.json), /version.json (commit = --commit, default
`git rev-parse HEAD`; mode live-api), / (the web app), POST /aoi/summary (a small Bangladesh request) and /docs.
The first request retries up to 6 times, 15 s apart, because a free Render service sleeps after 15 idle minutes.
Exit code 0 only when every check passes. Nothing from .env is printed except RENDER_URL. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
WAKE_TRIES, WAKE_PAUSE_S = 6, 15


def http(method: str, url: str, body: dict | None = None, timeout: float = 90) -> tuple[int, str]:
    """(status, text); the one network function, replaced in tests. Errors become status 0 with the reason."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"} if data else {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as e:
        return 0, str(getattr(e, "reason", e))


def render_url(cli: str | None) -> str | None:
    if cli:
        return cli.rstrip("/")
    if os.environ.get("RENDER_URL"):
        return os.environ["RENDER_URL"].strip().rstrip("/")
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("RENDER_URL="):
                return line.split("=", 1)[1].strip().strip('"').strip("'").rstrip("/") or None
    return None


def head_commit() -> str:
    r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT)
    return r.stdout.strip()


def check(url: str, commit: str, data_through: str, sleep=time.sleep, out=print) -> bool:
    results = []

    def report(name: str, ok: bool, measured: str):
        results.append(ok)
        out(f"{'PASS' if ok else 'FAIL'}  {name}: {measured}")

    status, text = 0, ""
    for attempt in range(1, WAKE_TRIES + 1):
        status, text = http("GET", f"{url}/health")
        if status == 200:
            break
        out(f"..    /health not answering yet (attempt {attempt}/{WAKE_TRIES}: {status or text[:80]}); waiting for the service to wake")
        if attempt < WAKE_TRIES:
            sleep(WAKE_PAUSE_S)
    try:
        h = json.loads(text) if status == 200 else {}
    except json.JSONDecodeError:
        h = {}
    report("/health status", h.get("status") == "ok", f"HTTP {status}, status={h.get('status')!r}")
    report("/health cells", isinstance(h.get("cells"), int) and h["cells"] > 0, f"cells={h.get('cells')}")
    report("/health data_through", h.get("data_through") == data_through,
           f"{h.get('data_through')} (expected {data_through} from deployment/runtime.json)")

    status, text = http("GET", f"{url}/version.json")
    try:
        v = json.loads(text) if status == 200 else {}
    except json.JSONDecodeError:
        v = {}
    report("/version.json commit", v.get("commit") == commit, f"{v.get('commit')} (expected {commit})")
    report("/version.json mode", v.get("mode") == "live-api", f"mode={v.get('mode')!r}")

    status, text = http("GET", f"{url}/")
    report("/ web app", status == 200 and '<div id="root">' in text, f"HTTP {status}")

    body = json.loads((ROOT / "contracts/fixtures/bangladesh_request.json").read_text(encoding="utf-8"))
    t0 = time.monotonic()
    status, text = http("POST", f"{url}/aoi/summary", body)
    took = time.monotonic() - t0
    try:
        n = len(json.loads(text).get("series", [])) if status == 200 else 0
    except json.JSONDecodeError:
        n = 0
    report("POST /aoi/summary", status == 200 and n > 0, f"HTTP {status}, {n} points in {took:.1f} s")

    status, _ = http("GET", f"{url}/docs")
    report("/docs", status == 200, f"HTTP {status}")
    ok = all(results)
    out(f"\n{'ALL CHECKS PASSED' if ok else 'SOME CHECKS FAILED'} for {url}")
    return ok


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--url", help="service URL (default: RENDER_URL from the environment or .env)")
    ap.add_argument("--commit", help="expected deployed commit (default: git rev-parse HEAD)")
    a = ap.parse_args(argv)
    url = render_url(a.url)
    if not url:
        print("Set RENDER_URL in .env (card H01) or pass --url.")
        return 2
    manifest = json.loads((ROOT / "deployment/runtime.json").read_text(encoding="utf-8"))
    print(f"Checking {url}")
    return 0 if check(url, a.commit or head_commit(), manifest["data_through"]) else 1


if __name__ == "__main__":
    sys.exit(main())
