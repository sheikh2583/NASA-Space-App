"""Shared dependency setup for Windows/Linux; never starts a data pipeline."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    print('+ ' + ' '.join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ui-only', action='store_true', help='Install development/API dependencies without requiring NVIDIA CUDA')
    parser.add_argument('--allow-compatible', action='store_true', help='Explicitly allow unpinned base dependencies if the lockfile fails')
    parser.add_argument('--gpu-id', type=int, default=0)
    parser.add_argument('--threads', type=int, default=8)
    args = parser.parse_args(argv)
    if args.gpu_id < 0 or args.threads < 1:
        raise RuntimeError('GPU ID must be nonnegative and helper threads must be positive.')
    if sys.version_info[:2] != (3, 11) or platform.architecture()[0] != '64bit':
        raise RuntimeError('Use 64-bit Python 3.11. Recreate .venv if it belongs to another Python version or OS.')
    if sys.prefix == sys.base_prefix:
        raise RuntimeError('Run the platform setup script to create .venv first.')
    npm = shutil.which('npm.cmd' if os.name == 'nt' else 'npm')
    if not npm or not shutil.which('node'):
        raise RuntimeError('Install Node.js 22 with npm, reopen the terminal, and rerun setup.')
    node = subprocess.check_output(['node', '--version'], text=True).strip()
    if tuple(map(int, node.lstrip('v').split('.')[:2])) < (22, 12):
        raise RuntimeError(f'Node.js 22.12 or newer is required; found {node}. CI uses Node.js 22.')
    with socket.socket() as probe:
        if probe.connect_ex(('127.0.0.1', 5173)) == 0:
            raise RuntimeError('Stop the Vite development server on port 5173 (Ctrl+C), then rerun setup. Windows locks native npm modules while Vite is running.')
    if not args.ui_only:
        if sys.platform not in {'win32', 'linux'}:
            raise RuntimeError('CUDA training requires NVIDIA Windows/Linux. Use --ui-only for development on this OS.')
        if not shutil.which('nvidia-smi'):
            raise RuntimeError('NVIDIA driver/nvidia-smi is missing. Install the driver, or use --ui-only for UI development.')
        run('nvidia-smi', '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader')
    run(sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip')
    manifest = 'requirements.lock.txt' if args.ui_only else 'requirements-cuda.txt'
    try:
        run(sys.executable, '-m', 'pip', 'install', '-r', manifest)
    except subprocess.CalledProcessError:
        if not args.allow_compatible:
            raise RuntimeError('Pinned dependency installation failed. Resolve the error above; explicitly pass --allow-compatible only if compatible unpinned dependencies are acceptable.') from None
        print('Using explicitly authorized compatible base dependencies; this environment is not lockfile-reproducible.', flush=True)
        run(sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt')
        if not args.ui_only:
            run(sys.executable, '-m', 'pip', 'install', 'xgboost==3.2.0')
    run(sys.executable, '-m', 'pip', 'check')
    run(sys.executable, '-c', 'import pandas, pyarrow, duckdb, lightgbm, geopandas, fastapi, pyhdf, rasterio; print("Scientific/API imports OK")')
    if not args.ui_only:
        run(sys.executable, 'scripts/workflow.py', 'gpu-check', '--gpu-id', str(args.gpu_id), '--threads', str(args.threads))
    for name in ('.env', 'ws5_frontend/.env'):
        target = ROOT / name
        if not target.exists():
            shutil.copyfile(str(target) + '.example', target)
    try:
        run(npm, 'ci', '--prefix', 'ws5_frontend', '--no-audit', '--no-fund')
    except subprocess.CalledProcessError:
        raise RuntimeError('npm installation failed. For EPERM/EBUSY, stop this project\'s Vite/test/preview processes and retry; also inspect antivirus/file permissions. Do not delete unrelated Node processes.') from None
    for name in ('data/raw/firms', 'data/raw/boundaries', 'data/raw/landcover', 'data/raw/power', 'results/logs'):
        (ROOT / name).mkdir(parents=True, exist_ok=True)
    print('SETUP COMPLETE. No datasets were downloaded and no pipeline outputs were changed.', flush=True)
    print(f'Next: {sys.executable} scripts/workflow.py dev --mock --open', flush=True)
    if not args.ui_only:
        print(f'Training readiness: {sys.executable} scripts/workflow.py prepare --backend cuda', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f'SETUP FAILED: {error}', file=sys.stderr)
        sys.exit(1)
