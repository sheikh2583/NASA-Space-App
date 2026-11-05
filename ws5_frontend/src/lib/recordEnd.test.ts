import { describe, expect, it } from "vitest";
import { metadataEnd, validRecordEnd } from "./recordEnd";

describe("runtime record end", () => {
  it("rejects absent, malformed and impossible dates", () => {
    for (const value of [undefined, null, "", "2026-02-30", "2026-13-01", "1999-01-01"]) {
      expect(validRecordEnd(value)).toBe(false);
    }
    expect(validRecordEnd("2026-11-03")).toBe(true);
  });
  it("updates defaults, preserves explicit ranges and clamps unavailable dates", () => {
    expect(metadataEnd("2026-11-02", "2026-11-03", false)).toBe("2026-11-03");
    expect(metadataEnd("2020-06-01", "2026-11-03", true)).toBe("2020-06-01");
    expect(metadataEnd("2026-11-03", "2026-11-02", true)).toBe("2026-11-02");
  });
});
