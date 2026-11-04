"""Season profile (I1). Synthetic seasons with known timing, plus the real hosted snapshot as a regression fixture."""
import json
import os

import jsonschema
import numpy as np
import pandas as pd
import pytest

from ws4_outlook import season_profile as sp

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUTUMN = sp.Season("autumn", (9, 15), (12, 31))
WINTER = sp.Season("winter", (11, 1), (5, 31))


def _series(years, peak_doy, shift_per_year=0.0, scale=None, start="2001-01-01", end="2024-12-31", modeled_before=None):
    ws = pd.date_range(pd.Timestamp(start) - pd.Timedelta(days=pd.Timestamp(start).dayofweek), end, freq="7D")
    mid = ws + pd.Timedelta(days=3.5)
    v = np.zeros(len(ws))
    rng = np.random.default_rng(7)
    for y in years:
        c = pd.Timestamp(y, 1, 1) + pd.Timedelta(days=peak_doy + shift_per_year * (y - years[0]) + rng.normal(0, 2))
        amp = (1000.0 if scale is None else scale(y)) * np.exp(rng.normal(0, 0.15))
        v += amp * np.exp(-0.5 * (((mid - c) / pd.Timedelta(days=1)).to_numpy() / 9.0) ** 2)
    src = np.where(mid < pd.Timestamp(modeled_before), "modeled_from_modis", "observed_viirs") if modeled_before \
        else np.full(len(ws), "observed_viirs")
    return pd.DataFrame({"week_start": ws, "value": v, "lo": np.where(src == "observed_viirs", v, 0.7 * v),
                         "hi": np.where(src == "observed_viirs", v, 1.3 * v), "source": src,
                         "modeled_share": (src != "observed_viirs").astype(float)})


def test_central_window_matches_a_known_symmetric_season():
    w = _series(range(2001, 2025), peak_doy=305)            # peak about 1-2 Nov
    p = sp.season_profile(w, "2025-01-15", seasons=[AUTUMN])["seasons"][0]
    t = p["typical"]
    assert t["n_seasons"] >= 20
    assert t["p50"]["median_md"] in ("11-01", "11-02") and t["peak"]["median_md"] in ("10-31", "11-01", "11-02", "11-03")
    # symmetric Gaussian, sd 9 days: 10% and 90% are about 11.5 days either side
    p10, p90 = t["p10"]["median_offset_days"], t["p90"]["median_offset_days"]
    assert 20 <= p90 - p10 <= 26


def test_timing_shift_and_magnitude_change_are_reported_separately():
    yrs = list(range(2001, 2025))
    later = sp.season_profile(_series(yrs, 300, shift_per_year=0.7), "2025-01-15", seasons=[AUTUMN])["seasons"][0]
    assert later["timing_trend"]["verdict"] == "later" and later["magnitude_trend"]["verdict"] == "no_clear_shift"
    fewer = sp.season_profile(_series(yrs, 300, scale=lambda y: 3000 * 0.9 ** (y - 2001)), "2025-01-15",
                              seasons=[AUTUMN])["seasons"][0]
    assert fewer["timing_trend"]["verdict"] == "no_clear_shift" and fewer["magnitude_trend"]["verdict"] == "fewer"


def test_trends_use_only_the_observed_era():
    yrs = list(range(2001, 2025))
    w = _series(yrs, 300, modeled_before="2012-01-20")
    p = sp.season_profile(w, "2025-01-15", seasons=[AUTUMN])["seasons"][0]
    assert p["timing_trend"]["basis"] == "observed_era" and p["timing_trend"]["n"] == 13      # 2012-2024
    assert p["typical"]["n_seasons"] > p["typical_observed_era"]["n_seasons"]
    early = [y for y in p["years"] if y["season_year"] == 2005][0]
    assert early["modeled_share"] == 1.0 and early["interval_sensitivity_days"] is not None


