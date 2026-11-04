# Git workflow (clone, pull, push, pull request) with scripts

Scripts live in scripts/git/. They run in Git Bash on Windows, or in a normal terminal on macOS and Linux. Python 3 must be installed.
The scripts were tested against a local test repository only, not against GitHub (docs/project/known-gaps.md, item 24).

## 0. One-time, everyone
1. Accept the GitHub invitation (email or notification) from Sheikh.
2. Sign in from your computer. Easiest: install the GitHub CLI and run `gh auth login` (choose HTTPS, sign in with the browser). Otherwise use Git Credential Manager or an SSH key.
3. Set your identity (use the email on your GitHub account; do not put emails in the repo):
   `git config --global user.name "Your Name"`
   `git config --global user.email "your-github-email"`
4. Clone and set up (REPO_URL is the clone URL from the green Code button; Sheikh will post it):
   `git clone <REPO_URL> nasa-space-apps`
   `cd nasa-space-apps`
   `bash scripts/git/setup.sh <your-github-username>`
   The setup turns on rebase-style pulling, installs the safety hooks, and remembers who you are.

## 1. Sheikh, once (already done for this repo)
1. Open a terminal in your clone.
2. Check scripts/git/config.sh: it points to https://github.com/sheikh2583/NASA-Space-App (found public and empty on 3 Nov 2026). Change it if your repo has another name.
3. Nothing to push: the repository already exists on GitHub with its history.
4. `bash scripts/git/setup.sh sheikh2583`
5. `bash scripts/git/invite_collaborators.sh`   (needs `gh auth login`; or invite in GitHub: Settings > Collaborators)
6. `bash scripts/git/protect_main.sh`   (needs gh; if your plan does not allow branch protection, skip: the hooks and the PR guard still work)
7. Tell everyone the clone URL and that they should do section 0.

## 2. The daily loop (everyone)
| Step | Command | What it does |
|---|---|---|
| Start a piece of work | `bash scripts/git/start.sh <topic>` | updates main, creates branch `<your-prefix>/<topic>` |
| Work | edit files in your own folder only | |
| Save | `bash scripts/git/save.sh "what you did"` | stages and commits; the guard blocks files that are not yours, data, keys and files over 5 MB |
| Stay current | `bash scripts/git/sync.sh` | rebases your branch on the latest main |
| Share | `bash scripts/git/ship.sh` | syncs, runs your folder's tests, pushes, opens the pull request (or prints the link) |
| After the merge | `bash scripts/git/cleanup.sh` | back to main, latest code, old branch deleted |
| Where am I | `bash scripts/git/status.sh` | branch, ahead/behind, last commits |

Raw git, if you ever need it: clone `git clone <URL>`; pull `git pull --rebase origin main`; branch `git switch -c ws2/topic`; push `git push -u origin HEAD`.

## 3. Who merges
The owner of the changed folder merges the pull request once the `guard` check is green (docs/project/file-ownership.md). No approval is required by GitHub, because every ws folder has one code owner (its author) and GitHub does not let authors approve their own pull requests. contracts/ and common/ still need Sheikh's approval by team rule: wait for his review before merging.
Use "Squash and merge" in GitHub. Merged branches are deleted automatically. Then the author runs `bash scripts/git/cleanup.sh`.

If GitHub says the branch has conflicts (usually data/MANIFEST.md), run `bash scripts/git/ship.sh` again: it rebases locally, where .gitattributes keeps both sides' lines, and updates your branch.

## 4. Your commands (branch prefix and folder)
| Person | GitHub | Prefix | Folder | Example |
|---|---|---|---|---|
| Sheikh (1) | sheikh2583 | ws1/ | ws1_harmonize/ | `bash scripts/git/setup.sh sheikh2583` then `bash scripts/git/start.sh panel-builder` |
| Sattyam (2) | sssatty | ws2/ | ws2_platform/ (+ contracts/openapi.yaml, fixtures/) | `bash scripts/git/setup.sh sssatty` then `bash scripts/git/start.sh api-mock` |
| Monazir (3) | Monajir | ws3/ | ws3_anomaly/ | `bash scripts/git/setup.sh Monajir` then `bash scripts/git/start.sh ingest-slice` |
| Samin (4) | Samin2712 | ws4/ | ws4_outlook/ and common/ | `bash scripts/git/setup.sh Samin2712` then `bash scripts/git/start.sh common-series` |
| Shammo (5) | Zanasin | ws5/ | ws5_frontend/ | `bash scripts/git/setup.sh Zanasin` then `bash scripts/git/start.sh scaffold` |
| Samiul (6) | samiulislam22 | ws6/ | ws6_validation/ (+ his docs files) | `bash scripts/git/setup.sh samiulislam22` then `bash scripts/git/start.sh qa-scaffolds` |

Everyone may add one line at the bottom of data/MANIFEST.md (append-only). Sattyam may also add to docs/project/contract-changes.md; Sheikh logs the rest.

## 5. What protects the team
- Pre-commit hook: runs scripts/git/guard.py; blocks changes outside your allowed paths (scripts/team.csv), data, .env and files over 5 MB.
- Pre-push hook: blocks direct pushes to main.
- GitHub Action `pr-guard` (.github/workflows/pr-guard.yml): runs the same guard on every pull request and checks your branch starts with your prefix.
- Branch protection (Sheikh, free on public repos): pull request required, guard check required, no force pushes to main. No approval count (see section 3).
- `.gitattributes`: data/MANIFEST.md and docs/project/contract-changes.md merge by union, so two people appending at once do not conflict.
- `ship.sh` updates an already-pushed branch with `--force-with-lease` after rebasing; it never touches main.
- If the guard blocks something you need: ask the owner (CONTRIBUTING.md section 7). Do not bypass it. `GUARD_OVERRIDE=1` exists for Sheikh in emergencies and does not work in CI.

## 6. When something goes wrong
- Conflict while syncing: open the files with `<<<<<<<`, keep the right lines, then `git add <file>` and `git rebase --continue`. Stuck: `git rebase --abort` and ask Sheikh.
- Committed on main by mistake: `git branch ws2/rescue` then `git reset --hard origin/main`, and continue on the rescue branch (replace ws2 with your prefix).
- Committed a file that is not yours or is too big: `git reset --soft HEAD~1`, unstage the file with `git restore --staged <path>`, commit again.
- Pushed a secret: tell Sheikh at once and change the key; deleting the commit does not remove it from history.
- Never: `git push --force` on main, `git add` data files, commit `.env`.
