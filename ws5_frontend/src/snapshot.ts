import { DEMOS } from "./config";
import type { AOIRequest, Envelope, SummaryResponse, ValidationResponse } from "./types";

export const STATIC_DEMO = import.meta.env.VITE_DEMO_MODE === "snapshot";
type Area = { request: AOIRequest; summary: SummaryResponse } & Record<string, unknown>;
export interface Snapshot { data_through?: string; validation: ValidationResponse; areas: Record<string, Area> }
let cached: Promise<Snapshot> | undefined;

export function areaKey(request: AOIRequest, snapshot?: Snapshot): string {
  const areas = snapshot ? Object.fromEntries(Object.entries(snapshot.areas).map(([key, area]) => [key, area.request])) : DEMOS;
  for (const [key, area] of Object.entries(areas)) {
    if (JSON.stringify(request.bbox ?? request.geometry) === JSON.stringify(area.bbox ?? area.geometry)) return key;
  }
  throw new Error("Snapshot mode supports the named saved areas only.");
}

export function selectSnapshot(snapshot: Snapshot, path: string, body?: unknown): unknown {
  if (path === "/health") return { data_through: snapshot.data_through };
  if (path === "/meta/validation") return snapshot.validation;
  if (path === "/aoi/compare") {
    const pair = body as { a: AOIRequest; b: AOIRequest };
    return { ...snapshot.areas[areaKey(pair.a, snapshot)].summary,
      a: snapshot.areas[areaKey(pair.a, snapshot)].summary, b: snapshot.areas[areaKey(pair.b, snapshot)].summary };
  }
  const request = body as AOIRequest;
  const area = snapshot.areas[areaKey(request, snapshot)];
  if (path === "/aoi/cells") return { ...area.summary, cells: [], period: { start: request.start, end: request.end } };
  if (request.start !== area.request.start || request.end !== area.request.end || (request.res ?? "week") !== "week") {
    throw new Error("Snapshot dates and weekly resolution are fixed; use the live backend for custom queries.");
  }
  const result = area[path.replace("/aoi/", "")];
  if (!result) throw new Error("Unavailable snapshot endpoint");
  return result;
}

export async function snapshotCall<T extends Envelope>(path: string, body?: unknown): Promise<T> {
  cached ??= fetch(`${import.meta.env.BASE_URL}demo/snapshot.json`).then(async response => {
    if (!response.ok) throw new Error("Snapshot unavailable");
    return response.json();
  }).catch((error) => {
    cached = undefined;
    throw error;
  });
  return selectSnapshot(await cached, path, body) as T;
}
