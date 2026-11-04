# Truth checks against NASA FIRMS (card T31)

Run on 2026-11-04 with `python -m ws6_validation.truth_checks`. Box: Punjab demo box lon 74.6-76.4, lat 29.8-31.2.
FIRMS counts every detection in the box by UTC date; ours counts our Punjab cells by local solar date.

| Check | Satellite | Period | FIRMS | Ours | Difference | Verdict |
|---|---|---|---:|---:|---:|---|
| a | SNPP (NRT) | 15 Sep-1 Nov 2026 | 460 | 455 | -1.1% | close |
| b | SNPP | 2024-11-02 | 345 | 353 | +2.3% | close |
| b | SNPP | 2024-11-03 | 0 | 3 | n/a | small counts (<10) |
| b | SNPP | 2024-11-04 | 0 | 0 | n/a | both 0 |
| b | SNPP | 2024-11-05 | 0 | 0 | n/a | both 0 |
| b | SNPP | 2024-11-06 | 2 | 0 | n/a | small counts (<10) |
| b | SNPP | 2024-11-07 | 400 | 395 | -1.2% | close |
| b | SNPP | 2024-11-08 | 488 | 489 | +0.2% | close |
| b | NOAA20 | 2024-11-02 | 229 | 230 | +0.4% | close |
| b | NOAA20 | 2024-11-03 | 288 | 285 | -1.0% | close |
| b | NOAA20 | 2024-11-04 | 259 | 262 | +1.2% | close |
| b | NOAA20 | 2024-11-05 | 209 | 208 | -0.5% | close |
| b | NOAA20 | 2024-11-06 | 182 | 181 | -0.5% | close |
| b | NOAA20 | 2024-11-07 | 269 | 271 | +0.7% | close |
| b | NOAA20 | 2024-11-08 | 407 | 401 | -1.5% | close |
| c | SNPP | 15 Sep-31 Dec 2016 | 63,646 | 63,621 | -0.0% | close |
| c | SNPP | 15 Sep-31 Dec 2024 | 5,917 | 5,907 | -0.2% | close |

## Notes

- Season-profile fixture, 2016 paddy season total (SNPP-equivalent, its own window): 63,626.0; FIRMS box count 15 Sep-31 Dec: 63,646.
- Season-profile fixture, 2024 paddy season total (SNPP-equivalent, its own window): 5,903.0; FIRMS box count 15 Sep-31 Dec: 5,917.
- Single-day differences of a few detections around the outage are expected: a night pass (about 01:30 local time) is the previous UTC date in FIRMS but the next local solar date in our grid.
