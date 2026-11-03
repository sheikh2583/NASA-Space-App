#!/usr/bin/env bash
# Run once after cloning:  bash scripts/git/setup.sh <your-github-username>
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
user="${1:-}"
[ -n "$user" ] || { echo "usage: bash scripts/git/setup.sh <your-github-username>"; exit 1; }
source scripts/git/_lib.sh
[ -n "$(field "$user" 1)" ] || { echo "'$user' is not in scripts/team.csv"; exit 1; }
echo "$user" > "$ME_FILE"
git config pull.rebase true
git config rebase.autoStash true
git config push.autoSetupRemote true
git config fetch.prune true
git config core.hooksPath scripts/git/hooks
chmod +x scripts/git/*.sh scripts/git/hooks/* 2>/dev/null || true
echo "Ready: $(my_name), branch prefix '$(my_prefix)/', your folder '$(my_folder)/'."
git config user.name  >/dev/null || echo "Next: git config --global user.name 'Your Name'"
git config user.email >/dev/null || echo "Next: git config --global user.email 'the email on your GitHub account'"
echo "Daily loop: start.sh <topic> -> (work) -> save.sh \"message\" -> ship.sh   (docs/GIT_WORKFLOW.md)"
