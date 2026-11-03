#!/usr/bin/env bash
# Update, test, push and open a pull request:  bash scripts/git/ship.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"; source scripts/git/_lib.sh
not_on_main
bash scripts/git/sync.sh
f="$(my_folder)"
if [ -d "$f/tests" ] && [ "${SKIP_TESTS:-0}" != "1" ]; then
  if command -v pytest >/dev/null 2>&1; then
    pytest -q "$f/tests" || { echo "Tests failed. Fix them or ask for help. (SKIP_TESTS=1 skips; use only with Sheikh's OK)"; exit 1; }
  else echo "pytest not found; activate your venv (see docs/WHERE_TO_WORK.md)."; exit 1; fi
fi
# sync.sh rebases, which rewrites commits already pushed by an earlier ship; --force-with-lease updates
# your own branch safely (it refuses if someone else pushed to it). The pre-push hook still blocks main.
git push --force-with-lease -u origin HEAD
if command -v gh >/dev/null 2>&1; then
  gh pr create --base main --fill || echo "PR may already exist: gh pr view --web"
else
  echo; echo "Open your pull request here:"; pr_url
fi
echo "Next: tell the owner of the changed folder (docs/FILE_OWNERSHIP.md) and post a HANDOFF if it is a deliverable."
