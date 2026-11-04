"""Truth-check plumbing without network: windowing, key masking, report writing (plan card T31)."""
import datetime as dt

import pandas as pd
import pytest

from ws6_validation import truth_checks as tc

KEY = "abcdef0123456789secret"


def test_windows_cover_the_range_exactly_in_steps_the_api_accepts():
    start, end = dt.date(2026, 9, 15), dt.date(2026, 11, 1)
    w = list(tc.windows(start, end))
    days = [first + dt.timedelta(days=i) for first, n in w for i in range(n)]
    assert days == [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]
    assert all(1 <= n <= tc.MAX_DAYS <= 5 for _, n in w)


def test_firms_count_sums_every_window_and_drops_days_outside_the_range():
    calls = []

    def fake(first, n):
        calls.append((first, n))
        # one detection per day, plus one before the range that must be dropped
        rows = [{"acq_date": (first + dt.timedelta(days=i)).isoformat()} for i in range(n)]
        rows.append({"acq_date": "2000-01-01"})
        return pd.DataFrame(rows)

    start, end = dt.date(2024, 11, 2), dt.date(2024, 11, 25)
    assert tc.firms_count(KEY, "VIIRS_SNPP_SP", tc.PB_BOX, start, end, fetch=fake) == 24
    assert sum(n for _, n in calls) == 24


def test_errors_never_carry_the_key():
    def failing(first, n):
        raise RuntimeError(f"HTTP 400 for https://firms.example/api/area/csv/{KEY}/VIIRS_SNPP_SP/...")

    with pytest.raises(RuntimeError) as e:
        tc.firms_count(KEY, "VIIRS_SNPP_SP", tc.PB_BOX, dt.date(2024, 1, 1), dt.date(2024, 1, 3), fetch=failing)
    assert KEY not in str(e.value) and KEY[:6] not in str(e.value) and "***" in str(e.value)


def test_report_has_every_row_and_verdict(tmp_path):
    rows = [{"check": "a", "sat": "SNPP", "period": "p", "firms": 1000, "ours": 950},
            {"check": "b", "sat": "SNPP", "period": "2024-11-04", "firms": 0, "ours": 0},
            {"check": "b", "sat": "SNPP", "period": "2024-11-06", "firms": 2, "ours": 0},
            {"check": "c", "sat": "SNPP", "period": "q", "firms": 100, "ours": 400}]
    path = tc.write_report(rows, ["a note"], tmp_path / "r.md", read_on="2026-11-04")
    text = path.read_text(encoding="utf-8")
    assert "| a | SNPP | p | 1,000 | 950 | -5.0% | close |" in text
    assert "both 0" in text and "small counts (<10)" in text and "LARGE GAP" in text and "- a note" in text
    assert KEY[:6] not in text
