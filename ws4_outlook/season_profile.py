"""Season profile (improvement I1): when burning usually happens in an area, and how this season compares.

Used by the API and the read-only summary CLI (spec: docs/specs/I1_SEASON_PROFILE.md).

Definitions (deliberately conservative):
- A *season window* is a fixed calendar search window per area (Punjab has two: wheat residue in spring and paddy
  residue in autumn). A week belongs to the season year whose window contains the week's midpoint.
- The *central activity window* of a season is the span between the days on which 10% and 90% of that season's
  detections had accumulated. It is a statistic of detections, NOT the physical start or end of burning.
- Timing is measured in days since the window start, so leap years do not shift it.
- A season is `complete` only if its window ended on or before `as_of`, at least 90% of its weeks have values and
  its total is not `low_activity`. Only complete seasons enter the typical profile and the trends.
- Nothing after `as_of` is used: weeks that end after `as_of` are dropped first.

Uncertainty, stated as what it is:
- `interval_sensitivity_days`: the largest shift of p10/p50/p90 when the non-observed weeks are set to their lower
  and then upper interval bound. A bounding scenario, not a calibrated interval (weekly bounds are not jointly
  calibrated).
- Trend confidence intervals are Theil-Sen intervals across seasons (interannual variability).

Timing trends and magnitude trends are reported separately: fewer detections is not a change in timing.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import theilslopes

SCHEMA_VERSION = "0.1.0-draft"
OBSERVED = "observed_viirs"
DEFINITION = ("Central activity window: from the day 10% to the day 90% of a season's satellite fire detections had "
              "accumulated. A detection statistic, not the physical start or end of burning.")


@dataclass(frozen=True)
class Season:
    name: str
    start: tuple[int, int]  # (month, day), inclusive
    end: tuple[int, int]    # (month, day), inclusive; earlier in the calendar than start = crosses 31 Dec

    def bounds(self, season_year: int) -> tuple[pd.Timestamp, pd.Timestamp]:
        end = pd.Timestamp(season_year, *self.end)
        start_year = season_year - 1 if self.start > self.end else season_year
        return pd.Timestamp(start_year, *self.start), end

    def md(self) -> dict:
        return {"start_md": f"{self.start[0]:02d}-{self.start[1]:02d}", "end_md": f"{self.end[0]:02d}-{self.end[1]:02d}"}


# Provisional windows chosen from the 2012-2026 observed monthly shares in the hosted snapshot (spec section 2):
# PB: Apr 1.9%, May 18.2%, Oct 23.9%, Nov 54.4% of detections; BD: Nov-Apr carry 96%.
SEASON_WINDOWS: dict[str, list[Season]] = {
    "pb": [Season("wheat_residue", (4, 1), (6, 30)), Season("paddy_residue", (9, 15), (12, 31))],
    "bd": [Season("dry_season", (11, 1), (5, 31))],
}

MIN_COVERAGE = 0.9
MIN_TOTAL = 30.0  # detections; below this, 10/50/90% crossing days are too noisy to report
MIN_TREND_SEASONS = 8
OBSERVED_ERA_MAX_MODELED = 0.5


# ---------------------------------------------------------------- helpers
def _prep(weekly: pd.DataFrame, as_of) -> pd.DataFrame:
    w = weekly.rename(columns={"t": "week_start"}).copy()
    w["week_start"] = pd.to_datetime(w["week_start"])
    w = w[w["week_start"] + pd.Timedelta(days=6) <= pd.Timestamp(as_of)]
    for c in ("lo", "hi"):
        if c not in w:
            w[c] = np.nan
    if "modeled_share" not in w:
        w["modeled_share"] = np.where(w.get("source", OBSERVED) == OBSERVED, 0.0, 1.0)
    w["mid"] = w["week_start"] + pd.Timedelta(days=3, hours=12)
    return w.sort_values("week_start").reset_index(drop=True)


def _crossing(offsets: np.ndarray, values: np.ndarray, q: float) -> float | None:
    """Day offset at which cumulative share q is reached; each week's value is spread evenly over its 7 days."""
    v = np.clip(np.nan_to_num(values, nan=0.0), 0, None)
    total = v.sum()
    if total <= 0:
        return None
    cum = np.cumsum(v)
    k = int(np.searchsorted(cum, q * total, side="left"))
    k = min(k, len(v) - 1)
    before = cum[k - 1] if k > 0 else 0.0
    frac = (q * total - before) / v[k] if v[k] > 0 else 0.0
    return float(offsets[k] - 3.5 + 7.0 * frac)


