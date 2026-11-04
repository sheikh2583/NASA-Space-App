"""Build concise machine- and human-readable summaries from validation outputs."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "data" / "processed" / "validation"


def load(name: str) -> dict:
    path = VALIDATION / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def build_summary() -> dict:
    harmonization = load("harmonization.json")
    intervals = load("intervals.json")
    drift = load("drift.json")
    outlook = load("outlook_skill.json")
    qa = load("qa.json")
    checks = qa.get("metrics", {}).get("checks", [])
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data_mode": "real" if any((ROOT / "data" / "raw" / "firms").glob("FIRMS_*.csv*")) else "synthetic",
        "model": harmonization.get("metrics", {}).get("method_chosen", {}),
        "intervals": intervals.get("metrics", {}),
        "drift": drift.get("metrics", {}),
        "outlook": outlook.get("metrics", {}),
        "qa": {
            "passed": sum(c.get("passed", 1) for c in checks if c.get("result") == "pass"),
            "failed": sum(c.get("failed", 1) for c in checks if c.get("result") == "fail"),
            "checks": checks,
        },
    }


def markdown(summary: dict) -> str:
    qa = summary["qa"]
    model = summary.get("model") or {}
    lines = [
        "# Latest pipeline results",
        "",
        f"Generated: `{summary['generated_at']}`  ",
        f"Data mode: **{summary['data_mode']}**  ",
        f"QA: **{qa['passed']} passed, {qa['failed']} failed**",
        "",
        "## Selected model",
        "",
        f"- Method: `{model.get('method', 'not available')}`",
        f"- Training backend: `{model.get('compute_backend', 'not recorded')}`",
        f"- Learned candidate: `{model.get('learned_candidate', 'not recorded')}`",
        f"- Mean held-out CCC: `{json.dumps(model.get('mean_ccc', {}), sort_keys=True)}`",
        f"- Selection CCC (both input combinations when available): `{json.dumps(model.get('selection_mean_ccc', model.get('mean_ccc', {})), sort_keys=True)}`",
        "",
        "## Checks",
        "",
        "| Check | Result | Detail |",
        "|---|---|---|",
    ]
    for check in qa["checks"]:
        detail = str(check.get("detail", "")).replace("|", "\\|")
        lines.append(f"| {check.get('check', '')} | {check.get('result', '')} | {detail} |")
    lines.extend(["", "Full validation artifacts are in `data/processed/validation/`.", ""])
    return "\n".join(lines)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(ROOT / "results"))
    args = parser.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    summary = build_summary()
    (out / "latest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "latest.md").write_text(markdown(summary), encoding="utf-8")
    print(f"Results: {out / 'latest.md'}")


if __name__ == "__main__":
    main()
