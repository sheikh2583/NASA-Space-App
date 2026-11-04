# Prompt pack: Sheikh (Team Member 1), harmonization, repo and integration
Folder: ws1_harmonize/ (plus repo setup and integration captain duties)

## P1.1 Repo setup (H0-1, timebox 60 minutes)
Inputs: this starter zip.
Prompt: "(The scripts in scripts/git/ and docs/GIT_WORKFLOW.md already cover most of this; use this prompt only for what is left, such as settings pages.) Give me the exact git and GitHub steps to: push this folder to the existing public repo (github.com/sheikh2583/NASA-Space-App; judges need a public link), add six collaborators, replace the handles in .github/CODEOWNERS, protect main (pull request required, no force push), tag nothing yet, create a shared drive folder mirroring data/, and open a team channel with docs/HANDOFF_TEMPLATE.md and docs/TIMELINE.md pinned. Then list a 6-line hello-world pull request each teammate should make from their own folder."
Output: repo live; six hello-world PRs merged; shared drive writable by all. HANDOFF: link to everyone.
Test: every teammate can clone, push from their folder and read/write the shared drive.

## P1.2 Panel builder (H3-6)
Inputs: first grid_daily slice or a fixture; cells.parquet.
Prompt: "Write ws1_harmonize/panel.py: build_panel(grid_daily, cells, start, end) returning a dense cell-day table for cells that ever had a detection, with MODIS (Terra+Aqua combined), VIIRS SNPP and VIIRS NOAA-20 counts, high-confidence counts and FRP sums as separate columns, day/night splits, mean scan, and a satellite-combination column (terra_only before Aqua's first day in July 2002, terra_aqua after). grid_daily is keyed by sat; missing rows are zeros only where sensor_days.parquet says that satellite was operating, otherwise NaN (decision 18). Add pytest tests on a tiny synthetic input."
Output: panel.py + tests.
Test: rows = cells x days; column sums equal grid_daily sums.

## P1.3 Baselines B0 and B1 (H6-12)
Inputs: panel; common/metrics (temporary local copy until H12).
Prompt: "Write baselines.py. B0: one global ratio = sum(SNPP count)/sum(MODIS count) over the overlap years. B1: ratio per admin1 region x calendar month, same formula. Fit both per satellite combination: terra_only uses Terra counts only (so it applies to Nov 2000 to Jul 2002), terra_aqua uses both (decision 19). Use only days on which all satellites involved were operating. Also fit the NOAA-20 to SNPP ratio per region x month on the SNPP/NOAA-20 overlap with the same code (decision 17). Provide fit_* and apply_* functions, applying to MODIS-only history. Also compute the 5th and 95th percentile of observed/predicted ratios over weekly region sums per region-month. Include tests on synthetic data where the true ratio is known."
Output: baselines.py + tests.
Test: on synthetic data the fitted ratio matches the known ratio within 1 percent.

## P1.4 Harmonized v0 and interval_table v0 (H12-14)  HANDOFF
Inputs: baselines; panel; contracts/parquet_schemas.json; json_schemas/interval_table.schema.json.
Prompt: "Write write_harmonized.py that produces harmonized.parquet exactly per contracts/parquet_schemas.json: value_count = observed SNPP count on SNPP operating days (sensor_days), NOAA-20 count x the NOAA-20-to-SNPP ratio after the SNPP cutoff (2 Nov 2026), else the B1 estimate; modeled_count = B1 estimate wherever MODIS inputs exist; source = observed_viirs / adjusted_from_noaa20 / modeled_from_modis / mixed; observed rows have lo = hi = value (decision 21); drift_flag False; method_version 'b1'. Also write interval_table.json v0: stratum 'region:<admin1_id>|month:<m>', res week and month, one magnitude bin (max_value null), lo_mult and hi_mult = the 5th and 95th percentile ratios divided by the median ratio, hi_add 0, level 0.9. Validate both files against the contracts."
Output: harmonized.parquet v0, interval_table.json v0. HANDOFF: to Sattyam, Monazir, Samin.
Test: lo <= value <= hi, no nulls or negatives, source on every row, on SNPP operating days weekly totals equal observed SNPP totals, JSON validates.

