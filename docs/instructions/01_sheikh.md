# Sheikh (Team Member 1): your instructions
Your job: build the harmonized series, set up the repo, keep everyone in step.
Folder: ws1_harmonize/. Prompt pack: prompts/ws1_sheikh.md. Always paste docs/AI_PREAMBLE.md first.

## Before the event (no project code)
1. Register your own FIRMS key and Earthdata login. Read docs/PIPELINE.md and docs/DECISIONS.md.
2. Ask the organizers: the venue's real hours and submission deadline; whether this starter structure may be brought; AI-use disclosure rules; licence rules. Tell everyone the answers and shift docs/TIMELINE.md if the hours differ.

## H0 to H1: repo
3. Unzip the starter, check the repo URL in scripts/config.sh (default: https://github.com/sheikh2583/NASA-Space-App), run `bash scripts/git/init_repo.sh`, `bash scripts/git/setup.sh sheikh2583`, `bash scripts/git/invite_collaborators.sh` and `bash scripts/git/protect_main.sh` (docs/GIT_WORKFLOW.md section 1). Do prompt P1.1 for the rest. Replace the handles in .github/CODEOWNERS. Invite all six.
4. Create the team channel. Pin docs/HANDOFF_TEMPLATE.md and docs/TIMELINE.md. Create the shared drive folder.
5. Ask each person to push a hello-world pull request from their own folder.
6. Talk to Sattyam: tell him contracts/openapi.yaml is ready for him to complete by H3.

## H1 to H3: kickoff
7. Run the 15-minute kickoff round: confirm the six slots (swap by preference), walk through docs/PIPELINE.md, read out docs/DECISIONS.md.
8. At H3 call G0: contracts frozen. Talk to Sattyam and Shammo: confirm the mock server answers. Talk to Samiul: confirm he has the fixtures.

## H3 to H14: first harmonization
9. Do P1.2 and P1.3 on the first Bangladesh slice. Talk to Monazir at H4: confirm the slice arrived. Talk to Sattyam at H6: confirm grid_daily is on track for H8.
10. Run the check-ins at H6 and H12 (done / next / blocked).
11. Talk to Samin: confirm splits and metrics arrive at H12 and that split labels are block_id % 5 (0 calib, 1 test).
12. At H8 call G1. At H14 finish P1.4 and post a HANDOFF to Sattyam, Monazir and Samin (harmonized v0 and interval_table v0).

## H14 to H30: learned model
13. Do P1.5 and P1.6. At H24 post a HANDOFF to Samin with predictions_oof.parquet. Call G2 and run the check-in.
14. Talk to Samin: confirm drift_flags.parquet and interval_table v1 arrive by H30.
15. Do P1.7 at H28 to H30; post a HANDOFF to Sattyam. Call G3.

## H30 to H46: finish
16. Do P1.8 by H34: HANDOFF to Sattyam and Samiul (validation JSON and method notes). Call the feature freeze at H36 and the code freeze at H42.
17. Update data/MANIFEST.md after every hand-off and docs/CONTRACT_CHANGES.md after every contract change.
18. Tag the final build, then submit at H46 with Samiul's checklist.

## Rules and fallbacks
- Never write conformal or drift code (Samin does). Never sum cell-level lo/hi.
- If you fall behind, ship B1 with honest wording and ask Samin to take a defined piece of evaluation.

## Manual tasks
Things an AI agent cannot do for you are listed under your name in docs/MANUAL_TASKS.md, and repeated inside each of your phase prompts (prompts/phases/).

## Your workspace, what you may write, how to verify
- Work in: your laptop with your own venv (python3.11 -m venv .venv). Use a Kaggle notebook for LightGBM only if the laptop is too slow; save outputs to the shared drive. Branch prefix: ws1/.
- You may write: ws1_harmonize/; data/processed/harmonized.parquet, predictions_oof.parquet, interval_table.json (v0 only), validation/harmonization.json; contracts/parquet_schemas.json and json_schemas/; docs/ (except Samiul's files). You merge pull requests into contracts/ and common/.
- You must not write: any other folder, or any data file another person owns (docs/FILE_OWNERSHIP.md).
- Verify before each HANDOFF: run tools/verify_files.py on the file; run the DuckDB checks for your stage in docs/VERIFY.md; run pytest ws1_harmonize/tests.
- Also do P1.10 (prompts/ws1_sheikh.md) after G0 so everyone has the verification tool.
