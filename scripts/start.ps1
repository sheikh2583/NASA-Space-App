# Start the API (port 8000) and the web app (port 5173), then open the browser. Ctrl+C stops both.
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start.ps1          trained data from data\processed\
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start.ps1 -Mock    bundled fixtures; no data or GPU needed
[CmdletBinding()]
param([switch]$Mock)
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
$vpy = Join-Path (Get-Location) '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $vpy)) {
  Write-Host 'No .venv yet. Run first: powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup.ps1 -UiOnly' -ForegroundColor Red
  exit 1
}
$workflowArgs = @('scripts\workflow.py', 'dev', '--open')
if ($Mock) { $workflowArgs += '--mock' }
& $vpy @workflowArgs
exit $LASTEXITCODE
