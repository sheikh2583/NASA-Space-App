import type { AOIRequest, Envelope } from "./types";
import { STATIC_DEMO, snapshotCall } from "./snapshot";

// A configured "/" becomes an empty prefix, keeping hosted requests same-origin.
const configuredBase = import.meta.env.VITE_API_BASE_URL as string | undefined;
const BASE = configuredBase === undefined ? "http://localhost:8000" : configuredBase.replace(/\/$/, "");
const FALLBACK = (import.meta.env.VITE_FALLBACK_BASE_URL as string | undefined)?.replace(/\/$/, "") || "";
const TIMEOUT_MS = 60000; // Free Render compute can take longer on uncached AOIs.

export class AOIError extends Error {}
export class ApiError extends Error {}

interface FallbackIndex { regions: { region_id: string; region_name: string; bbox: [number, number, number, number] }[] }
let fallbackIndex: Promise<FallbackIndex> | null = null;

export function centreOf(req: AOIRequest): [number, number] {
  if (req.bbox) return [(req.bbox[0] + req.bbox[2]) / 2, (req.bbox[1] + req.bbox[3]) / 2];
  const geometry = req.geometry!;
  const ring = geometry.type === "MultiPolygon" ? geometry.coordinates.flatMap((polygon) => polygon[0]) : geometry.coordinates[0];
  const xs = ring.map((p) => p[0]);
  const ys = ring.map((p) => p[1]);
  return [(Math.min(...xs) + Math.max(...xs)) / 2, (Math.min(...ys) + Math.max(...ys)) / 2];
}

async function fromFallback<T extends Envelope>(path: string, req?: AOIRequest): Promise<T> {
  if (!FALLBACK) throw new ApiError("api_down");
  if (path === "/meta/validation") {
    const r = await fetch(`${FALLBACK}/meta/validation.json`);
    return { ...(await r.json()), fromFallback: true };
  }
  fallbackIndex ??= fetch(`${FALLBACK}/index.json`).then((r) => r.json());
  const idx = await fallbackIndex;
  const [x, y] = centreOf(req!);
  const hit = idx.regions.find((g) => x >= g.bbox[0] && x <= g.bbox[2] && y >= g.bbox[1] && y <= g.bbox[3]);
  if (!hit) throw new ApiError("fallback_no_region");
  const name = path.replace("/aoi/", "");
  const r = await fetch(`${FALLBACK}/regions/${hit.region_id}/${name}.json`);
  if (!r.ok) throw new ApiError("fallback_missing");
  return { ...(await r.json()), fromFallback: true, notes: [`fallback:${hit.region_name}`] };
}

async function call<T extends Envelope>(path: string, body?: unknown): Promise<T> {
  if (STATIC_DEMO) return snapshotCall<T>(path, body);
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), TIMEOUT_MS);
  try {
    const r = await fetch(`${BASE}${path}`, {
      method: body === undefined ? "GET" : "POST",
      headers: body === undefined ? undefined : { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: ctl.signal,
    });
    if (r.status === 422) {
      const j = await r.json().catch(() => ({}));
      throw new AOIError(typeof j.detail === "string" ? j.detail : "invalid_area");
    }
    if (!r.ok) throw new ApiError(`HTTP ${r.status}`);
    return (await r.json()) as T;
  } catch (e) {
    if (e instanceof AOIError) throw e;
    return fromFallback<T>(path, (body as { a?: AOIRequest })?.a ?? (body as AOIRequest));
  } finally {
    clearTimeout(timer);
  }
}

export const api = {
  post: <T extends Envelope>(path: string, req: unknown) => call<T>(path, req),
  get: <T extends Envelope>(path: string) => call<T>(path),
  async exportCsv(req: AOIRequest, view: "summary" | "cells" | "critical_periods") {
    if (STATIC_DEMO) throw new ApiError("CSV exports require the live backend.");
    const r = await fetch(`${BASE}/export`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...req, view }) });
    if (!r.ok) throw new ApiError(`HTTP ${r.status}`);
    const blob = await r.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `burning_${view}_${req.start}_${req.end}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  },
};
