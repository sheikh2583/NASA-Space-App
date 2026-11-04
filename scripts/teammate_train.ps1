# HUMAN ONLY: setup performs fitting probes; the next command performs full training.
[CmdletBinding()]
param(
  [Parameter(Mandatory)][ValidatePattern('^[A-Za-z0-9_-]{1,40}$')][string]$Name,
  [ValidateRange(0,64)][int]$GpuId = 0,
  [ValidateRange(1,256)][int]$Threads = 8,
  [string]$PythonExecutable
)
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
if (@(Get-ChildItem -LiteralPath 'data/incoming' -Filter '*.zip' -ErrorAction SilentlyContinue).Count -ne 1) {
  throw 'First put the single FireSense training-inputs ZIP from Sheikh in data/incoming/.'
}
$setupArgs = @('-NoProfile','-ExecutionPolicy','Bypass','-File','scripts\setup.ps1','-TrainingOnly','-GpuId',"$GpuId",'-Threads',"$Threads")
if ($PythonExecutable) { $setupArgs += @('-PythonExecutable',$PythonExecutable) }
& powershell @setupArgs
if ($LASTEXITCODE -ne 0) { throw 'Setup failed; fix the first error before training.' }
& .\.venv\Scripts\python -u scripts\teammate.py run --human-run --name $Name --gpu-id $GpuId --threads $Threads
if ($LASTEXITCODE -ne 0) { throw 'Training/handoff failed; send the error and results/logs/teammate-*.log to Sheikh.' }
