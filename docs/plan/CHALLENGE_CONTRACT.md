# Challenge contract and evidence boundaries

Established 6 November 2026 for the revised scaffold. This maps verified challenge intent to reviewable outcomes; it is not a substitute for unavailable official resource/submission sheets.

## Sources and confidence

- [Official MODIS/VIIRS challenge](https://www.spaceappschallenge.org/2026/challenges/modis-and-viirs-hot-spots/): direct retrieval returned HTTP 502 on 6 November. An indexed summary was available in the preceding review. Full resources were not verified.
- [CONAE challenge announcement, 28 October 2026](https://www.argentina.gob.ar/noticias/desafio-nasa-space-apps-challenge-2026-crea-soluciones-para-monitorear-incendios-con-datos): retrieved 6 November. This is the challenge proposer's primary government announcement. It describes combining sensor records in a web application, regional selection, temporal activity and recent/historical comparisons for monitoring audiences.
- [Participant FAQ](https://www.spaceappschallenge.org/resources/participant-faqs/) and [terms](https://www.spaceappschallenge.org/legal/): direct refresh returned HTTP 502. Preserve the dated findings in [RULES_CHECK.md](../RULES_CHECK.md); do not call them freshly reverified. Organizer/eligibility decisions remain Sheikh's responsibility; do not contact anyone automatically.

Submission fields, current judging weights, media limits and local deadline remain verification items in T35. Seven slides, 30-second video and a 90-second tour are internal design targets, not verified official mandates.

## Traceability

The first six rows paraphrase the verified core intent. The remaining rows are project quality controls. Their thresholds are not NASA requirements.

| ID | Outcome | Implemented/planned evidence | Owning cards |
|---|---|---|---|
| C01 | Comparable MODIS/VIIRS record | Reference quantity, separate source labels, overlap evaluation and no double-counted satellite sum | T53-T56, T58 |
| C02 | Geographic selection | Named area and polygon/cell membership stay consistent; unsupported geography is explicit | T60 |
| C03 | Temporal activity/calendar | Day/week/month consistency, season windows, ranked periods and complete/missing distinctions | T14, T15, T60 |
| C04 | Recent versus historical comparison | Same-cutoff status and comparable periods with source/date labels | T59, T60 |
| C05 | Unusual conditions and critical periods | Interpretable weekly/seasonal findings without invented causal attribution | T14, T15, T60 |
| C06 | Useful web application for monitoring audiences | Browser journey, downloadable brief and observed task evidence | T22, T34, T61, H06 |
| Q01 | Scientific validity/provenance | Current targets, held-out diagnostics, explicit acceptance and compatibility | T51-T59 |
| Q02 | Honest spatial support | Loaded regions and interval applicability visible; no claim arbitrary AOIs acquire global data | T54, T58, T60 |
| Q03 | Corroboration and limits | Burned-area comparison discloses shared MODIS inputs and small-burn limitations | T33, T24 |
| Q04 | Accessible and reliable delivery | Actual interaction evidence, bounded resource measurements and live revision/runtime check | T27, T34, T62, T28 |
| Q05 | Reproducible, attributed submission | Sources, licences, AI-use disclosure, truthful assets and verified format limits | T29, T35, T63 |

## Scope

The submission is a regional historical burning-activity explorer. Forecast alerts, daily NRT acquisition, globally populated coverage and additional sensor families are not treated as verified mandatory capabilities. Defer them unless they solve a demonstrated user problem within the remaining capacity.

Maintain these interpretations: detections are not distinct fires or burned area; modeled MODIS, adjusted NOAA-20 and observed SNPP are distinct; weather is association; season timing is a central activity window. A supported historical comparison is useful even when forecast skill is absent.

## Claim discipline

Every headline claim needs an entry in the T51 claim register: source/run/target, evidence state, audience, UI/export location and permissible wording. Unknown resource-sheet details stay unknown until T35 verifies them. Do not add competitors' features as challenge requirements or treat a subjective 9/10 ambition as an acceptance measurement.