def _cum_at(offsets: np.ndarray, values: np.ndarray, cutoff: float) -> float:
    """Detections accumulated by day offset `cutoff` (same even-spread rule)."""
    v = np.clip(np.nan_to_num(values, nan=0.0), 0, None)
    covered = np.clip((cutoff - (offsets - 3.5)) / 7.0, 0.0, 1.0)
    return float((v * covered).sum())


def _peaks(offsets: np.ndarray, values: np.ndarray) -> tuple[float | None, list[float]]:
    v = np.nan_to_num(values, nan=0.0)
    if v.max(initial=0) <= 0:
        return None, []
    k = int(np.argmax(v))
    others = []
    for i in range(len(v)):
        left = v[i - 1] if i > 0 else -np.inf
        right = v[i + 1] if i + 1 < len(v) else -np.inf
        if i != k and v[i] >= left and v[i] >= right and v[i] >= 0.5 * v[k] and abs(i - k) >= 3:
            others.append(float(offsets[i]))
    return float(offsets[k]), others


def _num(x, nd=1):
    """Plain float or None (no NaN, no numpy types) for JSON."""
    if x is None:
        return None
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return round(x, nd) if np.isfinite(x) else None


def _date(start: pd.Timestamp, offset: float | None) -> str | None:
    if offset is None or not np.isfinite(offset):
        return None
    return (start + pd.Timedelta(days=float(offset))).date().isoformat()


def _md(offset: float | None, season: Season) -> str | None:
    """Offset as month-day in a reference non-leap season year (for typical dates)."""
    if offset is None or not np.isfinite(offset):
        return None
    start, _ = season.bounds(2023)
    return (start + pd.Timedelta(days=float(offset))).strftime("%m-%d")


def _trend(years: np.ndarray, y: np.ndarray) -> tuple[float | None, list[float] | None, int]:
    ok = np.isfinite(y)
    n = int(ok.sum())
    if n < 3:
        return None, None, n
    s, _, lo, hi = theilslopes(y[ok], years[ok], alpha=0.95)
    return float(s), [float(lo), float(hi)], n


def _verdict(slope, ci, n, up: str, down: str) -> str:
    if slope is None or n < MIN_TREND_SEASONS:
        return "insufficient_seasons"
    if ci[0] > 0:
        return up
    if ci[1] < 0:
        return down
    return "no_clear_shift"


# ---------------------------------------------------------------- per season year
def season_years(weekly: pd.DataFrame, season: Season, as_of) -> pd.DataFrame:
    """One row per season year with status, totals and timing offsets (days since window start)."""
    as_of = pd.Timestamp(as_of)
    w = _prep(weekly, as_of)
    if w.empty:
        return pd.DataFrame()
    first, last = int(w["mid"].dt.year.min()), int(as_of.year) + 1
    rows = []
    for y in range(first, last + 1):
        start, end = season.bounds(y)
        if start > as_of:
            continue
        all_mids = pd.date_range(start, end, freq="7D")  # expected number of weeks in the window
        sel = w[(w["mid"] >= start) & (w["mid"] <= end + pd.Timedelta(days=1))]
        offsets = ((sel["mid"] - start) / pd.Timedelta(days=1)).to_numpy()
        values = sel["value"].to_numpy(dtype=float)
        valid = np.isfinite(values)
        total = float(np.nansum(values))
        expected = max(len(all_mids), 1)
        partial = end > as_of
        coverage = float(valid.sum()) / expected
        modeled = float(np.nansum(values * sel["modeled_share"].to_numpy(dtype=float)) / total) if total > 0 else \
            float(sel["modeled_share"].mean()) if len(sel) else 1.0
        row = {"season_year": y, "start": start, "end": end, "partial": partial, "total": total,
               "coverage": round(min(coverage, 1.0), 3), "modeled_share": round(modeled, 3), "n_weeks": int(valid.sum()),
               "offsets": offsets, "values": values, "lo": sel["lo"].to_numpy(dtype=float),
               "hi": sel["hi"].to_numpy(dtype=float), "observed": (sel.get("source") == OBSERVED).to_numpy()
               if "source" in sel else np.zeros(len(sel), bool)}
        rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    low = MIN_TOTAL  # absolute on purpose: a genuinely small season is still a season (Punjab 2024-2026)
    status = np.where(df["partial"], "partial",
                      np.where(df["coverage"] < MIN_COVERAGE, "missing",
                               np.where(df["total"] < low, "low_activity", "complete")))
    df["status"] = status
    for q, col in ((0.1, "p10"), (0.5, "p50"), (0.9, "p90")):
        df[col] = [(_crossing(o, v, q) if s == "complete" else None) for o, v, s in zip(df["offsets"], df["values"], df["status"])]
    pk = [(_peaks(o, v) if s == "complete" else (None, [])) for o, v, s in zip(df["offsets"], df["values"], df["status"])]
    df["peak"] = [p for p, _ in pk]
    df["secondary_peaks"] = [o for _, o in pk]
    df["multi_peak"] = [bool(o) for _, o in pk]
    df["interval_sensitivity_days"] = [_sensitivity(r) if r["status"] == "complete" else None for _, r in df.iterrows()]
    return df


