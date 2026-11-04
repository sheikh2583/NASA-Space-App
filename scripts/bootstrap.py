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


def check_linux_runtime() -> None:
    """Fail with actionable host errors before downloading training packages."""
    if sys.platform != 'linux':
        return
    if platform.machine().lower() not in {'x86_64', 'amd64'}:
        raise RuntimeError('The supported Linux training environment is x86_64. ARM/Jetson is not verified by this lockfile.')
    libc, version = platform.libc_ver()
    if libc != 'glibc' or not version:
        raise RuntimeError('Linux training requires glibc 2.28+; musl/Alpine is not supported by this wheel-based setup.')
    if tuple(map(int, version.split('.')[:2])) < (2, 28):
        raise RuntimeError(f'Linux training requires glibc 2.28+; found {version}. Use a supported modern Linux distribution.')
    import ctypes
    try:
        ctypes.CDLL('libgomp.so.1')
    except OSError as error:
        raise RuntimeError('Missing Linux OpenMP runtime. On Debian/Ubuntu: sudo apt-get install libgomp1. See docs/guides/setup.md.') from error


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ui-only', action='store_true', help='Install development/API dependencies without requiring NVIDIA CUDA')
    parser.add_argument('--training-only', action='store_true', help='Install and verify CUDA training dependencies without Node/npm or frontend changes')
    parser.add_argument('--allow-compatible', action='store_true', help='Explicitly allow unpinned base dependencies if the lockfile fails')
    parser.add_argument('--gpu-id', type=int, default=0)
    parser.add_argument('--threads', type=int, default=8)
    args = parser.parse_args(argv)
    if args.ui_only and args.training_only:
        raise RuntimeError('--ui-only and --training-only select different setup modes; choose one.')
    if args.gpu_id < 0 or args.threads < 1:
        raise RuntimeError('GPU ID must be nonnegative and helper threads must be positive.')
    if sys.version_info[:2] != (3, 11) or platform.architecture()[0] != '64bit':
        raise RuntimeError('Use 64-bit Python 3.11. Recreate .venv if it belongs to another Python version or OS.')
    if sys.prefix == sys.base_prefix:
        raise RuntimeError('Run the platform setup script to create .venv first.')
    npm = None
    if not args.training_only:
        npm = shutil.which('npm.cmd' if os.name == 'nt' else 'npm')
        if not npm or not shutil.which('node'):
            raise RuntimeError('Install Node.js 22.12+ with npm, reopen the terminal, and rerun setup.')
        node = subprocess.check_output(['node', '--version'], text=True).strip()
        if tuple(map(int, node.lstrip('v').split('.')[:2])) < (22, 12):
            raise RuntimeError(f'Node.js 22.12 or newer is required; found {node}. CI uses Node.js 22.')
        for port, server in ((5173, 'development'), (4173, 'preview')):
            with socket.socket() as probe:
                if probe.connect_ex(('127.0.0.1', port)) == 0:
                    raise RuntimeError(f'Stop the Vite {server} server on port {port} (Ctrl+C), then rerun setup. Windows locks native npm modules while Vite is running. Use --training-only to leave the frontend running.')
    if not args.ui_only:
        if sys.platform not in {'win32', 'linux'}:
            raise RuntimeError('CUDA training requires NVIDIA Windows/Linux. Use --ui-only for development on this OS.')
        check_linux_runtime()
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
    try:
        run(sys.executable, '-c', 'import pandas, pyarrow, duckdb, lightgbm, geopandas, fastapi, pyhdf, rasterio; print("Scientific/API imports OK")')
    except subprocess.CalledProcessError:
        raise RuntimeError('Scientific imports failed. Windows DLL errors may need Microsoft Visual C++ x64 Redistributable; Linux libgomp errors may need libgomp1. See docs/guides/training.md and the import error above.') from None
    if not args.ui_only:
        run(sys.executable, 'scripts/workflow.py', 'gpu-check', '--gpu-id', str(args.gpu_id), '--threads', str(args.threads))
    for name in (('.env',) if args.training_only else ('.env', 'ws5_frontend/.env')):
        target = ROOT / name
        if not target.exists():
            shutil.copyfile(str(target) + '.example', target)
    if npm:
        try:
            run(npm, 'ci', '--prefix', 'ws5_frontend', '--no-audit', '--no-fund')
        except subprocess.CalledProcessError:
            raise RuntimeError('npm installation failed. For EPERM/EBUSY, stop this project\'s Vite/test/preview processes and retry; also inspect antivirus/file permissions. Do not delete unrelated Node processes.') from None
    for name in ('data/raw/firms', 'data/raw/boundaries', 'data/raw/landcover', 'data/raw/power', 'results/logs'):
        (ROOT / name).mkdir(parents=True, exist_ok=True)
    print('SETUP COMPLETE. No datasets were downloaded and no pipeline outputs were changed.', flush=True)
    if not args.training_only:
        print(f'Next: {sys.executable} scripts/workflow.py dev --mock --open', flush=True)
    if not args.ui_only:
        print(f'Training readiness: {sys.executable} scripts/workflow.py prepare --backend cuda', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f'SETUP FAILED: {error}', file=sys.stderr)
        sys.exit(1)
