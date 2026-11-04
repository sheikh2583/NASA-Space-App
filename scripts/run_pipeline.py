"""Run the whole pipeline in order (any OS). Uses real FIRMS files in data/raw/firms if present, else synthetic data.

  python scripts/run_pipeline.py            # full run (~35 min on 2 cores; the model step is most of it)
  python scripts/run_pipeline.py --quick    # fewer holdouts in the model step (~12 min)
  python scripts/run_pipeline.py --from v1  # resume from a step

Steps: synth, ingest, grid, sensors, cells, panel, v0, model, intervals, drift, v1, anomalies, outlook,
validation, fixtures, fallback, qa, results.
"""
from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PY = sys.executable


def cells_args(real: bool):
    """Real boundaries and land cover when present in data/raw (see docs/SHEIKH_GUIDE.md section 3)."""
    args = []
    admin = sorted(glob.glob(os.path.join(ROOT, "data", "raw", "boundaries", "*.geojson")))
    if admin:
        args += ["--admin1", *admin]
    lc = sorted(glob.glob(os.path.join(ROOT, "data", "raw", "landcover", "MCD12C1*.hdf")))
    if lc:
        args += ["--mcd12c1", lc[-1]]  # newest year
    elif real:
        args += ["--synthetic-landcover", "none"]  # never mix synthetic land cover with real fires
    return args


def steps(quick: bool):
    real = [p for p in glob.glob(os.path.join(ROOT, "data", "raw", "firms", "*.csv*")) if "synthetic_" not in os.path.basename(p)]
    firms_in = sorted(os.path.relpath(p, ROOT) for p in real) if real else ["data/raw/firms/synthetic_*.csv.gz"]
    model = ["-m", "ws1_harmonize.run", "model"] + (["--quick"] if quick else [])
    return [
        ("synth", None if real else [os.path.join("tools", "synth_firms.py")]),
        ("ingest", ["-m", "ws3_anomaly.ingest.normalize", *firms_in] + (["--clip", "demo"] if real else [])),
        ("grid", ["-m", "ws2_platform.grid"]),
        ("sensors", ["-m", "ws2_platform.sensors"]),
        ("cells", ["-m", "ws2_platform.cells"] + cells_args(bool(real))),
        ("panel", ["-m", "ws1_harmonize.run", "panel"]),
        ("v0", ["-m", "ws1_harmonize.run", "v0"]),
        ("model", model),
        ("intervals", ["-m", "ws4_outlook.run", "intervals"]),
        ("drift", ["-m", "ws4_outlook.run", "drift"]),
        ("v1", ["-m", "ws1_harmonize.run", "v1"]),
        ("anomalies", ["-m", "ws3_anomaly.batch"]),
        ("outlook", ["-m", "ws4_outlook.run", "outlook"]),
        ("validation", ["-m", "ws1_harmonize.run", "validation"]),
        ("fixtures", ["-m", "ws2_platform.api.make_fixtures"]),
        ("fallback", ["-m", "ws2_platform.api.static_export"]),
        ("qa", ["-m", "ws6_validation.qa"]),
        ("results", [os.path.join("scripts", "results.py")]),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--from", dest="start", default=None)
    a = ap.parse_args()
    todo = steps(a.quick)
    names = [n for n, _ in todo]
    if a.start:
        todo = todo[names.index(a.start):]
    real = any("synthetic_" not in os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "data", "raw", "firms", "*.csv*")))
    env = {**os.environ, "PYTHONPATH": ROOT, "PYTHONUNBUFFERED": "1"}
    if not real:
        env["ALLOW_SYNTHETIC_WEATHER"] = "1"  # synthetic fires go with synthetic weather only
    print("Mode:", "REAL FIRMS files" if real else "SYNTHETIC data (no real FIRMS files in data/raw/firms)", flush=True)
    for name, args in todo:
        if args is None:
            print(f"== {name}: skipped (real FIRMS files found)")
            continue
        t = time.time()
        print(f"== {name}", flush=True)
        r = subprocess.run([PY] + args, cwd=ROOT, env=env)
        if r.returncode != 0:
            print(f"!! step '{name}' failed. Fix it, then resume with:  python scripts/run_pipeline.py --from {name}")
            sys.exit(r.returncode)
        print(f"   done in {time.time() - t:.0f}s", flush=True)
    print("Pipeline complete. Start the app with scripts/start.sh (Linux/macOS) or scripts\\start.ps1 (Windows).")


if __name__ == "__main__":
    main()
