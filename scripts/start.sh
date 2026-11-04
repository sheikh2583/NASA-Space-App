#!/usr/bin/env bash
# Start the API (port 8000) and the web app (port 5173), then open the browser. Ctrl+C stops both.
#   bash scripts/start.sh          trained data from data/processed/
#   bash scripts/start.sh --mock   bundled fixtures; no data or GPU needed
set -euo pipefail
cd "$(dirname "$0")/.."
args=(dev --open)
case "${1:-}" in
  '') ;;
  --mock) args+=(--mock) ;;
  -h|--help) sed -n '2,4p' "$0"; exit 0 ;;
  *) echo "Unknown option: $1 (use --mock or nothing)" >&2; exit 2 ;;
esac
[ -x .venv/bin/python ] || { echo 'No .venv yet. Run first: bash scripts/setup.sh --ui-only' >&2; exit 1; }
exec .venv/bin/python scripts/workflow.py "${args[@]}"
