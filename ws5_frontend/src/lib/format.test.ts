import { describe, expect, it } from "vitest";
import { addDays, isoYear, weekColumn, weekOfYear } from "./format";
import { centreOf } from "../api";

describe("calendar helpers", () => {
  it("matches ISO weeks and folds week 53 into 52", () => {
    expect(weekOfYear("2024-01-01")).toBe(1);
    expect(weekOfYear("2020-12-28")).toBe(52);
    expect(isoYear("2021-01-01")).toBe(2020);
  });
  it("adds days in UTC", () => {
    expect(addDays("2026-10-31", 2)).toBe("2026-11-02");
  });
  it("maps month-day values to calendar columns", () => {
    expect(weekColumn("01-01")).toBe(1);
    expect(weekColumn("11-02")).toBe(44);
    expect(weekColumn("12-31")).toBe(52);
  });
  it("finds the centre of a drawn polygon for the static fallback", () => {
    expect(centreOf({ bbox: [88, 20, 90, 22], start: "", end: "" })).toEqual([89, 21]);
    const g = { type: "Polygon" as const, coordinates: [[[74, 30], [76, 30], [76, 32], [74, 30]]] };
    expect(centreOf({ geometry: g, start: "", end: "" })).toEqual([75, 31]);
  });
});
