# FireSense claim register

Established by T51 from the [protected baseline](../results/BASELINE_2026-11-06.md) at scaffold commit `4f0340a`, observed 2026-11-06T12:52:52.085970+00:00. This is an internal evidence/wording register, not a new public API status schema. [Challenge IDs](../plan/CHALLENGE_CONTRACT.md) distinguish verified core intent (C) from internal quality controls (Q).

## Evidence keys

- **E1:** saved `harmonized.parquet`, cells/grid/sensor calendar and current aggregation/writer source; producer-commit compatibility remains to be completed.
- **E2:** saved `method.json` / `metrics.csv` and named historical execution reports; historical selection, not numerical confirmation of revised code.
- **E3:** saved `interval_table.json` and `validation/intervals_by_stratum.json`; severe conditional failure and missing monthly target label.
- **E4:** saved `outlook_region.json` / skill report; revised forward-evaluation evidence pending.
- **E5:** current season/anomaly/weather/period source over existing saved artifacts; derived meanings do not establish causal or physical fire truth.
- **E6:** committed runtime manifest and dated live-check record; no fresh post-scaffold deployment observation in T51.
- **E7:** observed intended-user evidence is currently missing. T61 supplies the neutral [study protocol](../../ws6_validation/USER_STUDY.md); H06 supplies actual observations. A prepared protocol is not impact validation.
- **E8:** external corroboration and final submission assets are incomplete; current resource/format verification remains limited.

Exact hashes, dates, row counts and backup/recovery locations are in the baseline. A claim supported by source code is not automatically supported by numerical/user evidence.

## Claim, audience and wording controls

