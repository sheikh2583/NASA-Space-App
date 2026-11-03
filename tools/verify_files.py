"""Check any file in data/processed/ against the contracts; print PASS or the first failing rows.

Parquet: columns and types (contracts/parquet_schemas.json), allowed values (_enums), unique keys (_keys).
JSON: the matching JSON Schema in contracts/json_schemas/.

Usage: python tools/verify_files.py data/processed/*.parquet data/processed/*.json data/processed/validation/*.json
Exit code 1 if any file fails.
"""
from __future__ import annotations

import json
import os
import sys

import jsonschema
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = os.path.join(os.path.dirname(__file__), "..")
CONTRACT = json.load(open(os.path.join(ROOT, "contracts", "parquet_schemas.json")))
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
    schema = json.load(open(os.path.join(ROOT, "contracts", "json_schemas", f"{name}.schema.json")))
    errors = sorted(jsonschema.Draft7Validator(schema).iter_errors(json.load(open(path))), key=lambda e: list(e.path))
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


def main(paths) -> int:
    failed = 0
    for p in paths:
        errs = check(p)
        print(("PASS " if not errs else "FAIL ") + p)
        for e in errs:
            print("   - " + e)
        failed += bool(errs)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
