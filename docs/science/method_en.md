# How the burning calendar is made

Satellites flag fire hot spots, but different instruments see different amounts of fire. MODIS (Terra from 2000, Aqua from 2002) has 1 km pixels. VIIRS (Suomi NPP from 2012) has 375 m pixels and sees many more small fires, such as crop-residue burns. Suomi NPP stopped delivering data on 2 November 2026, so newer weeks come from NOAA-20, which carries the same VIIRS sensor.

We express every week in **Suomi NPP terms**:

- **Observed** (2012 to 2 Nov 2026): Suomi NPP detections as recorded.
- **Adjusted** (after 2 Nov 2026): NOAA-20 detections scaled by a ratio measured in the years both satellites flew.
- **Modeled** (before 2012): estimated from MODIS, using the relationship seen while MODIS and VIIRS overlapped.

Adjusted and modeled weeks carry an uncertainty band with a **nominal 90% target**. Held-out diagnostics show substantially weaker coverage for some positive-activity and Terra-only groups. This is not a conditional 90% guarantee.

A week is **unusual** when it is clearly above the same week in other years. The app also shows whether the week stays above normal across its whole uncertainty band; before 2012, flags lean on modeled values and are marked so. Runs of unusual weeks become **critical periods**, ranked by size. Each period is marked as likely agricultural when most of its fires fall in cropland.

**Associated conditions** are weather patterns that tend to occur alongside burning. They are associations, not proof of what started a fire.

**Limits.** Values before 2012 are estimates. Detection depends on cloud and overpass time, so it is not a full count of fires. The current real-data build covers Bangladesh and Punjab–Haryana–Delhi.

## What these numbers can and can't tell you

- Detections are not area burned. Small, short, cloud-covered or under-canopy fires are missed; a quiet week isn't proof that nothing burned.
- Satellites pass at fixed times: Terra about 10:30, Aqua and Suomi NPP about 13:30, and NOAA-20 about 50 minutes from Suomi NPP. NASA has reported Punjab burning moving later in the day, so falling counts can partly mean fires burned while no satellite was looking. Source: science.nasa.gov/?p=1160169
- Every year is shown as if seen by VIIRS on Suomi NPP. Before 2012, values are estimated from MODIS and carry wider bands.
- Suomi NPP fire data ended on 2 November 2026; later weeks use NOAA-20 scaled to the same standard. Terra and Aqua are ending their missions.
- Season timing, shown as “usually from … to …”, counts when 10% and 90% of a season's detections had happened. It isn't the date fields were set alight.
- Weather links are associations, not causes.
- This is not an alert service; for emergencies use national services and FIRMS directly.

## How we checked

Forecast-skill scores saved before the T44 correction used climatology influenced by held-out
seasons. They are historical and cannot establish forecast skill. Corrected evaluation uses
earlier-season training data and embargoes targets crossing the evaluation boundary.
Numerical forecast revalidation is pending; current observed-season status is a separate diagnostic.

- Punjab 15 Sep–1 Nov 2026, SNPP NRT: FIRMS 460, ours 455, close.
- Punjab 2 Nov 2024, SNPP: FIRMS 345, ours 353, close.
- Punjab 3 Nov 2024, SNPP: FIRMS 0, ours 3, small counts below 10.
- Punjab 4 Nov 2024, SNPP: FIRMS 0, ours 0, both 0.
- Punjab 5 Nov 2024, SNPP: FIRMS 0, ours 0, both 0.
- Punjab 6 Nov 2024, SNPP: FIRMS 2, ours 0, small counts below 10.
- Punjab 7 Nov 2024, SNPP: FIRMS 400, ours 395, close.
- Punjab 8 Nov 2024, SNPP: FIRMS 488, ours 489, close.
- Punjab 2 Nov 2024, NOAA-20: FIRMS 229, ours 230, close.
- Punjab 3 Nov 2024, NOAA-20: FIRMS 288, ours 285, close.
- Punjab 4 Nov 2024, NOAA-20: FIRMS 259, ours 262, close.
- Punjab 5 Nov 2024, NOAA-20: FIRMS 209, ours 208, close.
- Punjab 6 Nov 2024, NOAA-20: FIRMS 182, ours 181, close.
- Punjab 7 Nov 2024, NOAA-20: FIRMS 269, ours 271, close.
- Punjab 8 Nov 2024, NOAA-20: FIRMS 407, ours 401, close.
- Punjab 15 Sep–31 Dec 2016, SNPP: FIRMS 63,646, ours 63,621, close.
- Punjab 15 Sep–31 Dec 2024, SNPP: FIRMS 5,917, ours 5,907, close.
- FIRMS comparisons above: measured in ws6_validation/truth_checks.md, run 2026-11-04. UTC dates and our local-solar dates can shift a few night-pass detections.
- Held-out agreement: B1 selected at mean CCC 0.8900 versus XGBoost CUDA 0.8775 across Terra+Aqua and Terra-only holdouts; measured in docs/results/training-results.md, run results/runs/20261104-211232-599349.
- Historical marginal coverage: weekly 0.934 and monthly 0.924; measured in docs/results/training-results.md, run results/runs/20261104-211232-599349. These overall figures mask conditional failures; detailed held-out diagnostics require review and do not validate coverage in the actual pre-2012 record.
