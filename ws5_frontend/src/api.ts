import type { AOIRequest, Envelope } from "./types";

// A configured "/" becomes an empty prefix, keeping hosted requests same-origin.
const configuredBase = import.meta.env.VITE_API_BASE_URL as string | undefined;
const BASE = configuredBase === undefined ? "http://localhost:8000" : configuredBase.replace(/\/$/, "");
const TIMEOUT_MS = 60000; // Free Render compute can take longer on uncached AOIs.

export class AOIError extends Error {}
export class ApiError extends Error {}

async function call<T extends Envelope>(path: string, body?: unknown, signal?: AbortSignal): Promise<T> {
  if (signal?.aborted) throw signal.reason ?? new DOMException("Aborted", "AbortError");
  const ctl = new AbortController();
  const abort = () => ctl.abort(signal?.reason);
  signal?.addEventListener("abort", abort, { once: true });
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
    if (signal?.aborted) throw signal.reason ?? new DOMException("Aborted", "AbortError");
    if (e instanceof AOIError) throw e;
    throw e instanceof ApiError ? e : new ApiError("api_down");
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener("abort", abort);
  }
}

export const api = {
  recordEnd: () => call<Envelope & { data_through?: unknown }>("/health").then((value) => value.data_through),
  post: <T extends Envelope>(path: string, req: unknown, signal?: AbortSignal) => call<T>(path, req, signal),
  get: <T extends Envelope>(path: string) => call<T>(path),
  async exportCsv(req: AOIRequest, view: "summary" | "cells" | "critical_periods") {
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
