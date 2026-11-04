"""Truth checks against NASA FIRMS itself (plan card T31).

Compares our detection counts with what the FIRMS area API returns for the same box and dates:
  a) SNPP, 15 Sep - 1 Nov 2026 (this season so far)
  b) SNPP and NOAA-20 by day, 2-8 Nov 2024 (the SNPP outage: SNPP should be near 0 on 3-6 Nov, NOAA-20 not)
  c) SNPP season totals, 15 Sep - 31 Dec of 2016 and of 2024, also against the season-profile fixture

Run (needs FIRMS_MAP_KEY in the environment or .env, and network):
    python -m ws6_validation.truth_checks
The key is never printed: every API error is re-raised with the key replaced by ***.
Differences are expected: we count local solar days in our own 0.1 degree cells; FIRMS counts every detection in the box
by UTC date.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Callable

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PB_BOX = (74.6, 29.8, 76.4, 31.2)          # west, south, east, north: the Punjab demo box
REPORT = ROOT / "ws6_validation" / "truth_checks.md"
SAT_SOURCES = {"SNPP": "VIIRS_SNPP_SP", "NOAA20": "VIIRS_NOAA20_SP"}

Fetch = Callable[[dt.date, int], pd.DataFrame]   # (first_day, n_days) -> FIRMS rows


def read_key() -> str:
    key = os.environ.get("FIRMS_MAP_KEY", "").strip()
    env = ROOT / ".env"
    if not key and env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("FIRMS_MAP_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        raise RuntimeError("Set FIRMS_MAP_KEY in the environment or .env.")
    return key


def _masked(key: str, error: Exception) -> RuntimeError:
    return RuntimeError(str(error).replace(key, "***") if key else str(error))


def api_fetch(key: str, source: str, bbox) -> Fetch:
    """A fetch function over the FIRMS area API; errors never carry the key."""
    import requests
    from ws3_anomaly.ingest import firms
    session = requests.Session()

    def fetch(first: dt.date, n_days: int) -> pd.DataFrame:
        try:
            return firms.fetch_window(session, key, source, bbox, first, n_days)
        except Exception as e:  # noqa: BLE001 - re-raised without the key
            raise _masked(key, e) from None
    return fetch


# The FIRMS area API accepts 1-5 days per call (it answers "Invalid day range. Expects [1..5]." otherwise).
MAX_DAYS = 5


def windows(start: dt.date, end: dt.date, size: int = MAX_DAYS):
    """(first_day, n_days) windows that cover [start, end] exactly, at most `size` days each."""
    d = start
    while d <= end:
        n = min(size, (end - d).days + 1)
        yield d, n
        d += dt.timedelta(days=n)


def firms_rows(fetch: Fetch, start: dt.date, end: dt.date, key: str = "") -> pd.DataFrame:
    frames = []
    for first, n in windows(start, end):
        try:
            frames.append(fetch(first, n))
        except Exception as e:  # noqa: BLE001
            raise _masked(key, e) from None
    frames = [f for f in frames if len(f)]
    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["acq_date"])
    if "acq_date" in df:
        d = pd.to_datetime(df["acq_date"]).dt.date
        df = df[(d >= start) & (d <= end)]
    return df


def firms_count(key: str, source: str, bbox, start: dt.date, end: dt.date, fetch: Fetch | None = None) -> int:
    """Detections FIRMS returns for the box and UTC dates [start, end]."""
    return int(len(firms_rows(fetch or api_fetch(key, source, bbox), start, end, key)))


def area_cells(bbox=PB_BOX, country: str = "PB") -> pd.Series:
    cells = pd.read_parquet(ROOT / "data/processed/cells.parquet", columns=["cell_id", "lat_c", "lon_c", "country"])
    w, s, e, n = bbox
    inside = (cells["country"] == country) & cells["lon_c"].between(w, e) & cells["lat_c"].between(s, n)
    return cells.loc[inside, "cell_id"]


def our_daily(cells: pd.Series, start: dt.date, end: dt.date, sat: str) -> pd.Series:
    """Our detections per local solar date, for one satellite, over the given cells."""
    g = pd.read_parquet(ROOT / "data/processed/grid_daily.parquet", columns=["cell_id", "date", "sat", "n_det"],
                        filters=[("sat", "==", sat)])
    g = g[g["cell_id"].isin(set(cells))]
    d = pd.to_datetime(g["date"]).dt.date
    g = g[(d >= start) & (d <= end)]
    return g.groupby(pd.to_datetime(g["date"]).dt.date)["n_det"].sum()


def our_count(cells: pd.Series, start: dt.date, end: dt.date, sat: str) -> int:
    return int(our_daily(cells, start, end, sat).sum())


SMALL = 10   # below this many detections on both sides, a percentage difference means nothing


def _diff(firms_v: float, ours: float) -> tuple[str, str]:
    if max(firms_v, ours) < SMALL:
        return ("n/a", "both 0" if not (firms_v or ours) else f"small counts (<{SMALL})")
    if not firms_v:
        return ("n/a", "FIRMS returned 0" if ours else "both 0")
    rel = (ours - firms_v) / firms_v
    verdict = "close" if abs(rel) <= 0.10 else ("within 2x" if 0.5 <= ours / firms_v <= 2 else "LARGE GAP")
    return f"{rel:+.1%}", verdict


def write_report(rows: list[dict], notes: list[str], path: Path = REPORT, read_on: str | None = None) -> Path:
    lines = ["# Truth checks against NASA FIRMS (card T31)", "",
             f"Run on {read_on or dt.date.today().isoformat()} with `python -m ws6_validation.truth_checks`. "
             f"Box: Punjab demo box lon {PB_BOX[0]}-{PB_BOX[2]}, lat {PB_BOX[1]}-{PB_BOX[3]}.",
             "FIRMS counts every detection in the box by UTC date; ours counts our Punjab cells by local solar date.", "",
             "| Check | Satellite | Period | FIRMS | Ours | Difference | Verdict |", "|---|---|---|---:|---:|---:|---|"]
    for r in rows:
        diff, verdict = _diff(r["firms"], r["ours"])
        lines.append(f"| {r['check']} | {r['sat']} | {r['period']} | {r['firms']:,} | {r['ours']:,} | {diff} | {verdict} |")
    lines += ["", "## Notes", ""] + [f"- {n}" for n in notes]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run(key: str, fetch_for: Callable[[str], Fetch] | None = None) -> tuple[list[dict], list[str]]:
    fetch_for = fetch_for or (lambda source: api_fetch(key, source, PB_BOX))
    cells = area_cells()
    rows, notes = [], []

    # a) this season so far. Archive (SP) data lags by months, so 2026 uses SNPP near-real-time, which ran to 2 Nov.
    a0, a1 = dt.date(2026, 9, 15), dt.date(2026, 11, 1)
    rows.append({"check": "a", "sat": "SNPP (NRT)", "period": "15 Sep-1 Nov 2026",
                 "firms": firms_count(key, "VIIRS_SNPP_NRT", PB_BOX, a0, a1, fetch_for("VIIRS_SNPP_NRT")),
                 "ours": our_count(cells, a0, a1, "SNPP")})

    # b) the Nov 2024 SNPP outage, day by day
    b0, b1 = dt.date(2024, 11, 2), dt.date(2024, 11, 8)
    for sat, source in SAT_SOURCES.items():
        df = firms_rows(fetch_for(source), b0, b1, key)
        by_day = pd.to_datetime(df["acq_date"]).dt.date.value_counts() if len(df) else pd.Series(dtype=int)
        ours = our_daily(cells, b0, b1, sat)
        for i in range((b1 - b0).days + 1):
            day = b0 + dt.timedelta(days=i)
            rows.append({"check": "b", "sat": sat, "period": day.isoformat(),
                         "firms": int(by_day.get(day, 0)), "ours": int(ours.get(day, 0))})

    # c) whole-season SNPP totals, also against the season-profile fixture
    fixture = json.loads((ROOT / "contracts/fixtures/punjab_season_profile.json").read_text(encoding="utf-8"))
    years = {y["season_year"]: y for y in fixture["seasons"][1]["years"]}
    for year in (2016, 2024):
        c0, c1 = dt.date(year, 9, 15), dt.date(year, 12, 31)
        f = firms_count(key, "VIIRS_SNPP_SP", PB_BOX, c0, c1, fetch_for("VIIRS_SNPP_SP"))
        rows.append({"check": "c", "sat": "SNPP", "period": f"15 Sep-31 Dec {year}", "firms": f,
                     "ours": our_count(cells, c0, c1, "SNPP")})
        if year in years:
            notes.append(f"Season-profile fixture, {year} paddy season total (SNPP-equivalent, its own window): "
                         f"{years[year]['total']:,.1f}; FIRMS box count 15 Sep-31 Dec: {f:,}.")
    return rows, notes


def main() -> None:
    key = read_key()
    rows, notes = run(key)
    notes.append("Single-day differences of a few detections around the outage are expected: a night pass (about 01:30 "
                 "local time) is the previous UTC date in FIRMS but the next local solar date in our grid.")
    for r in rows:
        if max(r["firms"], r["ours"]) >= SMALL and r["firms"] and abs(r["ours"] - r["firms"]) / r["firms"] > 0.10:
            notes.append(f"Check {r['check']} {r['sat']} {r['period']}: difference over 10%; explain before quoting.")
    path = write_report(rows, notes)
    print(f"Wrote {path.relative_to(ROOT)} ({len(rows)} rows).")


if __name__ == "__main__":
    main()
