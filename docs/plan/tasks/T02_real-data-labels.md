---
id: T02
title: Remove the false "synthetic data" labels from the live validation page
kind: agent
owner: Samin
authors: [Samin, Shammo]
phase: P0
size: S
needs: [T00]
requires: [real-data]
branch: ws1/T02-real-data-labels
touches: [ws4_outlook/run.py, ws5_frontend/public/demo/snapshot.json]
creates: [ws4_outlook/tests/test_run_labels.py]
checks: [CHECK-PLAN, CHECK-PY, CHECK-QA, CHECK-FILES, CHECK-SNAP]
---
## Goal
The live Validation page says "Built on SYNTHETIC data; rerun on real data before quoting." under drift, intervals
and outlook skill, although the 4 Nov run used real FIRMS data. Fix the text at its source and relabel the existing
pieces without recomputing anything.

## Context
- `ws4_outlook/run.py` hard-codes that sentence in `step_intervals`, `step_drift` and `step_outlook`.
- `ws1_harmonize/run.py` `step_validation` already does this correctly: it looks for files under
  `data/raw/firms/*.csv*` whose names don't start with `synthetic_`.
- Re-running the drift or outlook steps would recompute flags and forecast skill. That is not wanted here, so this
  card only rewrites the sentence in the existing JSON files.

## Steps
1. In `ws4_outlook/run.py`, add `import glob` and this function:
   ```python
   def data_note() -> str:
       real = any(not os.path.basename(p).startswith("synthetic_") for p in glob.glob("data/raw/firms/*.csv*"))
       return ("These results were computed on downloaded FIRMS observations." if real
               else "Built on synthetic development data; rerun on real data before quoting.")
   ```
   Replace the three hard-coded sentences with `data_note()`.
2. Add a relabel step and register it in the dispatch dict at the bottom (`"relabel": step_relabel`):
   ```python
   def step_relabel():
       """Rewrite the data-source sentence in existing pieces; recomputes nothing."""
       for name in ("intervals", "drift", "outlook_skill"):
           path = f"{P}/validation/{name}.json"
           if not os.path.exists(path):
               continue
           piece_ = json.load(open(path))
           piece_["limitations"] = [data_note() if ("SYNTHETIC" in l or "synthetic development data" in l
                                    or "downloaded FIRMS observations" in l) else l for l in piece_["limitations"]]
           with open(path, "w") as f:
               json.dump(piece_, f, indent=1)
   ```
   Update the module docstring's usage lines too.
3. Create `ws4_outlook/tests/test_run_labels.py`. It must work in CI (no `data/`): use `monkeypatch.chdir(tmp_path)`
   and create files there.
   - With only `data/raw/firms/synthetic_x.csv.gz`, `data_note()` mentions "synthetic".
   - With `data/raw/firms/fire_archive_M-C61_1.csv`, it mentions "downloaded FIRMS observations".
   - `step_relabel()` on a piece containing the old sentence replaces it, keeps every other limitation, and doesn't
     touch any other key.
4. On the laptop with data, run in order:
   - `python -m ws4_outlook.run relabel`
   - `python -m ws6_validation.qa`
   - `python scripts/export_hosted_demo.py`
5. Check: `python -c "import json;s=json.load(open('ws5_frontend/public/demo/snapshot.json'));print([k for k,p in s['validation']['pieces'].items() if any('SYNTHETIC' in l for l in p['limitations'])])"`
   must print `[]`.
6. Run the checks, mark the card done, then commit with `split` (Samin: `ws4_outlook/`; Shammo: the snapshot), push
   and open the PR.

## Acceptance
- [ ] The new tests pass in CI, without data.
- [ ] No validation piece in `snapshot.json` mentions SYNTHETIC; the output of the step 5 check is pasted in the PR.
- [ ] `git diff --stat` shows that only `snapshot.json` changed under `ws5_frontend/`. `data/` is never committed.
- [ ] CHECK-QA: all five groups pass. CHECK-FILES passes.

## Stop and ask if
- QA fails after relabelling.
- `export_hosted_demo.py` refuses to export.
