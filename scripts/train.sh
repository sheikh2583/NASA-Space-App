#!/usr/bin/env bash
# HUMAN ONLY. Runs the whole CUDA training sequence on Linux, with logs:
#   setup (only if .venv is missing) -> weather cache (only if missing) -> readiness
#   -> quick training -> pause -> full training -> validate -> results [-> runtime ZIP]
# Coding agents must not run this script (AGENTS.md). Guide: docs/guides/training.md
set -euo pipefail
cd "$(dirname "$0")/.."

usage() {
  cat <<'EOF'
Usage: bash scripts/train.sh [options]

  --gpu-id N        CUDA device to use (default 0)
  --threads N       CPU helper threads (default 8)
  --quick-only      stop after the quick run
  --skip-quick      go straight to the full run
  --yes             don't pause between the quick and the full run
  --from STAGE      resume a failed run at STAGE (add --quick-only if that run was quick)
  --pack            after a full run, also build share/firesense-runtime.zip for deployment
  --python PATH     Python 3.11 to create .venv with (only used when .venv is missing)
  -h, --help        show this help
EOF
}

gpu_id=0; threads=8; quick_only=0; skip_quick=0; assume_yes=0; resume=''; pack=0; python_args=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --gpu-id|--threads|--from|--python)
      [ "$#" -ge 2 ] || { echo "Missing value for $1" >&2; exit 2; }
      case "$1" in
        --gpu-id) gpu_id="$2" ;; --threads) threads="$2" ;; --from) resume="$2" ;; --python) python_args=(--python "$2") ;;
      esac
      shift 2 ;;
    --quick-only) quick_only=1; shift ;;
    --skip-quick) skip_quick=1; shift ;;
    --yes|-y) assume_yes=1; shift ;;
    --pack) pack=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ "$gpu_id" =~ ^[0-9]+$ ]] || { echo '--gpu-id must be a number' >&2; exit 2; }
[[ "$threads" =~ ^[1-9][0-9]*$ ]] || { echo '--threads must be a positive number' >&2; exit 2; }
[ "$quick_only" -eq 0 ] || [ "$skip_quick" -eq 0 ] || { echo 'Choose --quick-only or --skip-quick, not both.' >&2; exit 2; }

step() { printf '\n\033[1;36m==> %s\033[0m\n' "$1"; }
die() { printf '\n\033[1;31mSTOPPED: %s\033[0m\n' "$1" >&2; exit 1; }

command -v nvidia-smi >/dev/null 2>&1 || die 'nvidia-smi not found. Install the NVIDIA driver, reboot, then rerun.'
nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader || die 'nvidia-smi failed. Fix the NVIDIA driver first.'

py=.venv/bin/python
if [ ! -x "$py" ]; then
  step 'Setting up the training environment (first run only)'
  bash scripts/setup.sh --training-only --gpu-id "$gpu_id" --threads "$threads" "${python_args[@]}" || die 'Setup failed. Fix the first error above, then rerun.'
fi

mkdir -p results/logs
label="$(date +%Y%m%d-%H%M%S)"
common=(--backend cuda --gpu-id "$gpu_id" --threads "$threads")

# Runs a Python step, mirrors its output into results/logs/<label>-<name>.log, and stops on failure.
run_logged() {
  local name="$1"; shift
  local log="results/logs/${label}-${name}.log"
  "$py" -u "$@" 2>&1 | tee "$log" || die "$name failed. Log: $log"
}

if [ ! -s data/interim/monazir/weather_BD.parquet ] || [ ! -s data/interim/monazir/weather_PB.parquet ]; then
  step 'Building the NASA POWER weather cache (first run only, 20-40 minutes, resumable)'
  run_logged weather -m ws3_anomaly.loaders.weather --start 2000-11-01 --end 2026-11-03
fi

step 'Checking that inputs and CUDA are ready'
run_logged prepare scripts/workflow.py prepare --gpu-id "$gpu_id" --threads "$threads"

if [ -n "$resume" ]; then
  extra=(); [ "$quick_only" -eq 1 ] && extra=(--quick)
  step "Resuming training at stage '$resume'"
  run_logged "resume-$resume" scripts/workflow.py train "${common[@]}" --from "$resume" "${extra[@]}"
else
  if [ "$skip_quick" -eq 0 ]; then
    step 'Quick training (reduced holdouts)'
    run_logged quick scripts/workflow.py train "${common[@]}" --quick
    if [ "$quick_only" -eq 1 ]; then
      run_logged results scripts/workflow.py results
      step 'Quick run finished. Read results/latest.md. Run again with --skip-quick for the full run.'
      exit 0
    fi
    if [ "$assume_yes" -eq 0 ]; then
      printf '\nQuick run passed. Check results/latest.md now.\nPress Enter to start the FULL run, or Ctrl+C to stop here: '
      read -r _
    fi
  fi
  step 'Full training (all six holdouts, both satellite-input configurations)'
  run_logged full scripts/workflow.py train "${common[@]}"
fi

step 'Scientific QA'
run_logged validate scripts/workflow.py validate
step 'Results summary'
run_logged results scripts/workflow.py results

if [ "$pack" -eq 1 ]; then
  [ "$quick_only" -eq 0 ] || die '--pack needs a full run, not a quick one.'
  step 'Packing the runtime ZIP for deployment'
  run_logged pack scripts/runtime_bundle.py pack
fi

step 'Done'
latest="$(ls -td results/runs/*/ 2>/dev/null | head -1 || true)"
echo "Summary:          results/latest.md"
echo "Execution report: ${latest:-results/runs/<timestamp>/}execution.json"
echo "Logs:             results/logs/${label}-*.log"
echo 'Accept the run only if execution.json says status: passed, quick: false, start_stage: null (docs/guides/training.md).'
