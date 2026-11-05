"""Check and complete common/outages.yaml against NASA's MODAPS Suomi NPP outage table (plan card T32).

    python -m tools.modaps_outages            # fetch the table, update common/outages.yaml, print the counts
    python -m tools.modaps_outages --dry-run  # print what would change

Table columns: Year-Day, Date, Start Time (UTC), End Time (UTC), Comments. Times in the table are used as given: its
End column already includes the granule length for "inclusive" outages (e.g. "17:30, inclusive" is listed as 17:36).
Multi-day rows ("2024-307 - 2024-311") start on the first day and end on the last; an end of 00:00:00 on a multi-day
row is the start of the last day, on a single-day row the end of that day. A single-day row whose end time is earlier
than its start runs past midnight. Standard library plus pandas only.
"""
from __future__ import annotations

import argparse
import datetime as dt
from html.parser import HTMLParser
from pathlib import Path
import re
import urllib.request

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
URL = "https://modaps.modaps.eosdis.nasa.gov/services/production/outages_suomi_npp.html"
REGISTRY = ROOT / "common" / "outages.yaml"
CACHE = ROOT / "data" / "raw" / "modaps_outages.html"
MATCH_MINUTES = 6


def fetch(url: str = URL) -> str:
    """The table page; falls back to a copy saved at data/raw/modaps_outages.html when the site can't be reached."""
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return r.read().decode("utf-8", "replace")
    except OSError:
        if CACHE.exists():
            return CACHE.read_text(encoding="utf-8")
        raise


class _Rows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self._row, self._cell = [], None, None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._row is not None and self._cell is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


_YDAY = re.compile(r"(\d{4})-(\d{3})")


def _day(yday: str) -> dt.date:
    y, d = map(int, _YDAY.fullmatch(yday).groups())
    return dt.date(y, 1, 1) + dt.timedelta(days=d - 1)


def _time(s: str) -> dt.time:
    return dt.time.fromisoformat(s.strip())


def parse(html: str) -> pd.DataFrame:
    """One row per table row: start_utc, end_utc (UTC Timestamps; end exclusive), comment."""
    p = _Rows()
    p.feed(html)
    out = []
    for cells in p.rows:
        if len(cells) < 5:
            continue
        ydays = _YDAY.findall(cells[0])
        if not ydays:
            continue                                              # header or malformed row
        first, last = _day("-".join(ydays[0])), _day("-".join(ydays[-1]))
        try:
            t0, t1 = _time(cells[2]), _time(cells[3])
        except ValueError:
            continue
        start = dt.datetime.combine(first, t0)
        end = dt.datetime.combine(last, t1)
        if first == last and end <= start:
            end += dt.timedelta(days=1)                           # 00:00:00 = end of day, or past midnight
        out.append({"start_utc": pd.Timestamp(start, tz="UTC"), "end_utc": pd.Timestamp(end, tz="UTC"),
                    "comment": cells[4], "year_day": cells[0]})
    return pd.DataFrame(out, columns=["start_utc", "end_utc", "comment", "year_day"])


def merged(table: pd.DataFrame, gap_minutes: float = MATCH_MINUTES) -> pd.DataFrame:
    """Rows that touch or overlap (within `gap_minutes`) joined into one interval, e.g. an outage the table splits at
    midnight into "2025-186" and "2025-187"."""
    out = []
    for _, r in table.sort_values("start_utc").iterrows():
        if out and r["start_utc"] <= out[-1]["end_utc"] + pd.Timedelta(minutes=gap_minutes):
            last = out[-1]
            last["end_utc"] = max(last["end_utc"], r["end_utc"])
            if r["comment"] not in last["comment"]:
                last["comment"] += " + " + r["comment"]
            last["year_day"] += " + " + r["year_day"]
        else:
            out.append(dict(r))
    return pd.DataFrame(out, columns=table.columns)


def _overlap(a0, a1, b0, b1) -> float:
    return max(0.0, (min(a1, b1) - max(a0, b0)).total_seconds())


def compare(registry: list[dict], table: pd.DataFrame) -> pd.DataFrame:
    """For each SNPP registry entry, the table row overlapping it most (at least 50% of the entry), with the start and
    end differences in minutes (table minus registry). No match: matched=False."""
    rows = []
    table = merged(table)
    for e in registry:
        if e.get("sat") != "SNPP":
            continue
        r0, r1 = pd.Timestamp(e["start_utc"]), pd.Timestamp(e["end_utc"])
        dur = (r1 - r0).total_seconds()
        best, best_ov = None, 0.0
        for _, t in table.iterrows():
            ov = _overlap(r0, r1, t["start_utc"], t["end_utc"])
            if ov > best_ov:
                best, best_ov = t, ov
        ok = best is not None and dur > 0 and best_ov / dur >= 0.5
        rows.append({"id": e["id"], "matched": ok,
                     "table_start": best["start_utc"] if ok else None, "table_end": best["end_utc"] if ok else None,
                     "table_comment": best["comment"] if ok else None,
                     "d_start_min": (best["start_utc"] - r0).total_seconds() / 60 if ok else None,
                     "d_end_min": (best["end_utc"] - r1).total_seconds() / 60 if ok else None})
    return pd.DataFrame(rows, columns=["id", "matched", "table_start", "table_end", "table_comment",
                                       "d_start_min", "d_end_min"])