| ID / challenge | Audience | Permitted claim and evidence state | Source/run/target | UI/export locations | Prohibited inference | Required next evidence |
|---|---|---|---|---|---|---|
| CL01 / C01 | All users | Historical activity is expressed as SNPP-equivalent detections; implemented, scope-limited | E1, count/reference scale | Chart, summary, CSV, Method, pitch | Actual distinct fires, burned area, emissions or all fires detected | T53/T56/T58 target/provenance |
| CL02 / C02 | Area users | Loaded catalog has eight Bangladesh divisions plus Punjab/Haryana/Delhi; API selects retained cells | E1, 2,532 retained cells | Area inspector, map, help | Arbitrary polygon acquires globally harmonized data | T54/T60 support/equivalence |
| CL03 / C01 | Scientific users | Observed SNPP, adjusted NOAA-20 and modeled MODIS are distinct; source priority follows availability | E1, source/calendar conventions | Legends, chart, CSV, brief | Every date inside the SNPP era is observed; adjusted means raw observed SNPP | T53/T58 source/cutoff checks |
| CL04 / Q01 | Judges/technical | B1 is the saved selected method; selection CCC 0.8900 versus 0.8775 is historical | E2, named historical holdouts/combinations | Validation, Method, submission | Classification accuracy or fresh confirmation of repaired features | T53/T56 all-holdout comparison |
| CL05 / Q01 | All users | 90% is a nominal interval target; current saved conditional bands are not accepted | E3, seven stop rows | Chart, Validation, Method, CSV, brief, tour | Uniform calibrated 90% reliability or accepted bands from marginal coverage | T54-T58 empirical support/disposition |
| CL06 / Q01 | Scientific users | Saved monthly report lacks target identity; revised calendar-month procedure needs new evidence | E3 versus current calendar-month daily allocation | Validation, Method, release dossier | Old Monday-month results validate current served calendar months | T53/T54/T56 aligned target |
| CL07 / C03 | All users | Zero requires operating-source support; unavailable periods are unknown | E1, local-solar days and coverage | Calendar, chart, status, CSV | Operating means cloud-free observation of every location/fire | T53/T60 availability cases |
| CL08 / C04 | Monitoring users | Current-status percentiles compare the latest eligible historical week with prior history | E1/E4, served record/complete-week cutoff | Status/season panels, brief | Wall-clock live fire conditions or future risk probability | T59/T60 missing/cutoff/reference tests |
| CL09 / C04 | All users | Saved forecast skill is not demonstrated in all 11 regions and alerts are off | E4, saved 2026-11-05 outlook | Outlook, Method, pitch | Demonstrated operational warning or validated future bound from a historical percentile | T59/S02 complete forward evidence |
| CL10 / C03 | Planners | p10-p90 is a central detected-activity window; seasonal trends need era/coverage/source caveats | E5, fixed season windows and saved history | Season card, calendar, brief | Physical beginning/end of burning or cause of a timing shift | T14/T15/T56/T58 compatible evidence |
| CL11 / C05 | Analysts | Weekly anomalies/critical periods rank unusual detected activity against a historical reference | E5, retrospective comparison | Calendar, periods, CSV | Damage ranking, emergency declaration or unbiased detection of every unusual season | T14/T15/T60 reference/support |
| CL12 / Q01 | Analysts | Weather panels describe associations | E5, saved regional analysis | Drivers, Method, brief | Weather caused a particular fire/activity change | T58 wording and retained inference limits |
| CL13 / C05 | Land users | Cropland shares/season fallback provide agricultural context | E5, land-cover association | Periods, Method, brief | Verified ignition-cause classifier or all crop burning identified | T58/T60 interpretation |
| CL14 / Q01 | Technical | FRP assumptions remain uncalibrated and optional feature is deferred | E1/E5, sampled FRP/count-ratio caveat | Method/limitations; no promised view | Continuous intensity/energy or validated cross-sensor FRP uncertainty | Separate reopened T25 scientific scope |
| CL15 / Q02 | Area users | Uncertainty applicability is limited to its evaluated domain, currently incompletely characterized | E3, overlap-era rectangle sampling | AOI warnings, Validation, export | <=400-cell rectangle diagnostics certify every full administrative AOI | T54/T57/T58 coherent supported-domain audit |
| CL16 / C06 | Judges/users | Product usefulness is a hypothesis until actual task evidence exists | E7 | Pitch, brief rationale, impact section | Adoption, decision benefit, saved losses or real participants from an agent simulation | T61/H06 observed tasks |
| CL17 / Q04 | Operators | Earlier review recorded e97d49f live; no fresh live check after scaffold push | E6, observation-specific | Release report, status updates | Latest commit is deployed merely because push succeeded | T28 live revision/runtime inspection |
| CL18 / Q01/Q04 | Operators | Runtime archive is checksum-pinned and serving reads existing artifacts | E6, manifest record end 2026-11-03 | Health, deployment, dossier | Serving fetches today's observations or pinned packaging accepts scientific quality | T57/T28 evidence compatibility |
| CL19 / Q03 | Scientific users | MCD64A1 is planned corroboration with shared MODIS inputs and small-burn limits | E8 | Future Validation/Method | Independent ground truth, absolute fire truth or guaranteed favorable correlation | T33/T24 declared sample/QA/geometry |
| CL20 / Q05 | Judges | AI use must describe actual coding/analysis/media history; disclosure file is currently absent | E8, missing docs/AI_USE.md | Submission and references | Human reviews or contributors that did not occur | T29 actual disclosure and T35 format check |
| CL21 / Q01 | Technical | Five saved engineering/check groups passed historically; science acceptance is separate | Saved QA 2026-11-05, no scientific_acceptance field | Validation, dossier, pitch | All scientific gates passed because QA process exited successfully | T57 recomputed scoped gate |
| CL22 / C06/Q05 | Judges | Brief, guided tour, study and final assets are planned, not current delivered evidence | E7/E8 | Feature list, submission | Planned features/languages/evidence portrayed as already delivered | T22/T23/H06/T29/T35 actual outputs |

## Promotion and maintenance

Update a row only with attributable new evidence and preserve the prior status in its linked run report. T56 records numerical trial outcomes, T58 carries support into product wording, T28 records verified release identity, and T63 audits the final claims/rating.

This register does not authorize a source/output-contract change. Use the corresponding card/spec/contract decision. A completed implementation row may still carry failed/limited scientific evidence. Missing participant observations or unavailable current resource sheets remain explicit, not inferred from other checks.
