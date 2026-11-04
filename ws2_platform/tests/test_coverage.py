"""Coverage audit (I8). The worked example is the SNPP GPS outage of 2-6 Nov 2024 (spec section 3)."""
import datetime as dt

import pandas as pd
import pytest

from ws2_platform import coverage as cov

EXT = {"PB": (73.5, 78.0), "BD": (88.0, 92.7)}
D = dt.date


def _reg(*events):
    base = {"source": "test", "source_url": "https://example.org", "products": "unspecified",
            "verification": "transcribed", "note": ""}
    rows = [{**base, **e} for e in events]
    for r in rows:
        r["start"], r["end"] = pd.Timestamp(r.pop("start_utc")).tz_convert(None), pd.Timestamp(r.pop("end_utc")).tz_convert(None)
    return pd.DataFrame(rows)


GPS = {"id": "gps", "sat": "SNPP", "start_utc": "2024-11-02T22:12:00Z", "end_utc": "2024-11-06T17:36:00Z"}


def test_registry_file_is_valid_and_keeps_the_nov_2024_event():
    reg = cov.load_registry()
    assert reg["id"].is_unique
    ev = reg.set_index("id").loc["snpp-2024-11-02-gps"]
    assert ev["start"] == pd.Timestamp("2024-11-02 22:12") and ev["end"] == pd.Timestamp("2024-11-06 17:36")
    assert set(reg["verification"]) <= set(cov.VERIFICATION)


@pytest.mark.parametrize("bad, msg", [
    ({"end_utc": "2024-11-01T00:00:00Z"}, "after start"),
    ({"sat": "Landsat"}, "unknown sat"),
    ({"start_utc": "2024-11-02T22:12:00"}, "UTC"),
    ({"source_url": ""}, "source_url"),
])
def test_registry_rejects_bad_entries(tmp_path, bad, msg):
    e = {"id": "x", "sat": "SNPP", "start_utc": "2024-11-02T22:12:00Z", "end_utc": "2024-11-06T17:36:00Z",
         "source": "s", "source_url": "https://example.org", "products": "p", "verification": "transcribed", **bad}
    import yaml
    p = tmp_path / "r.yaml"
    p.write_text(yaml.safe_dump({"events": [e]}))
    with pytest.raises(ValueError, match=msg):
        cov.load_registry(str(p))


def test_gps_outage_maps_to_local_days_and_passes():
    days = cov.day_table(cov.affected_passes(_reg(GPS), EXT)).set_index(["region", "date"])
    for r in ("PB", "BD"):
        got = sorted(d for reg, d in days.index if reg == r)
        # Starts late on 2 Nov UTC: the local 2 Nov passes are already over. Ends 17:36 UTC on 6 Nov: the 7 Nov night
        # pass is later. So local 3-6 Nov, matching detections in the archive on 7-9 Nov.
        assert got == [D(2024, 11, 3), D(2024, 11, 4), D(2024, 11, 5), D(2024, 11, 6)]
        for d in got:
            assert days.loc[(r, d), "overlap_D"] == 1.0
        for d in (D(2024, 11, 4), D(2024, 11, 5)):
            assert days.loc[(r, d), "overlap_N"] == 1.0
    assert 0 < days.loc[("PB", D(2024, 11, 3)), "overlap_N"] < 0.5   # only the late-evening part and the edge
    # 6 Nov night: the early-morning segment is inside the outage, the late-evening one mostly after it ends.
    assert 0.5 < days.loc[("BD", D(2024, 11, 6)), "overlap_N"] < 1.0


def test_thresholds_change_what_is_excluded():
    days = cov.day_table(cov.affected_passes(_reg(GPS), EXT))
    assert cov.excluded(days, 0.0).all()                 # every listed day has some overlap
    assert cov.excluded(days, 1.0).all()                 # and every one has a fully covered day pass
    short = {"id": "short", "sat": "SNPP", "start_utc": "2024-03-01T08:00:00Z", "end_utc": "2024-03-01T08:06:00Z"}
    d2 = cov.day_table(cov.affected_passes(_reg(short), EXT))
    assert len(d2) and cov.excluded(d2, 0.0).all() and not cov.excluded(d2, 0.25).any()


def test_overlapping_events_are_merged_before_summing():
    a = {"id": "a", "sat": "SNPP", "start_utc": "2024-03-01T00:00:00Z", "end_utc": "2024-03-02T00:00:00Z"}
    b = {"id": "b", "sat": "SNPP", "start_utc": "2024-03-01T12:00:00Z", "end_utc": "2024-03-02T12:00:00Z"}
    m = cov.merge_events(_reg(a, b))
    assert len(m) == 1 and m.iloc[0]["id"] == "a+b" and m.iloc[0]["end"] == pd.Timestamp("2024-03-02 12:00")
    days = cov.day_table(cov.affected_passes(_reg(a, b), EXT))
    assert days[["overlap_D", "overlap_N"]].le(1.0).all().all()


