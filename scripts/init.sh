#!/usr/bin/env bash
# Bootstrap Linux/macOS, then run any project workflow.
set -euo pipefail
cd "$(dirname "$0")/.."
workflow="${1:-setup}"
shift || true
bash scripts/setup.sh --no-pipeline
[ "$workflow" = setup ] || .venv/bin/python scripts/workflow.py "$workflow" "$@"
