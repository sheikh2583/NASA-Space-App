# How the burning calendar is made

Satellites flag fire hot spots, but different instruments see different amounts of fire. MODIS (Terra from 2000, Aqua from 2002) has 1 km pixels. VIIRS (Suomi NPP from 2012) has 375 m pixels and sees many more small fires, such as crop-residue burns. Suomi NPP stopped delivering data on 2 November 2026, so newer weeks come from NOAA-20, which carries the same VIIRS sensor.

We express every week in **Suomi NPP terms**:

- **Observed** (2012 to 2 Nov 2026): Suomi NPP detections as recorded.
- **Adjusted** (after 2 Nov 2026): NOAA-20 detections scaled by a ratio measured in the years both satellites flew.
- **Modeled** (before 2012): estimated from MODIS, using the relationship seen while MODIS and VIIRS overlapped.

Adjusted and modeled weeks carry a **90% uncertainty band**. The band was checked on areas held out of the fitting.

A week is **unusual** when it is clearly above the same week in other years. The app also shows whether the week stays above normal across its whole uncertainty band; before 2012, flags lean on modeled values and are marked so. Runs of unusual weeks become **critical periods**, ranked by size. Each period is marked as likely agricultural when most of its fires fall in cropland.

**Associated conditions** are weather patterns that tend to occur alongside burning. They are associations, not proof of what started a fire.

**Limits.** Values before 2012 are estimates. Detection depends on cloud and overpass time, so it is not a full count of fires. The demo covers Bangladesh and Punjab–Haryana–Delhi. Until real data is loaded, all numbers shown are synthetic.
