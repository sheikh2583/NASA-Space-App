---
id: H01
title: "Sheikh: create the Hugging Face Space and token"
kind: human
owner: Sheikh
phase: P2
size: S
needs: [T16]
---
## Goal
The hosted API needs your account. This takes about 10 minutes and costs nothing.

## Steps
1. On huggingface.co, sign in (or sign up). Create a Space:
   - SDK **Docker**;
   - hardware **CPU Basic (free)**;
   - visibility **public**;
   - name `firesense-api`.
2. Create an access token with write access, under Settings → Access Tokens. Store it **only** on the laptop: run
   `huggingface-cli login` in the project's virtual environment, or put `HF_TOKEN=…` in `.env`. Never paste it into
   chat or a commit.
3. Tell the agent: "H01 is done, Space is <account>/firesense-api". The agent records it with
   `python scripts/plan.py set H01 done --note "<account>/firesense-api"` and continues with T17.

## Done when
- The Space exists, and `python scripts/plan.py next` no longer skips T17 for a missing token.
