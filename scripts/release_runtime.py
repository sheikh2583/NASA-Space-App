"""Publish a new runtime-data version for the Render service in one checked command (plan card T16).

    python scripts/release_runtime.py --data-through 2026-11-02             # dry run: new manifest + the commands
    python scripts/release_runtime.py --data-through 2026-11-02 --publish   # upload, verify, then write the manifest

Packaging and uploading train nothing. The zip is share/firesense-runtime.zip (made by `train.ps1 -Pack` /
`train.sh --pack`, or here with `runtime_bundle.py pack` if missing). --publish needs the GitHub CLI signed in
(`gh auth login`). Every upload goes to a NEW tag, so a pinned asset is never replaced. deployment/runtime.json is
written only after the uploaded asset's SHA256 matches the local zip. It never commits or pushes.
Archive record-end verification uses the installed PyArrow package; no fitting occurs.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "deployment" / "runtime.json"
ZIP = ROOT / "share" / "firesense-runtime.zip"
ASSET = "firesense-runtime.zip"
URL_RE = re.compile(r"https://github\.com/(?P<repo>[^/]+/[^/]+)/releases/download/(?P<tag>[^/]+)/(?P<asset>[^/]+)$")


def validate_release_archive(zip_path: Path, data_through: str) -> str:
    """Check saved validation/layout and assert the record end against the selected archive."""
    import pyarrow.parquet as pq
    # Also support direct execution as `python scripts/release_runtime.py`.
    if __package__:
        from .runtime_bundle import validate_archive
    else:
        from runtime_bundle import validate_archive

    validate_archive(zip_path)
    with zipfile.ZipFile(zip_path) as package:
        dates = pq.read_table(io.BytesIO(package.read("sensor_days.parquet")), columns=["date"])["date"].to_pylist()
    if not dates or any(not isinstance(value, dt.date) for value in dates):
        raise ValueError("Runtime sensor_days must contain non-null dates")
    actual = max(dates).isoformat()
    if data_through != actual:
        raise ValueError(f"--data-through {data_through!r} disagrees with archive record end {actual}")
    return actual


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def current(manifest: dict) -> dict:
    m = URL_RE.match(manifest.get("url", ""))
    if not m:
        raise ValueError(f"deployment/runtime.json has an unexpected url: {manifest.get('url')!r}")
    return m.groupdict()


def plan_release(manifest: dict, zip_path: Path, tag: str, data_through: str) -> dict:
    """The new manifest for `tag`. Refuses the tag already pinned and a data_through that isn't an ISO date."""
    cur = current(manifest)
    if tag == cur["tag"]:
        raise ValueError(f"tag {tag} is the one already pinned; every release needs a new tag")
    try:
        dt.date.fromisoformat(data_through)
    except ValueError:
        raise ValueError(f"--data-through must be an ISO date (YYYY-MM-DD), not {data_through!r}") from None
    return {"data_through": data_through,
            "url": f"https://github.com/{cur['repo']}/releases/download/{tag}/{ASSET}",
            "sha256": sha256(zip_path)}


def default_tag(today: dt.date, existing: set[str]) -> str:
    """runtime-YYYYMMDD-render-vN with the lowest N not already used."""
    n = 1
    while f"runtime-{today:%Y%m%d}-render-v{n}" in existing:
        n += 1
    return f"runtime-{today:%Y%m%d}-render-v{n}"


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    """The one place that runs external commands (git, gh, python); tests replace it."""
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=ROOT, **kw)


def existing_tags(manifest: dict) -> set[str]:
    tags = {current(manifest)["tag"]}
    r = run(["git", "ls-remote", "--tags", "origin"])
    if r.returncode == 0:
        tags |= {ln.split("refs/tags/", 1)[1].removesuffix("^{}") for ln in r.stdout.splitlines() if "refs/tags/" in ln}
    return tags


def write_manifest(new: dict, path: Path = MANIFEST) -> None:
    path.write_text(json.dumps(new, indent=2) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-through", required=True, help="last day with data in the packaged outputs (YYYY-MM-DD)")
    ap.add_argument("--tag", help="release tag (default: runtime-YYYYMMDD-render-vN, the lowest free N)")
    ap.add_argument("--zip", type=Path, default=ZIP)
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    ap.add_argument("--publish", action="store_true", help="upload, verify and write the manifest (default: dry run)")
    a = ap.parse_args(argv)

    manifest = json.loads(a.manifest.read_text(encoding="utf-8"))
    repo = current(manifest)["repo"]
    if not a.zip.exists():
        print(f"{a.zip} is missing: packaging the saved outputs (no training).", flush=True)
        r = run([sys.executable, "scripts/runtime_bundle.py", "pack", "--output", str(a.zip)])
        print(r.stdout + r.stderr, end="")
        if r.returncode != 0:
            print("STOPPED: runtime_bundle.py pack refused the current outputs.")
            return 1
    validate_release_archive(a.zip, a.data_through)
    tag = a.tag or default_tag(dt.date.today(), existing_tags(manifest))
    new = plan_release(manifest, a.zip, tag, a.data_through)
    notes = f"{a.data_through}; packaged from validated outputs; no training"
    create = ["gh", "release", "create", tag, str(a.zip), "--repo", repo, "--title", tag, "--notes", notes]

    print("New deployment/runtime.json:\n" + json.dumps(new, indent=2))
    if not a.publish:
        print("\nDry run. With --publish it would run:\n  gh release view " + tag + f" --repo {repo}   (must fail: tag unused)\n  "
              + " ".join(create) + f"\n  gh release download {tag} --repo {repo} --pattern {ASSET}   (SHA256 must match)\n"
              "then write deployment/runtime.json.")
        return 0

    if run(["gh", "release", "view", tag, "--repo", repo]).returncode == 0:
        print(f"STOPPED: release {tag} already exists. Pick a new --tag; never replace a pinned asset.")
        return 1
    r = run(create)
    if r.returncode != 0:
        print("STOPPED: gh release create failed:\n" + r.stdout + r.stderr)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        r = run(["gh", "release", "download", tag, "--repo", repo, "--pattern", ASSET, "--dir", tmp])
        got = Path(tmp) / ASSET
        if r.returncode != 0 or not got.exists():
            print("STOPPED: could not download the uploaded asset to verify it:\n" + r.stdout + r.stderr)
            return 1
        if sha256(got) != new["sha256"]:
            print("STOPPED: the uploaded asset's SHA256 differs from the local zip. Manifest not written.")
            return 1
    write_manifest(new, a.manifest)
    print(f"Release {tag} verified; {a.manifest.relative_to(ROOT) if a.manifest.is_relative_to(ROOT) else a.manifest} updated.")
    print("Next: Sheikh commits deployment/runtime.json; Render rebuilds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
