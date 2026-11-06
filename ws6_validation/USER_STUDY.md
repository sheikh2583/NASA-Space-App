# Formative user-study protocol

Prepared by the coding agent under T61. **Protocol only: no participants have been contacted, observed or endorsed the product.** H06 is the actual human-evidence task. The [claim register](../docs/project/claim-register.md) remains at missing evidence for usefulness until observations exist.

## 1. Audience and purpose

Primary audience assumption: a Bangladesh environmental/agricultural analyst or planning practitioner who uses regional seasonal information. Punjab provides a contrasting case, not a substitute audience. Include at least two relevant practitioners among 3-5 participants where feasible; identify other participants as proxies without naming their organizations in Git.

This is formative usability/comprehension work. It can identify confusion and plausible usefulness; it cannot estimate population adoption, prevented fires, avoided losses or emergency-response effectiveness. Tool use by the agent is not participant evidence.

## 2. Ownership, privacy and consent

Sheikh recruits/contacts participants and requests consent. The agent prepares tasks, analyzes anonymized notes and makes authorized implementation fixes; it sends no invitations or messages.

Suggested introduction: “We are checking whether this regional satellite-history tool is understandable and useful. We are testing the tool, not you. You may skip any task or stop at any point. We would like to keep anonymized notes; recording is optional and requires separate agreement. Please avoid entering personal or confidential work information.”

Record consent outside Git. Use participant codes only in shared notes; no names, contact details, employer names, voices, faces or identifying screen content in the repository. Keep any identity/code mapping in Sheikh's private storage. If someone declines notes/recording, respect that choice. Do not use a participant quotation in public material without the corresponding consent.

## 3. Session readiness

H06 starts after T60 and T22 deliver the core journey and brief. Before recruitment/session execution:

1. Record exact app commit, runtime/data cutoff, scientific disposition, browser/device and which features are available.
2. Curate two supported area/season cases from the actual served data. Freeze a researcher answer key: AOI ID, dates, source/coverage, comparable cutoff, permissible inference and evidence source. Do not hardcode remembered trend values.
3. Include a quiet eligible period and, if the real supported record has one, an unavailable/partial-coverage period. If no suitable live case exists, record that limitation; a separately labelled comprehension scenario does not count as a delivered product case.
4. Confirm selection, comparison and export operate. A broken/unbuilt feature is an implementation readiness failure, not a participant failure.
5. Give the participant the task sheet only. Keep answer keys, desired interpretations and the comprehension rubric out of view until their independent attempt is recorded.

Record a brief context description (broad role, relevant data familiarity, proxy/practitioner) without collecting unnecessary demographics. Aim for 20-30 minutes, but report actual duration rather than claiming that target was achieved.

## 4. Neutral participant task sheet

Use names/dates from the frozen case sheet. Do not describe the expected click sequence or numerical answer.

| Task | Prompt | Observable output |
|---|---|---|
| A: seasonal pattern | “For this region, find when detected activity is usually concentrated. Show where you found that information and explain it in your own words.” | Selected region/window and interpretation |
| B: historical comparison | “Compare these two seasons using the tool. Tell a colleague what changed, which comparison you chose and one limitation.” | Comparable dates/cutoff, source recognition and qualified conclusion |
| C: quiet period | “Interpret this period. What can you conclude from the displayed information, and what remains uncertain?” | Zero/missing/partial distinction and observation limits |
| D: shareable output | “Prepare something you could send to a colleague for this region and season. Explain a plausible use and a use you would avoid.” | Brief/export with date, source, limitations and realistic use |

After each independent attempt, ask “What led you to that conclusion?” and “Was anything unclear?” After all tasks, ask how the tool would fit their existing workflow and what information they would need before acting. Do not solicit agreement with a promised impact claim.

## 5. Assistance and measurement

Start timing after the task is read; stop when the participant declares completion or stops. Record interrupted time separately. Use think-aloud only if comfortable; silent completion is valid.

Allow normal questions but count assistance consistently:

- **0 prompts:** no navigation/interpretation help beyond repeating the task.
- **1 neutral prompt:** “What would you try next?” or pointing back to the task without naming a control/answer.
- **2+ prompts/direct help:** record every hint and whether the answer was effectively supplied.

Separate task completion from interpretation correctness. Mark completed, partial, unable, declined or not run with a reason. A completed export with a false claim remains a comprehension failure.

## 6. Researcher comprehension rubric

Assess the participant's first explanation before correction. After recording it, provide an accurate explanation where necessary and record whether the later explanation improved; do not count taught comprehension as independent discovery.

| Topic | Adequate interpretation | Material confusion |
|---|---|---|
| Reference/source | Recognizes observed SNPP, adjusted NOAA-20 and modeled MODIS differ | Calls modeled/adjusted values directly observed SNPP |
| Quantity | Understands detections are not distinct fires or burned area | Interprets counts as validated burned hectares/number of fires |
| Season | Understands a central detected-activity window | Calls p10/p90 physical fire onset/end |
| Availability | Distinguishes zero with coverage from missing/partial observations | Treats no observation as verified no fire |
| Freshness | Can find the record cutoff and relate status to that record | Assumes historical status reflects wall-clock live conditions |
| Uncertainty | Notices limited/unsupported evidence and avoids a guarantee | Treats a nominal band as validated for every AOI |
| Warning | Does not interpret this as demonstrated future emergency risk | Treats percentile/status as a validated forecast alert |

Classify confusion severity: **critical** if it could reverse scientific meaning or support an unsupported action; **major** if it prevents a core task or hides an essential source/date/coverage limit; **minor** for recoverable friction without a misleading conclusion. Frequency and severity are both reported; one critical case is not dismissed because the other tasks passed.

## 7. Blank observation record

This is an unused template, not a participant entry:

```text
Participant code: [assigned privately; no personal identifiers]
Role class: [relevant practitioner / proxy / other, broad description]
Consent for anonymized notes: [recorded by Sheikh outside Git]
Session time and app/runtime identity:
Device/browser and supported case IDs:
For each task A-D:
  outcome / actual seconds / interruptions / prompt count and exact help:
  first explanation (anonymized paraphrase):
  source/date/coverage interpretation:
  confusion, severity, reproduction and affected claim ID:
  post-explanation comprehension, if taught (separate result):
Plausible workflow/use and stated limitations:
Follow-up questions or unresolved issue:
```

No example success, invented quote or synthetic participant row belongs in the results. The agent may test this form mechanically, but that remains a form check.

## 8. Analysis and acceptance

With five participants, the formative design target is at least four completing the core journey with no more than one neutral prompt. Report raw counts and denominators; with fewer people, do not present a precise population success rate. Disclose selection bias, proxy status and all not-run/declined tasks.

Report independently demonstrated and taught comprehension separately. Critical source/quantity/missingness/warning confusion must be fixed or retained as an unresolved limitation, even if the small completion target was met. Seek follow-up with a fresh participant where feasible after prioritized fixes; record when only the same participant was available.

T34 consumes the issue list and observed evidence. H06 is complete only after actual observations and their limitations are supplied. If recruitment is unavailable, keep it missing or explicitly defer it through Sheikh's scope decision. T63 retains the impact-evidence deduction. No score, endorsement or adoption claim follows merely from completing T61.
