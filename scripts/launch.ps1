param([ValidateSet("menu", "setup", "setup-cuda", "gpu-check", "cpu-train", "prepare", "smoke", "quick", "train", "dev", "mock", "results", "share", "all")][string]$Action = "menu")
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
if ($Action -eq "menu") {
  Write-Host "FireSense workflows" -ForegroundColor Cyan
  Write-Host "1 Setup CPU dependencies`n2 Prepare/check CUDA training inputs`n3 Smoke tests + UI build`n4 Quick CUDA training`n5 Full CUDA training`n6 Open trained UI`n7 Open mock UI (no datasets)`n8 Generate results`n9 Minimal share ZIP`n10 Full CUDA pipeline + tests + UI build`n11 Setup CUDA dependencies`n12 Verify GPU training`n13 Full CPU training`n0 Exit"
  $actions = @{"1"="setup"; "2"="prepare"; "3"="smoke"; "4"="quick"; "5"="train"; "6"="dev"; "7"="mock"; "8"="results"; "9"="share"; "10"="all"; "11"="setup-cuda"; "12"="gpu-check"; "13"="cpu-train"}
  $choice = Read-Host "Choose a number"
  if ($choice -eq "0") { exit 0 }
  if (-not $actions.ContainsKey($choice)) { Write-Host "Unknown choice"; exit 1 }
  $Action = $actions[$choice]
}
New-Item -ItemType Directory -Force -Path results\logs | Out-Null
$log = Join-Path (Get-Location) ("results\logs\{0}-{1}.log" -f $Action, (Get-Date -Format "yyyyMMdd-HHmmss"))
Start-Transcript -Path $log | Out-Null
try {
  if ($Action -eq "setup" -or $Action -eq "setup-cuda") {
    $setupArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\setup.ps1", "-NoPipeline")
    if ($Action -eq "setup-cuda") { $setupArgs += "-Cuda" }
    & powershell.exe @setupArgs
    $result = $LASTEXITCODE
  } else {
    $python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
    if (-not (Test-Path $python)) { throw "Run option 1 (Setup) first." }
    $workflowArgs = @("scripts\workflow.py", $Action)
    if ($Action -eq "quick") { $workflowArgs = @("scripts\workflow.py", "train", "--quick") }
    if ($Action -eq "cpu-train") { $workflowArgs = @("scripts\workflow.py", "train", "--backend", "cpu") }
    if ($Action -eq "dev") { $workflowArgs += "--open" }
    if ($Action -eq "mock") { $workflowArgs = @("scripts\workflow.py", "dev", "--mock", "--open") }
    & $python @workflowArgs
    $result = $LASTEXITCODE
  }
  if ($result -ne 0) { throw "Workflow failed with exit code $result. Log: $log" }
  Write-Host "Completed. Log: $log" -ForegroundColor Green
} catch {
  Write-Host $_ -ForegroundColor Red
  $result = 1
} finally {
  Stop-Transcript | Out-Null
}
exit $result
