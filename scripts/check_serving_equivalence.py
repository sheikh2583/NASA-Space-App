"""Read-only serving comparison, without fitting. Write diagnostic JSON outside the checkout.

python scripts/check_serving_equivalence.py --output-dir X:/temp/firesense-serving/baseline
python scripts/check_serving_equivalence.py --baseline X:/temp/firesense-serving/baseline --output-dir X:/temp/firesense-serving/review
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def areas(catalog):
    result = [(area["id"], area["request"]) for area in catalog["areas"]]
    result.extend([
        ("bd", {"bbox": [89.5, 23, 90.5, 24]}),
        ("pb", {"geometry": {"type": "Polygon", "coordinates": [
            [[74.6, 29.8], [76.4, 29.8], [76.4, 31.2], [74.6, 31.2], [74.6, 29.8]]
        ]}}),
        ("tiny", {"bbox": [90.35, 23.75, 90.45, 23.85]}),
        ("empty", {"bbox": [88, 21, 88.2, 21.2]}),
    ])
    return result


def capture(data_dir, output, baseline=None):
    required = ["cells.parquet", "harmonized.parquet", "sensor_days.parquet", "interval_table.json"]
    if not all((data_dir / name).is_file() for name in required):
        print("SKIP: existing processed serving artifacts are absent; no outputs generated.")
        return 0
    output = output.resolve()
    if output.is_relative_to(ROOT):
        raise ValueError("Write serving diagnostics outside the checkout")
    if output.exists() and any(output.iterdir()):
        raise ValueError("Refusing to overwrite existing diagnostics")
    catalog_path = ROOT / "ws5_frontend/public/demo/areas.json"
    inputs = {name: digest(data_dir / name) for name in required}
    for name in ("drivers_region.json", "outlook_region.json"):
        if (data_dir / name).is_file():
            inputs[name] = digest(data_dir / name)
    inputs["catalog"] = digest(catalog_path)
    previous = json.loads((baseline / "manifest.json").read_text(encoding="utf-8")) if baseline else None
    if previous and previous["inputs"] != inputs:
        raise ValueError("Saved inputs differ from the baseline; comparison refused")
    from ws2_platform.api import app as api
    from ws2_platform.api.query import Store

    started = time.perf_counter()
    api._store = Store(str(data_dir))
    init_seconds = time.perf_counter() - started
    api._cache.clear()
    output.mkdir(parents=True, exist_ok=True)
    records = {}
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    end = api._store.data_end.date().isoformat()
    started = time.perf_counter()
    for area_id, geometry in areas(catalog):
        full = {**geometry, "start": "2000-11-01", "end": end, "res": "week"}
        cases = [(f"summary-{res}", api.build_summary, {**full, "res": res}) for res in ("week", "month", "day")]
        cases += [
            ("partial-month", api.build_summary, {**full, "start": "2021-03-15", "end": "2021-06-10", "res": "month"}),
            ("cutoff-week", api.build_summary, {**full, "start": "2026-10-01", "end": "2026-11-30"}),
            ("seam-week", api.build_summary, {**full, "start": "2011-12-20", "end": "2012-02-20"}),
            ("periods", api.aoi_periods, full), ("outlook", api.aoi_outlook, full),
            ("season", api.aoi_season, full), ("drivers", api.aoi_drivers, full),
            ("cells", api.aoi_cells, {**full, "start": "2026-09-14", "end": "2026-11-02"}),
        ]
        for case, fn, body in cases:
            t0 = time.perf_counter()
            result = fn(api.AOIRequest(**body))
            seconds = time.perf_counter() - t0
            encoded = json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
            name = f"{area_id}-{case}.json"
            if Path(name).name != name:
                raise ValueError("Unsafe area identifier in catalog")
            (output / name).write_bytes(encoded)
            records[name] = {"sha256": hashlib.sha256(encoded).hexdigest(), "seconds": seconds, "bytes": len(encoded)}
        api._cache.clear()
        print(f"Captured {area_id}: {len(cases)} responses", flush=True)
    mismatches = []
    if previous:
        names = set(records) | set(previous["responses"])
        mismatches = sorted(name for name in names if records.get(name, {}).get("sha256") != previous["responses"].get(name, {}).get("sha256"))
    manifest = {"inputs": inputs, "responses": records, "mismatches": mismatches,
                "local_seconds": time.perf_counter() - started, "store_init_seconds": init_seconds,
                "harmonized_dataframe_bytes": int(api._store.harmonized.memory_usage(deep=True).sum())}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if {name: digest(data_dir / name) for name in required} != {name: inputs[name] for name in required}:
        raise RuntimeError("Processed inputs changed during comparison")
    print(f"LOCAL comparison: {len(records)} responses, {len(mismatches)} mismatches; {manifest['local_seconds']:.3f}s; init {init_seconds:.3f}s", flush=True)
    if mismatches:
        print("DIFFERENT: " + ", ".join(mismatches))
    return 1 if mismatches else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data/processed")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()
    return capture(args.data_dir, args.output_dir, args.baseline)


if __name__ == "__main__":
    raise SystemExit(main())
