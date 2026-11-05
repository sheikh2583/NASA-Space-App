import { describe, expect, it, vi } from "vitest";
import type L from "leaflet";
vi.mock("leaflet", () => ({ default: {} }));
import { updateRegionSelection } from "./MapView";

describe("retained administrative layers", () => {
  it("restyles only old/new selections and updates their accessibility state", () => {
    const layer = () => {
      const setAttribute = vi.fn();
      return { setStyle: vi.fn(), setAttribute,
        eachLayer: (fn: (child: unknown) => void) => fn({ getElement: () => ({ setAttribute }) }) };
    };
    const old = layer(), current = layer(), untouched = layer();
    const layers = new Map([["old", old], ["current", current], ["untouched", untouched]]);
    updateRegionSelection(layers as unknown as Map<string, L.GeoJSON>, "old", "current");
    expect(old.setStyle).toHaveBeenCalledTimes(1);
    expect(current.setStyle).toHaveBeenCalledTimes(1);
    expect(untouched.setStyle).not.toHaveBeenCalled();
    expect(old.setAttribute).toHaveBeenCalledWith("aria-pressed", "false");
    expect(current.setAttribute).toHaveBeenCalledWith("aria-pressed", "true");
    expect(layers.get("current")).toBe(current);
  });
});
