import { describe, expect, it } from "vitest";
import { format, parse, type UrlState } from "./urlState";

describe("URL state", () => {
  it("round-trips every supported field in stable order", () => {
    const state: UrlState = { v: "validation", a: "punjab-id", p: "2024-11-04", s: "2" };
    expect(format(state)).toBe("#v=validation&a=punjab-id&p=2024-11-04&s=2");
    expect(parse(format(state))).toEqual(state);
  });

  it("ignores unknown keys and invalid values", () => {
    expect(parse("#v=other&a=punjab&p=2024-13-40&l=bn&s=one&extra=value"))
      .toEqual({ a: "punjab", s: "one" });
  });

  it("returns an empty hash for empty state", () => {
    expect(format({})).toBe("");
  });
});
