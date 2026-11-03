# Manual tasks (things a coding agent cannot do for you)

A coding agent writes and tests code. It cannot sign up for services, use your logins, click through dashboards, talk to people, look at the app on a real phone, record a video, or submit a form. These tasks are yours. Tick them as you go; your phase prompts repeat the ones for the current phase.

## Team-wide

| When | Who | Task | Why an agent cannot |
|---|---|---|---|
| Before the event | Everyone | Bring chargers, power strips and a mobile hotspot; update the laptop; check you can reach the venue on time | physical preparation |
| Before the event | Everyone | Accept the GitHub invitation, sign in with `gh auth login` (or a credential manager or SSH key), set your git name and email, clone, and run `bash scripts/git/setup.sh <your-github-username>` | sign-in and invitation need your own accounts |
| Before the event | Everyone | Make sure you have a GitHub account, an Earthdata login and a way to reach the team channel | accounts and sign-ins |
| Before the event | Sheikh | Confirm the team is registered for the challenge on the Space Apps site with the right members | needs the official site and your login |
| H0 | Everyone | Check venue Wi-Fi works and note a backup (hotspot) | depends on the venue |
| Throughout | Everyone | Eat, drink water, and sleep in shifts; at least three people rested during H30-42 | people, not code |
| Throughout | Everyone | Keep keys and passwords out of chat and the repo; use .env only | a habit, not code |

## Sheikh

| Phase | Hours | Task | Why an agent cannot | Done |
|---|---|---|---|---|
| 1 | H0-3 | Create the GitHub repo from your own account, invite all six, and set branch protection in the repo settings | needs your login and clicks in the GitHub settings pages | [ ] |
| 1 | H0-3 | Create the team channel and the shared drive folder, and set sharing so all six can edit | needs your accounts and sharing dialogs | [ ] |
| 1 | H0-3 | Ask the organizers (in person or by message): venue hours, submission deadline, whether the starter structure may be brought, AI-use disclosure, licence rules, hardware rules; tell the team the answers | a conversation with people, not code | [ ] |
| 1 | H0-3 | Check that each teammate has git, Python 3.11 and Node LTS installed and can push; help them if not | depends on each person's laptop | [ ] |
| 1 | H0-3 | Run the 15-minute kickoff round (confirm the six slots, read out docs/DECISIONS.md) | a live conversation and decisions | [ ] |
| 2 | H3-8 | Run the H6 check-in with everyone (done / next / blocked) | a live conversation | [ ] |
| 2 | H3-8 | Open the first detections slice yourself and look at a few rows | a human sanity check | [ ] |
| 3 | H8-24 | Run the check-ins at H12, H18 and H24 | live conversations | [ ] |
| 3 | H8-24 | At G2 open the live app yourself on a laptop and a phone and try the demo path by hand | a human check on real devices | [ ] |
| 4 | H24-30 | At G3 open the live app and look at the bands, badges and drift icons yourself | a human visual check | [ ] |
| 4 | H24-30 | Talk to Samin and Sattyam about what slips if H30 is missed; decide the cut | a decision between people | [ ] |
| 5 | H30-36 | Walk the whole demo path by hand (Bangladesh, then Punjab) and note anything confusing | a human judgement | [ ] |
| 5 | H30-36 | Call the feature freeze at H36 in the channel and tell everyone what is cut | a decision and announcement | [ ] |
| 6 | H36-42 | Merge pull requests in the GitHub web page in dependency order (data, API, app) and tag the final build | needs your GitHub clicks and judgement | [ ] |
| 6 | H36-42 | Go through the bug lists with the owners and set times | a conversation | [ ] |
| 7 | H42-48 | Submit on the official Space Apps site from your login; check the right challenge is selected | needs your login and the live form | [ ] |
| 7 | H42-48 | Open every submitted link in a private browser window to confirm it works for outsiders | a manual check outside your logged-in session | [ ] |

## Sattyam

| Phase | Hours | Task | Why an agent cannot | Done |
|---|---|---|---|---|
| 1 | H0-3 | Create accounts on a static host and a container-capable API host (free tiers) and share access with Sheikh | sign-up, email verification and dashboards | [ ] |
| 1 | H0-3 | Read each host's free-tier limits (sleep time, memory, build minutes) and tell Sheikh | reading current pages and deciding | [ ] |
| 2 | H3-8 | Download boundary files (geoBoundaries ADM1) and the land-cover product by hand if they need a web form or login; put them in the shared drive | web downloads, possible sign-in | [ ] |
| 2 | H3-8 | Connect the repo to the hosting dashboards for the hello-world deploy | dashboard clicks | [ ] |
| 3 | H8-24 | Set environment variables in the hosting dashboard and press deploy; open the URL on your phone | dashboard clicks and a real-device check | [ ] |
| 4 | H24-30 | Check the cold-start delay by hand after the API has been idle | a timing test on the hosted app | [ ] |
| 5 | H30-36 | Time a typical AOI from your phone and laptop on the live site | a real-network timing check | [ ] |
| 6 | H36-42 | Test the static fallback by switching the API off in the dashboard and loading the app | dashboard action plus a visual check | [ ] |
| 7 | H42-48 | Do the final deploy in the dashboard, note the rollback step, and open the URLs from a different network | dashboard and a second network | [ ] |

