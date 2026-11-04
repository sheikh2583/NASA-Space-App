import { describe, expect, it } from "vitest";
import { EXAMPLE_AREAS, filterAreas, type AreaOption } from "./areas";
import { areaKey, selectSnapshot, type Snapshot } from "./snapshot";
import rawSnapshot from "../public/demo/snapshot.json";
import catalog from "../public/demo/areas.json";

describe("named area selection", () => {
  const areas = catalog.areas as AreaOption[];
  it("filters countries and matches names without case or accent sensitivity", () => {
    expect(filterAreas(areas, "BD", "dhaka").map((a) => a.name)).toEqual(["Dhaka"]);
    expect(filterAreas(areas, "IN", "dhaka")).toEqual([]);
    expect(filterAreas(areas, "IN", "haryana").map((a) => a.name)).toEqual(["Haryāna"]);
    expect(filterAreas(areas, "BD", "missing place")).toEqual([]);
  });
  it("serves every visible named area from its own saved request and rejects altered extents", () => {
    const snapshot = rawSnapshot as unknown as Snapshot;
    expect(areas).toHaveLength(11);
    for (const area of [...areas, ...EXAMPLE_AREAS]) {
      const request = { ...area.request, start: "2000-11-01", end: "2026-11-02", res: "week" as const };
      expect(areaKey(request, snapshot)).toBe(area.id);
      const summary = selectSnapshot(snapshot, "/aoi/summary", request) as { aoi: { n_cells: number }; series: unknown[] };
      expect(summary.series.length).toBeGreaterThan(1000);
      if (area.cellCount) expect(summary.aoi.n_cells).toBe(area.cellCount);
    }
    expect(() => areaKey({ bbox: [0, 0, 1, 1], start: "2020-01-01", end: "2021-01-01" }, snapshot)).toThrow();
  });
});
