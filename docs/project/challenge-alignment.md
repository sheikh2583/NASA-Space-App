# Does the plan match the official challenge?

The official description (pasted by the lead) asks for a web application that harmonizes the MODIS and VIIRS active-fire hotspot records
into a burning-activity calendar, so that early-warning staff, emergency responders, scientists and land managers can examine historical
fire patterns, unusual conditions and critical periods within a selected area. It covers wildfires and agricultural burns, and wants a
consistent picture of when and where burning has occurred.

Only the description was available. The official rules, resources and hardware notes have not been seen (docs/project/known-gaps.md, item 1).

| What the challenge asks for | Where the plan covers it | Status |
|---|---|---|
| Records split across sensors made comparable | harmonization pipeline (Sheikh, Samin) | covered; pre-2012 values are modeled and labeled |
| A burning-activity calendar from active-fire hotspots | calendar heatmap (Shammo) on harmonized series | covered |
| A selected area of interest | map drawing and /aoi/ endpoints | covered |
| Historical patterns over two decades | series from 2000 to the present with the 2012 seam shown | covered |
| Unusual conditions | anomaly flags (Monazir) | covered |
| Critical periods | ranked critical periods (Monazir) | covered |
| Wildfires and agricultural burns | agri_tag and agri_share on periods; cropland land cover | covered after this update (agri_share added) |
| When and WHERE burning occurred | calendar covers when; /aoi/cells map layer covers where (Sattyam, Shammo) | gap found and fixed: the where layer was missing |
| Use for early warning, responders and land managers | current-status card (never cut), data-through date, export; forecast alerts are optional | gap found and fixed: alerts were cut first; the status card is now core |
| The whole planet | pipeline is global-capable; demo loads South Asia only | not fully met; stated in the app and pitch |
| A web application | React app plus API plus static fallback | covered |

## What changed in the kit because of this
- New endpoint /aoi/cells and prompt P5.9 (where map layer and status card).
- outlook_region.json gained current_status; critical_periods gained agri_share.
- Cut order now cuts the forecast alerts and the forecast outlook first; the status card and the where-map are never cut (decision 14).
- The pitch names the three audiences and states the South Asia scope (decision 15; prompt P6.7).
- New gaps recorded as items 21 to 23 in docs/project/known-gaps.md.
