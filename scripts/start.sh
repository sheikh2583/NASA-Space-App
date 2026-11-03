#!/usr/bin/env bash
# Start the API (port 8000) and the web app (port 5173). Ctrl+C stops both.  bash scripts/start.sh [--mock]
set -euo pipefail
cd "$(dirname "$0")/.."
. .venv/bin/activate
export PYTHONPATH="$PWD"
if [ "${1:-}" = "--mock" ]; then
  echo "Mock API (contracts/fixtures) on http://localhost:8000"
  uvicorn ws2_platform.api.mock_server:app --port 8000 & API=$!
else
  [ -f data/processed/harmonized.parquet ] || { echo "No data/processed yet: run bash scripts/setup.sh (or start with --mock)."; exit 1; }
  echo "API on http://localhost:8000  (docs: http://localhost:8000/docs)"
  DATA_DIR=data/processed uvicorn ws2_platform.api.app:app --port 8000 & API=$!
fi
trap 'kill $API 2>/dev/null' EXIT
(cd ws5_frontend && npm run dev)
