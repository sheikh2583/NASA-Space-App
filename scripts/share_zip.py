"""Package an allowlisted source-only handoff, without Git or local datasets."""
from __future__ import annotations

import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIRS = {".github", "common", "contracts", "docs", "scripts", "tools", "ws1_harmonize", "ws2_platform", "ws3_anomaly", "ws4_outlook", "ws5_frontend", "ws6_validation"}
FILES = {"README.md", "START_HERE.cmd", "start.command", ".gitignore", ".gitattributes", ".env.example", "requirements.txt", "requirements.lock.txt", "requirements-cuda.txt", "pytest.ini", "CLAUDE.md", "data/README.md", "data/MANIFEST.md", "results/README.md"}
SKIP = {"node_modules", "dist", "__pycache__", ".pytest_cache", "static_fallback", ".venv"}
SUFFIXES = {".py", ".md", ".json", ".yaml", ".yml", ".ts", ".tsx", ".css", ".html", ".svg", ".mjs", ".sh", ".ps1", ".cmd", ".txt"}


def included(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if relative.as_posix() in FILES:
        return True
    if relative.parts[0] not in DIRS or any(part in SKIP for part in relative.parts):
        return False
    if path.name.startswith(".env"):
        return path.name == ".env.example"
    if relative.as_posix().startswith("ws5_frontend/public/method_"):
        return False
    return path.suffix in SUFFIXES or path.name in {"Dockerfile", "pre-commit", "pre-push"}


def main():
    out = ROOT / "share"
    out.mkdir(exist_ok=True)
    archive = out / "firesense-source.zip"
    paths = [ROOT / name for name in FILES if (ROOT / name).is_file()]
    for name in sorted(DIRS):
        for directory, subdirs, names in __import__("os").walk(ROOT / name):
            subdirs[:] = [sub for sub in subdirs if sub not in SKIP]
            paths.extend(path for file in names if included(path := Path(directory) / file))
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as package:
        for path in sorted(set(paths)):
            package.write(path, "firesense/" + path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as package:
        assert package.testzip() is None
        assert "firesense/START_HERE.cmd" in package.namelist()
    print(f"SHARE ZIP: {archive}\nFiles: {len(set(paths))}; size: {archive.stat().st_size:,} bytes")
    print("SHA256:", hashlib.sha256(archive.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
