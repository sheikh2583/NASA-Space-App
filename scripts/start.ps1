# Start the API (port 8000) and the web app (port 5173) on Windows.
#   powershell -ExecutionPolicy Bypass -File scripts\start.ps1 [-Mock]
param([switch]$Mock)
Set-Location (Join-Path $PSScriptRoot "..")
$env:PYTHONPATH = (Get-Location).Path
$vpy = Join-Path ".venv" "Scripts\python.exe"
if ($Mock) {
  Write-Host "Mock API (contracts/fixtures) on http://localhost:8000"
  $api = Start-Process -FilePath $vpy -ArgumentList "-m", "uvicorn", "ws2_platform.api.mock_server:app", "--port", "8000" -PassThru -NoNewWindow
} else {
  if (-not (Test-Path data\processed\harmonized.parquet)) { Write-Host "No data\processed yet: run scripts\setup.ps1 (or start with -Mock)."; exit 1 }
  $env:DATA_DIR = "data/processed"
  Write-Host "API on http://localhost:8000  (docs: http://localhost:8000/docs)"
  $api = Start-Process -FilePath $vpy -ArgumentList "-m", "uvicorn", "ws2_platform.api.app:app", "--port", "8000" -PassThru -NoNewWindow
}
try { Push-Location ws5_frontend; npm run dev } finally { Pop-Location; Stop-Process -Id $api.Id -ErrorAction SilentlyContinue }
