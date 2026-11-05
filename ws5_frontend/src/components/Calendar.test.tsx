import { describe, expect, it } from "vitest";
import { renderHtml, textOf } from "../test/render";
import Calendar from "./Calendar";
import type { SummaryPoint } from "../types";

const point = (t: string, value: number, extra: Partial<SummaryPoint> = {}): SummaryPoint => ({
  t, value, lo: value, hi: value, source: "observed_viirs", modeled_share: 0, drift_flag: false, ...extra,
});

describe("Calendar", () => {
  it("places week-52 and week-53 observations in separate visible squares", async () => {
    const html = await renderHtml(<Calendar series={[point("2015-12-21", 17), point("2015-12-28", 3)]}
      selected={null} onSelect={() => {}} />, "en");
    const positions = [...html.matchAll(/<rect class="cell[^"]*" x="([^"]+)" y="([^"]+)"/g)];
    expect(positions).toHaveLength(2);
    expect(positions[0][1]).not.toBe(positions[1][1]);
    expect(positions[0][2]).toBe(positions[1][2]);
    const width = Number(html.match(/<svg width="([^"]+)"/)?.[1]);
    expect(Number(positions[1][1]) + 11).toBeLessThanOrEqual(width);
    expect(textOf(html)).toContain("17");
    expect(textOf(html)).toContain("3");
  });
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
