#!/usr/bin/env bash
# SHEIKH ONLY, once: push this folder's prepared history (one commit per workstream) to the empty GitHub repo.
#   bash scripts/push_to_github.sh
# Needs: git, and you signed in to GitHub on this computer (gh auth login, or Git Credential Manager).
# It never force-pushes: if the repo already has commits it stops and tells you what to do.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/config.sh
echo "Repo: $REPO_URL"
git rev-parse --git-dir >/dev/null 2>&1 || { echo "This folder has no .git history. Unzip the full package again."; exit 1; }
[ "$(git branch --show-current)" = "main" ] || git switch main

echo; echo "Commits to push (author = workstream owner):"
git log --format='  %h  %an  %s' main

if git remote get-url origin >/dev/null 2>&1; then git remote set-url origin "$REPO_URL"; else git remote add origin "$REPO_URL"; fi
if [ -n "$(git ls-remote --heads origin 2>/dev/null)" ]; then
  echo; echo "The GitHub repo already has branches. Not pushing over them."
  echo "Push this history to a new branch instead and open a pull request:"
  echo "  ALLOW_MAIN_PUSH=0 git push -u origin main:ws1/initial-build"
  exit 1
fi

echo; read -r -p "Push main to $REPO_URL now? [y/N] " ok
[ "$ok" = "y" ] || [ "$ok" = "Y" ] || { echo "Stopped. Nothing pushed."; exit 0; }
ALLOW_MAIN_PUSH=1 git push -u origin main

echo; echo "Pushed. Next (docs/GIT_WORKFLOW.md section 1):"
echo "  bash scripts/git/setup.sh sheikh2583"
echo "  bash scripts/git/invite_collaborators.sh     # needs gh auth login"
echo "  bash scripts/git/protect_main.sh             # pull requests + guard check on main"
echo "Then each teammate: clone, bash scripts/setup.sh, bash scripts/git/setup.sh <their-username>  (docs/ONBOARDING.md)"
