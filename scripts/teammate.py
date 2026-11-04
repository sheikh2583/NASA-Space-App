"""Input ZIP transport and human-operated full training/return handoff."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.runtime_bundle import pack as pack_runtime

FIXED = {'data/raw/boundaries/BGD_ADM1.geojson', 'data/raw/boundaries/IND_ADM1.geojson',
         'data/interim/monazir/weather_BD.parquet', 'data/interim/monazir/weather_PB.parquet'}
MAX_INPUT_BYTES = 20 * 1024**3


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def allowed_input(name):
    path = PurePosixPath(name)
    if '\\' in name or path.is_absolute() or '..' in path.parts:
        return False
    if name in FIXED:
        return True
    if path.parent.as_posix() == 'data/raw/firms':
        return not path.name.startswith('synthetic_') and path.name.endswith(('.csv', '.csv.gz'))
    return path.parent.as_posix() == 'data/raw/landcover' and path.name.startswith('MCD12C1') and path.suffix == '.hdf'


def require_inputs(names):
    if not FIXED.issubset(names) or not any(n.startswith('data/raw/firms/') for n in names) or not any(n.startswith('data/raw/landcover/') for n in names):
        raise ValueError('Input ZIP needs FIRMS CSVs, both boundaries, original land cover, and both weather Parquets')


def pack_inputs(root, output):
    paths = [p for folder in ('data/raw/firms', 'data/raw/boundaries', 'data/raw/landcover', 'data/interim/monazir')
             for p in (root / folder).glob('*') if p.is_file() and allowed_input(p.relative_to(root).as_posix())]
    require_inputs({p.relative_to(root).as_posix() for p in paths})
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = {'schema_version': 1, 'files': {}}
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
        for path in sorted(paths):
            name = path.relative_to(root).as_posix()
            print('Packing', name, flush=True)
            sha = hashlib.sha256()
            size = 0
            with path.open('rb') as source, archive.open(name, 'w', force_zip64=True) as target:
                while chunk := source.read(1024 * 1024):
                    target.write(chunk); sha.update(chunk); size += len(chunk)
            manifest['files'][name] = {'sha256': sha.hexdigest(), 'bytes': size}
        archive.writestr('training-inputs.json', json.dumps(manifest, indent=2))
    output.with_suffix('.zip.sha256').write_text(digest(output) + '\n', encoding='utf-8')
    return output


def import_inputs(root, archive_path):
    with zipfile.ZipFile(archive_path) as archive:
        if 'training-inputs.json' not in archive.namelist():
            raise ValueError('Use the FireSense training-inputs ZIP from Sheikh, not the Render ZIP or individual NASA ZIPs')
        manifest = json.loads(archive.read('training-inputs.json'))
        if manifest.get('schema_version') != 1:
            raise ValueError('Unsupported input ZIP version')
        files = manifest['files']
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(files) | {'training-inputs.json'} or not all(allowed_input(n) for n in files):
            raise ValueError('Unexpected, duplicate, or unsafe files in input ZIP')
        require_inputs(set(files))
        total = sum(archive.getinfo(name).file_size for name in files)
        if total > MAX_INPUT_BYTES:
            raise ValueError('Input ZIP exceeds 20 GiB expanded limit')
        needed = 0
        for name, info in files.items():
            target = root / name
            if not target.resolve().is_relative_to(root.resolve()):
                raise ValueError('Input path escapes checkout')
            if info['bytes'] != archive.getinfo(name).file_size:
                raise ValueError('Input size manifest mismatch')
            if target.exists():
                if digest(target) != info['sha256']:
                    raise ValueError(f'Existing input differs: {name}. Use a fresh checkout; no overwrite performed.')
            else:
                needed += info['bytes']
        if shutil.disk_usage(root).free < needed + 5 * 1024**3:
            raise ValueError('Free more space: extracted inputs plus 5 GiB working space are required')
        for name, info in files.items():
            target = root / name
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(name) as source, target.open('xb') as destination:
                sha = hashlib.sha256()
                while chunk := source.read(1024 * 1024):
                    destination.write(chunk); sha.update(chunk)
            if sha.hexdigest() != info['sha256']:
                target.unlink()  # only the just-created, verified in-checkout path
                raise ValueError(f'Input checksum mismatch: {name}')
        return manifest


def full_report(path):
    report = json.loads(path.read_text(encoding='utf-8'))
    if report.get('status') != 'passed' or report.get('quick') is not False or report.get('start_stage') is not None:
        raise ValueError('Deliverable requires a newly completed full run, not a quick/failed/resumed run')
    return report


def run_logged(root, command, log):
    with log.open('a', encoding='utf-8') as output:
        output.write('+ ' + ' '.join(command) + '\n'); output.flush()
        with subprocess.Popen(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, encoding='utf-8', errors='replace', bufsize=1) as process:
            for line in process.stdout:
                print(line, end='', flush=True); output.write(line); output.flush()
            if process.wait() != 0:
                raise RuntimeError(f'Command failed; stop and send this log to Sheikh: {log}')


def run_human(root, name, gpu_id, threads):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,40}', name):
        raise ValueError('Use a short teammate label with letters, digits, hyphens or underscores')
    archives = sorted((root / 'data/incoming').glob('*.zip'))
    if len(archives) != 1:
        raise ValueError('Put exactly one FireSense training-inputs ZIP in data/incoming/')
    inputs = import_inputs(root, archives[0])
    label = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + name
    log = root / f'results/logs/teammate-{label}.log'; log.parent.mkdir(parents=True, exist_ok=True)
    before = set((root / 'results/runs').glob('*/execution.json'))
    git_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    run_logged(root, [sys.executable, '-u', 'scripts/workflow.py', 'train', '--backend', 'cuda',
                      '--gpu-id', str(gpu_id), '--threads', str(threads)], log)
    reports = set((root / 'results/runs').glob('*/execution.json')) - before
    if len(reports) != 1:
        raise RuntimeError('Cannot identify a single new full run; do not run parallel pipelines')
    report_path = reports.pop()
    full_report(report_path)
    method = json.loads((root / 'data/interim/sheikh/method.json').read_text())
    if method.get('compute_backend') != 'cuda':
        raise ValueError('Expected CUDA model evaluation in the completed run')
    runtime = root / f'share/runtime-{label}.zip'
    runtime_sha = pack_runtime(root / 'data/processed', runtime)
    handoff = {'teammate': name, 'git_commit': git_sha, 'gpu_id': gpu_id, 'threads': threads,
               'python': sys.version, 'platform': platform.platform(), 'input_zip_sha256': digest(archives[0]),
               'runtime_sha256': runtime_sha, 'full_run': report_path.parent.name,
               'packages': sorted((d.metadata['Name'], d.version) for d in metadata.distributions() if d.metadata['Name'])}
    gpu = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader'],
                         capture_output=True, text=True)
    handoff['gpu_info'] = gpu.stdout.strip()
    files = [p for p in (root / 'data/processed').rglob('*') if p.is_file() and p.suffix in {'.parquet', '.json'}]
    files += [p for p in (root / 'data/interim/sheikh').glob('*') if p.is_file() and p.name in {
        'method.json', 'metrics.csv', 'b1_params.pkl', 'panel.parquet', 'xgb_count.ubj', 'xgb_frp.ubj', 'xgb_metadata.json'}]
    files += [p for p in report_path.parent.glob('*') if p.is_file() and p.suffix in {'.json', '.jsonl'}]
    files += [root / 'results/latest.md', root / 'results/latest.json', log]
    destination = root / f'share/firesense-deliverable-{label}.zip'
    with zipfile.ZipFile(destination, 'x', zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
        for path in sorted(files):
            archive.write(path, path.relative_to(root).as_posix())
        archive.write(runtime, 'runtime/firesense-runtime.zip')
        archive.writestr('handoff.json', json.dumps(handoff, indent=2))
        archive.writestr('training-inputs.json', json.dumps(inputs, indent=2))
    destination.with_suffix('.zip.sha256').write_text(digest(destination) + '\n', encoding='utf-8')
    print(f'\nSEND TO SHEIKH: {destination}\nCHECKSUM: {destination}.sha256', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['pack-inputs', 'import-inputs', 'run'])
    parser.add_argument('--name', default='teammate')
    parser.add_argument('--gpu-id', type=int, default=0)
    parser.add_argument('--threads', type=int, default=8)
    parser.add_argument('--human-run', action='store_true')
    args = parser.parse_args()
    if args.gpu_id < 0 or args.threads < 1:
        parser.error('GPU ID must be nonnegative and threads positive')
    if args.action == 'pack-inputs':
        print('INPUT ZIP:', pack_inputs(ROOT, ROOT / 'share/firesense-training-inputs.zip'))
    elif args.action == 'import-inputs':
        archives = sorted((ROOT / 'data/incoming').glob('*.zip'))
        if len(archives) != 1:
            parser.error('Put exactly one FireSense training-inputs ZIP in data/incoming/')
        import_inputs(ROOT, archives[0]); print('Inputs verified and imported')
    elif not args.human_run:
        parser.error('Training is human-operated only; --human-run is required')
    else:
        run_human(ROOT, args.name, args.gpu_id, args.threads)


if __name__ == '__main__':
    main()
