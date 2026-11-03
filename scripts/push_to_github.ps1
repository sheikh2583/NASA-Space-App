# SHEIKH ONLY, once (Windows): push this folder's prepared history (one commit per workstream) to the empty GitHub repo.
#   powershell -ExecutionPolicy Bypass -File scripts\push_to_github.ps1
# Needs: Git for Windows and you signed in to GitHub (gh auth login, or Git Credential Manager). Never force-pushes.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
$repo = (Select-String -Path scripts\config.sh -Pattern 'REPO_URL:-([^}]+)\}').Matches[0].Groups[1].Value
Write-Host "Repo: $repo"
git rev-parse --git-dir | Out-Null
if ((git branch --show-current) -ne "main") { git switch main }

Write-Host "`nCommits to push (author = workstream owner):"
git log --format="  %h  %an  %s" main

$hasOrigin = $true; try { git remote get-url origin 2>$null | Out-Null; if ($LASTEXITCODE -ne 0) { $hasOrigin = $false } } catch { $hasOrigin = $false }
if ($hasOrigin) { git remote set-url origin $repo } else { git remote add origin $repo }
$heads = git ls-remote --heads origin 2>$null
if ($heads) {
  Write-Host "`nThe GitHub repo already has branches. Not pushing over them." -ForegroundColor Yellow
  Write-Host "Push this history to a new branch and open a pull request:  git push -u origin main:ws1/initial-build"
  exit 1
}
$ok = Read-Host "`nPush main to $repo now? [y/N]"
if ($ok -notin @("y", "Y")) { Write-Host "Stopped. Nothing pushed."; exit 0 }
$env:ALLOW_MAIN_PUSH = "1"
git push -u origin main
Remove-Item Env:ALLOW_MAIN_PUSH

Write-Host "`nPushed. Next, in Git Bash (docs/GIT_WORKFLOW.md section 1):"
Write-Host "  bash scripts/git/setup.sh sheikh2583"
Write-Host "  bash scripts/git/invite_collaborators.sh"
Write-Host "  bash scripts/git/protect_main.sh"
