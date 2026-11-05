import { afterEach, describe, expect, it, vi } from "vitest";
import { DEMOS } from "./config";
import { areaKey, selectSnapshot, type Snapshot } from "./snapshot";
import rawSnapshot from "../public/demo/snapshot.json";

const snapshot = rawSnapshot as unknown as Snapshot;
const savedBd = snapshot.areas.bd.request;
const savedPb = snapshot.areas.pb.request;
afterEach(() => vi.unstubAllGlobals());

describe("hosted real-data snapshot", () => {
  it.each(["network", "http", "json"])("retries after a transient %s download failure", async (kind) => {
    vi.resetModules();
    const fetcher = vi.fn();
    if (kind === "network") fetcher.mockRejectedValueOnce(new Error("offline"));
    else if (kind === "http") fetcher.mockResolvedValueOnce({ ok: false });
    else fetcher.mockResolvedValueOnce({ ok: true, json: async () => { throw new Error("bad JSON"); } });
    fetcher.mockResolvedValueOnce({ ok: true, json: async () => snapshot });
    vi.stubGlobal("fetch", fetcher);
    const { snapshotCall } = await import("./snapshot");
    await expect(snapshotCall("/aoi/summary", savedBd)).rejects.toThrow();
    const result = await snapshotCall("/aoi/summary", savedBd);
    expect(result).toEqual(snapshot.areas.bd.summary);
    await snapshotCall("/aoi/summary", savedBd);
    expect(fetcher).toHaveBeenCalledTimes(2);
  });
  it("serves exact demo areas and refuses arbitrary drawn areas", () => {
    expect(areaKey(DEMOS.bd)).toBe("bd");
    expect(() => areaKey({ ...DEMOS.bd, bbox: [88, 20, 89, 21] })).toThrow();
    const result = selectSnapshot(snapshot, "/aoi/summary", savedBd) as { series: unknown[] };
    expect(result.series.length).toBeGreaterThan(1000);
    expect(rawSnapshot.data_mode).toBe("real");
  });
  it("rejects unsupported dates and resolutions rather than returning misleading totals", () => {
    expect(() => selectSnapshot(snapshot, "/aoi/summary", { ...savedBd, start: "2020-01-01" })).toThrow();
    expect(() => selectSnapshot(snapshot, "/aoi/summary", { ...savedPb, res: "day" })).toThrow();
  });
  it("serves the season profile for both demo areas", () => {
    expect((selectSnapshot(snapshot, "/aoi/season", savedPb) as { seasons: unknown[] }).seasons).toHaveLength(2);
    expect((selectSnapshot(snapshot, "/aoi/season", savedBd) as { seasons: unknown[] }).seasons).toHaveLength(1);
  });
  it("compares demo series and omits unsupported spatial cell products", () => {
    const compare = selectSnapshot(snapshot, "/aoi/compare", { a: DEMOS.bd, b: DEMOS.pb }) as { a: unknown; b: unknown };
    expect(compare.a).toEqual(snapshot.areas.bd.summary);
    expect(compare.b).toEqual(snapshot.areas.pb.summary);
    expect((selectSnapshot(snapshot, "/aoi/cells", DEMOS.bd) as { cells: unknown[] }).cells).toEqual([]);
  });
});
