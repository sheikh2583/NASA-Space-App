import { describe, expect, it } from "vitest";
import { analysisArea } from "./App";
import type { AreaOption } from "./areas";

describe("analysis transport", () => {
  const option: AreaOption = { id: "catalog-id", name: "Area", country: "BD", cellCount: 1,
    request: { geometry: { type: "Polygon", coordinates: [[[90, 23], [91, 23], [91, 24], [90, 23]]] } } };
  it("uses the ID and preserves original geometry for map consumers", () => {
    expect(analysisArea(option)).toEqual({ area_id: option.id });
    expect(option.request.geometry).toBeDefined();
  });
  it("keeps custom/example geometry and bbox requests", () => {
    expect(analysisArea({ ...option, cellCount: undefined })).toEqual(option.request);
    const sample = { ...option, cellCount: undefined, request: { bbox: [89, 23, 90, 24] as [number, number, number, number] } };
    expect(analysisArea(sample)).toEqual(sample.request);
  });
});
