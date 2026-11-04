# Bootstrap once, then dispatch; ordinary workflows do not reinstall dependencies.
param(
  [ValidateSet('setup','gpu-check','prepare','smoke','share','train','validate','results','test','build','dev','all')]
  [string]$Workflow = 'setup',
  [switch]$UiOnly, [switch]$Quick, [switch]$Mock,
  [ValidateRange(0,64)][int]$GpuId = 0,
  [ValidateRange(1,256)][int]$Threads = 8
)
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
if ($UiOnly -and $Workflow -in @('train','prepare','all','gpu-check')) { throw '-UiOnly cannot prepare a CUDA training workflow.' }
if ($Workflow -eq 'setup' -or -not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
  $setupArgs = @('-NoProfile','-ExecutionPolicy','Bypass','-File','scripts/setup.ps1','-GpuId',"$GpuId",'-Threads',"$Threads")
  if ($UiOnly -or $Workflow -in @('smoke','dev','test','build','share')) { $setupArgs += '-UiOnly' }
  & powershell.exe @setupArgs
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
if ($Workflow -eq 'setup') { exit 0 }
$workflowArgs = @('scripts/workflow.py',$Workflow,'--gpu-id',"$GpuId",'--threads',"$Threads")
if ($Quick) { $workflowArgs += '--quick' }
if ($Mock) { $workflowArgs += '--mock' }
& .venv\Scripts\python.exe @workflowArgs
exit $LASTEXITCODE
