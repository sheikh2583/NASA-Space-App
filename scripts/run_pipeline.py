"""Run the whole pipeline in order (any OS). Real FIRMS inputs are required unless --allow-synthetic is explicit.

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
import hashlib
import platform
import uuid
from contextlib import contextmanager
from pathlib import Path

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PY = sys.executable

SCIENCE_MANIFEST = "FIRESENSE_SCIENCE_MANIFEST"
SCIENCE_TOKEN = "FIRESENSE_SCIENCE_TOKEN"
PROTECTED_OUTPUTS = (("data/processed", "processed"), ("data/interim/sheikh", "sheikh"))
GENERATED_SOURCE_OUTPUTS = ("contracts/fixtures/",)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_inventory(directory: Path) -> list[dict]:
    """Hash stable members without loading model files or executing any scientific code."""
    rows = []
    if not directory.exists():
        return rows
    if directory.is_symlink():
        raise RuntimeError("Scientific inventories require a physical input/output directory")
    for path in sorted(directory.rglob("*")):
        if path.is_symlink() or not path.resolve().is_relative_to(directory.resolve()):
            raise RuntimeError("Scientific input/output inventories do not follow external links")
        if not path.is_file():
            continue
        before = path.stat()
        digest = file_sha256(path)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise RuntimeError(f"File changed while being inventoried: {path.name}")
        rows.append({"path": path.relative_to(directory).as_posix(), "bytes": after.st_size, "sha256": digest})
    return rows


def save_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def preserve_outputs(root: Path, destination: Path) -> dict:
    """Create and verify a fresh backup before any probe, test or stage may replace outputs."""
    root, destination = root.resolve(), destination.resolve()
    if not destination.is_relative_to(root / "data/runs") or destination.exists():
        raise RuntimeError("Baseline backup must be a new directory under data/runs")
    before = {name: file_inventory(root / source) for source, name in PROTECTED_OUTPUTS}
    required = sum(row["bytes"] for rows in before.values() for row in rows)
    if shutil.disk_usage(root).free < required * 2 + 64 * 1024**2:
        raise RuntimeError("Insufficient free space to preserve scientific outputs")
    destination.mkdir(parents=True)
    for source, name in PROTECTED_OUTPUTS:
        if (root / source).exists():
            shutil.copytree(root / source, destination / name)
        if file_inventory(destination / name) != before[name] or file_inventory(root / source) != before[name]:
            raise RuntimeError("Baseline checksum verification failed; no scientific command may start")
    save_json(destination / "inventory.json", before)
    return before


def source_snapshot(root: Path, run_dir: Path) -> dict:
    """Capture executable source/patch identity, excluding credentials, data and dependencies."""
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True)
    commit = result.stdout.strip() if result.returncode == 0 else None
    excluded = {"data", "results", ".git", ".venv", "venv", "node_modules", "dist", "share", "codex", "__pycache__", ".pytest_cache"}
    suffixes = {".py", ".md", ".json", ".yaml", ".yml", ".toml", ".ini", ".ts", ".tsx", ".mjs", ".css", ".html", ".txt", ".lock", ".ps1", ".sh"}
    if commit:
        listing = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                                 cwd=root, capture_output=True, check=True).stdout
        paths = [root / os.fsdecode(p) for p in listing.split(b"\0") if p]
    else:
        paths = []
        for parent, dirs, names in os.walk(root):
            dirs[:] = [d for d in dirs if d not in excluded]
            paths.extend(Path(parent) / name for name in names)
    members = []
    for path in sorted(set(paths)):
        rel = path.relative_to(root)
        if any(part in excluded for part in rel.parts) or path.name.startswith(".env"):
            continue
        if not path.is_file() or path.is_symlink() or (path.suffix not in suffixes and path.name != "Dockerfile"):
            continue
        destination = run_dir / "source" / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        if file_sha256(path) != file_sha256(destination):
            raise RuntimeError("Source changed during scientific snapshot")
        members.append({"path": rel.as_posix(), "sha256": file_sha256(destination)})
    patch = b""
    if commit:
        patterns = ["*.py", "*.md", "*.json", "*.yml", "*.yaml", "*.ts", "*.tsx", "*.mjs", "*.toml", "*.ini", "*.css", "*.html", "*.txt", "*.lock", "*.ps1", "*.sh", "Dockerfile"]
        patch = subprocess.run(["git", "diff", "--binary", "HEAD", "--", *patterns, ":(exclude)data/**",
                                ":(exclude)results/**", ":(exclude)share/**", ":(exclude).env*"],
                               cwd=root, capture_output=True, check=True).stdout
    (run_dir / "source.patch").write_bytes(patch)
    return {"commit": commit, "kind": "git" if commit else "source-tree-without-git",
            "members": members, "patch_sha256": hashlib.sha256(patch).hexdigest()}


def inherited_science(root: Path) -> dict | None:
    """Only a child with the active owner's receipt/token may reuse its writer lock."""
    manifest = os.environ.get(SCIENCE_MANIFEST)
    if not manifest:
        return None
    path = Path(manifest).resolve()
    if not path.is_relative_to(root / "results/runs"):
        raise RuntimeError("Inherited scientific receipt is outside this checkout")
    receipt = json.loads(path.read_text(encoding="utf-8"))
    lock = json.loads((root / "results/.scientific-writer.lock").read_text(encoding="utf-8"))
    token = hashlib.sha256(os.environ.get(SCIENCE_TOKEN, "").encode()).hexdigest()
    if (receipt.get("status") != "running" or not receipt.get("baseline_verified") or
            lock.get("manifest") != str(path) or lock.get("token_sha256") != token):
        raise RuntimeError("Inherited scientific writer ownership is invalid")
    backup = Path(receipt.get("backup", "")).resolve()
    if not backup.is_relative_to(root / "data/runs") or not (backup / "inventory.json").is_file():
        raise RuntimeError("Inherited scientific baseline is missing or outside this checkout")
    return {"manifest": path, "receipt": receipt, "env": {
        SCIENCE_MANIFEST: str(path), SCIENCE_TOKEN: os.environ[SCIENCE_TOKEN],
        "FIRESENSE_COMPUTE_LOG": str(path.parent / "cuda-fits.jsonl"),
        "FIRESENSE_REQUIRE_REAL": "1" if receipt.get("require_real") else "0"}}


