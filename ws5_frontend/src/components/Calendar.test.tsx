import { describe, expect, it } from "vitest";
import { renderHtml, textOf } from "../test/render";
import Calendar from "./Calendar";
import type { SummaryPoint } from "../types";

const point = (t: string, value: number, extra: Partial<SummaryPoint> = {}): SummaryPoint => ({
  t, value, lo: value, hi: value, source: "observed_viirs", modeled_share: 0, drift_flag: false, ...extra,
});

describe("Calendar", () => {
  const series = [point("2026-10-26", 305), point("2026-11-02", 98, { complete: false, n_days: 1 })];

  it("outlines only the partial week with a dashed border and says it is partial", async () => {
    const html = await renderHtml(<Calendar series={series} selected={null} onSelect={() => {}} />, "en");
    expect(html.split('stroke-dasharray="2 2"').length - 1).toBe(1);
    expect(textOf(html)).toContain("Partial");
    expect(html).toContain("1 of 7 days have data");
  });

  it("draws no partial mark when every week is complete", async () => {
    const html = await renderHtml(<Calendar series={[point("2026-10-26", 305)]} selected={null} onSelect={() => {}} />, "en");
    expect(html).not.toContain('stroke-dasharray="2 2"');
  });
});
