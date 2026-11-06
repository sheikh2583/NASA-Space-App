# Training authorization and policy precedence

## Explicit instruction

On 6 November 2026, after discussing the roadmap and its training limitation, Sheikh instructed:

> I give you full reign on training, update and override, now how about that

This is the direct policy change required by the previous `AGENTS.md`. Agent-operated training/fitting is now authorized for implementing and validating the roadmap. The earlier no-training ban, human-only execution restrictions and no-more-training freeze no longer apply. Do not ask Sheikh to grant the same permission again.

The canonical current policy is [AGENTS.md](../../AGENTS.md). Older dated reviews remain historical evidence: the authorization does not retroactively change which tests/runs happened or make old scientific results current.

## What agents can execute

Agents can run supported local training, ratio estimation, calibration, model comparisons, outlook/drift fitting, readiness/CUDA probes, setup, fitting tests, full pytest, smoke, pipeline stages and integrated QA. Execution must follow a scientific-run spec with baseline preservation, source/input provenance and honest reporting across all holdouts.

Training permission is not a scientific result. Conditional interval failures still need diagnosis and measurement; revised forecast scores still need correct evaluation; model complexity does not earn a higher rating by itself.

## Current plan-runner integration

`scripts/plan.py` is intentionally left unchanged in this policy update. Its routine `checks` lane still rejects fitting, pipeline stages and blanket suites. That protects unrelated tasks from surprise execution. Its `human_checks` field and "Sheikh runs" messages are legacy names, not a current prohibition on agent execution.

For scientific work, read the commands, fixtures/imports and side effects, document the scientific-run card/spec, preserve outputs and execute the declared commands separately. This is the explicitly authorized scientific lane; it is not permission to disguise fitting as a routine check. Do not disable assertions or delete guard tests. A future runner enhancement should represent scientific commands explicitly rather than remove routine isolation.

H02/H03 remain completed historical runs. Their old "no more training" note has been superseded, not erased. New runs need new attributable scientific work items; a training authorization does not justify marking an old run as revalidated.

## Required run record

- Hypothesis/change, method/spec version and predeclared acceptance criteria.
- Source commit and any working-tree patch; input, parameter, interval and report hashes.
- Separate training, calibration, selection and evaluation roles, including disclosure of already inspected tests.
- Environment, CUDA device, configuration, seeds, commands, elapsed times, logs and run status.
- Preserved baseline and fresh run outputs, including all failed attempts and all relevant holdout results.
- Separate engineering, scientific and live-delivery dispositions before a new runtime release.

Use one pipeline per shared output tree. Preserve raw NASA inputs, prior accepted results and run backups. Keep models/data/logs outside Git. Maintain server-side credentials and the established commit/push workflow.

## Immediate effect on the roadmap

Q04's scientific-remediation route is now authorized for implementation and numerical validation after Q03 diagnosis and a concrete run spec. The limited historical-product route remains a fallback if evidence fails. No fitting was performed merely to record this policy change, and the current 6.5/10 assessment has not been increased.

## Subsequent Git execution authorization

On 6 November, while starting implementation, Sheikh instructed: "auto commit push using my credentials in the ssh in this pc". Agents may now commit verified scaffold/card work and push it to the existing repository using configured local SSH authentication. Earlier manual-commit handover wording is superseded. Preserve unrelated edits, stage only reviewed paths, use normal fast-forward pushes and report actual failures. No private key contents are read or printed; no force-push or unperformed human review is implied.