@contextmanager
def scientific_environment(environment: dict):
    before = {key: os.environ.get(key) for key in environment}
    os.environ.update(environment)
    try:
        yield
    finally:
        for key, value in before.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@contextmanager
def scientific_session(root: Path, label: str, spec: Path, commands: list, *, require_real=False, inherit=False,
                       allow_synthetic=False):
    """One writer, immutable provenance and verified backups; importing this module never fits."""
    root, spec = root.resolve(), spec.resolve()
    if not spec.is_relative_to(root) or not spec.is_file():
        raise RuntimeError("Scientific run specification must exist inside this checkout")
    if inherit:
        existing = inherited_science(root)
        if existing:
            if allow_synthetic and not existing["receipt"].get("allow_synthetic"):
                raise RuntimeError("Parent scientific run does not declare synthetic input generation")
            if require_real:
                if not any("synthetic_" not in p.name for p in (root / "data/raw/firms").glob("*.csv*")):
                    raise RuntimeError("Real FIRMS inputs required; refusing inherited synthetic fallback")
                existing["env"]["FIRESENSE_REQUIRE_REAL"] = "1"
            yield existing
            return
    spec_digest = file_sha256(spec)
    (root / "results").mkdir(exist_ok=True)
    lock_path = root / "results/.scientific-writer.lock"
    try:
        descriptor = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise RuntimeError("Scientific writer lock already exists; inspect its owner before recovery") from error
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    run_dir = root / "results/runs" / ("scientific-" + stamp)
    token = uuid.uuid4().hex
    manifest = run_dir / "scientific.json"
    receipt = {"run_id": run_dir.name, "label": label, "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
               "status": "preparing", "baseline_verified": False, "require_real": bool(require_real),
               "allow_synthetic": bool(allow_synthetic and not require_real),
               "spec": spec.relative_to(root).as_posix(), "spec_sha256": spec_digest,
               "commands": commands, "steps": [], "python": sys.version, "platform": platform.platform(),
               "configuration": {key: os.environ[key] for key in ("FIRESENSE_BACKEND", "FIRESENSE_GPU_ID", "FIRESENSE_THREADS") if key in os.environ}}
    lock = {"pid": os.getpid(), "manifest": str(manifest), "token_sha256": hashlib.sha256(token.encode()).hexdigest()}
    started = time.perf_counter()
    raw = None
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(lock, stream)
        run_dir.mkdir(parents=True)
        save_json(manifest, receipt)
        if require_real and not any("synthetic_" not in p.name for p in (root / "data/raw/firms").glob("*.csv*")):
            raise RuntimeError("Real FIRMS inputs required; refusing synthetic fallback")
        receipt["source"] = source_snapshot(root, run_dir)
        raw = file_inventory(root / "data/raw")
        save_json(run_dir / "raw-inputs.json", {"members": raw})
        backup = root / "data/runs" / run_dir.name / "baseline"
        receipt["baseline_members"] = preserve_outputs(root, backup)
        receipt.update(status="running", baseline_verified=True, backup=str(backup))
        save_json(manifest, receipt)
        context = {"manifest": manifest, "receipt": receipt, "env": {
            SCIENCE_MANIFEST: str(manifest), SCIENCE_TOKEN: token,
            "FIRESENSE_COMPUTE_LOG": str(run_dir / "cuda-fits.jsonl"),
            "PYTHONUNBUFFERED": "1",
            "FIRESENSE_REQUIRE_REAL": "1" if require_real else "0"}}
        yield context
        raw_after = file_inventory(root / "data/raw")
        def generated(row):
            return (receipt["allow_synthetic"] and row["path"].startswith("firms/synthetic_")
                    and row["path"].endswith((".csv", ".csv.gz")))
        if [row for row in raw_after if not generated(row)] != [row for row in raw if not generated(row)]:
            raise RuntimeError("Raw input mutation detected during scientific execution")
        receipt["generated_raw_inputs"] = {"before": [r for r in raw if generated(r)],
                                          "after": [r for r in raw_after if generated(r)]}
        for _, name in PROTECTED_OUTPUTS:
            if file_inventory(backup / name) != receipt["baseline_members"][name]:
                raise RuntimeError("Protected baseline changed during scientific execution")
        generated_before = {m["path"]: m["sha256"] for m in receipt["source"]["members"]
                            if m["path"].startswith(GENERATED_SOURCE_OUTPUTS) and m["path"].endswith(".json")}
        for member in receipt["source"]["members"]:
            source = root / member["path"]
            if member["path"] in generated_before:
                continue
            if not source.is_file() or file_sha256(source) != member["sha256"]:
                raise RuntimeError("Source changed during scientific execution")
        generated_after = {prefix + m["path"]: m["sha256"] for prefix in GENERATED_SOURCE_OUTPUTS
                           for m in file_inventory(root / prefix) if m["path"].endswith(".json")}
        receipt["generated_source_outputs"] = [
            {"path": name, "before_sha256": generated_before.get(name), "after_sha256": generated_after.get(name)}
            for name in sorted(generated_before.keys() | generated_after.keys())]
        receipt["raw_inputs_unchanged"] = raw_after == raw
        receipt["protected_raw_inputs_unchanged"] = True
        receipt["status"] = "passed"
    except BaseException as error:
        receipt.update(status="failed", error_type=type(error).__name__)
        raise
    finally:
        receipt["seconds"] = round(time.perf_counter() - started, 3)
        try:
            if raw is not None and receipt["status"] == "failed":
                try:
                    receipt["raw_inputs_unchanged"] = file_inventory(root / "data/raw") == raw
                except (OSError, RuntimeError):
                    receipt["raw_inputs_unchanged"] = None
            if run_dir.exists():
                save_json(manifest, receipt)
        finally:
            # Remove only this owner's lock; interrupted-process locks require explicit recovery.
            try:
                if json.loads(lock_path.read_text(encoding="utf-8")) == lock:
                    lock_path.unlink()
            except (OSError, ValueError):
                pass


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
    ap.add_argument("--allow-synthetic", action="store_true", help="Explicit synthetic development run, never real-data validation")
    a = ap.parse_args()
    root = Path(ROOT).resolve()
    real_present = any("synthetic_" not in p.name for p in (root / "data/raw/firms").glob("*.csv*"))
    require_real = real_present or not a.allow_synthetic or os.environ.get("FIRESENSE_REQUIRE_REAL") == "1"
    with scientific_session(root, "pipeline", root / "docs/guides/training.md", [sys.argv],
                            require_real=require_real, allow_synthetic=a.allow_synthetic and not require_real,
                            inherit=True) as context:
        with scientific_environment(context["env"]):
            _pipeline_run(a, context)


