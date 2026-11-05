import { describe, expect, it } from "vitest";
import { areaLabel, defaultArea, EXAMPLE_AREAS, filterAreas, selectableAreas, type AreaOption } from "./areas";
import { analysisArea } from "./App";
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
  it("preserves every catalog boundary and cell count for live named-area requests", () => {
    expect(areas).toHaveLength(11);
    for (const area of areas) {
      expect(analysisArea(area)).toEqual({ area_id: area.id });
      expect(area.request.geometry).toBeDefined();
      expect(area.cellCount).toBeGreaterThan(0);
    }
    for (const area of EXAMPLE_AREAS) expect(analysisArea(area)).toEqual(area.request);
  });
});
