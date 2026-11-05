# Debugging and tests

Commands use the activated `.venv` (`python`). Without activation, use `.venv\Scripts\python` (Windows) or `.venv/bin/python` (Linux/macOS).

## Checks that need no data and no GPU

```bash
python -m pip check
python -m compileall -q common scripts ws1_harmonize ws2_platform ws3_anomaly ws4_outlook
python -m pytest scripts/tests/test_bootstrap.py scripts/tests/test_runtime_bundle.py scripts/tests/test_share_zip.py ws2_platform/tests/test_frontend_hosting.py -q
python scripts/plan.py check
```

The pytest line is what CI runs ([`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)). Frontend checks, from `ws5_frontend/`:

```bash
npm test
npm run check:strings
npm run build
```

## Wider checks (human-only: some tests fit models)

```bash
python scripts/workflow.py smoke     # unit/script tests, fixture API, frontend tests and build; ends with SMOKE PASSED
python -m pytest -q                  # the whole configured suite, including real-output QA after training
```

Run one test verbosely, or stop in the debugger on the first failure:

```bash
python -m pytest ws1_harmonize/tests/test_harmonize.py -x -vv -s
python -m pytest ws1_harmonize/tests/test_harmonize.py -x --pdb
```

Real CUDA integration tests run only on a configured NVIDIA machine:

```powershell
$env:FIRESENSE_TEST_CUDA = '1'; python -m pytest ws1_harmonize/tests/test_cuda.py -q; Remove-Item Env:FIRESENSE_TEST_CUDA
```

```bash
FIRESENSE_TEST_CUDA=1 python -m pytest ws1_harmonize/tests/test_cuda.py -q
```

## Run the servers separately

Terminal 1, the API (`mock_server` for fixtures, `app` for trained data):

```bash
python -m uvicorn ws2_platform.api.mock_server:app --host 127.0.0.1 --port 8000 --reload
```

Terminal 2, the UI:

```bash
npm run dev --prefix ws5_frontend -- --host 127.0.0.1 --strictPort
```

For fixture mode, set `VITE_DATA_MODE=synthetic` in `ws5_frontend/.env`. Use the browser's DevTools (Console and Network) for requests. `/health` reports the method version, cell count and data-through date, and `/docs` lets you try requests. Quick health check from any shell:

```bash
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=30).read().decode())"
```

## Common problems

| Symptom | Next action |
|---|---|
| Wrong Python / missing module | `python -c "import sys; print(sys.executable)"` must point into this repo's `.venv`. Rerun setup and `pip check`. |
| `.venv` from another OS or Python | Rename it and rerun setup. Never copy virtual environments between machines. |
| Native geospatial/HDF package fails to install | Keep Python 3.11 and read the first error ([setup](setup.md)). |
| `NOT READY`, missing files, or API file-not-found | Complete the named inputs ([data](data.md)). Use the mock UI meanwhile. |
| CUDA unavailable / CPU rejected | Check the driver and GPU ID, then `python scripts/workflow.py gpu-check` (human-only). |
| npm `EPERM` / `EBUSY` on Windows | Stop this project's Vite, test and preview processes, then rerun setup. |
| Port 8000 or 5173 busy | Stop the earlier server (Ctrl+C). The launcher refuses busy ports on purpose. |
| UI can't reach the API | Check `VITE_API_BASE_URL` and restart Vite. The UI has no offline fallback: it always calls the API. |
| Stale results | Restart the API after data changes and Vite after `.env` changes. |
| Map tiles fail | Check the network and the OSM tile policy. The FIRMS key isn't used for tiles. |

## A useful bug report

Include the failing command, the first relevant traceback, the OS, `python --version`, `python -m pip check`, and for frontend issues `node --version` and `npm --version`. For GPU problems add `nvidia-smi` and the `gpu-check` output; for training problems add the run's `execution.json`. Remove credentials and any URL that contains a key before you share logs.
