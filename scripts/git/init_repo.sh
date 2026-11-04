#!/usr/bin/env bash
# SHEIKH ONLY, once. Run inside the unzipped starter folder:  bash scripts/git/init_repo.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
source scripts/config.sh
echo "Using repo: $REPO_URL"
[ -d .git ] || git init
git checkout -B main
git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
git add -A
git commit -m "Initial scaffold from the starter kit" || true
git fetch origin || { echo "Cannot reach $REPO_URL. Check the URL and that you are signed in (gh auth login)."; exit 1; }
if git ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
  git pull --rebase origin main --allow-unrelated-histories || { echo "Resolve the conflicts, then rerun."; exit 1; }
fi
ALLOW_MAIN_PUSH=1 git push -u origin main
chmod +x scripts/git/*.sh scripts/git/hooks/* 2>/dev/null || true
echo "Done. Now:  bash scripts/git/setup.sh sheikh2583"
