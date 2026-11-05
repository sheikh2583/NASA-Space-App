import { describe, expect, it } from "vitest";
import { renderHtml, textOf } from "../test/render";
import { ValidationNotices } from "./Pages";
import type { ValidationResponse } from "../types";

const report: ValidationResponse = {
  schema_version: "0.2.0", units: "detections", day_convention: "local_solar_date", pieces: {}, missing: [],
};

describe("validation report availability", () => {
  it("shows both missing pieces and corrupt files", async () => {
    const html = await renderHtml(<ValidationNotices report={{ ...report, missing: ["intervals_by_stratum"], corrupt: ["intervals.json"] }} />);
    expect(textOf(html)).toContain("Not yet available: intervals_by_stratum");
    expect(textOf(html)).toContain("Could not read validation files: intervals.json");
    expect(html).toContain('role="alert"');
  });

  it("accepts legacy responses without the optional corrupt field", async () => {
    expect(await renderHtml(<ValidationNotices report={report} />)).toBe("");
  });
});
