import { describe, expect, it } from "vitest";
import { renderHtml, textOf } from "../test/render";
import { StatusCard } from "./Panels";
import type { OutlookResponse } from "../types";

// StatusCard reads only current_status; the rest of the response is irrelevant here.
function outlookWith(level: OutlookResponse["current_status"]["level"], week_percentile: number): OutlookResponse {
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

  it("uses Bangla wording in Bangla", async () => {
    const text = textOf(await renderHtml(<StatusCard o={outlookWith("very_low", 0)} />, "bn"));
    expect(text).not.toContain("Much lower than usual");
    expect(text).not.toContain("Percentile");
    expect(text).toContain("স্বাভাবিকের চেয়ে অনেক কম");
  });

  it("labels an ordinary week as usual and a low one as lower than usual", async () => {
    expect(textOf(await renderHtml(<StatusCard o={outlookWith("none", 50)} />, "en"))).toContain("Usual");
    const low = textOf(await renderHtml(<StatusCard o={outlookWith("low", 20)} />, "en"));
    expect(low).toContain("Lower than usual");
    expect(low).not.toContain("Much lower");
  });
});
