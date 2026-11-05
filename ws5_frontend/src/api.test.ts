import { afterEach, describe, expect, it, vi } from "vitest";

afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); vi.resetModules(); });

describe("live deployment API address", () => {
  it("sends a compact named-area request", async () => {
    const fetcher = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({ series: [] }) });
    vi.stubGlobal("fetch", fetcher);
    const { api } = await import("./api");
    const req = { area_id: "named", start: "2020-01-01", end: "2020-12-31", res: "week" };
    await api.post("/aoi/summary", req);
    expect(JSON.parse(fetcher.mock.calls[0][1].body)).toEqual(req);
  });

  it("keeps each compared area and custom dates distinct in the live request", async () => {
    const a = { area_id: "dhaka", start: "2020-01-01", end: "2020-12-31", res: "month" };
    const b = { ...a, area_id: "khulna" };
    const response = { a: { series: [{ value: 1 }] }, b: { series: [{ value: 2 }] } };
    const fetcher = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => response });
    vi.stubGlobal("fetch", fetcher);
    const { api } = await import("./api");
    expect(await api.post("/aoi/compare", { a, b })).toEqual(response);
    expect(JSON.parse(fetcher.mock.calls[0][1].body)).toEqual({ a, b });
    expect(response.a).not.toEqual(response.b);
  });

  it.each(["network", "http", "json"])("retries live requests after a transient %s failure", async (kind) => {
    const fetcher = vi.fn();
    if (kind === "network") fetcher.mockRejectedValueOnce(new Error("offline"));
    else if (kind === "http") fetcher.mockResolvedValueOnce({ ok: false, status: 503 });
    else fetcher.mockResolvedValueOnce({ ok: true, json: async () => { throw new Error("bad JSON"); } });
    fetcher.mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ series: [] }) });
    vi.stubGlobal("fetch", fetcher);
    const { api } = await import("./api");
    await expect(api.post("/aoi/summary", { area_id: "named" })).rejects.toThrow();
    await expect(api.post("/aoi/summary", { area_id: "named" })).resolves.toEqual({ series: [] });
    expect(fetcher).toHaveBeenCalledTimes(2);
  });

  it("aborts an obsolete fetch without follow-up requests", async () => {
    const fetcher = vi.fn((_url, options) => new Promise((_resolve, reject) => {
      options.signal.addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError")));
    }));
    vi.stubGlobal("fetch", fetcher);
    const { api } = await import("./api");
    const ctl = new AbortController();
    const response = api.post("/aoi/summary", { area_id: "named" }, ctl.signal);
    ctl.abort();
    await expect(response).rejects.toMatchObject({ name: "AbortError" });
    expect(fetcher).toHaveBeenCalledTimes(1);
    expect(fetcher.mock.calls[0][1].signal.aborted).toBe(true);
  });

  it("does not start a fetch for an already cancelled request", async () => {
    const fetcher = vi.fn();
    vi.stubGlobal("fetch", fetcher);
    const { api } = await import("./api");
    const ctl = new AbortController(); ctl.abort();
    await expect(api.post("/aoi/summary", {}, ctl.signal)).rejects.toMatchObject({ name: "AbortError" });
    expect(fetcher).not.toHaveBeenCalled();
  });
  it("uses same-origin paths when configured with a root slash", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "/");
    const fetcher = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({ pieces: {} }) });
    vi.stubGlobal("fetch", fetcher);
    const { api } = await import("./api");
    await api.get("/meta/validation");
    expect(fetcher.mock.calls[0][0]).toBe("/meta/validation");
  });

  it("preserves an explicit separate API host for local development", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://localhost:8000/");
    const fetcher = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({ pieces: {} }) });
    vi.stubGlobal("fetch", fetcher);
    const { api } = await import("./api");
    await api.get("/meta/validation");
    expect(fetcher.mock.calls[0][0]).toBe("http://localhost:8000/meta/validation");
  });
});