def _pipeline_run(a, context):
    os.environ.update(FIRESENSE_BACKEND=a.backend, FIRESENSE_GPU_ID=str(a.gpu_id), FIRESENSE_THREADS=str(a.threads))
    validate_resume_backend(a.start, a.backend)
    todo = selected_steps(a.quick, a.start)
    cuda_stages, cpu_stages = stage_placement(todo, a.backend)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    root = Path(ROOT).resolve()
    run_dir = root / "results/runs" / stamp
    run_dir.mkdir(parents=True)
    report = {"started_at": dt.datetime.now(dt.timezone.utc).isoformat(), "quick": a.quick,
              "start_stage": a.start, "hardware": None, "backup": None, "stages": [], "status": "preparing",
              "scientific_manifest": str(context["manifest"]), "cuda_stages": cuda_stages, "cpu_stages": cpu_stages}
    started = time.perf_counter()
    log = run_dir / "cuda-fits.jsonl"
    os.environ["FIRESENSE_COMPUTE_LOG"] = str(log)
    save_json(run_dir / "execution.json", report)
    try:
        backup = root / "data/runs" / stamp / "baseline"
        preserve_outputs(root, backup)
        report["backup"] = str(backup)
        print("Previous outputs backed up and verified:", backup, flush=True)
        real = any("synthetic_" not in os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "data/raw/firms/*.csv*")))
        if not real and os.environ.get("FIRESENSE_REQUIRE_REAL") == "1":
            raise RuntimeError("Real FIRMS inputs required; refusing synthetic fallback")
        # Baseline preservation, resume validation and the fit log now precede the fitting probe.
        sys.path.insert(0, ROOT)
        from common import compute
        compute.configure_cuda_training()
        report["hardware"] = compute.probe_cuda()
        report.update(status="running", data_mode="real" if real else "synthetic")
        save_json(run_dir / "execution.json", report)
        env = {**os.environ, "PYTHONPATH": ROOT, "PYTHONUNBUFFERED": "1"}
        if not real:
            env["ALLOW_SYNTHETIC_WEATHER"] = "1"
        print("Mode:", report["data_mode"], flush=True)
        print("Compute:", report["hardware"], "report:", run_dir, flush=True)
        for name, args in todo:
            if args is None:
                print(f"== {name}: skipped (real FIRMS files found)", flush=True)
                continue
            print(f"== {name}", flush=True)
            stage_started = time.perf_counter()
            result = subprocess.run([PY] + args, cwd=ROOT, env=env)
            report["stages"].append({"name": name, "seconds": round(time.perf_counter() - stage_started, 3),
                                     "exit_code": result.returncode})
            save_json(run_dir / "execution.json", report)
            if result.returncode:
                raise subprocess.CalledProcessError(result.returncode, [PY] + args)
            print(f"   done in {time.perf_counter() - stage_started:.0f}s", flush=True)
        report["status"] = "passed"
    except subprocess.CalledProcessError as error:
        failed_stage = report["stages"][-1]["name"] if report["stages"] else a.start
        resume = f"python scripts/run_pipeline.py --from {failed_stage} --backend {a.backend} --gpu-id {a.gpu_id} --threads {a.threads}"
        if a.quick:
            resume += " --quick"
        report.update(status="failed", error_type=type(error).__name__, exit_code=error.returncode,
                      resume_command=resume)
        print(f"Pipeline stage failed (exit {error.returncode}); resume after fixing the cause: {resume}", flush=True)
        raise SystemExit(error.returncode) from error
    except BaseException as error:
        report.update(status="failed", error_type=type(error).__name__)
        raise
    finally:
        report["seconds"] = round(time.perf_counter() - started, 3)
        if log.exists():
            events = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
            report["cuda_fit_count"] = len(events)
            report["cuda_fit_seconds"] = round(sum(event["seconds"] for event in events), 3)
            report["cuda_fits_by_purpose"] = {
                purpose: sum(event["purpose"] == purpose for event in events)
                for purpose in sorted({event["purpose"] for event in events})}
        save_json(run_dir / "execution.json", report)
    print("Pipeline complete. Execution report:", run_dir / "execution.json", flush=True)


if __name__ == "__main__":
    main()
