#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
action="${1:-menu}"
if [ "$action" = menu ]; then
  printf 'FireSense\n1 Setup\n2 Prepare inputs\n3 Smoke + UI build\n4 Quick training\n5 Full training\n6 Open trained UI\n7 Mock UI\n8 Results\n9 Share ZIP\n10 Full pipeline + tests + build\n0 Exit\n'
  read -r -p 'Choose: ' choice
  case "$choice" in
    1) action=setup;; 2) action=prepare;; 3) action=smoke;; 4) action=quick;;
    5) action=train;; 6) action=dev;; 7) action=mock;; 8) action=results;;
    9) action=share;; 10) action=all;; 0) exit 0;; *) echo 'Unknown choice'; exit 1;;
  esac
fi
if [ "$action" = setup ]; then bash scripts/setup.sh --no-pipeline; exit; fi
[ -x .venv/bin/python ] || { echo 'Run setup first.'; exit 1; }
mkdir -p results/logs
args=("$action")
case "$action" in quick) args=(train --quick);; dev) args=(dev --open);; mock) args=(dev --mock --open);; esac
.venv/bin/python scripts/workflow.py "${args[@]}" 2>&1 | tee "results/logs/${action}-$(date +%Y%m%d-%H%M%S).log"
