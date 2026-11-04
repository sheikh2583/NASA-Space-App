import { describe, expect, it } from "vitest";
import { StatusCard } from "../components/Panels";
import type { OutlookResponse } from "../types";
import rawSnapshot from "../../public/demo/snapshot.json";
import { renderHtml, textOf } from "./render";

const outlook = (rawSnapshot as unknown as { areas: Record<string, { outlook: OutlookResponse }> }).areas.bd.outlook;

describe("component test harness", () => {
  it("renders a real component with translations in both languages", async () => {
    const en = textOf(await renderHtml(<StatusCard o={outlook} />, "en"));
    expect(en).toContain("Current status");
    const bn = textOf(await renderHtml(<StatusCard o={outlook} />, "bn"));
    expect(bn).not.toContain("Current status");
    expect(bn.length).toBeGreaterThan(10);
  });
});
