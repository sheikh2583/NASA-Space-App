# Known gaps and disclaimers (read this first)

This project began as a plan and now runs end to end on downloaded NASA data. The table is retained as a risk register: some early
items are closed by the 4 Nov 2026 smoke run, while rules, hosting, human review, and scientific interpretation still need manual checks.

## What was checked, and how
- The JSON Schemas accept valid sample documents and reject an invalid one; contracts/openapi.yaml validates as OpenAPI; parquet_schemas.json loads.
- Automated data, schema, seam, leakage, API-contract, and end-to-end checks pass on the current real-data outputs.
- Every docs/, prompts/ and contracts/ file named in the text exists in the zip (except files that are meant to be created at the event). Every prompt number used in the phase prompts and instructions is defined (54 prompts).
- Each person's phase file has seven phases and a manual-task block per phase.

## What was NOT checked
| # | Area | The gap | Effect if wrong | Closed by |
|---|---|---|---|---|
| 1 | Official rules | Challenge rules and resources, hardware rules, AI-use and disclosure, pre-event preparation, licence, submission format, team size and venue hours were not seen | plan may break a rule or miss a deadline | H0-01 |
| 2 | FIRMS access | Archive route, area API day and rate limits, MAP_KEY process, NOAA-20 near-real-time and standard-product start date (SNPP ended 2 Nov 2026), presence of a source-type field for each product, confidence formats are from memory | ingestion slower or different from the prompts | H0-02 |
| 3 | Land cover | Availability and format of a ready-made 0.05 degree product (such as MCD12C1) and the cropland class mapping are unverified | no cropland fraction; agricultural tag falls back to a region-season rule | H0-03 |
| 4 | Boundaries | geoBoundaries ADM1 download, licence and stable ids are unverified | regions need another source | H0-04 |
| 5 | Driver data | CHIRPS and NASA POWER access, resolution, request limits and the soil-wetness field are unverified | drivers panel shrinks or is cut | H0-05 |
| 6 | Installs | Library versions and installs were not tested; geospatial packages can be hard to install on some laptops | lost time at H0 | H0-06 |
| 7 | Hosting | Free-tier limits (sleep, memory, size, build minutes) and Docker availability for the chosen hosts are unverified | API unavailable or slow; static fallback carries the demo | H0-07 |
| 8 | Data size and speed | Row counts, memory and training time are unknown; the 0.1 degree daily panel size is untested | gridding or training too slow on laptops | H0-08 |
| 9 | Satellite status | ANSWERED 3 Nov 2026: FIRMS stopped new SNPP data on 2 Nov 2026; NASA says Terra and Aqua begin shutting down late 2026 / early 2027. See decisions 17-18. Still open: whether Aqua or Terra stop before or during the event | another seam or outage window | H0-09 |
| 10 | Science design | The learned model may not beat the per-region ratio; the AOI-sampling conformal scheme is a custom adaptation with no guarantee under shift (especially before 2012); drift thresholds, STL settings and forecast skill are untested; driver associations may be spurious | claims must be softened; floor tier still works | H12 design review |
| 11 | Chosen parameters | Demo-region boxes, high-confidence thresholds, the VIIRS confidence mapping, split rule (block_id % 5), 2x2 degree blocks, alert thresholds, AOI size limit and the 1.5 second target are my defaults, not tested on data | defaults need adjusting after the first look at data | H0-08, H12 |
| 12 | Prompts | No AI tool has run these prompts; results differ by tool; agents can drift from the contracts | code needs review and edits | contract tests, verify tool |
| 13 | Feasibility | Hour estimates are judgement; six workstreams in 48 hours is ambitious; Sheikh carries lead, integration and science; early dependency on data work | slips at gates | cut order, LEAD_GUIDE |
| 14 | Timeline | Assumes a continuous 48 hours; real venue hours and local-time mapping are unknown | gates need shifting | H0-01 |
| 15 | Roles | Slots reflect the lead's input; the plan does not assess anyone's skills | kickoff round may swap slots | kickoff round |
| 16 | Bangla | Needs a fluent human reviewer; Bengali numerals and fonts untested on devices | wrong or broken text | H36-42 review |
| 17 | Security | No authentication or rate limiting on the public API; not reviewed | fine for a demo; avoid private data | keep keys in .env |
| 18 | Licences | Data and software licences and attribution requirements were not checked | missing credits | H0-01, submission checklist |
| 19 | Accessibility | Only a colour-blind-safe palette and a phone layout are planned; no audit | gaps for some users | manual device checks |
| 20 | Backups | If the shared drive or a hosting account fails, the only backup is the static fallback | lost work | keep a local copy of final outputs |

