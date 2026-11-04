#!/usr/bin/env bash
# One-time setup on Linux or macOS:  bash scripts/setup.sh [--quick] [--no-pipeline]
#   1. checks git, Python 3.11 and Node; 2. creates .venv and installs the pinned packages;
#   3. installs the web app; 4. runs the pipeline on synthetic data (unless --no-pipeline).
set -euo pipefail
cd "$(dirname "$0")/.."
QUICK=""; RUN=1
for a in "$@"; do case "$a" in --quick) QUICK="--quick";; --no-pipeline) RUN=0;; esac; done

say() { printf '\n== %s\n' "$*"; }
need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing $1. $2"; exit 1; }; }

say "Checking tools"
PY=""
for c in python3.11 python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info[:2] == (3, 11) else 1)' 2>/dev/null; then PY="$c"; break; fi
done
[ -n "$PY" ] || { echo "Python 3.11 not found. Install it (python.org, pyenv, or your package manager) and rerun."; exit 1; }
need node "Install Node.js LTS (https://nodejs.org) and rerun."
need npm "Install Node.js LTS (it includes npm)."
echo "$($PY --version), node $(node --version)"

say "Python environment (.venv)"
[ -d .venv ] || "$PY" -m venv .venv
. .venv/bin/activate
python -m pip install -q --upgrade pip
if ! python -m pip install -q -r requirements.lock.txt; then
  echo "Pinned install failed on this platform; trying requirements.txt (newest compatible versions)."
  python -m pip install -q -r requirements.txt
fi
python -c "import pandas, pyarrow, duckdb, lightgbm, geopandas, fastapi, pyhdf; print('imports OK')"

say "Web app (ws5_frontend)"
[ -f ws5_frontend/.env ] || cp ws5_frontend/.env.example ws5_frontend/.env
(cd ws5_frontend && npm ci --no-audit --no-fund)
[ -f .env ] || cp .env.example .env

if [ "$RUN" = 1 ]; then
  say "Pipeline on synthetic data (real FIRMS files in data/raw/firms are used instead when present)"
  python scripts/run_pipeline.py $QUICK
fi

say "Done"
echo "Start the API and the web app:   bash scripts/start.sh"
echo "Run all tests:                   . .venv/bin/activate && python -m pytest -q"
echo "Push to GitHub (Sheikh only):    bash scripts/push_to_github.sh"
