"""Runtime-data release, offline: no network, no gh, no real data (plan card T16)."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

import pytest

from scripts import release_runtime as rr
from scripts import runtime_bundle as bundle
from scripts.tests.test_runtime_bundle import data_fixture

PINNED = {"data_through": "2026-11-02", "sha256": "0" * 64,
          "url": "https://github.com/sheikh2583/NASA-Space-App/releases/download/runtime-20261104-render-v1/firesense-runtime.zip"}


def make_zip(tmp_path: Path) -> Path:
    import pyarrow as pa
    import pyarrow.parquet as pq

    source = tmp_path / "saved"
    data_fixture(source)
    pq.write_table(pa.table({"date": [dt.date(2026, 11, 9), dt.date(2026, 11, 1)]}), source / "sensor_days.parquet")
    z = tmp_path / "firesense-runtime.zip"
    bundle.pack(source, z)
    return z


def test_plan_release_gives_the_url_and_checksum(tmp_path):
    z = make_zip(tmp_path)
    new = rr.plan_release(PINNED, z, "runtime-20261110-render-v1", "2026-11-09")
    assert new == {"data_through": "2026-11-09", "sha256": hashlib.sha256(z.read_bytes()).hexdigest(),
                   "url": "https://github.com/sheikh2583/NASA-Space-App/releases/download/runtime-20261110-render-v1/firesense-runtime.zip"}


def test_plan_release_refuses_the_pinned_tag_and_a_bad_date(tmp_path):
    z = make_zip(tmp_path)
    with pytest.raises(ValueError, match="already pinned"):
        rr.plan_release(PINNED, z, "runtime-20261104-render-v1", "2026-11-09")
    with pytest.raises(ValueError, match="ISO date"):
        rr.plan_release(PINNED, z, "runtime-20261110-render-v1", "9 Nov 2026")


def test_default_tag_skips_existing_versions():
    day = dt.date(2026, 11, 4)
    assert rr.default_tag(day, set()) == "runtime-20261104-render-v1"
    assert rr.default_tag(day, {"runtime-20261104-render-v1", "runtime-20261104-render-v2"}) == "runtime-20261104-render-v3"


class FakeGh:
    """Records commands; answers like gh. `exists`: the tag already has a release. `corrupt`: download differs."""

    def __init__(self, local_zip: Path, exists=False, corrupt=False):
        self.calls, self.local_zip, self.exists, self.corrupt = [], local_zip, exists, corrupt

    def __call__(self, cmd, **kw):
        self.calls.append(cmd)
        ok = subprocess.CompletedProcess(cmd, 0, "", "")
        if cmd[:3] == ["gh", "release", "view"]:
            return ok if self.exists else subprocess.CompletedProcess(cmd, 1, "", "release not found")
        if cmd[:3] == ["gh", "release", "download"]:
            out = Path(cmd[cmd.index("--dir") + 1]) / rr.ASSET
            if self.corrupt:
                out.write_bytes(b"different bytes")
            else:
                shutil.copy(self.local_zip, out)
        return ok


def setup(tmp_path, monkeypatch, **fake):
    z = make_zip(tmp_path)
    m = tmp_path / "runtime.json"
    m.write_text(json.dumps(PINNED, indent=2) + "\n", encoding="utf-8")
    gh = FakeGh(z, **fake)
    monkeypatch.setattr(rr, "run", gh)
    args = ["--data-through", "2026-11-09", "--tag", "runtime-20261110-render-v1", "--zip", str(z), "--manifest", str(m)]
    return z, m, gh, args


def test_publish_creates_the_release_then_writes_the_manifest(tmp_path, monkeypatch):
    z, m, gh, args = setup(tmp_path, monkeypatch)
    assert rr.main(args + ["--publish"]) == 0
    assert [c[:3] for c in gh.calls] == [["gh", "release", "view"], ["gh", "release", "create"], ["gh", "release", "download"]]
    new = json.loads(m.read_text(encoding="utf-8"))
    assert new["url"].endswith("/runtime-20261110-render-v1/firesense-runtime.zip")
    assert new["sha256"] == hashlib.sha256(z.read_bytes()).hexdigest() and m.read_text(encoding="utf-8").endswith("}\n")


def test_dry_run_runs_no_gh_command_and_writes_nothing(tmp_path, monkeypatch):
    _, m, gh, args = setup(tmp_path, monkeypatch)
    before = m.read_text(encoding="utf-8")
    assert rr.main(args) == 0
    assert not [c for c in gh.calls if c[0] == "gh"] and m.read_text(encoding="utf-8") == before


def test_an_existing_tag_stops_before_anything_is_written(tmp_path, monkeypatch):
    _, m, gh, args = setup(tmp_path, monkeypatch, exists=True)
    before = m.read_text(encoding="utf-8")
    assert rr.main(args + ["--publish"]) == 1
    assert m.read_text(encoding="utf-8") == before and not [c for c in gh.calls if c[:3] == ["gh", "release", "create"]]


def test_a_checksum_mismatch_after_upload_writes_nothing(tmp_path, monkeypatch):
    _, m, gh, args = setup(tmp_path, monkeypatch, corrupt=True)
    before = m.read_text(encoding="utf-8")
    assert rr.main(args + ["--publish"]) == 1
    assert m.read_text(encoding="utf-8") == before


def test_release_validates_existing_archive_record_end_before_any_external_command(tmp_path, monkeypatch):
    _, m, gh, args = setup(tmp_path, monkeypatch)
    before = m.read_bytes()
    args[args.index("--data-through") + 1] = "2026-11-10"
    with pytest.raises(ValueError, match="archive record end 2026-11-09"):
        rr.main(args + ["--publish"])
    assert not gh.calls
    assert m.read_bytes() == before


def test_existing_invalid_archive_cannot_reach_release_creation(tmp_path, monkeypatch):
    z, m, gh, args = setup(tmp_path, monkeypatch)
    before = m.read_bytes()
    with zipfile.ZipFile(z, "w") as package:
        package.writestr("../outside.txt", "unexpected")
    with pytest.raises(ValueError, match="unexpected"):
        rr.main(args + ["--publish"])
    assert not gh.calls
    assert m.read_bytes() == before
