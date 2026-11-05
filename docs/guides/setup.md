# Setup

How to install FireSense on a fresh Windows or Linux machine. Setup installs dependencies only and **never trains**.

## 1. Choose a mode

| Mode | Use it for | Needs | Windows (PowerShell) | Linux (Bash) |
|---|---|---|---|---|
| **UI only** | Working on the web app or API; the mock demo | Python 3.11, Node 22.12+ | `scripts\setup.ps1 -UiOnly` | `bash scripts/setup.sh --ui-only` |
| **Training only** | A GPU machine that only trains | Python 3.11, NVIDIA driver | `scripts\setup.ps1 -TrainingOnly` | `bash scripts/setup.sh --training-only` |
| **Everything** | Training plus the UI on one machine | All of the above | `scripts\setup.ps1` | `bash scripts/setup.sh` |

On Windows, run every `.ps1` script as `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\<name>.ps1 ...`, which works even when script execution is blocked. macOS supports **UI only**: there is no CUDA training on a Mac.

The training and everything modes run a few tiny GPU test fits to prove CUDA works. They are **human-only** ([AGENTS.md](../../AGENTS.md)).

## 2. Install the prerequisites

### Windows

```powershell
winget install --exact --id Git.Git --source winget
winget install --exact --id Python.Python.3.11 --source winget
winget install --exact --id 'Microsoft.VCRedist.2015+.x64' --source winget
winget install --exact --id OpenJS.NodeJS.LTS --source winget   # only for UI / everything
```

Close and reopen PowerShell so the new `PATH` takes effect. For training, `nvidia-smi` must print your GPU. Don't install the CUDA toolkit: the XGBoost wheel brings what it needs.

### Linux (Ubuntu / Debian, x86_64)

```bash
sudo apt-get update
sudo apt-get install -y git curl ca-certificates libgomp1
curl -LsSf https://astral.sh/uv/install.sh | sh
"$HOME/.local/bin/uv" python install 3.11
```

That installs a separate Python 3.11 and leaves the system Python alone. Pass it to setup with `--python "$("$HOME/.local/bin/uv" python find --system 3.11)"`. If your distro already has `python3.11` with `venv`, setup finds it by itself. For the UI you also need Node 22.12+ (for example from [nodejs.org](https://nodejs.org/) or `nvm`). Training needs a working NVIDIA driver (`nvidia-smi`), glibc 2.28+ and x86_64; ARM/Jetson and Alpine aren't supported.

## 3. Get the code and run setup

```bash
git clone https://github.com/sheikh2583/NASA-Space-App.git firesense
cd firesense
```

Then run the setup command for your mode from step 1. Setup:

1. Creates `.venv` with Python 3.11. It refuses a `.venv` from another OS: rename that folder and rerun.
2. Installs the pinned packages (`requirements.lock.txt`, plus `requirements-cuda.txt` for training) and runs `pip check`.
3. For training: checks the NVIDIA driver and fits tiny CUDA models for all four pipeline objectives.
4. For the UI: runs `npm ci` in `ws5_frontend/`. Stop any running Vite server first; on Windows it locks npm files.
5. Copies `.env.example` to `.env` (and the frontend one) only if they don't exist yet, and creates the `data/` folders.

It ends with **SETUP COMPLETE**. Rerunning is safe.

| Option | Windows | Linux |
|---|---|---|
| Use a specific Python 3.11 | `-PythonExecutable C:\path\python.exe` | `--python /path/to/python3.11` |
| Pick the GPU / helper threads for the probe | `-GpuId 1 -Threads 8` | `--gpu-id 1 --threads 8` |
| Accept compatible (unpinned) packages when the lockfile can't install | `-AllowCompatible` | `--allow-compatible` |

`-AllowCompatible` makes the environment non-reproducible. Use it only after reading the first install error.

## 4. First run: the mock demo

No data, GPU or keys are needed:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start.ps1 -Mock
```

```bash
bash scripts/start.sh --mock
```

The UI opens at <http://127.0.0.1:5173>, and the API docs are at <http://127.0.0.1:8000/docs>. **Ctrl+C** stops both. Without `-Mock` / `--mock` it serves your trained data from `data/processed/`.

## 5. Environment files

| Setting | File | Purpose |
|---|---|---|
| `FIRMS_MAP_KEY` | `.env` | Only for downloading recent FIRMS weeks through the API ([data guide](data.md)). Archive training doesn't need it. Never put it in a `VITE_*` variable. |
| `API_BASE_URL` | `.env` | API address for scripts and tests, normally `http://localhost:8000` |
| `VITE_API_BASE_URL` | `ws5_frontend/.env` | API address the browser calls; locally `http://localhost:8000` |
| `VITE_DATA_MODE` | `ws5_frontend/.env` | `synthetic` (mock) or `real`; the start scripts set it for you |

Vite reads `VITE_*` values when it starts, so restart it after changing them. Never commit `.env` files.

## Using the environment

Scripts call `.venv` Python directly, so you don't need to activate anything. To type `python` yourself, activate it once per terminal:

| Shell | Activate |
|---|---|
| PowerShell | `.\.venv\Scripts\Activate.ps1` |
| Bash | `source .venv/bin/activate` |

Next: [get the data](data.md), then [train](training.md).
