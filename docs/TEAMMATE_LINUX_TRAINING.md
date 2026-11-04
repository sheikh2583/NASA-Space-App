# FireSense: training on a Linux laptop

A step-by-step guide for a teammate who trains the model on their own Linux laptop and sends the results back to Sheikh.

- Repo: https://github.com/sheikh2583/NASA-Space-App
- Works on: Ubuntu / Debian (64-bit x86 PC) with an **NVIDIA GPU**
- Time: about 10 minutes of your attention. Setup takes 5–15 minutes (depends on internet) and training about 15–25 minutes.
- Disk: at least **15 GB free**

**How it works:** Sheikh sends you one data ZIP. You put it in the repo and run **one command**. That command sets everything up, trains on your GPU, and builds a results ZIP. You send that ZIP back.

---

## Part A: Sheikh (Windows PC), before handing off

Build the input ZIP in PowerShell. This only packs files. It does not train anything. It takes a few minutes and ends with `INPUT ZIP: ...`.

```powershell
cd "X:\Nasa Space Apps Challenge\nasa-modis-viirs"
.\.venv\Scripts\python.exe scripts\teammate.py pack-inputs
```

The first line must point at the repo folder (the one that contains `.venv` and `scripts`). Otherwise PowerShell says `The module '.venv' could not be loaded`.

Send your teammate these **2 files** (Google Drive, USB, etc.), plus a link to this guide:

| Send | What it is |
|---|---|
| `share/firesense-training-inputs.zip` | All training inputs: FIRMS CSVs, boundaries, land cover, weather (about 200 MB, 21 files) |
| `share/firesense-training-inputs.zip.sha256` | Checksum so they can confirm the download isn't broken |

Never send `.venv/`, `.env`, `node_modules/`, or `share/firesense-runtime.zip`.

---

## Part B: teammate (Linux)

Open a terminal (**Ctrl+Alt+T**). Copy each grey block, paste it into the terminal (**Ctrl+Shift+V**) and press Enter. Wait until a block finishes before pasting the next one.

> If anything prints an **error**, stop. Send Sheikh a screenshot or the text. Don't try random fixes. Most problems are in the [troubleshooting](#if-something-goes-wrong) table at the bottom.

### Step 1: Check your laptop

```bash
echo "--- GPU ---";        nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || echo "PROBLEM: NVIDIA driver not working"
echo "--- CPU type ---";   uname -m
echo "--- Free disk ---";  df -h ~ | tail -1
```

What you should see:
- **GPU:** your NVIDIA card name, for example `NVIDIA GeForce RTX 4070 Laptop GPU, 8188 MiB, 5xx.xx`
- **CPU type:** `x86_64`
- **Free disk:** the 4th column (Avail) should be **15G** or more

If the GPU line says `PROBLEM`, install the driver (Ubuntu: `sudo ubuntu-drivers install`), **reboot**, and do Step 1 again.

### Step 2: Install the tools (first time only)

It will ask for your laptop password once (for `sudo`).

```bash
sudo apt-get update
sudo apt-get install -y git curl ca-certificates libgomp1 tmux
curl -LsSf https://astral.sh/uv/install.sh | sh
"$HOME/.local/bin/uv" python install 3.11
"$HOME/.local/bin/uv" python find --system 3.11
```

The last line should print a path ending in `python3.11`. This installs a separate Python 3.11 and doesn't touch your system Python.

### Step 3: Get the code

**If you DON'T have the repo yet:**

```bash
cd ~
git clone https://github.com/sheikh2583/NASA-Space-App.git firesense-training
cd ~/firesense-training
```

**If you ALREADY have it** (change the path if your copy is somewhere else):

```bash
cd ~/firesense-training
git checkout main
git pull --ff-only
```

If `git pull` complains about "local changes", run `git stash` and then `git pull --ff-only` again.

Make sure you have the training scripts. This should print `OK`:

```bash
ls scripts/teammate_train.sh scripts/teammate.py >/dev/null && echo OK
```

### Step 4: Add Sheikh's data ZIP

If you saved the files somewhere other than `~/Downloads`, change `DL=` to that folder. **Don't unzip the ZIP.** The script does that and checks every file.

```bash
DL=~/Downloads
mkdir -p data/incoming
rm -f data/incoming/*.zip
cp "$DL/firesense-training-inputs.zip" data/incoming/
expected="$(tr -dc '0-9a-f' < "$DL/firesense-training-inputs.zip.sha256")"
actual="$(sha256sum data/incoming/firesense-training-inputs.zip | cut -d' ' -f1)"
[ "$expected" = "$actual" ] && echo "CHECKSUM OK" || echo "CHECKSUM MISMATCH: download the ZIP again"
```

