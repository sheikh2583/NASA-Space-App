# Teammate training (Windows or Linux)

For a teammate who trains on their own NVIDIA laptop and sends the results back to Sheikh. **Human-only** ([AGENTS.md](../../AGENTS.md)).

**How it works:** Sheikh sends one input ZIP. You put it in the repo and run **one command**, which sets up, checks the data, trains on your GPU, and builds a results ZIP. You send that ZIP back.

- Repo: <https://github.com/sheikh2583/NASA-Space-App>
- Needs: an **NVIDIA GPU** with a working driver, 64-bit Windows 10/11 or Ubuntu/Debian x86_64, and **15 GB free disk**
- Time: about 10 minutes of your attention. Setup takes 5–15 minutes, training about 15–25.

---

## Part A: Sheikh, before handing off

Build the input ZIP from the repo folder. It only packs files; nothing is trained:

```powershell
cd "X:\Nasa Space Apps Challenge\nasa-modis-viirs"
.\.venv\Scripts\python.exe scripts\teammate.py pack-inputs
```

Send the teammate the **2 files** it creates, plus a link to this page:

| Send | What it is |
|---|---|
| `share/firesense-training-inputs.zip` | FIRMS CSVs, boundaries, land cover, weather (about 200 MB, 21 files) |
| `share/firesense-training-inputs.zip.sha256` | Checksum |

Never send `.venv/`, `.env`, `node_modules/` or `share/firesense-runtime.zip`.

---

## Part B: teammate

Run each block in order. If a block shows an **error**, stop and send Sheikh a screenshot. Don't try random fixes; check the [table at the bottom](#if-something-goes-wrong) first.

### Windows (PowerShell)

**1. Check the GPU.** This should print your NVIDIA card:

```powershell
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
```

