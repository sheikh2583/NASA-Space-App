---
id: H01
title: "Sheikh: confirm the Render service, add the FIRMS key there, and note its URL"
kind: human
owner: Sheikh
phase: P0
size: S
needs: [T00]
---
## Goal
Render serves the UI and the live API from one free Docker service (`docs/guides/deployment.md`). Only you can sign in to
Render. This takes about 10 minutes and costs nothing. (Hugging Face is no longer used; the file name is historical.)

## Steps
1. If the service doesn't exist yet, create it exactly as in `docs/guides/deployment.md`, "Fill in the New Web Service form":
   Docker, branch `main`, Free plan, health check path `/health`, auto-deploy on commit.
2. In the service's **Environment** tab, add `FIRMS_MAP_KEY` with your key, as a secret value. Only the backend reads
   it, for the live season feed (T18, T19). Until T18 is merged, nothing uses it. Never paste the key into chat or a
   commit.
3. Open `https://<your-service>.onrender.com/health`. It must report `status: ok`. The first request after a sleep can
   take about a minute.
4. On the laptop, add one line to `.env`: `RENDER_URL=https://<your-service>.onrender.com`. The URL isn't a secret, but
   keeping it in `.env` lets `plan.py next` see it.
5. Tell the agent: "H01 is done". It runs `python scripts/plan.py set H01 done --note "<service URL>"` and continues
   with T17.

## Done when
- `/health` answers `status: ok`, the key is set in Render, and `RENDER_URL` is in `.env`.
