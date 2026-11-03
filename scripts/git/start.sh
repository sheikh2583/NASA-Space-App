#!/usr/bin/env bash
# Start a branch from the latest main:  bash scripts/git/start.sh <topic>
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"; source scripts/git/_lib.sh
topic="${1:?usage: bash scripts/git/start.sh <topic>   (example: panel-builder)}"
p="$(my_prefix)"
git fetch origin
git switch main 2>/dev/null || git checkout main
git pull --rebase origin main
git switch -c "$p/$topic"
echo "On branch $p/$topic. Work only in: $(my_folder)/ (and files listed for you in scripts/team.csv)."
