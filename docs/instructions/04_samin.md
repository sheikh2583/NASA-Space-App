# Samin (Team Member 4): your instructions
Your job: the shared library, calibrated intervals, drift checks and the outlook.
Folders: common/ and ws4_outlook/. Prompt pack: prompts/ws4_samin.md. Paste docs/AI_PREAMBLE.md first.

## H0 to H12: shared library
1. Talk to Sattyam: ask which columns he needs from series.py. Talk to Monazir: ask which climatology functions he needs. Talk to Sheikh: agree the split labels (block_id % 5: 0 calib, 1 test).
2. Do P4.1 to P4.3. At H10 post a HANDOFF to Sattyam, Monazir and Sheikh.
3. Do P4.4. At H12 post a HANDOFF of splits.py and metrics.py to Sheikh and Samiul.

## H12 to H24: outlook floor and conformal groundwork
4. Ask Sheikh for harmonized v0 (H14). Do P4.7 (include current_status, which is never cut).
5. Prepare conformal code on fixtures. Talk to Sheikh: agree the exact columns and timing of predictions_oof.parquet (H24).

## H24 to H30: intervals and drift
6. Do P4.5 and P4.6 as soon as the out-of-fold file lands. Talk to Sattyam: confirm interval_table v1 loads in the API.
7. At H30 post a HANDOFF of interval_table.json v1 and drift_flags.parquet to Sheikh and Sattyam.
8. At H26 take the weather loaders from Monazir.

## H30 to H36: outlook and validation pieces
9. Do P4.8. Talk to Shammo: agree how the status no_demonstrated_skill is worded. At H34 post a HANDOFF to Sattyam and Shammo.
10. Do P4.9: validation pieces by H34. Stretch: the burned-area comparison.

## Rules and fallbacks
- Never change split definitions silently. Never sum cell-level intervals. Never hide a no-skill result.
- If you fall behind, cut alerts, then the forecast; keep the season-to-date comparison; ship empirical-quantile intervals if conformal slips.

## Manual tasks
Things an AI agent cannot do for you are listed under your name in docs/MANUAL_TASKS.md, and repeated inside each of your phase prompts (prompts/phases/).

## Your workspace, what you may write, how to verify
- Work in: your laptop; a Kaggle notebook for conformal sampling or the forecast if the laptop is slow (save outputs to the shared drive). Branch prefix: ws4/.
- You may write: common/; ws4_outlook/; data/processed/drift_flags.parquet, outlook_region.json, interval_table.json (v1 only), validation/intervals.json, drift.json, outlook_skill.json, mcd64a1.json.
- You must not write: other folders. Others import common/ and never edit it; tell them to ask you.
- Verify before each HANDOFF: pytest common/ and ws4_outlook/tests; read your own coverage table; tools/verify_files.py on every file; the splits test (no calib or test row in training).
