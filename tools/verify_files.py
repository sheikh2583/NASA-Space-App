"""Check any file in data/processed/ against the contracts; print PASS or the first failing rows.

Parquet: columns and types (contracts/parquet_schemas.json), allowed values (_enums), unique keys (_keys).
JSON: the matching JSON Schema in contracts/json_schemas/.

Usage: python tools/verify_files.py data/processed/*.parquet data/processed/*.json data/processed/validation/*.json
       python tools/verify_files.py --all     # every contracted file in data/processed (works in PowerShell too)
Exit code 1 if any file fails.
"""
from __future__ import annotations

import glob
import json
import os
import sys

import jsonschema
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = os.path.join(os.path.dirname(__file__), "..")
CONTRACT = json.load(open(os.path.join(ROOT, "contracts", "parquet_schemas.json"), encoding="utf-8"))
PA_TYPES = {"string": pa.string(), "int32": pa.int32(), "float32": pa.float32(), "float64": pa.float64(),
            "date32": pa.date32(), "bool": pa.bool_()}
JSON_SCHEMA_FOR = {"interval_table.json": "interval_table", "drivers_region.json": "drivers_region",
                   "outlook_region.json": "outlook_region"}


def arrow_schema(name: str) -> pa.Schema:
    return pa.schema([(c, PA_TYPES[t]) for c, t in CONTRACT[name].items()])


def write_parquet_contract(df: pd.DataFrame, path: str, name: str):
    """Write df with exactly the contract's columns and types (temp file, then rename)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    pq.write_table(pa.Table.from_pandas(df[list(CONTRACT[name])], schema=arrow_schema(name), preserve_index=False), path + ".tmp")
    os.replace(path + ".tmp", path)


def check_parquet(path: str, name: str) -> list[str]:
    errs = []
    schema = pq.read_schema(path)
    want = CONTRACT[name]
    got = {f.name: f.type for f in schema}
    for c, t in want.items():
        if c not in got:
            errs.append(f"missing column {c}")
        elif got[c] != PA_TYPES[t]:
            errs.append(f"column {c}: type {got[c]} != {t}")
    extra = set(got) - set(want)
    if extra:
        errs.append(f"columns not in the contract: {sorted(extra)}")
    if errs:
        return errs
    df = pd.read_parquet(path)
    for key, allowed in CONTRACT.get("_enums", {}).items():
        table, col = key.split(".")
        if table == name and col in df:
            bad = df.loc[~df[col].isin(allowed) & df[col].notna(), col]
            if len(bad):
                errs.append(f"{col}: values outside {allowed}, e.g. rows {bad.index[:20].tolist()} -> {bad.unique()[:5].tolist()}")
    keys = CONTRACT.get("_keys", {}).get(name)
    if keys:
        dup = df.duplicated(keys, keep=False)
        if dup.any():
            errs.append(f"duplicate keys {keys}: first rows {df.index[dup][:20].tolist()}")
    if name == "harmonized":
        bad = df[(df["lo_count"] > df["value_count"] + 1e-4) | (df["value_count"] > df["hi_count"] + 1e-4) | (df["value_count"] < 0)]
        if len(bad):
            errs.append(f"lo <= value <= hi or value >= 0 fails: rows {bad.index[:20].tolist()}")
    return errs


def check_json(path: str) -> list[str]:
    base = os.path.basename(path)
    name = "validation_piece" if os.path.basename(os.path.dirname(path)) == "validation" else JSON_SCHEMA_FOR.get(base)
    if name is None:
        return [f"no JSON Schema known for {base}"]
    schema = json.load(open(os.path.join(ROOT, "contracts", "json_schemas", f"{name}.schema.json"), encoding="utf-8"))
    errors = sorted(jsonschema.Draft7Validator(schema).iter_errors(json.load(open(path, encoding="utf-8"))), key=lambda e: list(e.path))
    return [f"{'/'.join(map(str, e.path)) or '(root)'}: {e.message}" for e in errors[:20]]


def check(path: str) -> list[str]:
    if path.endswith(".parquet"):
        name = os.path.basename(path)[: -len(".parquet")]
        if name not in CONTRACT:
            return [f"no contract for {name}"]
        return check_parquet(path, name)
    if path.endswith(".json"):
        return check_json(path)
    return ["unknown file type"]


def contracted_files(root: str = ROOT) -> tuple[list[str], list[str]]:
    """(files with a contract, other files) under data/processed and data/processed/validation."""
    d = os.path.join(root, "data", "processed")
    found = sorted(glob.glob(os.path.join(d, "*.parquet")) + glob.glob(os.path.join(d, "*.json"))
                   + glob.glob(os.path.join(d, "validation", "*.json")))
    known, other = [], []
    for p in found:
        base = os.path.basename(p)
        if p.endswith(".parquet"):
            ok = base[: -len(".parquet")] in CONTRACT
        else:
            ok = os.path.basename(os.path.dirname(p)) == "validation" or base in JSON_SCHEMA_FOR
        (known if ok else other).append(p)
    return known, other


def check_snapshot_seasons(root: str = ROOT) -> int:
    """Each areas.<key>.season in the legacy snapshot against json_schemas/season_profile.schema.json (card T07)."""
    path = os.path.join(root, "ws5_frontend", "public", "demo", "snapshot.json")
    if not os.path.exists(path):
        return 0
    snap = json.load(open(path, encoding="utf-8"))
    schema = json.load(open(os.path.join(ROOT, "contracts", "json_schemas", "season_profile.schema.json"), encoding="utf-8"))
    failed = 0
    for key in ("bd", "pb"):
        season = snap.get("areas", {}).get(key, {}).get("season")
        if season is None:
            print(f"FAIL snapshot season {key}")
            print("   - missing (run scripts/export_hosted_demo.py)")
            failed += 1
            continue
        doc = {**season, "schema_version": season.get("profile_version", season.get("schema_version"))}
        doc = {k: v for k, v in doc.items() if k in schema.get("properties", doc)}
        errs = sorted(jsonschema.Draft7Validator(schema).iter_errors(doc), key=lambda e: list(e.path))
        print(("PASS " if not errs else "FAIL ") + f"snapshot season {key}")
        for e in errs[:5]:
            print(f"   - {list(e.path)}: {e.message}")
        failed += bool(errs)
    return failed


def main(paths) -> int:
    snapshot_failed = 0
    if paths == ["--all"]:
        paths, other = contracted_files()
        for p in other:
            print("SKIP " + p + "  (no contract for this file)")
        snapshot_failed = check_snapshot_seasons()
        if not paths:
            print("SKIP: no contracted files in data/processed on this machine")
            return 1 if snapshot_failed else 0
    failed = snapshot_failed
    for p in paths:
        errs = check(p)
        print(("PASS " if not errs else "FAIL ") + p)
        for e in errs:
            print("   - " + e)
        failed += bool(errs)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