def test_pass_window_measured_and_wraps_midnight():
    n = 60
    det = pd.DataFrame({"sat": "SNPP", "region": "PB", "lon": 75.0,
                        "daynight": ["N"] * (2 * n) + ["D"] * n,
                        # local = UTC + 5 h: 18:50 UTC -> 23:50 local, 20:10 UTC -> 01:10 local, 08:30 -> 13:30
                        "acq_time": [1850] * n + [2010] * n + [830] * n})
    w = cov.pass_windows(det).set_index(["sat", "region", "pass"])
    a, b = w.loc[("SNPP", "PB", "N"), ["start_h", "end_h"]]
    assert a > 23.5 and b < 1.5                      # crosses midnight
    a, b = w.loc[("SNPP", "PB", "D"), ["start_h", "end_h"]]
    assert a == pytest.approx(13.5) and b == pytest.approx(13.5)
    few = cov.pass_windows(det.head(5)).set_index("pass")
    assert (few["basis"] == "default").all()


def test_contradiction_when_a_fully_covered_pass_has_detections():
    days = cov.day_table(cov.affected_passes(_reg(GPS), EXT))
    counts = pd.DataFrame({"sat": ["SNPP", "SNPP"], "region": ["PB", "PB"], "date": [D(2024, 11, 4), D(2024, 11, 7)],
                           "pass": ["D", "D"], "n": [12, 40]})
    c = cov.contradictions(days, counts)
    assert list(c["date"]) == [D(2024, 11, 4)]       # 7 Nov is outside the outage, so its detections are fine


def test_candidate_gaps_need_an_operating_reference():
    days = [D(2024, 3, d) for d in (1, 2, 3)]
    sd = pd.DataFrame({"date": days * 2, "sat": ["SNPP"] * 3 + ["NOAA20"] * 3,
                       "operating": [True, True, True, True, True, False]})
    counts = pd.DataFrame({"region": "BD", "date": [D(2024, 3, 1), D(2024, 3, 2), D(2024, 3, 2), D(2024, 3, 3)],
                           "sat": ["NOAA20", "NOAA20", "SNPP", "NOAA20"], "n_day": [30, 30, 5, 30], "n_night": [0, 0, 0, 0]})
    g = cov.candidate_gaps(counts, sd, refs=("NOAA20",))
    # 1 Mar: SNPP zero, NOAA-20 30 -> candidate. 2 Mar: SNPP saw 5 -> not. 3 Mar: NOAA-20 not operating -> not.
    assert list(zip(g["date"], g["pass"])) == [(D(2024, 3, 1), "D")]


def test_would_flip_only_counts_days_marked_operating():
    days = cov.day_table(cov.affected_passes(_reg(GPS), EXT))
    sd = pd.DataFrame({"date": pd.date_range("2024-11-01", "2024-11-08").date, "sat": "SNPP", "operating": True})
    sd.loc[sd["date"] == D(2024, 11, 5), "operating"] = False
    f = cov.would_flip(days, sd, 0.0)
    assert list(f["date"]) == [D(2024, 11, 3), D(2024, 11, 4), D(2024, 11, 6)]
    assert set(f["regions"]) == {"BD;PB"}


def test_audit_end_to_end_writes_reports_and_leaves_inputs(tmp_path):
    from common.grid import cell_id
    proc, out = tmp_path / "processed", tmp_path / "audit"
    proc.mkdir()
    cid = int(cell_id(30.05, 75.05))
    pd.DataFrame({"cell_id": [cid], "lon_c": [75.05], "country": ["PB"]}).to_parquet(proc / "cells.parquet")
    det = pd.DataFrame({"sat": ["SNPP", "SNPP"], "acq_date": [D(2024, 11, 4), D(2024, 11, 8)], "acq_time": [830, 830],
                        "lat": [30.05, 30.05], "lon": [75.05, 75.05], "daynight": ["D", "D"]})
    det.to_parquet(proc / "detections.parquet")
    pd.DataFrame({"cell_id": [cid, cid], "date": [D(2024, 11, 4), D(2024, 11, 8)], "sat": ["SNPP", "SNPP"],
                  "n_day": [1, 1], "n_night": [0, 0]}).to_parquet(proc / "grid_daily.parquet")
    pd.DataFrame({"date": pd.date_range("2024-11-01", "2024-11-09").date, "sat": "SNPP", "operating": True,
                  "note": ""}).to_parquet(proc / "sensor_days.parquet")
    before = {p.name: p.stat().st_mtime_ns for p in proc.iterdir()}
    s = cov.audit(str(proc), cov.REGISTRY, str(out))
    assert s["contradictions"] == 1                      # the 4 Nov detection sits inside the GPS outage
    assert s["would_flip_sensor_days"]["0"] >= 4
    assert (out / "summary.md").exists() and (out / "affected_days.csv").exists()
    assert before == {p.name: p.stat().st_mtime_ns for p in proc.iterdir()}