def _word(comment: str) -> str:
    c = comment.lower()
    for key, word in (("gps", "gps"), ("safe", "safehold"), ("smd", "smd"), ("cdp", "cdp"), ("ssr", "ssr"),
                      ("dmu", "dmu"), ("lrm", "lrm"), ("maneuver", "maneuver"), ("anomal", "anomaly")):
        if key in c:
            return word
    return "outage"


def propose(table: pd.DataFrame, min_hours: float = 1.0, years=(2012, 2023)) -> list[dict]:
    """Registry entries for table rows of at least `min_hours` that start in the given years (inclusive)."""
    out = []
    for _, t in merged(table).iterrows():
        hours = (t["end_utc"] - t["start_utc"]).total_seconds() / 3600
        if hours < min_hours or not (years[0] <= t["start_utc"].year <= years[1]):
            continue
        out.append({"id": f"snpp-{t['start_utc']:%Y-%m-%d}-{_word(t['comment'])}", "sat": "SNPP",
                    "start_utc": f"{t['start_utc']:%Y-%m-%dT%H:%M:%SZ}", "end_utc": f"{t['end_utc']:%Y-%m-%dT%H:%M:%SZ}",
                    "source": f"MODAPS table {t['year_day']}", "source_url": URL, "products": "unspecified",
                    "verification": "table_and_data", "note": t["comment"]})
    return out


def _flow(e: dict) -> str:
    """One registry entry as a single flow-style YAML line, like the existing transcribed lines."""
    def q(v):
        return yaml.safe_dump(v, default_flow_style=True, width=10_000).strip().removesuffix("...").strip()
    keys = ["id", "sat", "start_utc", "end_utc", "source", "source_url", "products", "verification", "note"]
    return "  - {" + ", ".join(f"{k}: {q(e[k])}" for k in keys if k in e) + "}"


def update(registry_text: str, table: pd.DataFrame, today: str) -> tuple[str, dict]:
    """New registry text and the counts confirmed / corrected / rejected / added."""
    doc = yaml.safe_load(registry_text)
    events = doc["events"]
    cmp = compare([e for e in events if e.get("verification") == "transcribed"], table).set_index("id")
    counts = {"confirmed": 0, "corrected": 0, "rejected": 0, "added": 0}
    lines = registry_text.splitlines()
    for e in events:
        if e.get("verification") != "transcribed":
            continue
        c = cmp.loc[e["id"]]
        new = dict(e)
        if not c["matched"]:
            new["verification"] = "rejected"
            new["note"] = f"{e.get('note', '')}; no matching MODAPS table row on {today}".lstrip("; ")
            counts["rejected"] += 1
        elif abs(c["d_start_min"]) <= MATCH_MINUTES and abs(c["d_end_min"]) <= MATCH_MINUTES:
            new["verification"] = "table_and_data"
            new["note"] = f"{e.get('note', '')}; checked against MODAPS table {today}".lstrip("; ")
            counts["confirmed"] += 1
        else:
            new["start_utc"] = f"{c['table_start']:%Y-%m-%dT%H:%M:%SZ}"
            new["end_utc"] = f"{c['table_end']:%Y-%m-%dT%H:%M:%SZ}"
            new["verification"] = "table_and_data"
            new["note"] = (f"{e.get('note', '')}; corrected to the MODAPS table {today} "
                           f"(was {e['start_utc']} to {e['end_utc']})").lstrip("; ")
            counts["corrected"] += 1
        idx = next(i for i, ln in enumerate(lines) if f"id: {e['id']}," in ln)
        lines[idx] = _flow(new)
    existing = {e["id"] for e in events}
    covered = [(pd.Timestamp(e["start_utc"]), pd.Timestamp(e["end_utc"])) for e in events if e.get("sat") == "SNPP"]

    def uncovered(p):
        return not any(_overlap(pd.Timestamp(p["start_utc"]), pd.Timestamp(p["end_utc"]), a, b) > 0 for a, b in covered)

    historical = [p for p in propose(table) if uncovered(p)]
    recent = [p for p in propose(table, years=(2024, 2026)) if uncovered(p)]
    counts["added_2024_2026"] = len(recent)
    added = []
    for p in historical + recent:
        pid, n = p["id"], 2
        while p["id"] in existing:
            p["id"] = f"{pid}-{n}"
            n += 1
        existing.add(p["id"])
        added.append(_flow(p))
    counts["added"] = len(added) - len(recent)
    if added:
        lines += ["", f"  # ---- added from the MODAPS table on {today}: every outage of at least one hour in 2012-2023, "
                      "plus any 2024-2026 one missing above ----"] + added
    text = "\n".join(lines) + "\n"
    text = text.replace("  # ---- transcribed, not yet checked by a person ----",
                        f"  # ---- 2024-2026, checked against the MODAPS table on {today} ----")
    return text, counts


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    table = parse(fetch())
    print(f"MODAPS table rows parsed: {len(table)}")
    if len(table) < 100:
        raise SystemExit("Fewer than 100 rows parsed: the page layout changed. Stop and check it by hand.")
    text, counts = update(REGISTRY.read_text(encoding="utf-8"), table, dt.date.today().isoformat())
    print("counts:", counts)
    if not a.dry_run:
        REGISTRY.write_text(text, encoding="utf-8", newline="")
        print(f"Updated {REGISTRY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