Continue only if it prints **`CHECKSUM OK`**.

### Step 5: Train (one command)

Before you start:
- **Plug in** the charger.
- Turn off auto-suspend: **Settings → Power → Automatic Suspend → Off**. Turn it back on afterwards.

Start a `tmux` session. Training then keeps running even if you close the terminal window by accident:

```bash
tmux new -s train
```

The screen goes blank with a green bar at the bottom. Go back to the repo, set **your name** (letters and numbers only, no spaces), and run:

```bash
cd ~/firesense-training
NAME=yourname
bash scripts/teammate_train.sh --name "$NAME" --python "$("$HOME/.local/bin/uv" python find --system 3.11)"
```

What happens, all automatically:
1. **Setup.** Creates `.venv`, installs packages, and checks that CUDA works on your GPU.
2. **Import.** Checks the data ZIP and unpacks it into `data/`.
3. **Training.** The full run on your GPU, with lots of output scrolling past.
4. **Packing.** Builds your results ZIP.

**Done** when you see:

```
SEND TO SHEIKH: /home/.../share/firesense-deliverable-<date>-yourname.zip
CHECKSUM: /home/.../share/firesense-deliverable-<date>-yourname.zip.sha256
```

Using `tmux`:
- Closed the window by accident? Open a terminal and run `tmux attach -t train`.
- Want to watch the GPU? Open another terminal and run `nvidia-smi -l 2`. Press Ctrl+C to stop watching. Low GPU use at times is normal.
- When finished, type `exit` to leave tmux.

### Step 6: Send the results to Sheikh

```bash
cd ~/firesense-training
ls -lh share/firesense-deliverable-*
xdg-open share/
```

That opens the folder. Send these **2 files** (Google Drive etc.):

| Send back | |
|---|---|
| `firesense-deliverable-<date>-yourname.zip` | Trained models, results, validation, logs, GPU info |
| `firesense-deliverable-<date>-yourname.zip.sha256` | Checksum |

Add a short message with:
- Your GPU model
- How long training took
- Whether anything failed or had to be re-run

**Never** `git commit` / `git push` data, models, ZIPs, or logs. They stay off GitHub.

---

## If something goes wrong

**Retrying is safe.** After fixing a problem, just run Step 5 again. Setup and data import pick up where they left off. Training starts over.

| Message / problem | What to do |
|---|---|
| `nvidia-smi: command not found` or `NVIDIA-SMI has failed` | Install the driver (`sudo ubuntu-drivers install`), reboot, and redo Step 1. |
| `uv: No such file or directory` | Step 2 didn't finish. Run Step 2 again. |
| `Install 64-bit Python 3.11` / `--python must select...` | Run `"$HOME/.local/bin/uv" python install 3.11`, then Step 5 again. |
| `.venv exists but has no Linux/macOS Python` | Run `mv .venv .venv-old`, then Step 5 again. |
| `Provide --name with a short teammate label` | `NAME=` is empty or has spaces/symbols. Use e.g. `NAME=samin`. |
| `First put the single FireSense training-inputs ZIP...` | `data/incoming/` must have exactly one ZIP. Redo Step 4. |
| `Use the FireSense training-inputs ZIP from Sheikh...` | Wrong ZIP (not the inputs ZIP). Redo Step 4 with `firesense-training-inputs.zip`. |
| `Input checksum mismatch` / `CHECKSUM MISMATCH` | The download is broken. Download the ZIP again and redo Step 4. |
| `Existing input differs` | Different data is already in this copy. Use a fresh copy (see below). |
| `Free more space` | Free up disk space (15 GB+), then Step 5 again. |
| CUDA / GPU check fails during setup | Usually the driver. Reboot, check `nvidia-smi`, then Step 5 again. If it still fails, send Sheikh the output. |
| Training stops with an error | Send Sheikh the newest log: `ls -t results/logs/teammate-*.log \| head -1` shows its name. |
| Laptop went to sleep / lost power | Turn off auto-suspend, plug in, and run Step 5 again. |
| `Cannot identify a single new full run` | Two trainings ran at once. Close all of them and run Step 5 once. |

**Start completely fresh** (a clean second copy, keeps the old one):

```bash
cd ~
git clone https://github.com/sheikh2583/NASA-Space-App.git firesense-training-2
cd ~/firesense-training-2
```

Then do Steps 4–6 inside `~/firesense-training-2` (in Step 5, `cd ~/firesense-training-2` instead).
