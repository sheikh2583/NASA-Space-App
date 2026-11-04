import { DEMOS } from "./config";
import type { AOIRequest, Envelope, SummaryResponse, ValidationResponse } from "./types";

export const STATIC_DEMO = import.meta.env.VITE_DEMO_MODE === "snapshot";
type Area = { request: AOIRequest; summary: SummaryResponse } & Record<string, unknown>;
export interface Snapshot { validation: ValidationResponse; areas: Record<string, Area> }
let cached: Promise<Snapshot> | undefined;

export function areaKey(request: AOIRequest): string {
  for (const [key, area] of Object.entries(DEMOS)) {
    if (JSON.stringify(request.bbox ?? request.geometry) === JSON.stringify(area.bbox ?? area.geometry)) return key;
  }
  throw new Error("Snapshot mode supports the two named demo areas only.");
}

export function selectSnapshot(snapshot: Snapshot, path: string, body?: unknown): unknown {
  if (path === "/meta/validation") return snapshot.validation;
  if (path === "/aoi/compare") {
    const pair = body as { a: AOIRequest; b: AOIRequest };
    return { ...snapshot.areas[areaKey(pair.a)].summary,
      a: snapshot.areas[areaKey(pair.a)].summary, b: snapshot.areas[areaKey(pair.b)].summary };
  }
  const request = body as AOIRequest;
  const area = snapshot.areas[areaKey(request)];
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
  });
  return selectSnapshot(await cached, path, body) as T;
}
