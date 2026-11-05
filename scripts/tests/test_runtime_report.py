import hashlib
import zipfile
import pytest
from scripts import runtime_bundle as bundle
from scripts.tests.test_runtime_bundle import data_fixture


def test_new_bundle_requires_and_transports_detailed_report(tmp_path):
    source = tmp_path / "source"
    data_fixture(source)
    report = source / "validation/intervals_by_stratum.json"
    report.write_text('{"metrics":{"acceptance_status":"stop_condition"}}')
    digest = bundle.pack(source, tmp_path / "new.zip")
    bundle.unpack(tmp_path / "new.zip", tmp_path / "out", digest)
    assert (tmp_path / "out/validation/intervals_by_stratum.json").read_bytes() == report.read_bytes()
    report.unlink()
    with pytest.raises(ValueError, match="intervals_by_stratum"):
        bundle.pack(source, tmp_path / "missing.zip")


def test_exact_legacy_archive_is_still_supported(tmp_path):
    source = tmp_path / "source"
    data_fixture(source)
    archive = tmp_path / "legacy.zip"
    with zipfile.ZipFile(archive, "w") as package:
        for name in bundle.LEGACY_NAMES:
            package.writestr(name, (source / name).read_bytes())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    bundle.unpack(archive, tmp_path / "out", digest)
    assert (tmp_path / "out/cells.parquet").is_file()


def test_new_format_does_not_allow_unexpected_extras(tmp_path):
    source = tmp_path / "source"
    data_fixture(source)
    archive = tmp_path / "bad.zip"
    bundle.pack(source, archive)
    with zipfile.ZipFile(archive, "a") as package:
        package.writestr("private.env", "not a credential")
    with pytest.raises(ValueError, match="unexpected"):
        bundle.unpack(archive, tmp_path / "out", hashlib.sha256(archive.read_bytes()).hexdigest())
