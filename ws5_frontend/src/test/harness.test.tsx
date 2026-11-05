import { describe, expect, it } from "vitest";
import { StatusCard } from "../components/Panels";
import { outlook } from "./fixtures/products";
import { renderHtml, textOf } from "./render";
import i18n from "../i18n";
import { num, date } from "../lib/format";

describe("component test harness", () => {
  it("renders English consistently with an obsolete language preference", async () => {
    const en = textOf(await renderHtml(<StatusCard o={outlook} />, "en"));
    expect(en).toContain("Current status");
    const bn = textOf(await renderHtml(<StatusCard o={outlook} />, "bn"));
    expect(bn).toBe(en);
    expect(bn.length).toBeGreaterThan(10);
    expect(i18n.hasResourceBundle("bn", "translation")).toBe(false);
    expect(num(1234)).toBe("1,234");
    expect(date("2026-11-03")).toContain("Nov");
  });
});
