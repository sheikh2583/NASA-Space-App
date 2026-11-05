// Deterministic UI/transport fixtures only. These are not measured scientific results.
import type { OutlookResponse, SeasonInfo, SeasonProfileResponse } from "../../types";

const envelope = { schema_version: "0.2.0", units: "SNPP-equivalent detections per week", day_convention: "local_solar_date", notes: [] };
export const outlook: OutlookResponse = {
  ...envelope, region: { region_id: "test", region_name: "Test area" }, as_of: "2026-11-04",
  current_status: { level: "none", week_percentile: 50, data_through: "2026-11-03", data_source: "observed_viirs", message: "Synthetic test fixture." },
  season_to_date_percentile: 50, expected_range: { q10: 10, q50: 20, q90: 30 }, skill: { n_seasons: 0 },
  status: "no_demonstrated_skill", alert: { level: "none" },
};
const timing = (md: string) => ({ median_md: md, q25_md: md, q75_md: md, median_offset_days: 1 });
const season = (name: string, from: string, mid: string, to: string): SeasonInfo => ({
  name, window: { start_md: from, end_md: to },
  typical: { n_seasons: 10, p10: timing(from), p50: timing(mid), p90: timing(to), peak: timing(mid) },
  timing_trend: null, magnitude_trend: null, current: { season_year: 2026, status: "ended" },
});
export const punjabProfile: SeasonProfileResponse = {
  ...envelope, area: "pb", as_of: "2026-11-04", data_through: "2026-11-01", definition: "Synthetic test fixture.",
  seasons: [season("wheat_residue", "05-01", "05-10", "05-20"), season("paddy_residue", "10-20", "11-01", "11-15")],
};
export const bangladeshProfile: SeasonProfileResponse = {
  ...punjabProfile, area: "bd", seasons: [season("dry_season", "12-20", "03-01", "04-01")],
};
