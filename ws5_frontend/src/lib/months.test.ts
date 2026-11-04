import { describe, expect, it } from "vitest";
import { monthColumns } from "./months";

describe("calendar month columns", () => {
  it("places labels in each month's first full ISO week", () => {
    const columns = monthColumns();
    expect(columns).toHaveLength(12);
    expect(columns[0]).toEqual({ month: 1, col: 1 });
    expect(columns[6]).toEqual({ month: 7, col: 27 });
    expect(columns[11]).toEqual({ month: 12, col: 49 });
  });
});
