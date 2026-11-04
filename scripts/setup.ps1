# Install the complete CUDA environment; -UiOnly prepares the mock/UI workflow.
[CmdletBinding()]
param(
  [switch]$UiOnly,
  [switch]$TrainingOnly,
  [switch]$AllowCompatible,
  [ValidateRange(0, 64)][int]$GpuId = 0,
  [ValidateRange(1, 256)][int]$Threads = 8,
  [switch]$NoPipeline, # Compatibility: setup never starts a pipeline now.
  [switch]$Cuda,
  [switch]$Quick
)
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
try {
  if ($UiOnly -and $Cuda) { throw 'Choose -UiOnly or CUDA setup, not both.' }
  if ($UiOnly -and $TrainingOnly) { throw 'Choose -UiOnly or -TrainingOnly, not both.' }
  if ($Quick) { Write-Host 'Setup no longer trains. Run workflow.py train --quick after readiness passes.' }
  $vpy = Join-Path (Get-Location) '.venv\Scripts\python.exe'
  if (-not (Test-Path -LiteralPath $vpy)) {
    if (Test-Path -LiteralPath '.venv') { throw '.venv exists but has no Windows Python. Rename it before creating a Windows environment.' }
    $pyCommand = $null
    $pyFlags = @()
    if (Get-Command py -ErrorAction SilentlyContinue) {
      try {
        & py -3.11 -c 'import sys' 2>$null
        if ($LASTEXITCODE -eq 0) { $pyCommand = 'py'; $pyFlags = @('-3.11') }
      } catch { $pyCommand = $null }
    }
    if (-not $pyCommand -and (Get-Command python -ErrorAction SilentlyContinue)) {
      & python -c 'import sys; sys.exit(0 if sys.version_info[:2] == (3, 11) else 1)'
      if ($LASTEXITCODE -eq 0) { $pyCommand = 'python' }
    }
    if (-not $pyCommand) { throw 'Install 64-bit Python 3.11 and reopen the terminal.' }
    & $pyCommand @pyFlags -m venv .venv
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  }
  $setupArgs = @('scripts/bootstrap.py', '--gpu-id', "$GpuId", '--threads', "$Threads")
  if ($UiOnly) { $setupArgs += '--ui-only' }
  if ($TrainingOnly) { $setupArgs += '--training-only' }
  if ($AllowCompatible) { $setupArgs += '--allow-compatible' }
  & $vpy @setupArgs
  exit $LASTEXITCODE
} catch {
  Write-Host "SETUP FAILED: $_" -ForegroundColor Red
  exit 1
}