## P1.5 Features and CUDA XGBoost (H14-20)
Inputs: panel; common/splits (H12).
Prompt: "Maintain features.py and model.py using the CUDA setup in docs/TRAINING.md and common/compute.py. Features must be MODIS-derived or static, never VIIRS-derived or year. Train XGBoost CUDA with Poisson for counts and Tweedie for FRP sum; verify actual CUDA placement and reject fallback. Preserve forbidden-column and leakage tests. This is an experiment template; inspect current features and validation before proposing changes."
Output: features.py, model.py, tests.
Test: both tests pass; training runs on a one-region slice.

## P1.6 Holdout evaluation and out-of-fold file (H20-24)  HANDOFF
Inputs: model; common/splits and metrics.
Prompt: "Maintain evaluate.py: evaluate B0, B1 and XGBoost CUDA on AOI-week sums across every configured holdout, for both Terra+Aqua and Terra-only inputs. Preserve spatial, temporal, backward, and drift-era checks and calibration separation in common/splits. Report signed relative bias, RMSE on log1p, Spearman and Lin's CCC, and write predictions_oof.parquet per contract. Select using both satellite configurations; do not force the learned candidate to win."
Output: metrics table; predictions_oof.parquet. HANDOFF: to Samin.
Test: no calib or test row appears in training; file validates against the schema.

## P1.7 Harmonized v1 (H28-30)  HANDOFF
Inputs: model; drift_flags.parquet and interval_table.json v1 from Samin.
Prompt: "Maintain assemble_v1.py: produce harmonized.parquet v1 using observed SNPP on operating days, adjusted NOAA-20 after the cutoff, and the method selected in method.json for reconstruction. B1 can win against XGBoost CUDA. Preserve method version, drift flags, provenance, contract validation, and scientific seam checks; account for operating-day gaps rather than assuming every post-2012 day is observed."
Output: harmonized.parquet v1. HANDOFF: to Sattyam.
Test: same checks as P1.4 plus the seam check.

## P1.8 Validation JSON and method notes (H32-34)  HANDOFF
Prompt: "Write validation/harmonization.json per contracts/json_schemas/validation_piece.schema.json with B0, B1 and XGBoost CUDA metrics across all configured holdouts and both satellite-input combinations. Record compute backend and selected method, and limitations for pre-2012 modeling, extrapolation, and indicative cell-level intervals. Keep quick-run metrics distinct from full evaluation. Explain what was modeled and the limits in plain language."
Output: harmonization.json, docs/method_notes_sheikh.md. HANDOFF: to Sattyam, Samiul.
Test: JSON validates; every number appears in the metrics table.

## P1.9 Integration-captain routine (standing)
Prompt: "Give me a 10-minute check-in agenda for H6, H12, H18, H24, H30, H36 and H42 (done / next / blocked, one line each), a 5-minute gate checklist, and a template for docs/CONTRACT_CHANGES.md entries. Remind me to update data/MANIFEST.md after each hand-off."
Output: a pinned agenda and checklist.
Test: every check-in produces a written blocker list with owners.

## P1.10 Verification tool and CI (after G0, H3-6)  HANDOFF
Inputs: contracts/parquet_schemas.json; contracts/json_schemas/.
Prompt: "Write tools/verify_files.py: given a path in data/processed/, detect the file type, check the columns, types and enum values against contracts/parquet_schemas.json or the matching JSON Schema in contracts/json_schemas/, and print PASS or the first 20 failing rows. Add a GitHub Actions workflow .github/workflows/ci.yml (permissions: contents: read) that runs pytest on every pull request, with no secrets and no network access. data/ is not in git and there is no API in CI, so tests that need data files or API_BASE_URL must call pytest.skip when they are missing; CI runs only the unit tests and the contract-file checks. Add a short usage note to docs/VERIFY.md."
Output: tools/verify_files.py, ci.yml. HANDOFF: to everyone.
Test: a deliberately broken file prints failing rows; a valid file prints PASS; CI runs on a test pull request.
