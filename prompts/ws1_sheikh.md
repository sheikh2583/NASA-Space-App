# Prompt pack: Sheikh (Team Member 1), harmonization, repo and integration
Folder: ws1_harmonize/ (plus repo setup and integration captain duties)

## P1.1 Repo setup (H0-1, timebox 60 minutes)
Inputs: this starter zip.
Prompt: "(The scripts in scripts/git/ and docs/GIT_WORKFLOW.md already cover most of this; use this prompt only for what is left, such as settings pages.) Give me the exact git and GitHub steps to: create a private repo from this folder, add six collaborators, replace the handles in .github/CODEOWNERS, protect main (pull request required, no force push), tag nothing yet, create a shared drive folder mirroring data/, and open a team channel with docs/HANDOFF_TEMPLATE.md and docs/TIMELINE.md pinned. Then list a 6-line hello-world pull request each teammate should make from their own folder."
Output: repo live; six hello-world PRs merged; shared drive writable by all. HANDOFF: link to everyone.
Test: every teammate can clone, push from their folder and read/write the shared drive.

## P1.2 Panel builder (H3-6)
Inputs: first grid_daily slice or a fixture; cells.parquet.
Prompt: "Write ws1_harmonize/panel.py: build_panel(grid_daily, cells, start, end) returning a dense cell-day table for cells that ever had a detection, with MODIS (Terra+Aqua combined) and VIIRS SNPP counts, high-confidence counts and FRP sums as separate columns, day/night splits, mean scan, and an active-satellite flag (Terra only before mid-2002). Missing grid_daily rows are zeros. Add pytest tests on a tiny synthetic input."
Output: panel.py + tests.
Test: rows = cells x days; column sums equal grid_daily sums.

## P1.3 Baselines B0 and B1 (H6-12)
Inputs: panel; common/metrics (temporary local copy until H12).
Prompt: "Write baselines.py. B0: one global ratio = sum(VIIRS count)/sum(MODIS count) over the overlap years. B1: ratio per admin1 region x calendar month, same formula. Provide fit_* and apply_* functions, applying to MODIS-only history. Also compute the 5th and 95th percentile of observed/predicted ratios over weekly region sums per region-month. Include tests on synthetic data where the true ratio is known."
Output: baselines.py + tests.
Test: on synthetic data the fitted ratio matches the known ratio within 1 percent.

## P1.4 Harmonized v0 and interval_table v0 (H12-14)  HANDOFF
Inputs: baselines; panel; contracts/parquet_schemas.json; json_schemas/interval_table.schema.json.
Prompt: "Write write_harmonized.py that produces harmonized.parquet exactly per contracts/parquet_schemas.json: value_count = observed SNPP count where SNPP exists (2012 onward), else the B1 estimate; modeled_count = B1 estimate wherever MODIS inputs exist; source = observed_viirs / modeled_from_modis / mixed; drift_flag False; method_version 'b1'. Also write interval_table.json v0: stratum 'region:<admin1_id>|month:<m>', res week and month, one magnitude bin (max_value null), lo_mult and hi_mult = the 5th and 95th percentile ratios divided by the median ratio, hi_add 0, level 0.9. Validate both files against the contracts."
Output: harmonized.parquet v0, interval_table.json v0. HANDOFF: to Sattyam, Monazir, Samin.
Test: lo <= value <= hi, no nulls or negatives, source on every row, for 2012+ weekly totals equal observed SNPP totals, JSON validates.

## P1.5 Features and LightGBM (H14-20)
Inputs: panel; common/splits (H12).
Prompt: "Write features.py and model.py. Features, MODIS-derived or static only: MODIS counts, high-confidence counts, FRP sum/max/mean, mean confidence, mean scan and track (day and night separately), the same for the 3x3 neighbourhood and the previous 7 days, sin/cos of day of year, coarse lat/lon, land-cover and cropland fractions, active-satellite flag. Forbidden: any VIIRS-derived feature and the year. Train LightGBM with a Poisson objective for counts and Tweedie for FRP sum. Add a test that fails if a forbidden column is in the feature list, and a leakage test that shuffles all VIIRS columns and checks predictions do not change."
Output: features.py, model.py, tests.
Test: both tests pass; training runs on a one-region slice.

## P1.6 Holdout evaluation and out-of-fold file (H20-24)  HANDOFF
Inputs: model; common/splits and metrics.
Prompt: "Write evaluate.py: evaluate B0, B1 and LightGBM on AOI-week sums under (a) spatial-block CV, (b) rolling temporal folds, (c) backward holdout (train 2018-2024, test 2012-2017). Report signed relative bias, RMSE on log1p, Spearman and Lin's CCC in one table. Then write predictions_oof.parquet (columns per contracts) with split labels from common/splits; calibration rows are never used for training."
Output: metrics table; predictions_oof.parquet. HANDOFF: to Samin.
Test: no calib or test row appears in training; file validates against the schema.

## P1.7 Harmonized v1 (H28-30)  HANDOFF
Inputs: model; drift_flags.parquet and interval_table.json v1 from Samin.
Prompt: "Write assemble_v1.py: produce harmonized.parquet v1 with the same value rule (observed SNPP where it exists, else LightGBM), method_version 'v1', drift_flag filled from drift_flags.parquet by region and year, and source flags correct. Run the seam check: modeled share drops to zero at 2012. Validate against the contract."
Output: harmonized.parquet v1. HANDOFF: to Sattyam.
Test: same checks as P1.4 plus the seam check.

## P1.8 Validation JSON and method notes (H32-34)  HANDOFF
Prompt: "Write validation/harmonization.json per contracts/json_schemas/validation_piece.schema.json with the metrics table for B0, B1 and LightGBM on all three holdouts, plus a limitations list (modeled before 2012; extrapolation; cell-level intervals indicative). Also write one page of method notes in plain language for Samiul: what was done, what is modeled, limits."
Output: harmonization.json, docs/method_notes_sheikh.md. HANDOFF: to Sattyam, Samiul.
Test: JSON validates; every number appears in the metrics table.

## P1.9 Integration-captain routine (standing)
Prompt: "Give me a 10-minute check-in agenda for H6, H12, H18, H24, H30, H36 and H42 (done / next / blocked, one line each), a 5-minute gate checklist, and a template for docs/CONTRACT_CHANGES.md entries. Remind me to update data/MANIFEST.md after each hand-off."
Output: a pinned agenda and checklist.
Test: every check-in produces a written blocker list with owners.

## P1.10 Verification tool and CI (after G0, H3-6)  HANDOFF
Inputs: contracts/parquet_schemas.json; contracts/json_schemas/.
Prompt: "Write tools/verify_files.py: given a path in data/processed/, detect the file type, check the columns, types and enum values against contracts/parquet_schemas.json or the matching JSON Schema in contracts/json_schemas/, and print PASS or the first 20 failing rows. Add a GitHub Actions workflow .github/workflows/ci.yml that runs pytest on every pull request, with no secrets and no network access. Add a short usage note to docs/VERIFY.md."
Output: tools/verify_files.py, ci.yml. HANDOFF: to everyone.
Test: a deliberately broken file prints failing rows; a valid file prints PASS; CI runs on a test pull request.