If it fails, install the driver from [nvidia.com/drivers](https://www.nvidia.com/drivers), reboot, and try again.

**2. Install the tools (first time only).** Then close and reopen PowerShell:

```powershell
winget install --exact --id Git.Git --source winget
winget install --exact --id Python.Python.3.11 --source winget
winget install --exact --id 'Microsoft.VCRedist.2015+.x64' --source winget
```

**3. Get the code.** If you don't have it yet:

```powershell
cd $HOME
git clone https://github.com/sheikh2583/NASA-Space-App.git firesense-training
cd $HOME\firesense-training
```

If you already have it:

```powershell
cd $HOME\firesense-training
git checkout main
git pull --ff-only
```

**4. Add Sheikh's ZIP.** Don't unzip it. Change `$dl` if you saved it somewhere else:

```powershell
$dl = "$HOME\Downloads"
New-Item -ItemType Directory -Force data\incoming | Out-Null
Remove-Item data\incoming\*.zip -ErrorAction SilentlyContinue
Copy-Item "$dl\firesense-training-inputs.zip" data\incoming\
$expected = (Get-Content "$dl\firesense-training-inputs.zip.sha256" -Raw).Trim().ToLower()
$actual = (Get-FileHash data\incoming\firesense-training-inputs.zip -Algorithm SHA256).Hash.ToLower()
if ($expected -eq $actual) { 'CHECKSUM OK' } else { 'CHECKSUM MISMATCH: download the ZIP again' }
```

**5. Train.** Plug in the charger and set sleep to **Never** (Settings → System → Power). Then run it with **your name** (letters and numbers only):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\teammate_train.ps1 -Name yourname
```

### Linux (Ubuntu / Debian)

**1. Check the GPU:**

```bash
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
uname -m          # must print x86_64
df -h ~ | tail -1 # "Avail" should be 15G or more
```

If `nvidia-smi` fails, run `sudo ubuntu-drivers install`, reboot, and try again.

**2. Install the tools (first time only):**

```bash
sudo apt-get update
sudo apt-get install -y git curl ca-certificates libgomp1 tmux
curl -LsSf https://astral.sh/uv/install.sh | sh
"$HOME/.local/bin/uv" python install 3.11
```

**3. Get the code.** If you don't have it yet:

```bash
cd ~ && git clone https://github.com/sheikh2583/NASA-Space-App.git firesense-training && cd ~/firesense-training
```

If you already have it:

```bash
cd ~/firesense-training && git checkout main && git pull --ff-only
```

**4. Add Sheikh's ZIP.** Don't unzip it:

```bash
DL=~/Downloads
mkdir -p data/incoming && rm -f data/incoming/*.zip
cp "$DL/firesense-training-inputs.zip" data/incoming/
expected="$(tr -dc '0-9a-f' < "$DL/firesense-training-inputs.zip.sha256")"
actual="$(sha256sum data/incoming/firesense-training-inputs.zip | cut -d' ' -f1)"
[ "$expected" = "$actual" ] && echo "CHECKSUM OK" || echo "CHECKSUM MISMATCH: download the ZIP again"
```

**5. Train.** Plug in the charger and turn off auto-suspend (Settings → Power). Start `tmux`, so closing the window doesn't stop training; `tmux attach -t train` gets you back:

```bash
tmux new -s train
```

Then, inside tmux, with **your name**:

```bash
cd ~/firesense-training
bash scripts/teammate_train.sh --name yourname --python "$("$HOME/.local/bin/uv" python find --system 3.11)"
```

### What the command does (both systems)

1. **Setup:** creates `.venv`, installs packages, and checks CUDA on your GPU.
2. **Import:** checks every file in the ZIP against its checksum and unpacks it into `data/`.
3. **Training:** the full run on your GPU, with lots of scrolling output. To watch the GPU, run `nvidia-smi -l 2` in a second terminal.
4. **Packing:** builds your results ZIP.

It's **done** when it prints:

```
SEND TO SHEIKH: .../share/firesense-deliverable-<date>-yourname.zip
CHECKSUM: .../share/firesense-deliverable-<date>-yourname.zip.sha256
```

---

## Part C: send the results back

Send Sheikh **both files** from `share/`: the `firesense-deliverable-…zip` and its `.sha256`. Open the folder with `explorer share` (Windows) or `xdg-open share/` (Linux).

The ZIP holds the trained models, processed outputs, validation, logs, a runtime ZIP, and GPU and package info. Add a short message with your GPU model, how long training took, and whether anything failed or was re-run.

**Never** commit or push data, models, ZIPs or logs.

---

## If something goes wrong

**Retrying is safe.** After fixing a problem, run step 5 again. Setup and the import resume; training starts over.

| Message / problem | What to do |
|---|---|
| `nvidia-smi` not found / failed | Install the NVIDIA driver, reboot, and redo step 1. |
| `Install 64-bit Python 3.11` | Redo step 2. On Linux: `"$HOME/.local/bin/uv" python install 3.11`. |
| `.venv exists but has no ... Python` | Rename the folder (`.venv` → `.venv-old`) and redo step 5. |
| `Provide --name ...` / `-Name` rejected | Use letters, numbers, `-` or `_` only, e.g. `samin`. |
| `First put the single FireSense training-inputs ZIP...` | `data/incoming/` must contain exactly one ZIP. Redo step 4. |
| `Use the FireSense training-inputs ZIP from Sheikh...` | That's the wrong ZIP. Use `firesense-training-inputs.zip`. |
| `Input checksum mismatch` / `CHECKSUM MISMATCH` | The download is broken. Download it again and redo step 4. |
| `Existing input differs` | Different data is already here. Clone a fresh copy into a new folder (step 3). |
| `Free more space` | You need about 15 GB free. |
| CUDA check fails during setup | Usually the driver: reboot and check `nvidia-smi`. If it persists, send the output to Sheikh. |
| Windows: script execution is blocked | Use the exact `powershell -NoProfile -ExecutionPolicy Bypass -File ...` line above. |
| Training stops with an error | Send Sheikh the newest `results/logs/teammate-*.log`. |
| `Cannot identify a single new full run` | Two trainings ran at once. Close them all and run step 5 once. |
