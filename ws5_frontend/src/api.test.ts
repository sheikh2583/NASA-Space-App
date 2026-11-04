import { afterEach, describe, expect, it, vi } from "vitest";

afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); vi.resetModules(); });

describe("live deployment API address", () => {
  it("uses same-origin paths when configured with a root slash", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "/");
    vi.stubEnv("VITE_DEMO_MODE", "live");
    const fetcher = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({ pieces: {} }) });
    vi.stubGlobal("fetch", fetcher);
    const { api } = await import("./api");
    await api.get("/meta/validation");
    expect(fetcher.mock.calls[0][0]).toBe("/meta/validation");
  });

  it("preserves an explicit separate API host for local development", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://localhost:8000/");
    vi.stubEnv("VITE_DEMO_MODE", "live");
    const fetcher = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({ pieces: {} }) });
    vi.stubGlobal("fetch", fetcher);
    const { api } = await import("./api");
    await api.get("/meta/validation");
    expect(fetcher.mock.calls[0][0]).toBe("http://localhost:8000/meta/validation");
  });
});
