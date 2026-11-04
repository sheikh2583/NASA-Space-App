import { describe, expect, it } from "vitest";
import { DEMOS } from "./config";
import { areaKey, selectSnapshot, type Snapshot } from "./snapshot";
import rawSnapshot from "../public/demo/snapshot.json";

const snapshot = rawSnapshot as unknown as Snapshot;

describe("hosted real-data snapshot", () => {
  it("serves exact demo areas and refuses arbitrary drawn areas", () => {
    expect(areaKey(DEMOS.bd)).toBe("bd");
    expect(() => areaKey({ ...DEMOS.bd, bbox: [88, 20, 89, 21] })).toThrow();
    const result = selectSnapshot(snapshot, "/aoi/summary", DEMOS.bd) as { series: unknown[] };
    expect(result.series.length).toBeGreaterThan(1000);
    expect(rawSnapshot.data_mode).toBe("real");
  });
  it("rejects unsupported dates and resolutions rather than returning misleading totals", () => {
    expect(() => selectSnapshot(snapshot, "/aoi/summary", { ...DEMOS.bd, start: "2020-01-01" })).toThrow();
    expect(() => selectSnapshot(snapshot, "/aoi/summary", { ...DEMOS.pb, res: "day" })).toThrow();
  });
  it("serves the season profile for both demo areas", () => {
    expect((selectSnapshot(snapshot, "/aoi/season", DEMOS.pb) as { seasons: unknown[] }).seasons).toHaveLength(2);
    expect((selectSnapshot(snapshot, "/aoi/season", DEMOS.bd) as { seasons: unknown[] }).seasons).toHaveLength(1);
  });
  it("compares demo series and omits unsupported spatial cell products", () => {
    const compare = selectSnapshot(snapshot, "/aoi/compare", { a: DEMOS.bd, b: DEMOS.pb }) as { a: unknown; b: unknown };
    expect(compare.a).toEqual(snapshot.areas.bd.summary);
    expect(compare.b).toEqual(snapshot.areas.pb.summary);
    expect((selectSnapshot(snapshot, "/aoi/cells", DEMOS.bd) as { cells: unknown[] }).cells).toEqual([]);
  });
});
