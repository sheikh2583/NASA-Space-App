"""Samiul's QA run (prompt P6.5): runs the test suites, checks flag rates around the 2012 seam (decision 21) and
whether the planted synthetic anomalies are recovered, then writes data/processed/validation/qa.json.

Usage: python -m ws6_validation.qa [--api-base-url URL]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys

import pandas as pd

P = "data/processed"


def run_pytest(path, env_extra=None):
    env = {**os.environ, **(env_extra or {})}
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", path], capture_output=True, text=True, env=env)
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]
    m = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|skipped|error)", tail)}
    return {"check": path, "result": "pass" if r.returncode == 0 else "fail", "detail": tail, **m}


def flag_rates() -> dict:
    an = pd.read_parquet(f"{P}/anomalies_region_week.parquet")
    an["year"] = pd.to_datetime(an["week_start"]).dt.year
    by_year = an.groupby("year")["flag"].mean()
    before, after = by_year[by_year.index < 2012].mean(), by_year[(by_year.index >= 2012) & (by_year.index <= 2026)].mean()
    return {"flag_rate_by_year": {int(k): round(float(v), 4) for k, v in by_year.items()},
            "before_2012": round(float(before), 4), "after_2012": round(float(after), 4),
            "decision_21_ok": bool(before >= 0.5 * after)}


def planted() -> list[dict]:
    truth = "data/raw/synthetic/TRUTH.json"
    if not os.path.exists(truth):
        return []
    cp = pd.read_parquet(f"{P}/critical_periods.parquet")
    cp["start"] = pd.to_datetime(cp["start"])
    out = []
    for key, mult in json.load(open(truth))["planted"].items():
        code, year = key.split("-")
        year = int(year)
        months = (2, 5) if code == "BD" else (9, 12)
        sel = cp[cp["region_id"].str.startswith(code) & (cp["start"].dt.year == year) & cp["start"].dt.month.between(*months)]
        out.append({"planted": key, "multiplier": mult, "regions_with_a_period": int(sel["region_id"].nunique()),
                    "best_rank": int(sel["rank"].min()) if len(sel) else None,
                    "expected": "flagged" if mult > 1 else "not flagged (only high anomalies are flagged)"})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-base-url", default=None)
    a = ap.parse_args(argv)
    env = {"API_BASE_URL": a.api_base_url} if a.api_base_url else {}
    checks = [run_pytest(p, env) for p in ("ws6_validation/tests/test_data_qa.py", "ws6_validation/tests/test_contract.py",
                                            "ws6_validation/tests/test_e2e.py")]
    checks.append(run_pytest("common ws1_harmonize ws2_platform ws3_anomaly ws4_outlook".split()[0]))
    fr = flag_rates()
    real_data = any(name.startswith("FIRMS_") and (name.endswith(".csv") or ".csv." in name)
                    for name in os.listdir("data/raw/firms")) if os.path.isdir("data/raw/firms") else False
    pl = [] if real_data else planted()
    checks.append({"check": "flag rate before vs after 2012 (decision 21)", "result": "pass" if fr["decision_21_ok"] else "fail",
                   "detail": f"before {fr['before_2012']:.3f}, after {fr['after_2012']:.3f}"})
    n_pass = sum(c["result"] == "pass" for c in checks)
    hv = json.load(open(f"{P}/validation/harmonization.json"))["metrics"]["method_chosen"] if os.path.exists(f"{P}/validation/harmonization.json") else {}
    iv = json.load(open(f"{P}/validation/intervals.json"))["metrics"]["coverage"] if os.path.exists(f"{P}/validation/intervals.json") else []
    cov = {r["res"]: r["coverage"] for r in iv if r["landcover"] == "all"}
    summary = [
        f"What was checked: {len(checks)} groups of automated checks on the data files, every API endpoint against the contract, "
        f"and the demo path for Bangladesh and Punjab ({n_pass} of {len(checks)} passed).",
        f"How well it held up: the {'per-region ratio (B1)' if hv.get('method') == 'b1' else 'learned model'} was chosen by held-out agreement "
        f"(mean Lin's CCC {hv.get('mean_ccc', {})}); the 90% bands covered {cov.get('week', 'n/a')} of held-out weekly totals.",
        "Where it is weak: values before 2012 are modeled and whole unusually-strong seasons may be flagged only at their edges. "
        + ("This run uses downloaded FIRMS observations." if real_data else "This development run uses synthetic FIRMS-like observations."),
    ]
    limitations = [
        "Values before VIIRS began in 2012 are modeled from MODIS and include calibrated uncertainty.",
        "The manual FIRMS web-viewer comparison (QA_CHECKLIST) must be done by a person on real data.",
        "Bangla text has not yet been reviewed by a fluent reader.",
    ]
    if not real_data:
        limitations.insert(0, "Synthetic data: the checks prove the pipeline and contracts, not real-world accuracy.")
    piece = {"schema_version": "1.0", "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
             "producer": "qa", "metrics": {"summary": summary, "checks": checks, "seam_flag_rates": fr, "planted_anomalies": pl},
             "limitations": limitations}
    os.makedirs(f"{P}/validation", exist_ok=True)
    with open(f"{P}/validation/qa.json", "w") as f:
        json.dump(piece, f, indent=1)
    for c in checks:
        print(f"{c['result']:4}  {c['check']}: {c['detail']}")
    print("planted:", pl)
    print("\n".join(summary))
    if n_pass != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