def _sensitivity(r) -> float | None:
    base = [_crossing(r["offsets"], r["values"], q) for q in (0.1, 0.5, 0.9)]
    nonobs = ~r["observed"]
    if not np.isfinite(r["lo"][nonobs]).any():
        return None
    shifts = []
    for bound in ("lo", "hi"):
        v = np.where(nonobs & np.isfinite(r[bound]), r[bound], r["values"])
        for b, q in zip(base, (0.1, 0.5, 0.9)):
            c = _crossing(r["offsets"], v, q)
            if b is not None and c is not None:
                shifts.append(abs(c - b))
    return round(max(shifts), 1) if shifts else None


# ---------------------------------------------------------------- profile
def _typical(done: pd.DataFrame, season: Season) -> dict:
    out = {"n_seasons": int(len(done)), "season_years": [int(y) for y in done["season_year"]]}
    for col in ("p10", "p50", "p90", "peak"):
        x = pd.to_numeric(done[col], errors="coerce").dropna()
        out[col] = None if x.empty else {"median_md": _md(x.median(), season), "q25_md": _md(x.quantile(0.25), season),
                                         "q75_md": _md(x.quantile(0.75), season), "median_offset_days": round(float(x.median()), 1)}
    t = done["total"]
    out["total"] = None if t.empty else {"median": round(float(t.median()), 1), "q25": round(float(t.quantile(0.25)), 1),
                                         "q75": round(float(t.quantile(0.75)), 1)}
    return out


def profile_one(weekly: pd.DataFrame, season: Season, as_of) -> dict:
    as_of = pd.Timestamp(as_of)
    df = season_years(weekly, season, as_of)
    res = {"name": season.name, "window": season.md()}
    if df.empty:
        return {**res, "typical": None, "typical_observed_era": None, "timing_trend": None, "magnitude_trend": None,
                "current": None, "years": []}
    done = df[df["status"] == "complete"]
    obs = done[done["modeled_share"] < OBSERVED_ERA_MAX_MODELED]
    res["typical"] = _typical(done, season)
    res["typical_observed_era"] = _typical(obs, season)

    yrs = obs["season_year"].to_numpy(dtype=float)
    s, ci, n = _trend(yrs, pd.to_numeric(obs["p50"], errors="coerce").to_numpy(dtype=float))
    res["timing_trend"] = {"metric": "p50 day", "basis": "observed_era", "n": n,
                           "days_per_decade": None if s is None else round(10 * s, 1),
                           "ci": None if ci is None else [round(10 * ci[0], 1), round(10 * ci[1], 1)],
                           "verdict": _verdict(s, ci, n, "later", "earlier")}
    tot = obs["total"].to_numpy(dtype=float)
    s, ci, n = _trend(yrs, np.log(np.where(tot > 0, tot, np.nan)))
    pct = (lambda b: _num((np.exp(10 * b) - 1) * 100))
    res["magnitude_trend"] = {"metric": "season total", "basis": "observed_era", "n": n,
                              "pct_per_decade": None if s is None else pct(s),
                              "ci": None if ci is None else [pct(ci[0]), pct(ci[1])],
                              "verdict": _verdict(s, ci, n, "more", "fewer"),
                              "caveat": "Detections, not burned area; overpass timing changes can lower counts."}
    res["current"] = _current(df, done, as_of)
    res["years"] = [{
        "season_year": int(r["season_year"]), "status": r["status"], "total": _num(r["total"]),
        "coverage": _num(r["coverage"], 3), "modeled_share": _num(r["modeled_share"], 3),
        "p10_date": _date(r["start"], r["p10"]), "p50_date": _date(r["start"], r["p50"]),
        "p90_date": _date(r["start"], r["p90"]), "peak_date": _date(r["start"], r["peak"]),
        "multi_peak": bool(r["multi_peak"]), "interval_sensitivity_days": _num(r["interval_sensitivity_days"]),
    } for _, r in df.iterrows()]
    return res


