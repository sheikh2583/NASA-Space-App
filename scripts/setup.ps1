# One-time setup on Windows (PowerShell):  powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 [-Quick] [-NoPipeline]
#   1. checks git, Python 3.11 and Node; 2. creates .venv and installs the pinned packages;
#   3. installs the web app; 4. runs the pipeline on synthetic data (unless -NoPipeline).
param([switch]$Quick, [switch]$NoPipeline, [switch]$Cuda)
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

function Say($m) { Write-Host "`n== $m" -ForegroundColor Cyan }
function Need($cmd, $hint) { if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { Write-Host "Missing $cmd. $hint" -ForegroundColor Red; exit 1 } }

Say "Checking tools"
$py = $null
if (Get-Command py -ErrorAction SilentlyContinue) { try { & py -3.11 -c "import sys" 2>$null; if ($LASTEXITCODE -eq 0) { $py = @("py", "-3.11") } } catch {} }
if (-not $py -and (Get-Command python -ErrorAction SilentlyContinue)) {
  & python -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 11) else 1)" 2>$null
  if ($LASTEXITCODE -eq 0) { $py = @("python") }
}
if (-not $py) { Write-Host "Python 3.11 not found. Install it from python.org (tick 'Add to PATH') and rerun." -ForegroundColor Red; exit 1 }
Need node "Install Node.js LTS from https://nodejs.org and rerun."
Need npm "Install Node.js LTS (it includes npm)."
$pyCommand = $py[0]
$pyFlags = @($py | Select-Object -Skip 1)
Write-Host "Python 3.11; node $(node --version)"

Say "Python environment (.venv)"
if (-not (Test-Path .venv)) { & $pyCommand @pyFlags -m venv .venv; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }
$vpy = Join-Path ".venv" "Scripts\python.exe"
& $vpy -m pip install -q --upgrade pip
& $vpy -m pip install -q -r requirements.lock.txt
if ($LASTEXITCODE -ne 0) {
  Write-Host "Pinned install failed on Windows; trying requirements.txt (newest compatible versions)." -ForegroundColor Yellow
  & $vpy -m pip install -q -r requirements.txt
  if ($LASTEXITCODE -ne 0) { Write-Host "Install failed. See docs/ONBOARDING.md (Troubleshooting)." -ForegroundColor Red; exit 1 }
}
& $vpy -c "import pandas, pyarrow, duckdb, lightgbm, geopandas, fastapi, pyhdf; print('imports OK')"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if ($Cuda) {
  & $vpy -m pip install -r requirements-cuda.txt
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  & $vpy scripts\workflow.py gpu-check
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Say "Web app (ws5_frontend)"
if (-not (Test-Path ws5_frontend\.env)) { Copy-Item ws5_frontend\.env.example ws5_frontend\.env }
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
Push-Location ws5_frontend
try { & npm.cmd ci --no-audit --no-fund; $npmResult = $LASTEXITCODE } finally { Pop-Location }
if ($npmResult -ne 0) { exit $npmResult }

if (-not $NoPipeline) {
  Say "Pipeline on synthetic data (real FIRMS files in data\raw\firms are used instead when present)"
  $pipeArgs = @("scripts\run_pipeline.py"); if ($Quick) { $pipeArgs += "--quick" }
  & $vpy @pipeArgs
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Say "Done"
Write-Host "Start the API and the web app:   powershell -ExecutionPolicy Bypass -File scripts\start.ps1"
Write-Host "Run all tests:                   .venv\Scripts\python -m pytest -q"
Write-Host "Push to GitHub (Sheikh only):    powershell -ExecutionPolicy Bypass -File scripts\push_to_github.ps1"
