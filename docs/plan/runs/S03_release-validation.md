# S03: integration and release validation

Agent-operated under AGENTS.md; this is a scientific-validation specification because full tests/QA can fit learners and rewrite validation outputs. It does not instruct repeating S01 training by default.

## Preconditions

Read the invoking card's exact legacy human_checks list and all relevant fixtures/import/setup paths. Preserve the accepted candidate/baseline, source patch, input/report hashes and current QA before any command. Use one writer per output tree; no live process reads replaced local artifacts.

## Commands

Run only the invoking card's declared scientific commands: typically `python -m pytest -q` and/or `python scripts/workflow.py validate`. T52's scientific selector executes this lane separately from ordinary checks. If a test fits or mutates artifacts, capture that activity and isolate temporary paths; never treat a test learner's output as production evidence.

Do not execute smoke as an automatic extra model fit. Add it only for an unresolved integration concern after reviewing its full execution path and declaring its side effects. Authorized execution is not a reason to duplicate compatible completed validation.

## Acceptance and report

Record interpreter/environment, command, source/artifact identity, counts, exit codes and warnings. Read generated QA and scientific acceptance independently. Confirm target, record end, table/report compatibility and forecast disposition were not silently changed by tests. Restore only intended validated scientific outputs from verified backups if a test wrote to shared locations; never erase failed-run evidence.

An engineering failure is fixed or reported. Scientific stop rows remain visible; no test count accepts them. T28 links the actual evidence to the release dossier and verifies it live after publication. T15/T21/T24 may use this spec for scoped integration validation with their actual artifact versions; they do not inherit permission to silently refit the whole harmonization procedure.
