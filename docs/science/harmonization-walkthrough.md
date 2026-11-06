# How FireSense harmonization works

Reviewed 6 November 2026 at source revision `e97d49f`. This is a technical explanation of the implementation, not a declaration that its current uncertainty bands or revised learners are scientifically accepted. The companion [architecture guide](../project/architecture.md) explains runtime behavior.

## 1. The quantity being estimated

The output is **satellite active-fire detections in Suomi NPP VIIRS-equivalent terms**. A detection is not a distinct fire event, burned area, emissions, damage or proof of agricultural ignition. Sensor resolution, clouds, overpass time, viewing geometry and product differences affect the counts.

The useful question is: “How does this area's detected burning activity compare through time after accounting for a change in instrument?” This is narrower than estimating every fire that actually occurred.

NASA's [challenge summary](https://www.spaceappschallenge.org/2026/challenges/modis-and-viirs-hot-spots/) asks for comparable hotspot records in a calendar with geographic and historical exploration. FireSense chooses a reference-sensor reconstruction rather than adding all satellite counts together.

## 2. Coordinate, date and missingness conventions

`common/grid.py` defines a 0.1-degree global grid. Cell IDs derive from rounded/clamped latitude and longitude indices, so all workstreams share one convention. This is an angular grid: physical cell area varies with latitude.

Acquisition date/time stays in UTC in the normalized detections. The daily panel uses local solar date, computed from UTC plus longitude/15 hours. Weeks start Monday. ISO week 53 is folded into 52 for climatology but gets its own display column in the calendar.

An absent sparse detection row means zero only when the relevant satellite operated. `sensor_days.parquet` determines whether observations were available. A period without an operating source is unknown, not a verified quiet period. `common.series` carries `n_days` to distinguish partial sensor coverage from a full observed week.

Operating-day metadata is still an approximation: it does not model the probability that clouds or an individual swath prevented detection at every cell. “Operating” must not be explained as perfect observation of every fire.

## 3. Ingestion and availability

1. `normalize.py` maps satellite identities, keeps UTC acquisition fields and normalizes confidence formats. VIIRS confidence codes are mapped to project values; those values are not measured probabilities equivalent to MODIS confidence.
2. Standard and near-real-time duplicates are removed, with standard products preferred. Known non-vegetation source types are filtered where the product provides that field; absent NRT type information is retained and remains a limitation.
3. `grid.py` builds per-satellite cell-day aggregates. `cells.py` assigns boundaries and land cover and retains the project administrative domain.
4. `sensors.py` combines operating windows with the verified outage registry. Decision 24 excludes days when an outage exceeds 0.25 of a modeled pass window in either demo region. This shared-day policy is a regional design choice, not a global outage model.

See [outage decisions](decisions.md), the [audit](../specs/I8_AUDIT_RESULTS.md), and [source files](../../ws2_platform/sensors.py). The confidence mapping, outage exclusion, deduplication and geographic retention rules all affect what downstream counts mean.

## 4. Weekly panel and reference scale

`panel.py` builds cell-week rows over active cells and attaches per-satellite counts, fire radiative power (FRP), day/night information, scan features, administrative attributes and operating-day counts. Full overlap weeks are used for harmonization fitting.

Terra-only and Terra+Aqua input configurations are evaluated separately. A ratio learned from two MODIS instruments is not silently applied to the historical Terra-only period.

The deployed saved harmonization method is B1, a shrunk ratio per administrative region and calendar month, separately for each MODIS combination. Schematically:

```text
global ratio r0 = sum(SNPP detections) / sum(MODIS input detections)
regional monthly ratio r = (sum(SNPP) + k*r0) / (sum(MODIS) + k)
estimated SNPP-equivalent count = r * MODIS input count
```

The implementation's shrinkage constant is `k=20`; absent local groups fall back to the global ratio. These are fitted statistical parameters, even though B1 is much simpler than a boosted-tree learner. Agent-operated B1 fitting is now authorized through the scientific-run policy in [AGENTS.md](../../AGENTS.md), with preserved baselines and recorded provenance.

NOAA-20 has its own region/month adjustment against SNPP overlap. NOAA-21 is not automatically interchangeable with NOAA-20 and is not mixed into the reference series without a separate decision/calibration.

## 5. Learned candidate and selection

The candidate learner predicts count/FRP from MODIS-derived and static features. It prohibits VIIRS-derived feature prefixes and direct year/date/cell-ID features. Current features include nearby MODIS activity, exact previous/next calendar-week context, seasonality, coarse location and land cover.

Using next-week MODIS context is appropriate to a retrospective reconstruction; it does not make this model an operational forecast. Feature context is built on the full MODIS panel, then row masks select training/test examples. The latest correction avoids treating the next available row across a missing week as the next calendar week.

Evaluation includes spatial blocks, rolling temporal holdouts, backward reconstruction and later drift-era holdouts. Calibration/test blocks are distinct from fitting blocks; a spatial buffer reduces immediate neighbor overlap. Selection averages agreement across both MODIS combinations and prefers B1 on ties.

