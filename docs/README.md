# Documentation

## Guides: how to do things

| Guide | For |
|---|---|
| [Setup](guides/setup.md) | Installing on Windows or Linux: UI-only, training-only, or everything |
| [Data](guides/data.md) | Accounts, the NASA and boundary downloads, and where each file goes |
| [Training](guides/training.md) | The one-command CUDA training run, acceptance, monitoring and recovery (human-only) |
| [Teammate training](guides/teammate-training.md) | Training on a teammate's laptop from an input ZIP and sending results back |
| [Deployment](guides/deployment.md) | The Render service (UI and API), publishing new data, the legacy Pages snapshot |
| [Debugging](guides/debugging.md) | Tests, running the servers separately, common problems, bug reports |
| [Git workflow](guides/git-workflow.md) | Branch and pull-request helpers in `scripts/git/` |

## Science: how it works

| Doc | Content |
|---|---|
| [Method (English)](science/method_en.md) | The short public method text shown in the app. [Bangla](science/method_bn.md) is an unreviewed draft and is not shown in the app. |
| [Pipeline](science/pipeline.md) | The project in plain words, stage by stage |
| [Decisions](science/decisions.md) | Numbered science and data decisions (these win over older notes) |
| [CUDA pipeline](science/cuda-pipeline.md) | How the GPU learners, device checks and selection work |
| [Area selection](science/area-selection.md) | The named-area explorer and boundary sources |
| [Glossary](science/glossary.md) | Terms in plain words |

## Results: what was measured

| Doc | Content |
|---|---|
| [Training results](results/training-results.md) | The current accepted numbers. Quote numbers from here, with their source |
| [CUDA results](results/cuda-results.md) | GPU verification evidence and the selection correction |
| [GPU time estimates](results/gpu-training-times.md) | RTX 4070 / 3090 planning ranges and their assumptions |

## Project: plan, contracts, checklists

| Doc | Content |
|---|---|
| [Plan](plan/README.md) · [Status board](plan/STATUS.md) · [Cards](plan/tasks/) | The task plan run with `python scripts/plan.py` |
| [Specs](specs/) | Feature specs (season profile, coverage and outages) |
| [Contract changes](project/contract-changes.md) | Append-only log of API and data contract changes |
| [File ownership](project/file-ownership.md) | Who writes which path |
| [Known gaps](project/known-gaps.md) | Risk register and disclaimers |
| [Challenge alignment](project/challenge-alignment.md) | How the project maps to the official challenge |
| [Tech stack](project/tech-stack.md) | Tools and versions |
| [QA checklist](project/qa-checklist.md) · [Submission checklist](project/submission-checklist.md) · [Demo script](project/demo-script.md) | Release and presentation |

## For coding agents

[AGENTS.md](../AGENTS.md) (rules, including no training) · [CLAUDE.md](../CLAUDE.md) · [Claude handoff](agents/claude-handoff.md) · [Claude review](agents/claude-review.md)
