"""QA keeps scientific interval acceptance separate from passing engineering checks. Pure; runs no suites."""
import json
from pathlib import Path

from ws6_validation.qa import bands_sentence, interval_acceptance

SAVED = Path(__file__).resolve().parents[2] / "data/processed/validation/intervals_by_stratum.json"


def report(status, stop=()):
    rows = [{"res": "week", "sat_combo": c, "dimension": "activity", "value": "positive", "coverage": v, "n": 1100}
            for c, v in (("terra_aqua", 0.73), ("terra_only", 0.47))]
    return {"metrics": {"rows": rows, "stop_rows": list(stop), "acceptance_status": status}}


def test_stop_condition_is_headline_not_hidden_by_marginal_coverage():
    a = interval_acceptance(report("stop_condition", [{"stratum": "week | terra_only | activity:positive", "n": 1095, "coverage": 0.47}]))
    assert a["status"] == "stop_condition" and len(a["stop_rows"]) == 1
    text = bands_sentence(a)
    assert "SCIENTIFIC STOP CONDITION" in text and "not accepted" in text and "week|terra_only 0.47" in text


def test_missing_report_is_never_accepted():
    a = interval_acceptance(None)
    assert a["status"] == "missing" and "not accepted" in bands_sentence(a)


def test_reported_status_still_says_nominal():
    assert "nominal" in bands_sentence(interval_acceptance(report("reported")))


def test_saved_report_is_read_as_stop_condition_when_present():
    if not SAVED.exists():
        return
    a = interval_acceptance(json.loads(SAVED.read_text(encoding="utf-8")))
    assert a["status"] in {"stop_condition", "reported"}
    assert all(r["n"] >= 500 and r["coverage"] < 0.8 for r in a["stop_rows"])
