#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
action="${1:-menu}"
if [ "$action" = menu ]; then
  printf 'FireSense\n1 Setup CPU\n2 Prepare CUDA inputs\n3 Smoke + UI build\n4 Quick CUDA training\n5 Full CUDA training\n6 Open trained UI\n7 Mock UI\n8 Results\n9 Share ZIP\n10 Full CUDA pipeline + tests + build\n11 Setup CUDA\n12 GPU check\n13 Full CPU training\n0 Exit\n'
  read -r -p 'Choose: ' choice
  case "$choice" in
    1) action=setup;; 2) action=prepare;; 3) action=smoke;; 4) action=quick;;
    5) action=train;; 6) action=dev;; 7) action=mock;; 8) action=results;;
    9) action=share;; 10) action=all;; 11) action=setup-cuda;; 12) action=gpu-check;; 13) action=cpu-train;; 0) exit 0;; *) echo 'Unknown choice'; exit 1;;
  esac
fi
if [ "$action" = setup ]; then bash scripts/setup.sh --no-pipeline; exit; fi
if [ "$action" = setup-cuda ]; then bash scripts/setup.sh --no-pipeline --cuda; exit; fi
[ -x .venv/bin/python ] || { echo 'Run setup first.'; exit 1; }
mkdir -p results/logs
args=("$action")
case "$action" in quick) args=(train --quick);; cpu-train) args=(train --backend cpu);; dev) args=(dev --open);; mock) args=(dev --mock --open);; esac
.venv/bin/python scripts/workflow.py "${args[@]}" 2>&1 | tee "results/logs/${action}-$(date +%Y%m%d-%H%M%S).log"
