"""Package/download existing validated API artifacts. Never fits or trains models."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {'cells.parquet', 'harmonized.parquet', 'sensor_days.parquet',
            'interval_table.json', 'drivers_region.json', 'outlook_region.json'}
VALIDATION = {'validation/harmonization.json', 'validation/intervals.json',
              'validation/drift.json', 'validation/outlook_skill.json', 'validation/qa.json'}
LEGACY_NAMES = REQUIRED | VALIDATION
VALIDATION = VALIDATION | {'validation/intervals_by_stratum.json'}
MAX_BYTES = 64 * 1024 * 1024


def validate_saved_outputs(read):
    harmonization = json.loads(read('validation/harmonization.json'))
    if harmonization['metrics'].get('data_mode') != 'real':
        raise ValueError('Runtime bundle requires existing real-data validation')
    checks = json.loads(read('validation/qa.json'))['metrics']['checks']
    if not checks or not all(item['result'] == 'pass' for item in checks):
        raise ValueError('Runtime bundle requires existing passing QA')


def pack(data: Path, output: Path) -> str:
    names = sorted(REQUIRED | VALIDATION)
    for name in names:
        if not (data / name).is_file():
            raise ValueError(f'Missing runtime artifact: {name}')
    validate_saved_outputs(lambda name: (data / name).read_bytes())
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as package:
        for name in names:
            entry = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            package.writestr(entry, (data / name).read_bytes())
    return hashlib.sha256(output.read_bytes()).hexdigest()


def validate_archive(archive: Path) -> tuple[str, ...]:
    """Validate either supported runtime layout without extracting or changing any files."""
    if archive.stat().st_size > MAX_BYTES:
        raise ValueError('Runtime archive is too large')
    with zipfile.ZipFile(archive) as package:
        names = package.namelist()
        if len(names) != len(set(names)) or set(names) not in (LEGACY_NAMES, REQUIRED | VALIDATION):
            raise ValueError('Runtime archive has missing, duplicate, or unexpected files')
        if sum(info.file_size for info in package.infolist()) > MAX_BYTES:
            raise ValueError('Expanded runtime archive is too large')
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or '..' in path.parts or '\\' in name:
                raise ValueError('Unsafe runtime archive path')
        validate_saved_outputs(package.read)
        return tuple(names)


def unpack(archive: Path, output: Path, expected_sha256: str) -> None:
    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected_sha256:
        raise ValueError('Runtime archive SHA256 mismatch')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Refusing to overwrite an existing runtime data directory')
    names = validate_archive(archive)
    with zipfile.ZipFile(archive) as package:
        # Exact allowlist above excludes traversal, symlinks, scripts and secrets.
        for name in names:
            target = output / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(package.read(name))


def fetch(manifest: Path, output: Path) -> None:
    config = json.loads(manifest.read_text(encoding='utf-8'))
    url = config['url']
    if not url.startswith('https://'):
        raise ValueError('Runtime download must use HTTPS')
    with tempfile.TemporaryDirectory(prefix='firesense-runtime-') as directory:
        archive = Path(directory) / 'runtime.zip'
        with urllib.request.urlopen(url, timeout=120) as response, archive.open('wb') as stream:
            total = 0
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_BYTES:
                    raise ValueError('Runtime download is too large')
                stream.write(chunk)
        unpack(archive, output, config['sha256'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['pack', 'fetch'])
    parser.add_argument('--data', type=Path, default=ROOT / 'data/processed')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--manifest', type=Path, default=ROOT / 'deployment/runtime.json')
    args = parser.parse_args()
    if args.action == 'pack':
        output = args.output or ROOT / 'share/firesense-runtime.zip'
        digest = pack(args.data, output)
        print(f'Runtime ZIP: {output}\nSHA256: {digest}')
    else:
        output = args.output or ROOT / 'data/processed'
        fetch(args.manifest, output)
        print(f'Validated runtime data installed: {output}')


if __name__ == '__main__':
    main()
