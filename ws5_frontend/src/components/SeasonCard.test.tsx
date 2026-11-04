import { describe, expect, it } from "vitest";
import raw from "../../public/demo/snapshot.json";
import type { SeasonProfileResponse } from "../types";
import { renderHtml, textOf } from "../test/render";
import SeasonCard from "./SeasonCard";

const profile = (raw as unknown as { areas: Record<string, { season: SeasonProfileResponse }> }).areas.pb.season;

describe("season card", () => {
  it("shows both Punjab seasons and their central windows in English", async () => {
    const html = await renderHtml(<SeasonCard profile={profile} />);
    expect(html.match(/<h3>/g)).toHaveLength(2);
    const text = textOf(html);
    expect(text).toContain("Oct");
    expect(text).toContain("Nov");
  });

  it("uses translated Bangla copy", async () => {
    const text = textOf(await renderHtml(<SeasonCard profile={profile} />, "bn"));
    expect(text).not.toContain("Usually");
    expect(text.toLowerCase()).not.toContain("paddy");
  });

  it("explains when no season profile is available", async () => {
    const text = textOf(await renderHtml(<SeasonCard profile={{ ...profile, seasons: [] }} />));
    expect(text).toContain("No season profile is available for this area.");
  });

  it("shows a measured later timing trend", async () => {
    const seasons = profile.seasons.map((season) => season.name === "paddy_residue" ? {
      ...season,
      timing_trend: {
        verdict: "later" as const, days_per_decade: 4.3, ci: [1, 6.6] as [number, number], n: 14,
        metric: "p50 day", basis: "observed_era",
      },
    } : season);
    const text = textOf(await renderHtml(<SeasonCard profile={{ ...profile, seasons }} />));
    expect(text).toContain("later");
  });
});
