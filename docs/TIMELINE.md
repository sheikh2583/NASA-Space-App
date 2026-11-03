# Timeline and workflow (hours from the start; shift everything if the venue's real hours differ)

> Disclaimer: hour estimates are judgement and assume a continuous 48 hours; confirm the venue's real hours at H0 (docs/KNOWN_GAPS.md items 13 and 14).

| Phase | Hours | Goal | Who does what |
|---|---|---|---|
| Prep | before | Start fast | Everyone: accounts (Earthdata, own FIRMS key), read data notes. No project code. |
| 1 Kickoff | H0-3 | Everyone can start; G0 at H3 | Sheikh: repo, contracts skeleton, hello-world PRs (H0-1), kickoff round. Sattyam: openapi + fixtures + mock (H3). Monazir: FIRMS key, first slice. Samin: start common/. Shammo: scaffold on mock. Samiul: QA checklist + test scaffolds (H4). |
| 2 Data | H3-8 | Gridded data exists; G1 at H8; check-in H6 | Monazir: slice H4, full H6. Sattyam: hosting hello-world H4, grid + cells H8. Sheikh: panel + baseline code. Samin: series, climatology, intervals (H10). Shammo: demo link + key list (H8). Samiul: data QA (H10). |
| 3 Floor | H8-24 | Draw area -> calendar -> flagged periods; G2 at H24; check-ins H12, H18, H24 | Sheikh: v0 + interval v0 (H14), LightGBM prototype, OOF (H24). Sattyam: live API + fallback (H16). Monazir: stub (H8), anomalies v0 (H18). Samin: splits/metrics (H12), outlook floor, conformal on fixtures. Shammo: live UI (H16). Samiul: end-to-end run (H24). |
| 4 Core | H24-30 | Learned series with calibrated intervals, where-map and current-status card; G3 at H30 | Sheikh: finalize LightGBM, v1. Samin: conformal + drift, interval v1 (H30). Monazir: robust anomalies (H26). Sattyam: all endpoints on v1. Shammo: bands, badges, drift icon. Samiul: end-to-end (H30). |
| 5 Scale-up | H30-36 | Drivers, outlook, comparison, validation page; freeze H36 | Monazir: drivers (H36). Samin: outlook + validation pieces (H34). Sheikh: validation JSON + method notes (H34). Sattyam: /meta/validation (H34). Shammo: all panels (H36). Samiul: qa.json, end-to-end (H36). |
| 6 Polish | H36-42 | Fix, translate, rehearse; code freeze H42 | Bug fixes only. Samiul: method text (H38), slides (H40), Bangla review (H42). Shammo: Bangla, mobile. Sattyam: performance. Monazir: wording review. Sheikh: final integration, tags. |
| 7 Ship | H42-48 | Submitted with a buffer | Sattyam and Shammo: final deploy (H44). Samiul: video (H44), checklist (H46). Sheikh: submit (H46). Two spare hours. |

At every gate (5 minutes, Sheikh): is the promised artifact delivered and tested? If not, cut by the agreed order
(Bangla polish, forecast alerts, PM2.5, comparison, forecast outlook (the current-status card and the where-map are never cut)), keep the floor intact, never move a gate more than two hours.

Rest (suggested): sleep in two shifts; at least three people rested during H30-42; nobody works alone after H40.
