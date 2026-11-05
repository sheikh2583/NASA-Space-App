"""Offline shared archive validation; temporary fixture bytes only, no fitting or extraction."""
import json
import zipfile

import pytest

from scripts import runtime_bundle as bundle
from scripts.tests.test_runtime_bundle import data_fixture


def test_shared_validator_accepts_exact_new_and_legacy_layouts_without_extracting(tmp_path):
    source = tmp_path / "source"
    data_fixture(source)
    for name, names in (("new", bundle.REQUIRED | bundle.VALIDATION), ("legacy", bundle.LEGACY_NAMES)):
        archive = tmp_path / f"{name}.zip"
        with zipfile.ZipFile(archive, "w") as package:
            for member in sorted(names):
                package.writestr(member, (source / member).read_bytes())
        assert set(bundle.validate_archive(archive)) == names
    assert {p.name for p in tmp_path.iterdir()} == {"source", "new.zip", "legacy.zip"}


def test_shared_validator_rejects_failed_saved_qa(tmp_path):
    source = tmp_path / "source"
    data_fixture(source)
    (source / "validation/qa.json").write_text(json.dumps({"metrics": {"checks": [{"result": "fail"}]}}))
    archive = tmp_path / "invalid.zip"
    with zipfile.ZipFile(archive, "w") as package:
        for member in bundle.REQUIRED | bundle.VALIDATION:
            package.writestr(member, (source / member).read_bytes())
    with pytest.raises(ValueError, match="passing QA"):
        bundle.validate_archive(archive)


def test_shared_validator_checks_expanded_size_before_reading_artifacts(tmp_path, monkeypatch):
    source = tmp_path / "source"
    data_fixture(source)
    (source / "cells.parquet").write_bytes(b"x" * 100_000)
    archive = tmp_path / "large.zip"
    bundle.pack(source, archive)
    monkeypatch.setattr(bundle, "MAX_BYTES", archive.stat().st_size + 100)
    with pytest.raises(ValueError, match="Expanded"):
        bundle.validate_archive(archive)
