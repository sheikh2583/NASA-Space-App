"""One cross-platform entry point for project workflows."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def run(*command: str, cwd: Path = ROOT, env: dict | None = None) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def train(quick: bool, start: str | None) -> None:
    command = [PY, "scripts/run_pipeline.py"]
    if quick:
        command.append("--quick")
    if start:
        command.extend(["--from", start])
    run(*command)


def test() -> None:
    run(PY, "-m", "pytest", "-q")
    run("npm", "test", cwd=ROOT / "ws5_frontend")


def build_ui() -> None:
    run("npm", "run", "build", cwd=ROOT / "ws5_frontend")


def serve(mock: bool) -> None:
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    app = "ws2_platform.api.mock_server:app" if mock else "ws2_platform.api.app:app"
    if not mock:
        env["DATA_DIR"] = str(ROOT / "data" / "processed")
    api = subprocess.Popen([PY, "-m", "uvicorn", app, "--port", "8000"], cwd=ROOT, env=env)
    try:
        run("npm", "run", "dev", cwd=ROOT / "ws5_frontend")
    finally:
        api.terminate()
        try:
            api.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api.kill()


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", choices=["train", "validate", "results", "test", "build", "dev", "all"])
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--from", dest="start")
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args(argv)

    if args.workflow == "train":
        train(args.quick, args.start)
    elif args.workflow == "validate":
        run(PY, "-m", "ws6_validation.qa")
    elif args.workflow == "results":
        run(PY, "scripts/results.py")
    elif args.workflow == "test":
        test()
    elif args.workflow == "build":
        build_ui()
    elif args.workflow == "dev":
        serve(args.mock)
    else:
        train(args.quick, args.start)
        run(PY, "scripts/results.py")
        test()
        build_ui()


if __name__ == "__main__":
    main()
