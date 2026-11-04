# HUMAN ONLY. Runs the whole CUDA training sequence on Windows, with logs:
#   setup (only if .venv is missing) -> weather cache (only if missing) -> readiness
#   -> quick training -> pause -> full training -> validate -> results [-> runtime ZIP]
# Coding agents must not run this script (AGENTS.md). Guide: docs/guides/training.md
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\train.ps1 [-QuickOnly | -SkipQuick] [-Yes] [-Pack]
#                                                    [-GpuId 0] [-Threads 8] [-From STAGE] [-PythonExecutable PATH]
[CmdletBinding()]
param(
  [ValidateRange(0, 64)][int]$GpuId = 0,
  [ValidateRange(1, 256)][int]$Threads = 8,
  [switch]$QuickOnly,
  [switch]$SkipQuick,
  [switch]$Yes,
  [string]$From,
  [switch]$Pack,
  [string]$PythonExecutable
)
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')

function Write-Step([string]$Text) { Write-Host "`n==> $Text" -ForegroundColor Cyan }
function Stop-Run([string]$Text) { Write-Host "`nSTOPPED: $Text" -ForegroundColor Red; exit 1 }

if ($QuickOnly -and $SkipQuick) { Stop-Run 'Choose -QuickOnly or -SkipQuick, not both.' }
if (-not (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) { Stop-Run 'nvidia-smi not found. Install the NVIDIA driver, reboot, then rerun.' }
& nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader
if ($LASTEXITCODE -ne 0) { Stop-Run 'nvidia-smi failed. Fix the NVIDIA driver first.' }

$vpy = Join-Path (Get-Location) '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $vpy)) {
  Write-Step 'Setting up the training environment (first run only)'
  $setupArgs = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'scripts\setup.ps1', '-TrainingOnly', '-GpuId', "$GpuId", '-Threads', "$Threads")
  if ($PythonExecutable) { $setupArgs += @('-PythonExecutable', $PythonExecutable) }
  & powershell.exe @setupArgs
  if ($LASTEXITCODE -ne 0) { Stop-Run 'Setup failed. Fix the first error above, then rerun.' }
}

New-Item -ItemType Directory -Force -Path results\logs | Out-Null
$label = Get-Date -Format 'yyyyMMdd-HHmmss'
$common = @('--backend', 'cuda', '--gpu-id', "$GpuId", '--threads', "$Threads")

# Runs a Python step, mirrors its output into results\logs\<label>-<name>.log (UTF-8), and stops on failure.
function Invoke-Logged([string]$Name, [string[]]$PythonArgs) {
  $log = Join-Path (Get-Location) "results\logs\$label-$Name.log"
  $writer = New-Object System.IO.StreamWriter($log, $true, (New-Object System.Text.UTF8Encoding($false)))
  $saved = $ErrorActionPreference
  try {
    # Windows PowerShell turns native stderr lines into errors; keep them as plain output instead.
    $ErrorActionPreference = 'Continue'
    & $vpy -u @PythonArgs 2>&1 | ForEach-Object { $line = "$_"; Write-Host $line; $writer.WriteLine($line); $writer.Flush() }
    $code = $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $saved
    $writer.Dispose()
  }
  if ($code -ne 0) { Stop-Run "$Name failed (exit $code). Log: $log" }
}

$weather = 'data\interim\monazir'
if (-not ((Test-Path "$weather\weather_BD.parquet") -and (Test-Path "$weather\weather_PB.parquet"))) {
  Write-Step 'Building the NASA POWER weather cache (first run only, 20-40 minutes, resumable)'
  Invoke-Logged 'weather' @('-m', 'ws3_anomaly.loaders.weather', '--start', '2000-11-01', '--end', '2026-11-03')
}

Write-Step 'Checking that inputs and CUDA are ready'
Invoke-Logged 'prepare' @('scripts\workflow.py', 'prepare', '--gpu-id', "$GpuId", '--threads', "$Threads")

if ($From) {
  $extra = @(); if ($QuickOnly) { $extra = @('--quick') }
  Write-Step "Resuming training at stage '$From'"
  Invoke-Logged "resume-$From" (@('scripts\workflow.py', 'train') + $common + @('--from', $From) + $extra)
} else {
  if (-not $SkipQuick) {
    Write-Step 'Quick training (reduced holdouts)'
    Invoke-Logged 'quick' (@('scripts\workflow.py', 'train') + $common + @('--quick'))
    if ($QuickOnly) {
      Invoke-Logged 'results' @('scripts\workflow.py', 'results')
      Write-Step 'Quick run finished. Read results\latest.md. Run again with -SkipQuick for the full run.'
      exit 0
    }
    if (-not $Yes) {
      Write-Host "`nQuick run passed. Check results\latest.md now."
      Read-Host 'Press Enter to start the FULL run, or Ctrl+C to stop here' | Out-Null
    }
  }
  Write-Step 'Full training (all six holdouts, both satellite-input configurations)'
  Invoke-Logged 'full' (@('scripts\workflow.py', 'train') + $common)
}

Write-Step 'Scientific QA'
Invoke-Logged 'validate' @('scripts\workflow.py', 'validate')
Write-Step 'Results summary'
Invoke-Logged 'results' @('scripts\workflow.py', 'results')

if ($Pack) {
  if ($QuickOnly) { Stop-Run '-Pack needs a full run, not a quick one.' }
  Write-Step 'Packing the runtime ZIP for deployment'
  Invoke-Logged 'pack' @('scripts\runtime_bundle.py', 'pack')
}

Write-Step 'Done'
$latest = Get-ChildItem results\runs -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Write-Host 'Summary:          results\latest.md'
if ($latest) { Write-Host "Execution report: $($latest.FullName)\execution.json" }
Write-Host "Logs:             results\logs\$label-*.log"
Write-Host 'Accept the run only if execution.json says status: passed, quick: false, start_stage: null (docs\guides\training.md).'
