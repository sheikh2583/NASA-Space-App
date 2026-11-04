import { describe, expect, it } from "vitest";
import { renderHtml } from "../test/render";
import HelpButton, { helpReducer } from "./Help";

describe("plain-language help", () => {
  it("handles every reducer action", () => {
    expect(helpReducer(false, "open")).toBe(true);
    expect(helpReducer(true, "close")).toBe(false);
    expect(helpReducer(false, "toggle")).toBe(true);
    expect(helpReducer(true, "toggle")).toBe(false);
    expect(helpReducer(true, "escape")).toBe(false);
  });

  it("renders collapsed help with its explanation available", async () => {
    const html = await renderHtml(<HelpButton topic="calendar" />);
    expect(html).toContain('aria-expanded="false"');
    expect(html).toMatch(/role="dialog"[^>]*hidden=""/);
    expect(html).toContain("Each square is one week");
  });
});
