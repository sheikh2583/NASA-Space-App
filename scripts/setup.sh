#!/usr/bin/env bash
# CUDA-first Windows/Linux parity; --ui-only also supports macOS development.
set -euo pipefail
cd "$(dirname "$0")/.."
args=()
task_python=''
while [ "$#" -gt 0 ]; do
  case "$1" in
    --ui-only|--training-only|--allow-compatible) args+=("$1"); shift ;;
    --gpu-id|--threads) [ "$#" -ge 2 ] || { echo "Missing value for $1" >&2; exit 2; }; args+=("$1" "$2"); shift 2 ;;
    --python) [ "$#" -ge 2 ] && [ -n "$2" ] || { echo 'Missing interpreter path for --python' >&2; exit 2; }; task_python="$2"; shift 2 ;;
    --no-pipeline|--cuda) shift ;; # Compatibility: CUDA is default, setup never trains.
    --quick) echo 'Setup no longer trains; use workflow.py train --quick.'; shift ;;
    --help|-h) echo 'Usage: bash scripts/setup.sh [--ui-only | --training-only] [--python PATH] [--allow-compatible] [--gpu-id N] [--threads N]'; exit 0 ;;
    *) echo "Unknown setup option: $1" >&2; exit 2 ;;
  esac
done
case "$(uname -s)" in
  Linux|Darwin) ;;
  *) echo 'Use scripts/setup.ps1 from Windows PowerShell; use setup.sh on native Linux/macOS or WSL with its own Linux environment.' >&2; exit 1 ;;
esac
if [ ! -x .venv/bin/python ]; then
  [ ! -d .venv ] || { echo '.venv exists but has no Linux/macOS Python. Rename it before recreating it on this OS.' >&2; exit 1; }
  if [ -z "$task_python" ]; then
    for candidate in python3.11 python3 python; do
      if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import struct,sys; sys.exit(0 if sys.version_info[:2] == (3, 11) and struct.calcsize("P") == 8 else 1)' 2>/dev/null; then task_python="$candidate"; break; fi
    done
    if [ -z "$task_python" ] && command -v uv >/dev/null 2>&1; then
      task_python="$(uv python find --system 3.11 2>/dev/null || true)"
    fi
  fi
  [ -n "$task_python" ] || { echo 'Install 64-bit Python 3.11. With uv: uv python install 3.11; bash scripts/setup.sh --training-only --python "$(uv python find --system 3.11)". See docs/TEAM_TRAINING.md.' >&2; exit 1; }
  "$task_python" -c 'import struct,sys; sys.exit(0 if sys.version_info[:2] == (3, 11) and struct.calcsize("P") == 8 else 1)' || { echo '--python must select a working 64-bit Python 3.11 executable.' >&2; exit 1; }
  "$task_python" -m venv .venv || { echo 'Could not create .venv. Install the matching venv package (for distro Python) or use uv-managed Python 3.11.' >&2; exit 1; }
fi
exec .venv/bin/python scripts/bootstrap.py "${args[@]}"