## Monazir

| Phase | Hours | Task | Why an agent cannot | Done |
|---|---|---|---|---|
| 1 | H0-3 | Register your own FIRMS MAP_KEY and an Earthdata login; put the key in your .env | web forms and email confirmation | [ ] |
| 1 | H0-3 | Submit the FIRMS archive download requests (MODIS and VIIRS SNPP, demo regions) on the website as early as possible | web request forms; links arrive by email later | [ ] |
| 2 | H3-8 | Check your email for the archive download links, download the big files, and move them to the shared drive | manual downloads and disk space | [ ] |
| 2 | H3-8 | Check you have enough free disk space on your laptop | depends on your machine | [ ] |
| 3 | H8-24 | Open the FIRMS web map for one day and one small area and compare it with your rows | a human visual check against the website | [ ] |
| 4 | H24-30 | Check that the weather data sources (CHIRPS, NASA POWER) are reachable from your network and note any sign-in needed | network and account checks | [ ] |
| 5 | H30-36 | Read every driver sentence aloud with Shammo and decide the final wording together | human judgement on wording | [ ] |
| 6 | H36-42 | Review the anomaly and driver text in the running app with your own eyes and fix any causal wording | a human review | [ ] |
| 7 | H42-48 | Check the anomaly and period outputs on the deployed app for both demo regions | a human check on the live site | [ ] |

## Samin

| Phase | Hours | Task | Why an agent cannot | Done |
|---|---|---|---|---|
| 1 | H0-3 | Check Python deps install cleanly on your laptop; agree the split labels with Sheikh in conversation | laptop setup and a conversation | [ ] |
| 2 | H3-8 | Ask Sattyam and Monazir what they need from common/ before you write it | a conversation | [ ] |
| 3 | H8-24 | Agree the exact columns and timing of the out-of-fold file with Sheikh | a conversation | [ ] |
| 4 | H24-30 | Look at the coverage table and decide with Sheikh whether to ship conformal intervals or the empirical-quantile fallback | a judgement between people | [ ] |
| 5 | H30-36 | Agree the wording of no_demonstrated_skill with Shammo | wording and tone | [ ] |
| 6 | H36-42 | If you do the burned-area comparison, download the MCD64A1 files from NASA Earthdata with your login | sign-in and manual downloads | [ ] |
| 7 | H42-48 | Open the deployed app and check that the bands, drift icons and outlook status match your files | a human check on the live site | [ ] |

## Shammo

| Phase | Hours | Task | Why an agent cannot | Done |
|---|---|---|---|---|
| 1 | H0-3 | Set up your AI tool project with docs/AI_PREAMBLE.md pasted in; install Node LTS and the editor you will use | your tools and accounts | [ ] |
| 1 | H0-3 | Pick the map and chart libraries with Sattyam so the fixtures match | a short conversation | [ ] |
| 2 | H3-8 | Open the demo link on your phone and on a desktop browser and look at it | a real-device check | [ ] |
| 3 | H8-24 | Try drawing an area with a finger on your phone | touch behaviour is easiest to judge by hand | [ ] |
| 3 | H8-24 | Check the colours with a colour-blindness simulator or a teammate | a human visual check | [ ] |
| 4 | H24-30 | Look at the app next to Samiul's bug list and decide the order of fixes | a conversation and judgement | [ ] |
| 5 | H30-36 | Check Bangla text on a real phone: numerals, line breaks, long strings | fonts and rendering vary by device | [ ] |
| 6 | H36-42 | Take clean screenshots of the final screens for the slides and give them to Samiul | a visual task | [ ] |
| 7 | H42-48 | Open the final URL on another device and network; rehearse the demo path with Samiul | a real-world rehearsal | [ ] |

## Samiul

| Phase | Hours | Task | Why an agent cannot | Done |
|---|---|---|---|---|
| 1 | H0-3 | Join the channel; get the QA and submission checklists from the repo; confirm your tools run | setup on your own laptop | [ ] |
| 2 | H3-8 | Open the FIRMS web viewer, pick one day and one small area, count the detections by hand and compare with our number | a manual check against the website | [ ] |
| 3 | H8-24 | Use the app by hand on a phone and a laptop for the full demo path; take screenshots of every bug | a human, real-device check | [ ] |
| 4 | H24-30 | Repeat the hand test with intervals and drift icons visible; add new bugs with screenshots | a human check | [ ] |
| 5 | H30-36 | Ask a fluent Bangla speaker to be ready for the review at H42; collect the numbers for slides from the validation files | finding a person and reading files | [ ] |
| 6 | H36-42 | Sit with the Bangla reviewer and go through every line; rehearse the demo aloud and time it | a person-to-person task | [ ] |
| 7 | H42-48 | Record the video with a screen recorder and a microphone, watch it end to end, upload it; fill in the submission forms with Sheikh | recording, uploading and forms | [ ] |
