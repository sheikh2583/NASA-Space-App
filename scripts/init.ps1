# Bootstrap Windows, then run any project workflow.
param(
  [ValidateSet("setup", "train", "validate", "results", "test", "build", "dev", "all")]
  [string]$Workflow = "setup",
  [switch]$Quick,
  [switch]$Mock
)
$ErrorActionPreference = "Stop"
$root = Join-Path $PSScriptRoot ".."
& (Join-Path $PSScriptRoot "setup.ps1") -NoPipeline
if ($Workflow -eq "setup") { exit 0 }
$args = @((Join-Path $PSScriptRoot "workflow.py"), $Workflow)
if ($Quick) { $args += "--quick" }
if ($Mock) { $args += "--mock" }
& (Join-Path $root ".venv\Scripts\python.exe") @args
exit $LASTEXITCODE
