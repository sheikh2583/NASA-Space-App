import { describe, expect, it } from "vitest";
import { addDays, isoYear, isoWeekOfYear, weekColumn, weekOfYear } from "./format";

describe("calendar helpers", () => {
  it("preserves week 53 for display independently of folded climatology", () => {
    expect(isoWeekOfYear("2015-12-21")).toBe(52);
    expect(isoWeekOfYear("2015-12-28")).toBe(53);
    expect(isoWeekOfYear("2021-01-01")).toBe(53);
    expect(weekOfYear("2015-12-28")).toBe(52);
  });
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
});
