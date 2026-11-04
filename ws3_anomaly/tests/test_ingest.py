import datetime as dt
import io

import pandas as pd
import pytest

from ws3_anomaly.ingest import firms, normalize

VIIRS_CSV = """latitude,longitude,bright_ti4,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_ti5,frp,daynight,type
23.1,90.2,330,0.4,0.4,2024-03-01,730,N,VIIRS,h,2.0SP,290,5.1,D,0
23.1,90.2,330,0.4,0.4,2024-03-01,730,N,VIIRS,h,2.0NRT,290,5.1,D,0
23.2,90.3,330,0.4,0.4,2024-03-01,1930,N20,VIIRS,l,2.0SP,290,1.1,N,0
23.3,90.4,330,0.4,0.4,2024-03-01,730,N,VIIRS,n,2.0SP,290,9.0,D,2
"""
MODIS_CSV = """latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_t31,frp,daynight,type
30.1,75.2,320,1.2,1.1,2001-11-01,520,Terra,MODIS,85,6.1SP,295,20.0,D,0
"""

SNPP_ARCHIVE_CSV = """latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_t31,frp,daynight,type
23.1,90.2,330,0.4,0.4,2012-01-20,730,SNPP,SNPP,n,2,290,5.1,D,0
"""


def test_normalize_maps_sats_confidence_and_drops_static_sources():
    df, st = normalize.normalize_frame(pd.read_csv(io.StringIO(VIIRS_CSV)))
    assert st == {"rows_in": 4, "dropped_non_vegetation": 1, "rows_out": 3}
    assert df["sat"].tolist() == ["SNPP", "SNPP", "NOAA20"]
    assert df["conf"].tolist() == [90, 90, 20]
    m, _ = normalize.normalize_frame(pd.read_csv(io.StringIO(MODIS_CSV)))
    assert m.loc[0, "sensor"] == "MODIS" and m.loc[0, "conf"] == 85 and m.loc[0, "acq_date"] == dt.date(2001, 11, 1)
    snpp, _ = normalize.normalize_frame(pd.read_csv(io.StringIO(SNPP_ARCHIVE_CSV)))
    assert snpp.loc[0, "sensor"] == "VIIRS" and snpp.loc[0, "sat"] == "SNPP" and snpp.loc[0, "conf"] == 60


def test_unknown_satellite_code_is_an_error():
    bad = VIIRS_CSV.replace(",N20,", ",XX,")
    with pytest.raises(ValueError):
        normalize.normalize_frame(pd.read_csv(io.StringIO(bad)))


def test_normalize_files_drops_nrt_duplicates(tmp_path):
    p = tmp_path / "v.csv"
    p.write_text(VIIRS_CSV)
    det, report, dups = normalize.normalize_files([str(p)], str(tmp_path / "d.parquet"))
    assert dups == 1 and len(det) == 2
    assert pd.read_parquet(tmp_path / "d.parquet").columns.tolist() == [f.name for f in normalize.SCHEMA]


def test_firms_windows_and_url():
    w = list(firms.windows(dt.date(2024, 1, 1), dt.date(2024, 1, 25)))
    assert w == [(dt.date(2024, 1, 1), 10), (dt.date(2024, 1, 11), 10), (dt.date(2024, 1, 21), 5)]
    u = firms.url("KEY", "VIIRS_NOAA20_NRT", [88, 20.5, 92.7, 26.7], dt.date(2026, 11, 1), 3)
    assert u.endswith("/KEY/VIIRS_NOAA20_NRT/88,20.5,92.7,26.7/3/2026-11-01")


def test_firms_refuses_retired_snpp_nrt(tmp_path):
    with pytest.raises(ValueError, match="NOAA20"):
        firms.download("VIIRS_SNPP_NRT", [88, 20, 89, 21], dt.date(2026, 11, 1), dt.date(2026, 11, 2), str(tmp_path), key="k")


def test_firms_download_caches_and_records_gaps(tmp_path):
    class Resp:
        def __init__(self, code, text):
            self.status_code, self.text = code, text

    class Session:
        calls = 0

        def get(self, url, timeout):
            Session.calls += 1
            if "2024-01-11" in url:
                return Resp(500, "error")
            return Resp(200, VIIRS_CSV)

    firms.time.sleep = lambda s: None
    paths, gaps = firms.download("VIIRS_NOAA20_SP", [88, 20, 89, 21], dt.date(2024, 1, 1), dt.date(2024, 1, 15),
                                 str(tmp_path), key="k", session=Session())
    assert len(paths) == 1 and len(gaps) == 1
    before = Session.calls
    firms.download("VIIRS_NOAA20_SP", [88, 20, 89, 21], dt.date(2024, 1, 1), dt.date(2024, 1, 10),
                   str(tmp_path), key="k", session=Session())
    assert Session.calls == before  # cached window, no new request


def test_clip_to_demo_regions():
    df, _ = normalize.normalize_frame(pd.read_csv(io.StringIO(VIIRS_CSV + "10.0,10.0,330,0.4,0.4,2024-03-01,730,N,VIIRS,h,2.0SP,290,5.1,D,0\n")))
    assert len(df) == 4 and len(normalize.clip_to_demo(df)) == 3
