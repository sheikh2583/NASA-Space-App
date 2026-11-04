"""MODAPS outage-table parsing and registry comparison, offline (plan card T32)."""
import pandas as pd
import yaml

from tools import modaps_outages as mo

HTML = """<table>
<tr><th>Year-Day</th><th>Date</th><th>Start Time (UTC)</th><th>End Time (UTC)</th><th>Comments</th></tr>
<tr><td>2024-317</td><td>November 12, 2024</td><td>03:12:00</td><td>03:24:00</td><td>LRM outage 03:12 &amp; 03:18 granules</td></tr>
<tr><td>2024-307 - 2024-311</td><td>November 2, 2024 - November 6, 2024</td><td>22:12:00</td><td>17:36:00</td>
    <td>GPS Anomaly outage (11/2/24 22:12 - 11/6/24 17:30, inclusive)</td></tr>
<tr><td>2015-100</td><td>April 10, 2015</td><td>23:00:00</td><td>00:00:00</td><td>SMD outage to end of day</td></tr>
<tr><td>2016-200 - 2016-202</td><td>July 18, 2016 - July 20, 2016</td><td>06:00:00</td><td>00:00:00</td><td>Safe hold</td></tr>
</table>"""


def ts(s):
    return pd.Timestamp(s, tz="UTC")


def test_parse_reads_multi_day_and_short_rows():
    t = mo.parse(HTML)
    assert len(t) == 4
    gps = t[t["comment"].str.startswith("GPS")].iloc[0]
    assert gps["start_utc"] == ts("2024-11-02 22:12") and gps["end_utc"] == ts("2024-11-06 17:36")
    lrm = t[t["comment"].str.startswith("LRM")].iloc[0]
    assert lrm["end_utc"] - lrm["start_utc"] == pd.Timedelta(minutes=12)


def test_midnight_end_means_end_of_day_on_one_day_and_start_of_last_day_on_several():
    t = mo.parse(HTML).set_index("comment")
    assert t.loc["SMD outage to end of day", "end_utc"] == ts("2015-04-11 00:00")
    assert t.loc["Safe hold", "end_utc"] == ts("2016-07-20 00:00")


def test_compare_finds_the_gps_outage_and_flags_a_missing_one():
    reg = [{"id": "snpp-2024-11-02-gps", "sat": "SNPP", "start_utc": "2024-11-02T22:12:00Z", "end_utc": "2024-11-06T17:30:00Z"},
           {"id": "snpp-2020-01-01-none", "sat": "SNPP", "start_utc": "2020-01-01T00:00:00Z", "end_utc": "2020-01-02T00:00:00Z"},
           {"id": "terra-x", "sat": "Terra", "start_utc": "2024-11-02T22:12:00Z", "end_utc": "2024-11-06T17:30:00Z"}]
    c = mo.compare(reg, mo.parse(HTML)).set_index("id")
    assert list(c.index) == ["snpp-2024-11-02-gps", "snpp-2020-01-01-none"]          # Terra entries are not compared
    assert c.loc["snpp-2024-11-02-gps", "matched"] and c.loc["snpp-2024-11-02-gps", "d_end_min"] == 6
    assert not c.loc["snpp-2020-01-01-none", "matched"]


def test_propose_keeps_rows_of_at_least_an_hour_in_the_years_asked():
    ids = [p["id"] for p in mo.propose(mo.parse(HTML), min_hours=1.0, years=(2012, 2023))]
    assert ids == ["snpp-2015-04-10-smd", "snpp-2016-07-18-safehold"]                # 2024 rows and the 12-minute row out


def test_update_confirms_corrects_rejects_and_adds_valid_yaml():
    registry = """events:
  # ---- transcribed, not yet checked by a person ----
  - {id: a, sat: SNPP, start_utc: "2024-11-02T22:12:00Z", end_utc: "2024-11-06T17:36:00Z", source: s, source_url: u, products: unspecified, verification: transcribed, note: n}
  - {id: b, sat: SNPP, start_utc: "2024-11-02T20:00:00Z", end_utc: "2024-11-06T17:36:00Z", source: s, source_url: u, products: unspecified, verification: transcribed, note: n}
  - {id: c, sat: SNPP, start_utc: "2020-01-01T00:00:00Z", end_utc: "2020-01-02T00:00:00Z", source: s, source_url: u, products: unspecified, verification: transcribed, note: n}
"""
    text, counts = mo.update(registry, mo.parse(HTML), "2026-11-04")
    assert counts == {"confirmed": 1, "corrected": 1, "rejected": 1, "added": 2, "added_2024_2026": 0}
    ev = {e["id"]: e for e in yaml.safe_load(text)["events"]}
    assert ev["a"]["verification"] == "table_and_data" and "checked against MODAPS table 2026-11-04" in ev["a"]["note"]
    assert ev["b"]["start_utc"] == "2024-11-02T22:12:00Z" and "was 2024-11-02T20:00:00Z" in ev["b"]["note"]
    assert ev["c"]["verification"] == "rejected"
    assert "transcribed" not in [e["verification"] for e in ev.values()]


def test_rows_split_at_midnight_are_one_outage():
    html = """<table>
<tr><td>2025-187</td><td>July 6, 2025</td><td>00:00:00</td><td>02:00:00</td><td>L0 Data gap</td></tr>
<tr><td>2025-186</td><td>July 5, 2025</td><td>08:00:00</td><td>00:00:00</td><td>L0 Data gap</td></tr>
</table>"""
    reg = [{"id": "x", "sat": "SNPP", "start_utc": "2025-07-05T08:00:00Z", "end_utc": "2025-07-06T02:00:00Z"}]
    c = mo.compare(reg, mo.parse(html)).iloc[0]
    assert c["matched"] and c["d_start_min"] == 0 and c["d_end_min"] == 0
