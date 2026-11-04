#!/usr/bin/env bash
# SHEIKH ONLY. Needs gh signed in. Not tested against GitHub. CODEOWNERS still auto-requests reviewers; the guard check enforces ownership. Branch protection on private repos may need a paid plan; if this fails, rely on the hooks, the PR guard and the rules in CONTRIBUTING.md.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"; source scripts/git/config.sh
path="${REPO_URL#https://github.com/}"; path="${path%.git}"
gh api -X PUT "repos/$path/branches/main/protection" --input - <<'JSON'
{
  "required_status_checks": {"strict": false, "contexts": ["guard"]},
  "enforce_admins": false,
  "required_pull_request_reviews": {"require_code_owner_reviews": false, "required_approving_review_count": 0},
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
# Delete branches after merge so cleanup.sh can find them as "gone".
gh api -X PATCH "repos/$path" -F delete_branch_on_merge=true >/dev/null
echo "main is protected: pull request and passing guard check required, no force pushes; merged branches are deleted."
echo "Approvals are not required: every ws folder has one code owner (its author), and GitHub does not let authors approve their own pull requests."
