from pathlib import Path
import importlib.util


def test_share_allowlist_excludes_sensitive_and_generated_paths(monkeypatch, tmp_path):
    script = Path(__file__).resolve().parents[1] / "share_zip.py"
    spec = importlib.util.spec_from_file_location("share_zip", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    for path in (".env", "ws5_frontend/.env", "ws5_frontend/node_modules/a/index.ts",
                 "data/raw/firms/FIRMS.csv", "ws2_platform/static_fallback/meta.json",
                 "ws5_frontend/tsconfig.tsbuildinfo", "codex/private.md"):
        assert not module.included(tmp_path / path), path
    for path in (".env.example", "ws5_frontend/.env.example", "scripts/launch.ps1",
                 "ws5_frontend/src/App.tsx", "CLAUDE.md"):
        assert module.included(tmp_path / path), path