def _current(df: pd.DataFrame, done: pd.DataFrame, as_of: pd.Timestamp) -> dict | None:
    cur = df[df["partial"]]
    if cur.empty:
        last = df.iloc[-1]
        return {"season_year": int(last["season_year"]), "status": "ended", "to_date_total": round(float(last["total"]), 1)}
    r = cur.iloc[-1]
    covered = r["offsets"][np.isfinite(r["values"])]
    cutoff = float(covered.max() + 3.5) if len(covered) else 0.0
    if cutoff <= 0:
        return {"season_year": int(r["season_year"]), "status": "not_started", "to_date_total": 0.0}
    past = np.array([_cum_at(o, v, cutoff) for o, v in zip(done["offsets"], done["values"])])
    share = np.array([_cum_at(o, v, cutoff) / t for o, v, t in zip(done["offsets"], done["values"], done["total"])])
    to_date = float(r["total"])
    return {
        "season_year": int(r["season_year"]), "status": "in_progress", "cutoff_offset_days": round(cutoff, 1),
        "data_through": (r["start"] + pd.Timedelta(days=cutoff)).date().isoformat(),
        "to_date_total": round(to_date, 1), "n_past": int(len(past)),
        "percentile_at_cutoff": None if not len(past) else round(float((past < to_date).mean() * 100), 1),
        "typical_to_date_total": None if not len(past) else round(float(np.median(past)), 1),
        "typical_share_by_cutoff": None if not len(share) else round(float(np.median(share)), 3),
        "modeled_share": _num(r["modeled_share"], 3),
    }


def season_profile(weekly: pd.DataFrame, as_of, area: str | None = None, seasons: list[Season] | None = None) -> dict:
    """Profile of every configured season for one AOI weekly series.

    weekly: week_start (or t), value, and optionally lo, hi, source, modeled_share (common.series.weekly_series output
    or a snapshot summary series). as_of: date; nothing later is used."""
    seasons = seasons or SEASON_WINDOWS[area]
    w = _prep(weekly, as_of)
    through = (w.loc[w["value"].notna(), "week_start"].max() + pd.Timedelta(days=6)) if len(w) else None
    return {
        "schema_version": SCHEMA_VERSION, "area": area, "as_of": pd.Timestamp(as_of).date().isoformat(),
        "data_through": None if through is None or pd.isna(through) else through.date().isoformat(),
        "units": "SNPP-equivalent detections per season", "definition": DEFINITION,
        "seasons": [profile_one(weekly, s, as_of) for s in seasons],
    }


def from_summary(summary: dict, area: str, as_of) -> dict:
    """Profile from a saved weekly summary with an explicit observation cutoff."""
    series = pd.DataFrame(summary["series"])
    return season_profile(series, as_of, area)


def main(argv=None):
    import argparse
    import json
    ap = argparse.ArgumentParser(description="Season profile from a saved weekly summary (read-only)")
    ap.add_argument("--summary", required=True, help="Weekly summary JSON, e.g. contracts/fixtures/punjab_summary.json")
    ap.add_argument("--area", choices=sorted(SEASON_WINDOWS), required=True)
    ap.add_argument("--as-of", required=True)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    with open(a.summary, encoding="utf-8") as f:
        prof = from_summary(json.load(f), a.area, a.as_of)
    text = json.dumps(prof, indent=2, default=lambda o: None if isinstance(o, float) and not np.isfinite(o) else str(o))
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    else:
        print(text)


if __name__ == "__main__":
    main()
