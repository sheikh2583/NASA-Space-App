#!/usr/bin/env bash
# Bring your branch up to date with main:  bash scripts/git/sync.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"; source scripts/git/_lib.sh
git fetch origin
if [ "$(current_branch)" = "main" ]; then
  git pull --rebase origin main
else
  if ! git rebase origin/main; then
    echo; echo "Conflict. Edit the files marked <<<<<<<, then:  git add <file>  and  git rebase --continue"
    echo "To give up:  git rebase --abort   (then ask Sheikh)"; exit 1
  fi
fi
git status -sb