Historical selection evidence favored B1. This demonstrates an engineering/scientific choice against forcing a more complex GPU candidate to win. However, choosing a method using those holdouts means the selection score is not an additional untouched confirmatory test. New feature construction changes also need new numerical evaluation before quoting old scores as current validation.

Source: [baselines](../../ws1_harmonize/baselines.py), [features](../../ws1_harmonize/features.py), [evaluation](../../ws1_harmonize/evaluate.py), [historical results](../results/training-results.md).

## 6. Building the served record

For each cell-day, the source priority is:

| Available source | Served value | Label |
|---|---|---|
| SNPP operating | SNPP count | `observed_viirs` |
| SNPP unavailable, NOAA-20 operating | NOAA-20 count multiplied by its SNPP adjustment | `adjusted_from_noaa20` |
| Neither available, MODIS available | MODIS-based reconstruction | `modeled_from_modis` |
| No applicable operating source | Missing value | No observed value |

Thus adjusted/modelled values can occur inside the nominal SNPP era on outage days. The source label is more precise than a simple before/after date legend.

`write_harmonized.py` allocates modeled weekly totals to days in proportion to MODIS detections. Without MODIS detections, the estimate is booked on Monday. That allocation supports aggregation; it is not recovered daily fire truth. FRP uses additional assumptions and must not be presented as cross-sensor calibrated intensity.

Observed counts have degenerate stored bounds by project convention. This means no harmonization uncertainty was added to them; it does not mean perfect physical detection.

## 7. Aggregate uncertainty

The API does not sum cell-level lower/upper bounds. `common.series` sums the requested cells, separates the observed and non-observed portions, applies the aggregate lookup table to the non-observed total, and adds the observed portion back.

`conformal.py` calibrates log-ratio errors on sampled rectangles in held-out calibration blocks. Lookup strata use land cover, season and predicted magnitude, with fallbacks. The nominal level is 0.9. Calibration targets a distribution of sampled aggregates; this does not guarantee 90% coverage for every region, activity level, historical era or user-drawn shape.

The detailed report retains both unique contributing cells and nominal drawn-rectangle size. It reports zero and positive activity, magnitude groups, seasons, MODIS input combinations and stop-condition groups. A large marginal coverage number can conceal failures in the positive-activity groups that matter most to users.

The latest monthly implementation constructs calendar-month truth/predictions from daily allocation, matching served months. The older whole-week-by-Monday-month target remains an explicitly labelled fallback for tiny tests. **The saved local report inspected for this review predates that new target and has no `month_target` label. Its monthly numbers cannot validate the revised calendar-month procedure.**

Current saved interval acceptance is `stop_condition`. See the [dated evidence table](../project/review-2026-11-06.md); no calibration was executed for this documentation.

## 8. Derived products

| Product | Computation | Interpretation limit |
|---|---|---|
| Unusual weeks | Same-week seasonal baseline, robust residual scale and high-percentile rule | Retrospective comparison, affected by history and sensor seams |
| Critical periods | Nearby flagged weeks grouped and ranked by excess activity relative to typical weekly activity | Not a damage ranking or emergency declaration |
| Cropland association | Cropland-weighted share, or a region/season fallback | Does not classify ignition causes |
| Weather associations | Deseasonalized correlations across lags; max-over-lags block permutations and selected-lag bootstrap intervals | Association, not causal attribution; regional weather can hide local differences |
| Drift | Sensor/model relationship and applicability diagnostics | Flags uncertainty; does not automatically repair bias |
| Season profile | Fixed search windows, p10/p50/p90 cumulative detection dates, peak and robust trends | A central activity window, not the physical start/end of burning |
| Current status | Latest calendar-complete, coverage-checked week versus prior same-week values | Historical status relative to the served record, not necessarily this week's live conditions |
| Season-to-date position | Comparable cumulative histories with incomplete seasons excluded | Sparse/missing references yield insufficient coverage/history rather than false zeros |
| Forecast evaluation | Forward-season folds, training-only reference and target-boundary embargo | Corrected skill still requires new numerical validation |

Forecast alerts are disabled when genuine validated forecast lower-bound percentiles are unavailable. A current-status percentile is not a substitute for a forecast uncertainty bound.

## 9. Four independent evidence questions

1. **Does the code work as specified?** Unit, contract and serving-equivalence tests address this.
2. **Did the statistical procedure perform well on relevant holdouts?** Attributable saved scientific-run results address this, with era, source and target qualifications.
3. **Do the artifacts match this source revision?** Provenance, immutable release hashes and refreshed reports are needed; passing new unit tests cannot refresh old numerical results.
4. **Is the deployed revision serving the intended artifacts?** Live version/health checks and deployment logs address this; Git push success alone does not.

Passing one question does not answer the others. In particular, `qa.py` now reports scientific interval acceptance separately from engineering check results. The serving packer's saved-QA markers are not a certificate that conditional coverage is acceptable.
