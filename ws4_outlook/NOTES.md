# NOTES (ws4_outlook)

## Decisions and assumptions
- common/: grid.py and regions.py added (grid convention and satellite windows shared by all).
- conformal: lower multiplier taken at each magnitude bin's lower edge (the contract has no additive lower term); without this
  coverage was 36%. Held-out coverage on synthetic data: about 95% weekly, 97% monthly (slightly conservative).
- drift: CUSUM on observed/predicted per region-year after 2012; classifier two-sample test before 2012.
- outlook: current_status and season position computed live per AOI by the API; forecast skill per region in batch.
  Alerts stay off unless the forecast CI excludes zero.

## Known issues
- On synthetic data most regions show no_demonstrated_skill, which the app explains in plain words.

## AI assistance log (where AI tools helped)
- 2026-11-03: everything in this folder was written with Claude (AI assistant) at Sheikh's direction before the event, on synthetic data, and assigned to this workstream's owner. Review it before relying on it; rerun on real data.
