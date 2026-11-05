"""Run the whole pipeline in order (any OS). Uses real FIRMS files in data/raw/firms if present, else synthetic data.

  python scripts/run_pipeline.py            # full CUDA run; measured timings in results/runs/
  python scripts/run_pipeline.py --backend cuda --threads 8  # explicit CUDA ML stages
  python scripts/run_pipeline.py --quick    # fewer holdouts in the model step
  python scripts/run_pipeline.py --from v1  # resume from a step

Steps: synth, ingest, grid, cells, sensors, panel, v0, model, intervals, interval_report, drift, v1, anomalies, outlook,
validation, fixtures, qa, results.
"""
from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys
import time
import json
import shutil
import datetime as dt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PY = sys.executable


def cells_args(real: bool):
    """Real boundaries and land cover when present in data/raw (see docs/guides/data.md section 3)."""
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
        ("cells", ["-m", "ws2_platform.cells"] + cells_args(bool(real))),
        ("sensors", ["-m", "ws2_platform.sensors"]),
        ("panel", ["-m", "ws1_harmonize.run", "panel"]),
        ("v0", ["-m", "ws1_harmonize.run", "v0"]),
        ("model", model),
        ("intervals", ["-m", "ws4_outlook.run", "intervals"]),
        ("interval_report", ["-m", "ws4_outlook.run", "interval_report"]),
        ("drift", ["-m", "ws4_outlook.run", "drift"]),
        ("v1", ["-m", "ws1_harmonize.run", "v1"]),
        ("anomalies", ["-m", "ws3_anomaly.batch"]),
        ("outlook", ["-m", "ws4_outlook.run", "outlook"]),
        ("validation", ["-m", "ws1_harmonize.run", "validation"]),
        ("fixtures", ["-m", "ws2_platform.api.make_fixtures"]),
        ("qa", ["-m", "ws6_validation.qa"]),
        ("results", [os.path.join("scripts", "results.py")]),
    ]


def selected_steps(quick: bool, start: str | None = None):
    """Plan execution only. A sensors resume rebuilds cells from current boundary inputs."""
    todo = steps(quick)
    names = [name for name, _ in todo]
    if start:
        selected = todo[names.index(start):]
        if start == "sensors":
            selected.insert(0, todo[names.index("cells")])
        return selected
    return todo


def validate_resume_backend(start: str | None, backend: str) -> None:
    names = [name for name, _ in steps(False)]
    downstream = names[names.index("intervals"):]
    if start not in downstream:
        return
    path = os.path.join(ROOT, "data/interim/sheikh/method.json")
    if not os.path.exists(path):
        raise RuntimeError("Resuming downstream stages requires an existing method.json; start from model instead.")
    with open(path) as stream:
        prior_backend = json.load(stream).get("compute_backend", "cpu")
    if prior_backend != backend:
        raise RuntimeError(f"Stored model evaluation used {prior_backend}; requested {backend}. Resume from model to avoid mixing backends.")


def stage_placement(todo, backend):
    active = [name for name, args in todo if args is not None]
    cuda = [name for name in active if backend == "cuda" and name in {"model", "drift", "outlook"}]
    return cuda, [name for name in active if name not in cuda]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--from", dest="start", default=None, choices=[name for name, _ in steps(False)])
    ap.add_argument("--backend", choices=["cuda"], default="cuda")
    ap.add_argument("--gpu-id", type=int, default=0)
    ap.add_argument("--threads", type=int, default=8)
    a = ap.parse_args()
    sys.path.insert(0, ROOT)
    os.environ.update(FIRESENSE_BACKEND=a.backend, FIRESENSE_GPU_ID=str(a.gpu_id), FIRESENSE_THREADS=str(a.threads))
    os.environ.pop("FIRESENSE_COMPUTE_LOG", None)  # preflight must not append to a previous run's audit log
    from common import compute
    compute.configure_cuda_training()
    hardware = compute.probe_cuda()
    validate_resume_backend(a.start, a.backend)
    todo = selected_steps(a.quick, a.start)
    cuda_stages, cpu_stages = stage_placement(todo, a.backend)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    run_dir = os.path.join(ROOT, "results", "runs", stamp)
    os.makedirs(run_dir)
    os.environ["FIRESENSE_COMPUTE_LOG"] = os.path.join(run_dir, "cuda-fits.jsonl")
    # Keep the previous validated outputs recoverable before any CUDA run writes.
    backup = None
    if a.backend == "cuda":
        backup = os.path.join(ROOT, "data", "runs", stamp, "baseline")
        for source, name in (("data/processed", "processed"), ("data/interim/sheikh", "sheikh")):
            if os.path.isdir(os.path.join(ROOT, source)):
                shutil.copytree(os.path.join(ROOT, source), os.path.join(backup, name))
        print("Previous outputs backed up:", backup, flush=True)
    report = {"started_at": dt.datetime.now(dt.timezone.utc).isoformat(), "quick": a.quick,
              "start_stage": a.start, "hardware": hardware, "backup": backup, "stages": [], "status": "running",
              "cuda_stages": cuda_stages, "cpu_stages": cpu_stages}
    def save_report():
        with open(os.path.join(run_dir, "execution.json"), "w", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2)
    save_report()
    real = any("synthetic_" not in os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "data", "raw", "firms", "*.csv*")))
    env = {**os.environ, "PYTHONPATH": ROOT, "PYTHONUNBUFFERED": "1"}
    if not real:
        env["ALLOW_SYNTHETIC_WEATHER"] = "1"  # synthetic fires go with synthetic weather only
    print("Mode:", "REAL FIRMS files" if real else "SYNTHETIC data (no real FIRMS files in data/raw/firms)", flush=True)
    print("Compute:", hardware, "report:", run_dir, flush=True)
    pipeline_started = time.perf_counter()
    for name, args in todo:
        if args is None:
            print(f"== {name}: skipped (real FIRMS files found)")
            continue
        t = time.time()
        print(f"== {name}", flush=True)
        r = subprocess.run([PY] + args, cwd=ROOT, env=env)
        report["stages"].append({"name": name, "seconds": round(time.time() - t, 3), "exit_code": r.returncode})
        save_report()
        if r.returncode != 0:
            report["status"] = "failed"
            report["seconds"] = round(time.perf_counter() - pipeline_started, 3)
            save_report()
            quick_flag = " --quick" if a.quick else ""
            print(f"!! step '{name}' failed. Fix it, then resume with:  python scripts/run_pipeline.py --from {name} --backend {a.backend} --gpu-id {a.gpu_id} --threads {a.threads}{quick_flag}")
            sys.exit(r.returncode)
        print(f"   done in {time.time() - t:.0f}s", flush=True)
    report["status"] = "passed"
    report["seconds"] = round(time.perf_counter() - pipeline_started, 3)
    log = os.environ["FIRESENSE_COMPUTE_LOG"]
    if os.path.exists(log):
        events = [json.loads(line) for line in open(log, encoding="utf-8")]
        report["cuda_fit_count"] = len(events)
        report["cuda_fit_seconds"] = round(sum(event["seconds"] for event in events), 3)
        report["cuda_fits_by_purpose"] = {purpose: sum(event["purpose"] == purpose for event in events)
                                         for purpose in sorted({event["purpose"] for event in events})}
    save_report()
    print("Pipeline complete. Execution report:", os.path.join(run_dir, "execution.json"))


if __name__ == "__main__":
    main()
