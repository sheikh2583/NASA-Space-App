#!/usr/bin/env bash
# HUMAN ONLY: setup performs fitting probes; the next command performs full training.
set -euo pipefail
cd "$(dirname "$0")/.."
name=''
gpu_id=0
threads=8
python_args=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --name|--gpu-id|--threads|--python)
      [ "$#" -ge 2 ] || { echo "Missing value for $1" >&2; exit 2; }
      case "$1" in
        --name) name="$2" ;;
        --gpu-id) gpu_id="$2" ;;
        --threads) threads="$2" ;;
        --python) python_args=(--python "$2") ;;
      esac
      shift 2 ;;
    *) echo 'Usage: bash scripts/teammate_train.sh --name SAMIN [--gpu-id 0] [--threads 8] [--python /path/to/python3.11]' >&2; exit 2 ;;
  esac
done
[[ "$name" =~ ^[A-Za-z0-9_-]{1,40}$ ]] || { echo 'Provide --name with a short teammate label.' >&2; exit 2; }
shopt -s nullglob
archives=(data/incoming/*.zip)
[ "${#archives[@]}" -eq 1 ] || { echo 'First put the single FireSense training-inputs ZIP from Sheikh in data/incoming/.' >&2; exit 1; }
bash scripts/setup.sh --training-only --gpu-id "$gpu_id" --threads "$threads" "${python_args[@]}"
exec .venv/bin/python -u scripts/teammate.py run --human-run --name "$name" --gpu-id "$gpu_id" --threads "$threads"
