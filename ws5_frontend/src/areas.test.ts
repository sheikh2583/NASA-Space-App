import { describe, expect, it } from "vitest";
import { areaLabel, defaultArea, EXAMPLE_AREAS, filterAreas, selectableAreas, type AreaOption } from "./areas";
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
    expect(filterAreas(areas, "BD", "ঢাকা").map((a) => a.name)).toEqual(["Dhaka"]);
    expect(filterAreas(areas, "BD", "Chattogram").map((a) => a.name)).toEqual(["Chittagong"]);
    expect(filterAreas(areas, "BD", "Rajshahi").map((a) => a.name)).toEqual(["Rajshani"]);
    expect(filterAreas(areas, "BD", "Dhaka Bangladesh").map((a) => a.name)).toEqual(["Dhaka"]);
  });
  it("opens a real administrative boundary and keeps rectangular samples out of the selector", () => {
    const visible = selectableAreas([...areas, ...EXAMPLE_AREAS]);
    expect(visible).toHaveLength(11);
    expect(visible.some((area) => area.id === "bd" || area.id === "pb")).toBe(false);
    const initial = defaultArea(visible)!;
    expect(initial.name).toBe("Dhaka");
    expect(initial.request.geometry).toBeDefined();
    expect(initial.request.bbox).toBeUndefined();
    expect(areaLabel(initial, "bn")).toBe("ঢাকা");
    expect(defaultArea([])).toBeUndefined();
  });
  it("compares actual administrative areas using their own saved responses", () => {
    const snapshot = rawSnapshot as unknown as Snapshot;
    const request = (name: string) => snapshot.areas[areas.find((a) => a.name === name)!.id].request;
    const a = request("Dhaka"), b = request("Khulna");
    const result = selectSnapshot(snapshot, "/aoi/compare", { a, b }) as { a: unknown; b: unknown };
    expect(result.a).toEqual(snapshot.areas[areaKey(a, snapshot)].summary);
    expect(result.b).toEqual(snapshot.areas[areaKey(b, snapshot)].summary);
    expect(result.a).not.toEqual(result.b);
  });
  it("serves every visible named area from its own saved request and rejects altered extents", () => {
    const snapshot = rawSnapshot as unknown as Snapshot;
    expect(areas).toHaveLength(11);
    for (const area of [...areas, ...EXAMPLE_AREAS]) {
      const request = { ...snapshot.areas[area.id].request, ...area.request };
      expect(areaKey(request, snapshot)).toBe(area.id);
      const summary = selectSnapshot(snapshot, "/aoi/summary", request) as { aoi: { n_cells: number }; series: unknown[] };
      expect(summary.series.length).toBeGreaterThan(1000);
      if (area.cellCount) expect(summary.aoi.n_cells).toBe(area.cellCount);
    }
    expect(() => areaKey({ bbox: [0, 0, 1, 1], start: "2020-01-01", end: "2021-01-01" }, snapshot)).toThrow();
  });
});
