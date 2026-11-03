#!/usr/bin/env bash
# Where am I?  bash scripts/git/status.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"; source scripts/git/_lib.sh
echo "You: $(my_name) ($(me)); prefix $(my_prefix)/; folder $(my_folder)/"
git fetch origin --quiet || true
echo "Branch: $(current_branch)"
git status -sb | head -20
echo "--- behind/ahead of origin/main:"; git rev-list --left-right --count origin/main...HEAD 2>/dev/null || true
echo "--- last 5 commits:"; git log --oneline -5
