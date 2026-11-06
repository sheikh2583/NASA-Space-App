---
id: T01
title: Licence, references and AI-use statement
kind: agent
owner: Sheikh
authors: [Sheikh, Samiul]
phase: P0
size: S
needs: [T30]
requires: []
branch: ws1/T01-licence-references
touches: [README.md, docs/project/submission-checklist.md]
creates: [LICENSE, docs/REFERENCES.md]
checks: [CHECK-PLAN]
---
## Goal
Give the repository a licence and two documents the submission needs: every external resource with a link, and an
honest statement of AI use.

**6 November scaffold reconciliation:** the historical status note records that AI_USE was left to the team, and
the file is still absent. Its unfinished creation is now owned by T29; this removes duplicate creator ownership,
not an assertion that the original disclosure was completed. The steps below remain the historical request.

## Context
- The Space Apps judging guide requires an originality confirmation and a References field listing all external
  resources.
- NASA's open-source projects usually use Apache-2.0.
- The method text (`docs/science/method_en.md`) and the decisions (`docs/science/decisions.md`) name the data sources.

## Steps
1. Create `LICENSE` with the full Apache License 2.0 text, with copyright line "Copyright 2026 the FireSense team".
   Use the official text from apache.org; don't paraphrase it.
2. In `README.md`, add a "Licence" section with one line: "Apache-2.0, see LICENSE. Data products remain under their
   providers' terms (see docs/REFERENCES.md)."
3. Create `docs/REFERENCES.md` with these sections. Every entry is one bullet with its name, what we use it for, and
   its URL. Use only URLs found in the repository docs or that you have opened and confirmed.
   - **NASA data:**
     - FIRMS MODIS C6.1, VIIRS S-NPP, NOAA-20 and NOAA-21 (archive and NRT): https://firms.modaps.eosdis.nasa.gov/
     - MODAPS Suomi NPP outage table:
       https://modaps.modaps.eosdis.nasa.gov/services/production/outages_suomi_npp.html
     - MCD12C1 land cover (Earthdata)
     - NASA POWER weather
   - **Boundaries and maps:** geoBoundaries ADM1; OpenStreetMap tiles, with the attribution text.
   - **Software:** every package in `requirements.txt`, and every package in `ws5_frontend/package.json` under
     "dependencies", one bullet each with its licence name from the package metadata. Don't list devDependencies.
   - **Papers and articles:** the NASA Science Punjab article (https://science.nasa.gov/?p=1160169), plus anything
     cited in `docs/science/method_en.md` or `docs/science/decisions.md`.
4. Create `docs/AI_USE.md`.
   - It says that AI assistants (Claude, and the coding agent used in the IDE) wrote much of the code and
     documentation under the team's direction.
   - It says every commit names the team member whose folder it changes, and that Sheikh, the team lead, reviews
     every pull request before merging it.
   - It lists what was checked automatically against NASA sources (FIRMS API truth checks, the MODAPS outage table), and
     that the Bangla text was drafted with AI assistance.
   - Keep it under 200 words and in plain English.
5. In `docs/project/submission-checklist.md`, add a section "References and AI use" pointing to the two new files.
6. Run the checks, mark the card done, commit with `split` (two commits: Sheikh, Samiul), then push and open the PR.

## Acceptance
- [ ] `LICENSE` is the unmodified Apache-2.0 text.
- [ ] Every package named in `requirements.txt` and in `package.json` "dependencies" appears in `docs/REFERENCES.md`.
  Check with: `python -c "import re,json;r=open('docs/REFERENCES.md').read();req=[l.split('=')[0].split('<')[0].split('>')[0].strip() for l in open('requirements.txt') if l.strip() and not l.startswith('#')];dep=list(json.load(open('ws5_frontend/package.json'))['dependencies']);print([p for p in req+dep if p.lower() not in r.lower()])"`
  It must print `[]`.
- [ ] CHECK-PLAN and CHECK-PY pass.

## Stop and ask if
- `docs/RULES_CHECK.md` (T30) says the licence or the submission needs something different.