## How to use this page
- Do the H0 checks in docs/H0_VERIFICATION.md in the first 90 minutes; record each result in docs/DECISIONS.md.
- Where a result differs from what the prompts assume, change the decision first, then tell the affected person, then update the prompt text.
- Do not present anything in the app or pitch as validated unless a validation piece or test in the repo shows it.

## Added after reading the official challenge description
| # | Area | The gap | Effect | Closed by |
|---|---|---|---|---|
| 21 | Global scope | The challenge speaks of the whole planet; the demo loads South Asia only | the app is global-capable but not globally populated | state it in the app and pitch (decision 15) |
| 22 | Early warning | The current-status card depends on near-real-time data being available and recent; this is unverified | status may be stale or unavailable | H0-02; show the data-through date |
| 23 | New work | The where map layer, the status card and agri_share were not in the original hour estimates | more load on Sattyam, Shammo and Samin | cut order protects the floor; forecast alerts and the forecast outlook go first |

## Added with the git automation
| # | Area | The gap | Effect | Closed by |
|---|---|---|---|---|
| 24 | Git scripts | Tested only against a local test repository (clone, branch, save, ship, guard rules, cleanup). Not tested against GitHub: the pull-request creation, collaborator invites, branch protection and the pr-guard Action are untested; branch protection may need a paid plan on private repos | a script may need fixing on first use | Sheikh runs through docs/GIT_WORKFLOW.md section 1 at H0 and the team does the hello-world PR |
| 25 | Repo URL and handles | The URL given was cut off; github.com/sheikh2583/NASA-Space-App exists, is public and empty (checked 3 Nov 2026) and is assumed to be the one. All six GitHub handles exist, but "Monajir" has no profile name, and a different account "Monazir" also exists, so confirm Monazir's handle | a wrong handle breaks CODEOWNERS and the guard for that person | fix scripts/team.csv and .github/CODEOWNERS |
| 26 | Platform | Windows needs Git Bash or WSL; Python 3 must be on the path for the hooks | hooks fail to run | H0-06 |
| 27 | Privacy | Emails were not stored in the repo or the kit; each person uses the email on their own GitHub account | none | by design |

## Added after checking GitHub
| # | Area | The gap | Effect | Closed by |
|---|---|---|---|---|
| 28 | Public repo | The repo is public, so every file in this kit (plans, team handles, notes) is visible to anyone, and it has no licence file yet (so by default all rights are reserved) | exposure; unclear reuse terms | H0-01: confirm the organizers' open-source and licence rules; never commit emails, keys or data |
| 29 | Push not tested | I could read the repo but have no credentials, so the first push, the invitations and branch protection have not been run | first-use fixes possible | Sheikh runs GIT_WORKFLOW.md section 1 |

## Added after the kit review (3 Nov 2026)
| # | Area | The gap | Effect | Closed by |
|---|---|---|---|---|
| 30 | NOAA-20 overlap | The first date of NOAA-20 standard-product data in FIRMS, and so the length of the SNPP/NOAA-20 overlap used for the adjustment ratio, is unverified | the ratio may need to be per region instead of per region-month | H0-02 |
| 31 | Sensor outages | sensor_days only knows the windows found in notices and the data's first and last dates; short outages may be missing | a few zero days that should be missing | Samiul's data QA: look for runs of zero days across the whole demo region |
| 32 | Local solar date | grid_daily uses the local solar date; the FIRMS web viewer uses UTC | the manual one-day comparison must count by UTC from detections.parquet, not grid_daily | QA_CHECKLIST note |
| 33 | Proposed fixes | Decisions 17-23 and the contract and script changes were drafted by Shammo with an AI assistant and tested only locally (contracts validate; git scripts re-run against a local remote) | Sheikh must approve before G0 | Sheikh review |

