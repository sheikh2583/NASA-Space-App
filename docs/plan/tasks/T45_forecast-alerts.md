---
id: T45
title: Correct alert transitions and disable unsupported forecast alerts
kind: agent
owner: Samin
authors: ["Samin", "Sheikh"]
phase: P1
size: M
needs: ["T44"]
requires: []
branch: ws1/T45-forecast-alerts
touches: ["ws4_outlook/alerts.py", "ws4_outlook/run.py", "docs/science/decisions.md"]
creates: ["ws4_outlook/tests/test_alert_inputs.py"]
checks: ["CHECK-PLAN", "python -m pytest -q ws4_outlook/tests/test_alert_inputs.py"]
human_checks: [CHECK-QA]
---
## Goal
Make alert semantics agree with their rule and prevent observed status from masquerading as forecast evidence.

## Context
ws4_outlook/alerts.py; ws4_outlook/run.py; ws4_outlook/outlook.py; contracts/openapi.yaml.

## Steps
Test and fix watch->high when the genuine lower-bound percentile clears the threshold; retain high hysteresis until the point falls below 80. Define malformed/mismatched percentile inputs. Remove the caller that duplicates the current point as lower-bound evidence. Since this caller has no genuine forecast interval percentiles, explicitly disable forecast alerts there with an explanatory rule; preserve current_status. Any future activation requires validated forecast inputs. Tests exercise the pure state machine and caller wiring without running pipeline stages or training. Record the changed scientific behavior in a decision.

## Acceptance
85->95 with qualifying lower bounds promotes watch to high; insufficient uncertainty evidence cannot produce high; current-status UI remains distinct.

## Stop and ask if
Enabling alerts requires manufacturing forecast uncertainty or reusing current-status percentiles.

