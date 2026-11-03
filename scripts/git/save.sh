#!/usr/bin/env bash
# Commit your work:  bash scripts/git/save.sh "what you did"
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"; source scripts/git/_lib.sh
msg="${1:?usage: bash scripts/git/save.sh \"what you did\"}"
not_on_main
git add -A
git commit -m "[$(my_prefix)] $msg"
echo "Saved. When a piece passes its test:  bash scripts/git/ship.sh"