def test_as_of_cutoff_uses_no_later_data_and_compares_at_the_same_cutoff():
    yrs = list(range(2001, 2025))
    w = _series(yrs, 305, scale=lambda y: 200.0 if y == 2024 else 1000.0)   # a weak current season
    base = sp.season_profile(w, "2024-10-29", seasons=[AUTUMN])["seasons"][0]
    w2 = w.copy()
    w2.loc[w2["week_start"] >= "2024-10-29", "value"] *= 50                         # changes after as_of
    again = sp.season_profile(w2, "2024-10-29", seasons=[AUTUMN])["seasons"][0]
    assert json.dumps(base, default=str) == json.dumps(again, default=str)
    cur = base["current"]
    assert cur["status"] == "in_progress" and cur["season_year"] == 2024
    assert cur["percentile_at_cutoff"] <= 10                                         # far below past years at the same cutoff
    assert 0.1 < cur["typical_share_by_cutoff"] < 0.6


def test_window_crossing_new_year_and_leap_years():
    w = _series(range(2001, 2025), peak_doy=75)              # mid-March, inside a Nov-May window
    p = sp.season_profile(w, "2024-07-01", seasons=[WINTER])["seasons"][0]
    y2024 = [y for y in p["years"] if y["season_year"] == 2024][0]
    assert y2024["status"] == "complete" and y2024["p50_date"].startswith("2024-03")
    start, end = WINTER.bounds(2024)
    assert start == pd.Timestamp("2023-11-01") and end == pd.Timestamp("2024-05-31")


def test_missing_low_activity_and_multi_peak():
    w = _series(range(2001, 2025), 305)
    w.loc[(w["week_start"] >= "2010-10-01") & (w["week_start"] < "2010-11-15"), "value"] = np.nan   # gap
    w.loc[(w["week_start"] >= "2015-09-01") & (w["week_start"] < "2016-01-01"), "value"] *= 0.001   # tiny season
    extra = (w["week_start"] >= "2018-10-01") & (w["week_start"] < "2018-10-08")
    w.loc[extra, "value"] = 900                                                        # second peak, 4 weeks early
    p = sp.season_profile(w, "2025-01-15", seasons=[AUTUMN])["seasons"][0]
    st = {y["season_year"]: y for y in p["years"]}
    assert st[2010]["status"] == "missing" and st[2015]["status"] == "low_activity"
    assert st[2018]["multi_peak"] is True
    assert st[2010]["p50_date"] is None and 2010 not in p["typical"]["season_years"]


def test_profile_from_the_real_snapshot_matches_schema():
    snap_path = os.path.join(ROOT, "ws5_frontend", "public", "demo", "snapshot.json")
    with open(os.path.join(ROOT, "contracts", "json_schemas", "season_profile.schema.json"), encoding="utf-8") as f:
        schema = json.load(f)
    with open(snap_path, encoding="utf-8") as f:
        snap = json.load(f)
    for area in ("pb", "bd"):
        prof = sp.from_snapshot(snap, area)
        json.dumps(prof, allow_nan=False)
        jsonschema.Draft7Validator(schema).validate(prof)
    pb = sp.from_snapshot(snap, "pb")
    assert [s["name"] for s in pb["seasons"]] == ["wheat_residue", "paddy_residue"]
    paddy = pb["seasons"][1]["typical"]
    assert paddy["p50"]["median_md"][:2] in ("10", "11")                           # autumn peak, as documented


def test_example_fixture_is_valid():
    with open(os.path.join(ROOT, "contracts", "json_schemas", "season_profile.schema.json"), encoding="utf-8") as f:
        schema = json.load(f)
    with open(os.path.join(ROOT, "contracts", "fixtures", "punjab_season_profile.json"), encoding="utf-8") as f:
        jsonschema.Draft7Validator(schema).validate(json.load(f))


@pytest.mark.parametrize("area", sorted(sp.SEASON_WINDOWS))
def test_configured_windows_do_not_overlap(area):
    seasons = sp.SEASON_WINDOWS[area]
    days = []
    for s in seasons:
        a, b = s.bounds(2023)
        days.append(set(pd.date_range(a, b).dayofyear))
    for i in range(len(days)):
        for j in range(i + 1, len(days)):
            assert not days[i] & days[j]
