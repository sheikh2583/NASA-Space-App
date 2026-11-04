# Create .venv and install dependencies. Never trains.
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup.ps1 -UiOnly        UI/API development, no GPU needed
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup.ps1 -TrainingOnly  CUDA training only, no Node needed (HUMAN ONLY: runs GPU probes)
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup.ps1               everything (HUMAN ONLY: runs GPU probes)
# Guide: docs/guides/setup.md
[CmdletBinding()]
param(
  [switch]$UiOnly,
  [switch]$TrainingOnly,
  [switch]$AllowCompatible,
  [string]$PythonExecutable,
  [ValidateRange(0, 64)][int]$GpuId = 0,
  [ValidateRange(1, 256)][int]$Threads = 8
)
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
try {
  if ($UiOnly -and $TrainingOnly) { throw 'Choose -UiOnly or -TrainingOnly, not both.' }
  $vpy = Join-Path (Get-Location) '.venv\Scripts\python.exe'
  if (-not (Test-Path -LiteralPath $vpy)) {
    if (Test-Path -LiteralPath '.venv') { throw '.venv exists but has no Windows Python. Rename it before creating a Windows environment.' }
    $pyCommand = $null
    $pyFlags = @()
    if ($PythonExecutable) {
      $pyCommand = (Get-Command $PythonExecutable -ErrorAction Stop).Source
      & $pyCommand -c 'import struct,sys; sys.exit(0 if sys.version_info[:2] == (3, 11) and struct.calcsize("P") == 8 else 1)'
      if ($LASTEXITCODE -ne 0) { throw '-PythonExecutable must select a working 64-bit Python 3.11 executable.' }
    }
    if (-not $pyCommand -and (Get-Command py -ErrorAction SilentlyContinue)) {
      try {
        & py -3.11 -c 'import sys' 2>$null
        if ($LASTEXITCODE -eq 0) { $pyCommand = 'py'; $pyFlags = @('-3.11') }
      } catch { $pyCommand = $null }
    }
    if (-not $pyCommand -and (Get-Command python -ErrorAction SilentlyContinue)) {
      & python -c 'import sys; sys.exit(0 if sys.version_info[:2] == (3, 11) else 1)'
      if ($LASTEXITCODE -eq 0) { $pyCommand = 'python' }
    }
    if (-not $pyCommand) { throw 'Install 64-bit Python 3.11 and reopen the terminal, or pass -PythonExecutable with its full path. See docs/guides/setup.md.' }
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
