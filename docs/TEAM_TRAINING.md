# Copyable teammate training handoff

Human-operated instructions, updated 4 November 2026. **Coding agents must not execute setup fitting probes, readiness checks, training, or fitting tests**; see [AGENTS.md](../AGENTS.md). Deployment serves existing artifacts and does not authorize training. Follow only the section for your OS.

Repository: https://github.com/sheikh2583/NASA-Space-App

Use an NVIDIA RTX 4070 Laptop 8 GB or RTX 3090 Desktop 24 GB, a working driver (`nvidia-smi`), 64-bit Python 3.11, and local SSD space for inputs plus at least 5 GiB of intermediates and any output backups. Linux training supports x86_64/glibc 2.28+; ARM/Jetson and Alpine/musl are not verified/supported by this setup. Node/npm is not needed for training-only initialization. Training runs locally, not on Render.

## Required input bundle

Obtain the project's existing input bundle from Sheikh. The bundle must contain this tree, copied into the fresh checkout:

```text
data/raw/firms/                       Original FIRMS CSV/CSV.GZ files, ZIPs extracted
data/raw/boundaries/BGD_ADM1.geojson   Bangladesh ADM1 boundaries
data/raw/boundaries/IND_ADM1.geojson   India ADM1 boundaries
data/raw/landcover/MCD12C1*.hdf       Original land-cover HDF, original filename
data/interim/monazir/weather_BD.parquet
data/interim/monazir/weather_PB.parquet
```

FIRMS inputs must include MODIS Terra/Aqua, VIIRS SNPP, and NOAA-20 for Bangladesh and Punjab–Haryana–Delhi. Preserve original filenames and use each product's actual available period. NOAA-21 is optional. Use the same complete input bundle on both GPUs; the current fire record ends on **2026-11-02**. Raw `data/raw/power/` tiles are optional when both weather Parquets already exist.

The Render runtime ZIP is **not training input**. Do not copy `.venv`, `node_modules`, or private `.env` files between computers. Archive training needs no FIRMS key. Run one pipeline at a time per checkout and keep inputs unchanged until the run finishes.

## Windows: initial installation

Install missing prerequisites in PowerShell. Skip commands for prerequisites already installed. NVIDIA drivers must already be installed for the machine; do not install the full CUDA toolkit just for this pipeline.

```powershell
winget install --exact --id Git.Git --source winget
winget install --exact --id Python.Python.3.11 --source winget
winget install --exact --id 'Microsoft.VCRedist.2015+.x64' --source winget
```

Reopen PowerShell so PATH changes take effect, then run:

```powershell
$ErrorActionPreference = 'Stop'
git clone https://github.com/sheikh2583/NASA-Space-App.git firesense-training
if ($LASTEXITCODE -ne 0) { throw 'Clone failed' }
Set-Location firesense-training
nvidia-smi
if ($LASTEXITCODE -ne 0) { throw 'Fix the NVIDIA driver first' }
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup.ps1 -TrainingOnly
if ($LASTEXITCODE -ne 0) { throw 'Setup failed; resolve its first error' }
```

Setup creates the OS-specific `.venv`, installs complete locked training dependencies, verifies actual CUDA fits, preserves `.env`, and creates input directories. It never starts the project pipeline. For a nonstandard interpreter location, use `-PythonExecutable 'C:\full\path\to\python.exe'`; it must be 64-bit Python 3.11 and is used when creating a new environment.

## Windows: copy data and run

Edit the input-bundle path below. Its root must contain the `data/` tree shown above.

