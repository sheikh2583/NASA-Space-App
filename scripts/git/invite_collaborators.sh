#!/usr/bin/env bash
# SHEIKH ONLY. Needs the GitHub CLI signed in (gh auth login). Not tested against GitHub.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"; source scripts/git/config.sh
path="${REPO_URL#https://github.com/}"; path="${path%.git}"
owner="${path%%/*}"
tail -n +2 scripts/team.csv | cut -d, -f1 | while read -r u; do
  [ "$(echo "$u" | tr A-Z a-z)" = "$(echo "$owner" | tr A-Z a-z)" ] && continue
  gh api -X PUT "repos/$path/collaborators/$u" -f permission=push >/dev/null && echo "Invited $u (they must accept the email or notification)"
done
