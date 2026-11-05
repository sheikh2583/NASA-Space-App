import { describe, expect, it } from "vitest";
import { renderHtml, textOf } from "../test/render";
import { OutlookPanel, StatusCard } from "./Panels";
import type { OutlookResponse } from "../types";

// StatusCard reads only current_status; the rest of the response is irrelevant here.
function outlookWith(level: OutlookResponse["current_status"]["level"], week_percentile: number | null): OutlookResponse {
  return {
    current_status: {
      level, week_percentile, data_through: "2026-11-02", data_source: "harmonized",
      message: "server message (not shown by the card)",
    },
  } as unknown as OutlookResponse;
}

describe("StatusCard", () => {
  it("says a record-low week is much lower than usual, with its percentile", async () => {
    const text = textOf(await renderHtml(<StatusCard o={outlookWith("very_low", 0)} />, "en"));
    expect(text).toContain("Much lower than usual");
    expect(text).toContain("Percentile 0");
    expect(text).not.toContain("Normal");
  });

  it("uses English when an obsolete Bangla preference is requested", async () => {
    const text = textOf(await renderHtml(<StatusCard o={outlookWith("very_low", 0)} />, "bn"));
    expect(text).toContain("Much lower than usual");
    expect(text).toContain("Percentile 0");
    expect(text).not.toContain("স্বাভাবিকের চেয়ে অনেক কম");
  });

  it("labels an ordinary week as usual and a low one as lower than usual", async () => {
    expect(textOf(await renderHtml(<StatusCard o={outlookWith("none", 50)} />, "en"))).toContain("Usual");
    const low = textOf(await renderHtml(<StatusCard o={outlookWith("low", 20)} />, "en"));
    expect(low).toContain("Lower than usual");
    expect(low).not.toContain("Much lower");
  });

  it("explains insufficient history without displaying a percentile or usual verdict", async () => {
    const text = textOf(await renderHtml(<StatusCard o={outlookWith("insufficient_history", null)} />, "en"));
    expect(text).toContain("Insufficient history");
    expect(text).toContain("Not enough complete same-week history");
    expect(text).not.toContain("Percentile");
    expect(text).not.toContain("Usual");
    expect(text).not.toContain("NaN");
  });

  it.each([
    ["observed_viirs", "observed (VIIRS SNPP)"],
    ["adjusted_from_noaa20", "adjusted from NOAA-20"],
    ["modeled_from_modis", "modeled from MODIS"],
    ["mixed", "mixed sources"],
    ["VIIRS_NOAA20_NRT", "VIIRS_NOAA20_NRT"],
  ])("labels evaluated-week provenance %s and retains legacy saved labels", async (source, label) => {
    const o = outlookWith("none", 50);
    o.current_status.data_source = source;
    const text = textOf(await renderHtml(<StatusCard o={o} />, "en"));
    expect(text).toContain(`Evaluated week source: ${label}`);
    expect(text).not.toContain("Near-real-time source");
  });

  it("says when the latest week was not fully observed instead of comparing it", async () => {
    const text = textOf(await renderHtml(<StatusCard o={outlookWith("incomplete_coverage", null)} />, "en"));
    expect(text).toContain("Incomplete coverage");
    expect(text).toContain("did not observe every day");
    expect(text).not.toContain("Not enough complete same-week history");
    expect(text).not.toContain("Percentile");
  });
});

describe("OutlookPanel with incomplete coverage", () => {
  it("explains unobserved weeks rather than missing history", async () => {
    const o: OutlookResponse = {
      schema_version: "0.2.0", units: "detections", day_convention: "local_solar_date",
      region: { region_id: "r", region_name: "Test region" }, as_of: "2026-11-02",
      current_status: outlookWith("incomplete_coverage", null).current_status,
      season_to_date_percentile: null, season_to_date_status: "incomplete_coverage",
      expected_range: { q10: 0, q50: 0, q90: 0 },
      skill: { n_seasons: 0 }, status: "no_demonstrated_skill", alert: { level: "none" },
    };
    const text = textOf(await renderHtml(<OutlookPanel o={o} />, "en"));
    expect(text).toContain("not fully observed");
    expect(text).not.toContain("Not enough earlier seasons");
  });
});

describe("OutlookPanel with insufficient history", () => {
  it("does not present placeholder zeros as a historical range", async () => {
    const o: OutlookResponse = {
      schema_version: "0.2.0", units: "detections", day_convention: "local_solar_date",
      region: { region_id: "r", region_name: "Test region" }, as_of: "2026-11-02",
      current_status: outlookWith("insufficient_history", null).current_status,
      season_to_date_percentile: null, expected_range: { q10: 0, q50: 0, q90: 0 },
      skill: { n_seasons: 0 }, status: "no_demonstrated_skill", alert: { level: "none" },
    };
    const text = textOf(await renderHtml(<OutlookPanel o={o} />, "en"));
    expect(text).toContain("Not enough earlier seasons");
    expect(text).not.toContain("Season-to-date total is higher than");
    expect(text).not.toContain("Usual range at this point");
    expect(text).not.toContain("NaN");
  });
});
