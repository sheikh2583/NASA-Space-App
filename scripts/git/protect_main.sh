#!/usr/bin/env bash
# SHEIKH ONLY. Needs gh signed in. Not tested against GitHub. Branch protection on private repos may need a paid plan; if this fails, rely on the hooks, the PR guard and the rules in docs/WORKING_TOGETHER.md.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"; source scripts/config.sh
path="${REPO_URL#https://github.com/}"; path="${path%.git}"
gh api -X PUT "repos/$path/branches/main/protection" --input - <<'JSON'
{
  "required_status_checks": {"strict": false, "contexts": ["guard"]},
  "enforce_admins": false,
  "required_pull_request_reviews": {"require_code_owner_reviews": true, "required_approving_review_count": 1},
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
echo "main is protected: pull request, code-owner review, guard check, no force pushes."
