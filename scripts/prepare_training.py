"""Read-only readiness check for real-data training. Never prints credentials."""
from __future__ import annotations

import importlib
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    failures = []

    def check(label, ok, hint=""):
        print(f"{'PASS' if ok else 'FAIL'} {label}" + (f" — {hint}" if not ok else ""))
        if not ok:
            failures.append(label)

    check("Python 3.11", sys.version_info[:2] == (3, 11), "Run the setup launcher with Python 3.11 installed.")
    for module in ("numpy", "pandas", "pyarrow", "lightgbm", "shapely", "pyhdf", "fastapi", "duckdb", "scipy", "statsmodels"):
        try:
            importlib.import_module(module)
            check(module, True)
        except ImportError:
            check(module, False, "Run setup.")
    firms = [p for p in (ROOT / "data/raw/firms").glob("*.csv*") if "synthetic_" not in p.name]
    check(f"Real FIRMS inputs ({len(firms)} files)", bool(firms), "See docs/TRAINING.md for downloads and folder names.")
    for name in ("BGD_ADM1.geojson", "IND_ADM1.geojson"):
        check(name, (ROOT / "data/raw/boundaries" / name).is_file(), "Save the ADM1 GeoJSON in data/raw/boundaries/.")
    check("MCD12C1 land cover", any((ROOT / "data/raw/landcover").glob("MCD12C1*.hdf")), "Save the original HDF in data/raw/landcover/.")
    for region in ("BD", "PB"):
        path = ROOT / f"data/interim/monazir/weather_{region}.parquet"
        check(f"Weather cache {region}", path.is_file() and path.stat().st_size > 0,
              "Run python -m ws3_anomaly.loaders.weather --start 2000-11-01 --end 2026-11-03")
    check("Free disk >= 5 GiB", shutil.disk_usage(ROOT).free >= 5 * 1024**3, "Free space for intermediate outputs.")
    print("INFO CPU training; a GPU and FIRMS_MAP_KEY are not required for local archive training.")
    print("INFO Presence/import checks only; smoke QA validates processed data. Keep inputs unchanged during a run.")
    print(f"{'READY' if not failures else 'NOT READY'}: {len(failures)} blocking check(s).")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
