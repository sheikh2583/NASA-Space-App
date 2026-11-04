"""Enable/status GitHub Pages using the existing Git credential helper; never prints credentials."""
from __future__ import annotations

import argparse
import os
import subprocess
import requests

REPO = "sheikh2583/NASA-Space-App"
API = f"https://api.github.com/repos/{REPO}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--enable", action="store_true", help="Set repository Pages source to GitHub Actions")
    args = parser.parse_args()
    credential = subprocess.run(["git", "credential", "fill"],
        input=f"protocol=https\nhost=github.com\npath={REPO}.git\n\n", text=True,
        capture_output=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "Never"})
    fields = dict(line.split("=", 1) for line in credential.stdout.splitlines() if "=" in line)
    token = fields.get("password")
    if not token:
        raise SystemExit("No existing Git credential available. Use GitHub Settings > Pages > Source: GitHub Actions.")
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    response = session.get(API + "/pages", timeout=30)
    if args.enable:
        if response.status_code == 404:
            response = session.post(API + "/pages", json={"build_type": "workflow"}, timeout=30)
        elif response.ok and response.json().get("build_type") != "workflow":
            response = session.put(API + "/pages", json={"build_type": "workflow"}, timeout=30)
        if not response.ok:
            raise SystemExit(f"Pages configuration HTTP {response.status_code}. An admin must select GitHub Actions in repository Settings > Pages.")
        response = session.get(API + "/pages", timeout=30)
    if response.ok:
        site = response.json()
        print("Pages:", site.get("html_url"), "source:", site.get("build_type"), "status:", site.get("status"))
    else:
        print("Pages status HTTP", response.status_code)
    runs = session.get(API + "/actions/workflows/pages.yml/runs", params={"per_page": 3}, timeout=30)
    if runs.ok:
        for run in runs.json()["workflow_runs"]:
            print(run["head_sha"][:8], run["status"], run.get("conclusion"), run["html_url"])


if __name__ == "__main__":
    main()
