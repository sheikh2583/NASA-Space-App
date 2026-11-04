#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
workflow="${1:-setup}"
if [ "$#" -gt 0 ]; then shift; fi
if [ "$workflow" = setup ]; then exec bash scripts/setup.sh "$@"; fi
if [ ! -x .venv/bin/python ]; then
  case "$workflow" in smoke|dev|test|build|share) bash scripts/setup.sh --ui-only ;; *) bash scripts/setup.sh ;; esac
fi
exec .venv/bin/python scripts/workflow.py "$workflow" "$@"