```powershell
$ErrorActionPreference = 'Stop'
$inputBundle = 'D:\FireSense-inputs' # CHANGE to the actual shared-drive/download path
foreach ($folder in 'firms', 'boundaries', 'landcover') {
  Copy-Item -LiteralPath (Join-Path $inputBundle "data\raw\$folder") -Destination 'data\raw' -Recurse -Force
}
New-Item -ItemType Directory -Force data\interim\monazir, results\logs | Out-Null
foreach ($region in 'BD', 'PB') {
  Copy-Item -LiteralPath (Join-Path $inputBundle "data\interim\monazir\weather_$region.parquet") -Destination 'data\interim\monazir'
}

function Invoke-FireSense {
  $savedPreference = $ErrorActionPreference
  try {
    # Windows PowerShell can otherwise treat native stderr warnings as fatal.
    $ErrorActionPreference = 'Continue'
    & .\.venv\Scripts\python @args
    $commandExit = $LASTEXITCODE
  } finally { $ErrorActionPreference = $savedPreference }
  if ($commandExit -ne 0) { throw "FireSense command failed: $args" }
}
$runLabel = Get-Date -Format 'yyyyMMdd-HHmmss'
Invoke-FireSense scripts\workflow.py prepare --gpu-id 0 --threads 8
# Proceed only when readiness prints READY: 0 blocking check(s).
Invoke-FireSense -u scripts\workflow.py train --backend cuda --gpu-id 0 --threads 8 --quick 2>&1 | Tee-Object "results\logs\quick-$runLabel.log"
```

Inspect `results/latest.md` and quick-run QA before starting the full run. Then:

```powershell
Invoke-FireSense -u scripts\workflow.py train --backend cuda --gpu-id 0 --threads 8 2>&1 | Tee-Object "results\logs\full-$runLabel.log"
Invoke-FireSense scripts\workflow.py validate
Invoke-FireSense scripts\workflow.py results
Invoke-FireSense scripts\runtime_bundle.py pack 2>&1 | Tee-Object results\logs\runtime-sha256.txt
git rev-parse HEAD | Set-Content results\logs\git-commit.txt
nvidia-smi | Set-Content results\logs\nvidia-smi.txt
Invoke-FireSense --version 2>&1 | Set-Content results\logs\python-version.txt
Invoke-FireSense -m pip freeze | Set-Content results\logs\python-packages.txt
Compress-Archive -Path share\firesense-runtime.zip, results\latest.md, results\latest.json, results\logs, results\runs, data\processed, data\interim\sheikh -DestinationPath share\firesense-training-deliverables.zip -Force
```

Use the same PowerShell terminal so `Invoke-FireSense` and `$runLabel` remain defined. All Python commands use the project interpreter; activation is unnecessary. A thrown error means stop and inspect the failed command.

## Linux: initial installation (Debian/Ubuntu x86_64)

These commands install system prerequisites and Python 3.11 without replacing the distribution's system Python. NVIDIA drivers must already work. Run in Bash; WSL users need an operational NVIDIA CUDA bridge and a separate Linux checkout/environment.

```bash
set -euo pipefail
sudo apt-get update
sudo apt-get install -y git curl ca-certificates libgomp1
curl -LsSf https://astral.sh/uv/install.sh | sh
"$HOME/.local/bin/uv" python install 3.11
training_python="$("$HOME/.local/bin/uv" python find --system 3.11)"
git clone https://github.com/sheikh2583/NASA-Space-App.git firesense-training
cd firesense-training
nvidia-smi
bash scripts/setup.sh --training-only --python "$training_python"
```

If a suitable 64-bit `python3.11` is already installed with venv support, `bash scripts/setup.sh --training-only` is enough. On other distributions install Git, curl, CA certificates, and the OpenMP runtime using the distribution's package manager. Do not run pip/setup with sudo. See the [official uv installer](https://docs.astral.sh/uv/getting-started/installation/) and [Python management guide](https://docs.astral.sh/uv/guides/install-python/).

## Linux: copy data and run

Edit the input-bundle path; its root must contain `data/`.

```bash
set -euo pipefail
input_bundle='/path/to/FireSense-inputs' # CHANGE to the actual mounted/download path
mkdir -p data/raw data/interim/monazir results/logs
for folder in firms boundaries landcover; do
  cp -a "$input_bundle/data/raw/$folder" data/raw/
done
for region in BD PB; do
  cp "$input_bundle/data/interim/monazir/weather_$region.parquet" data/interim/monazir/
done
run_label="$(date +%Y%m%d-%H%M%S)"
.venv/bin/python scripts/workflow.py prepare --gpu-id 0 --threads 8
# Proceed only when readiness prints READY: 0 blocking check(s).
.venv/bin/python -u scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8 --quick 2>&1 | tee "results/logs/quick-$run_label.log"
```

