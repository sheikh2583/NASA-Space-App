// Shapes from contracts/openapi.yaml 0.2.0. Keep in step with the contract; never add fields here first.
export type Source = "observed_viirs" | "adjusted_from_noaa20" | "modeled_from_modis" | "mixed";
export type Res = "day" | "week" | "month";
export type Level = "none" | "watch" | "high";
export type StatusLevel = Level | "low" | "very_low" | "insufficient_history";

export interface AOIRequest {
  area_id?: string;
  geometry?: GeoJSON.Polygon | GeoJSON.MultiPolygon;
  bbox?: [number, number, number, number];
  start: string;
  end: string;
  res?: Res;
}

export interface Envelope {
  schema_version: string;
  units: string;
  day_convention: string;
  notes?: string[];
}

export interface Anomaly {
  flag: boolean;
  score: number;
  exceeds_lower_bound?: boolean;
  depends_on_modeled_history?: boolean;
}

export interface SummaryPoint {
  t: string;
  value: number | null;
  lo: number | null;
  hi: number | null;
  source: Source;
  modeled_share: number;
  drift_flag: boolean;
  anomaly?: Anomaly;
  /** false when the period runs past the last day with data; missing means complete. */
  complete?: boolean;
  n_days?: number;
}

export interface SummaryResponse extends Envelope {
  aoi: { n_cells: number; area_km2: number };
  res: Res;
  seams?: string[];
  series: SummaryPoint[];
}

export interface Cell { cell_id: number; lat_c: number; lon_c: number; value: number; modeled_share: number }
export interface CellsResponse extends Envelope { period: { start: string; end: string }; cells: Cell[] }

export interface CriticalPeriod {
  start: string; end: string; severity: number; rank: number; peak_value: number;
  agri_tag: boolean; agri_share: number | null; n_weeks: number; depends_on_modeled_history: boolean;
}
export interface CriticalPeriodsResponse extends Envelope { periods: CriticalPeriod[] }

export interface Region { region_id: string; region_name: string }
export interface DriverItem {
  driver: string; lag_weeks: number; direction: "positive" | "negative"; strength: number;
  ci: [number, number]; evidence: "weak" | "moderate" | "strong";
}
export interface DriversResponse extends Envelope {
  region: Region; status: "ok" | "insufficient_data"; items: DriverItem[]; caveats: string[];
}

export interface CurrentStatus {
  week_percentile: number | null; level: StatusLevel; data_through: string; data_source?: string; message: string;
}
export interface OutlookResponse extends Envelope {
  region: Region; as_of: string; current_status: CurrentStatus; season_to_date_percentile: number | null;
  expected_range: { q10: number; q50: number; q90: number };
  skill: { vs_climatology?: number; vs_persistence?: number; ci?: [number, number]; n_seasons?: number };
  status: "skill" | "no_demonstrated_skill"; alert: { level: Level; rule?: string };
}

export interface SeasonTiming {
  median_md: string | null;
  q25_md: string | null;
  q75_md: string | null;
  median_offset_days: number;
}

export interface SeasonTrend {
  metric: string;
  basis: string;
  n: number;
  ci: [number, number] | null;
  verdict: "later" | "earlier" | "more" | "fewer" | "no_clear_shift" | "insufficient_seasons";
  days_per_decade?: number | null;
  pct_per_decade?: number | null;
  caveat?: string;
}

export interface SeasonCurrent {
  season_year: number;
  status: "in_progress" | "ended" | "not_started";
  to_date_total?: number;
  percentile_at_cutoff?: number | null;
  typical_to_date_total?: number | null;
  typical_share_by_cutoff?: number | null;
  data_through?: string;
}

export interface SeasonInfo {
  name: string;
  window: { start_md: string; end_md: string };
  typical: {
    n_seasons: number;
    p10: SeasonTiming | null;
    p50: SeasonTiming | null;
    p90: SeasonTiming | null;
    peak: SeasonTiming | null;
  } | null;
  timing_trend: SeasonTrend | null;
  magnitude_trend: SeasonTrend | null;
  current: SeasonCurrent | null;
}

export interface SeasonProfileResponse extends Envelope {
  area: string | null;
  as_of: string;
  data_through: string | null;
  definition: string;
  seasons: SeasonInfo[];
}

export interface ValidationPiece {
  schema_version: string; generated_at: string; producer: string;
  metrics: Record<string, unknown>; limitations: string[];
}
export interface ValidationResponse extends Envelope { pieces: Record<string, ValidationPiece>; missing: string[] }

export interface CompareResponse extends Envelope { a: SummaryResponse; b: SummaryResponse }
