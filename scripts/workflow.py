"""One cross-platform entry point for project workflows."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import shutil
import socket
import time
import urllib.request
import webbrowser


ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def run(*command: str, cwd: Path = ROOT, env: dict | None = None) -> None:
    if command[0] == "npm":
        command = (shutil.which("npm.cmd" if os.name == "nt" else "npm") or "npm", *command[1:])
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def train(quick: bool, start: str | None, backend: str = "cuda", gpu_id: int = 0, threads: int = 8) -> None:
    os.environ.update(FIRESENSE_BACKEND=backend, FIRESENSE_GPU_ID=str(gpu_id), FIRESENSE_THREADS=str(threads))
    run(PY, "scripts/prepare_training.py")
    command = [PY, "scripts/run_pipeline.py", "--backend", backend, "--gpu-id", str(gpu_id), "--threads", str(threads)]
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


def serve(mock: bool, open_browser: bool = False) -> None:
    for port in (8000, 5173):
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                raise RuntimeError(f"Port {port} is busy. Close the existing project server first.")
    if not mock and not (ROOT / "data/processed/harmonized.parquet").exists():
        raise RuntimeError("No trained outputs. Run train first, or dev --mock for the fixture demo.")
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    env["VITE_DATA_MODE"] = "synthetic" if mock else "real"
    app = "ws2_platform.api.mock_server:app" if mock else "ws2_platform.api.app:app"
    if not mock:
        env["DATA_DIR"] = str(ROOT / "data" / "processed")
    api = subprocess.Popen([PY, "-m", "uvicorn", app, "--port", "8000"], cwd=ROOT, env=env)
    frontend = None
    try:
        npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
        if not npm:
            raise RuntimeError("npm is missing; run setup first.")
        frontend = subprocess.Popen([npm, "run", "dev", "--", "--host", "127.0.0.1", "--strictPort"],
                                    cwd=ROOT / "ws5_frontend", env=env)
        deadline = time.monotonic() + 60
        for url in ("http://127.0.0.1:8000/openapi.json", "http://127.0.0.1:5173"):
            while True:
                if api.poll() is not None or frontend.poll() is not None:
                    raise RuntimeError("A server exited during startup; see the messages above.")
                try:
                    with urllib.request.urlopen(url, timeout=2):
                        break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise RuntimeError(f"Timed out waiting for {url}")
                    time.sleep(0.3)
        print("UI ready: http://127.0.0.1:5173 — Ctrl+C stops both servers.", flush=True)
        if open_browser:
            webbrowser.open("http://127.0.0.1:5173")
        while api.poll() is None and frontend.poll() is None:
            time.sleep(0.5)
        raise RuntimeError("A server stopped unexpectedly.")
    except KeyboardInterrupt:
        print("Stopping project servers.")
    finally:
        for process in (frontend, api):
            if process is None or process.poll() is not None:
                continue
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
            else:
                process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", choices=["gpu-check", "prepare", "smoke", "share", "train", "validate", "results", "test", "build", "dev", "all"])
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--from", dest="start")
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--open", action="store_true", help="Open browser when both servers are ready")
    parser.add_argument("--backend", choices=["cpu", "cuda"], default="cuda", help="Training backend; CUDA is explicit and cannot fall back silently")
    parser.add_argument("--gpu-id", type=int, default=0)
    parser.add_argument("--threads", type=int, default=8, help="CPU workers for model libraries and matrix construction")
    args = parser.parse_args(argv)

    if args.workflow == "prepare":
        os.environ.update(FIRESENSE_BACKEND=args.backend, FIRESENSE_GPU_ID=str(args.gpu_id), FIRESENSE_THREADS=str(args.threads))
        run(PY, "scripts/prepare_training.py")
    elif args.workflow == "gpu-check":
        os.environ.update(FIRESENSE_BACKEND="cuda", FIRESENSE_GPU_ID=str(args.gpu_id), FIRESENSE_THREADS=str(args.threads))
        sys.path.insert(0, str(ROOT))
        from common.compute import probe_cuda
        print(probe_cuda())
    elif args.workflow == "smoke":
        run(PY, "scripts/smoke.py")
    elif args.workflow == "share":
        run(PY, "scripts/share_zip.py")
    elif args.workflow == "train":
        train(args.quick, args.start, args.backend, args.gpu_id, args.threads)
    elif args.workflow == "validate":
        run(PY, "-m", "ws6_validation.qa")
    elif args.workflow == "results":
        run(PY, "scripts/results.py")
    elif args.workflow == "test":
        test()
    elif args.workflow == "build":
        build_ui()
    elif args.workflow == "dev":
        serve(args.mock, args.open)
    else:
        train(args.quick, args.start, args.backend, args.gpu_id, args.threads)
        run(PY, "scripts/results.py")
        test()
        build_ui()


if __name__ == "__main__":
    main()