Inspect the quick-run results and QA before continuing:

```bash
set -euo pipefail
.venv/bin/python -u scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8 2>&1 | tee "results/logs/full-$run_label.log"
.venv/bin/python scripts/workflow.py validate
.venv/bin/python scripts/workflow.py results
.venv/bin/python scripts/runtime_bundle.py pack 2>&1 | tee results/logs/runtime-sha256.txt
git rev-parse HEAD > results/logs/git-commit.txt
nvidia-smi > results/logs/nvidia-smi.txt
.venv/bin/python --version > results/logs/python-version.txt
.venv/bin/python -m pip freeze > results/logs/python-packages.txt
tar -czf share/firesense-training-deliverables.tar.gz share/firesense-runtime.zip results/latest.md results/latest.json results/logs results/runs data/processed data/interim/sheikh
```

Use the same Bash terminal so `run_label` remains defined. `set -euo pipefail` stops on a failed command, including Python failing before `tee`. If the shell closes/exits after a failure, inspect the logs and repair the error before resuming.

## Optional weather rebuild and monitoring

If the input bundle lacks the two weather Parquets, omit their copy commands and rebuild them before readiness:

```powershell
# Windows, human-operated:
.venv\Scripts\python -m ws3_anomaly.loaders.weather --start 2000-11-01 --end 2026-11-03
```

```bash
# Linux, human-operated:
.venv/bin/python -m ws3_anomaly.loaders.weather --start 2000-11-01 --end 2026-11-03
```

Existing raw POWER tiles under `data/raw/power/` can be transferred first to resume acquisition. In a second terminal run `nvidia-smi -l 2`. GPU activity varies during I/O and statistical stages. Stage progress and completed fits are recorded in `results/runs/<timestamp>/execution.json` and `cuda-fits.jsonl`.

## Acceptance and deliverables

The final run must exit successfully, print `Pipeline complete`, and record `status: passed`, `quick: false`, and `start_stage: null` in its execution report. Verify real-data provenance, CUDA backend, all configured holdouts for both Terra+Aqua and Terra-only inputs, and all five QA groups. Inspect agreement, interval coverage, seam behavior, and forecast skill; B1 can legitimately beat the CUDA learner.

Return the generated `share/firesense-training-deliverables.zip` (Windows) or `.tar.gz` (Linux) through the shared drive. It contains:

- Deployment ZIP and SHA256 output.
- All `data/processed/` scientific outputs and five validation JSON files.
- `data/interim/sheikh/`: selected-method record, metrics, B1 parameters, CUDA count/FRP models and metadata, and panel.
- Quick/full logs and execution directories, latest Markdown/JSON results, Git SHA, Python/package versions, GPU and driver information.

Include actual elapsed times, failures, resumes, and any input/code changes in the accompanying message. Do not commit data, models, ZIPs, secrets, or run logs to Git. Keep backups until results are reviewed. A successful resumed run does not establish a fresh full-run benchmark; do not bypass QA or force GPU-model selection.

Full-run planning estimates: 4070 Laptop **18–25 minutes**, 3090 Desktop **13–22 minutes**, excluding installation/downloads/quick training. The 3090 has not been benchmarked; report actual timings.

For Render refresh, publish the approved runtime ZIP under a **new GitHub Release**, update its URL/SHA256 in `deployment/runtime.json`, then push that manifest. Render serves those existing artifacts; it never trains. See [RENDER.md](RENDER.md).

## Verification limits

The initialization changes passed PowerShell/Bash syntax checks and nine reviewed setup tests with external installs/probes mocked. No setup, GPU probes, fitting tests, or training were executed by the coding agent. A fresh native Linux installation and a fresh Windows installation using these commands still need to be performed by a human on the target machines.
