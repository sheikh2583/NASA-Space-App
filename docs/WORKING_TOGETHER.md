# Working together without stepping on each other

## 1. One writer per path
Docs/FILE_OWNERSHIP.md lists the only person who writes each path. You read everything; you write only your own.
Never edit a file you do not own, even for a one-line fix. Ask the owner (section 7).

## 2. Git
Use the scripts in scripts/git/ (docs/GIT_WORKFLOW.md); they enforce the rules below with hooks and a pull-request check.
- Branch from main with your prefix: `ws1/...` (Sheikh), `ws2/...` (Sattyam), `ws3/...`, `ws4/...`, `ws5/...`, `ws6/...`.
- Commit small and often. Before you push: `git pull --rebase origin main`. Never force-push main.
- Open a pull request into main. The owner of the changed folder merges it once the guard check passes. contracts/ and common/ also need Sheikh's review before merging.
- A pull request touches only your own folder. If it touches anything else, split it.
- Never commit data files, keys or .env. Never commit notebook outputs.
- After G2 main stays deployable: merge only work that has passed its tests.

## 3. Data files
- Work in data/interim/<your-name>/. When the tests pass, copy the file to data/processed/ under a temporary name, then rename it, so nobody reads half a file.
- Then post the HANDOFF message and add one line to data/MANIFEST.md (append at the bottom).
- Consumers copy the file to their own machine before using it. Never write into data/processed/ unless you are the owner.
- Keep the previous version until the receiver says GOT IT (name it `*_prev`).

## 4. Environments
- Everyone uses their own virtual environment and their own `.env`. Never share a venv or a key.
- Each person registers their own FIRMS key (limits are per key).
- Do not run Sattyam's laptop API as a shared service. Use the hosted mock or live API.
- Add a Python package only by asking Sheikh (it goes into requirements.txt). Add a web package in ws5_frontend/package.json yourself.

## 5. Deploy targets are separate
- API: Sattyam's account. Web app: Shammo's project. Static fallback JSON: a separate site owned by Sattyam.
- The web app reads the fallback address from an env var, so no one writes into another person's deploy.

## 6. Shared documents
- docs/DECISIONS.md and TIMELINE.md change only through Sheikh. MANIFEST.md and CONTRACT_CHANGES.md are append-only.
- Report bugs in the channel or Samiul's bug list; do not edit someone else's code to fix them.

## 7. When you need a change in someone else's file
1. Post in the channel: who, which file, exactly what, and by when.
2. The owner makes the change (or says no and why) and posts a HANDOFF.
3. If it is a contract change, Sheikh approves and logs it in docs/CONTRACT_CHANGES.md first.
4. Keep working on the fixture or stub until it lands.

## 8. If two people collide
Stop, tell Sheikh, and let the owner of the path decide. Do not resolve a conflict in someone else's file.
