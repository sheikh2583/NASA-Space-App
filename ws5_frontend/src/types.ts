// Shapes from contracts/openapi.yaml 0.2.0. Keep in step with the contract; never add fields here first.
export type Source = "observed_viirs" | "adjusted_from_noaa20" | "modeled_from_modis" | "mixed";
export type Res = "day" | "week" | "month";
export type Level = "none" | "watch" | "high";

export interface AOIRequest {
  geometry?: GeoJSON.Polygon;
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
  fromFallback?: boolean; // set by the client when the static fallback answered
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
  week_percentile: number; level: Level; data_through: string; data_source?: string; message: string;
}
export interface OutlookResponse extends Envelope {
  region: Region; as_of: string; current_status: CurrentStatus; season_to_date_percentile: number;
  expected_range: { q10: number; q50: number; q90: number };
  skill: { vs_climatology?: number; vs_persistence?: number; ci?: [number, number]; n_seasons?: number };
  status: "skill" | "no_demonstrated_skill"; alert: { level: Level; rule?: string };
}

export interface ValidationPiece {
  schema_version: string; generated_at: string; producer: string;
  metrics: Record<string, unknown>; limitations: string[];
}
export interface ValidationResponse extends Envelope { pieces: Record<string, ValidationPiece>; missing: string[] }

export interface CompareResponse extends Envelope { a: SummaryResponse; b: SummaryResponse }
