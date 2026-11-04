#!/usr/bin/env bash
# CUDA-first Windows/Linux parity; --ui-only also supports macOS development.
set -euo pipefail
cd "$(dirname "$0")/.."
args=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --ui-only|--allow-compatible) args+=("$1"); shift ;;
    --gpu-id|--threads) [ "$#" -ge 2 ] || { echo "Missing value for $1" >&2; exit 2; }; args+=("$1" "$2"); shift 2 ;;
    --no-pipeline|--cuda) shift ;; # Compatibility: CUDA is default, setup never trains.
    --quick) echo 'Setup no longer trains; use workflow.py train --quick.'; shift ;;
    --help|-h) echo 'Usage: bash scripts/setup.sh [--ui-only] [--allow-compatible] [--gpu-id N] [--threads N]'; exit 0 ;;
    *) echo "Unknown setup option: $1" >&2; exit 2 ;;
  esac
done
if [ ! -x .venv/bin/python ]; then
  [ ! -d .venv ] || { echo '.venv exists but has no Linux/macOS Python. Rename it before recreating it on this OS.' >&2; exit 1; }
  task_python=''
  for candidate in python3.11 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; sys.exit(0 if sys.version_info[:2] == (3, 11) else 1)' 2>/dev/null; then task_python="$candidate"; break; fi
  done
  [ -n "$task_python" ] || { echo 'Install 64-bit Python 3.11 (and python3.11-venv on Debian/Ubuntu).' >&2; exit 1; }
  "$task_python" -m venv .venv
fi
exec .venv/bin/python scripts/bootstrap.py "${args[@]}"
