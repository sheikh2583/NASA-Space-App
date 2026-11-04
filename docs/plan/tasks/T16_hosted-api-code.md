---
id: T16
title: "Render data releases: publish a new runtime data version with one command"
kind: agent
owner: Sheikh
authors: [Sheikh]
phase: P1
size: M
needs: [T00]
requires: []
branch: ws1/T16-runtime-release
touches: [docs/guides/deployment.md]
creates: [scripts/release_runtime.py, scripts/tests/test_release_runtime.py]
checks: [CHECK-PLAN, "python -m pytest -q scripts/tests/test_release_runtime.py scripts/tests/test_runtime_bundle.py"]
---
## Goal
The hosted API already exists: one Render service builds the UI and serves FastAPI with data from a pinned GitHub
Release (`deployment/runtime.json`, `docs/guides/deployment.md`). What is still manual is publishing a **new** data version after
Sheikh's training runs (H02, H03). Make that one checked command, so T40 and T28 can do it without mistakes.

## Context
- `scripts/runtime_bundle.py pack` packages existing validated outputs into `share/firesense-runtime.zip` and prints
  its SHA256. Sheikh's `scripts/train.ps1 -Pack` / `train.sh --pack` already runs it at the end of a full run (H02,
  H03), so the zip is usually there already. `fetch` (used by the Dockerfile) refuses a bad checksum, synthetic or failed saved QA, unexpected files,
  or a populated target folder. Read both before writing anything.
- `docs/guides/deployment.md`, "Data delivery and updates": upload to a **new** versioned release; never replace an asset under
  a pinned URL; update the URL and SHA256 in `deployment/runtime.json`; commit and push. Render rebuilds on the commit.
- Release asset URLs look like
  `https://github.com/sheikh2583/NASA-Space-App/releases/download/<tag>/firesense-runtime.zip`.
- Packaging and uploading train nothing. This card must not change `Dockerfile`, `render.yaml` or the requirements.

## Steps
1. **`scripts/release_runtime.py`** (standard library only; `encoding="utf-8"` on every text read and write):
   - `plan_release(manifest: dict, zip_path: Path, tag: str, data_through: str) -> dict` returns the new manifest:
     `url` for the tag, `sha256` of the zip, `data_through`. It raises `ValueError` if the tag equals the tag in the
     current URL, or if `data_through` isn't an ISO date.
   - `default_tag(today: date, existing: set[str]) -> str` returns `runtime-YYYYMMDD-render-vN` with the lowest free `N`.
   - `main(argv)`:
     - `--data-through` (required) and `--tag` (default `default_tag`).
     - `--zip` (default `share/firesense-runtime.zip`). If it is missing, run `runtime_bundle.py pack` with the
       current interpreter. That only packages saved outputs; it trains nothing.
     - Without `--publish`, a dry run: print the new manifest and the commands it would run.
     - With `--publish`:
       - check that `gh release view <tag>` fails, meaning the tag is unused; otherwise stop;
       - `gh release create <tag> share/firesense-runtime.zip --title <tag> --notes "<data_through>; packaged from
         validated outputs; no training"`;
       - download the asset back to a scratch folder with `gh release download`, and compare its SHA256 with the
         local zip;
       - only then write `deployment/runtime.json` (2-space indent, trailing newline).
     - Every `gh` call goes through one `run(cmd)` function, so tests can replace it.
     - It never commits or pushes; it prints "Next: Sheikh commits deployment/runtime.json; Render rebuilds".
2. **`scripts/tests/test_release_runtime.py`** (no network, no `gh`, no real data):
   - `plan_release` gives the expected URL and checksum for a small zip made in `tmp_path`;
   - it refuses the current tag and a bad date;
   - `default_tag` skips existing versions;
   - with `run` replaced by a fake that records commands, `--publish` creates the release and writes the manifest;
   - when the fake reports that the tag exists, nothing is written;
   - when the downloaded checksum differs, nothing is written.
3. **`docs/guides/deployment.md`**, "Data delivery and updates": replace the manual steps with the dry run and the `--publish`
   command, keep the rules (new tag every time, never replace an asset), and add rollback: put the previous URL and
   SHA256 back in `deployment/runtime.json` and commit.
4. Run the checks and mark the card done. Then hand over for commit: Sheikh commits himself, unless he asked for the
   PR flow (`docs/plan/README.md` section 3).

## Acceptance
- [ ] The tests pass without network or data.
- [ ] A dry run on the laptop packs the zip and prints a manifest; paste it into the hand-over (no upload in this
  card).
- [ ] `deployment/runtime.json` is unchanged by this card.

## Stop and ask if
- `runtime_bundle.py pack` refuses the current outputs.
- `gh` is missing or isn't logged in as sheikh2583 when T40 or T28 first use `--publish`.
