#!/usr/bin/env bash
# After your PR is merged:  bash scripts/git/cleanup.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"; source scripts/git/_lib.sh
git fetch -p origin
git switch main 2>/dev/null || git checkout main
git pull --rebase origin main
git branch -vv | awk '/: gone]/{print $1}' | xargs -r git branch -D
echo "Clean. Start the next piece:  bash scripts/git/start.sh <topic>"
