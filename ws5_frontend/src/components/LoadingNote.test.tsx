import { describe, expect, it } from "vitest";
import { renderHtml, textOf } from "../test/render";
import LoadingNote from "./LoadingNote";
import { RETRY_AFTER_MS, WAKING_AFTER_MS, wakePhase } from "../lib/waking";

describe("wakePhase", () => {
  it("is a plain load first, then waking after 3 s, then retry after 90 s", () => {
    expect(wakePhase(0)).toBe("loading");
    expect(wakePhase(WAKING_AFTER_MS - 1)).toBe("loading");
    expect(wakePhase(WAKING_AFTER_MS)).toBe("waking");
    expect(wakePhase(RETRY_AFTER_MS - 1)).toBe("waking");
    expect(wakePhase(RETRY_AFTER_MS)).toBe("retry");
  });
});

describe("LoadingNote", () => {
  const noop = () => {};

  it("says Loading at first, with no spinner", async () => {
    const html = await renderHtml(<LoadingNote onRetry={noop} />, "en");
    expect(textOf(html)).toBe("Loading…");
    expect(html).not.toContain("spinner");
  });

  it("explains a cold start with a spinner after 3 s", async () => {
    const html = await renderHtml(<LoadingNote onRetry={noop} initialElapsedMs={5_000} />, "en");
    expect(textOf(html)).toContain("Waking the server");
    expect(html).toContain("spinner");
    expect(html).not.toContain("<button");
  });

  it("offers a retry after 90 s", async () => {
    const html = await renderHtml(<LoadingNote onRetry={noop} initialElapsedMs={95_000} />, "en");
    expect(textOf(html)).toContain("Try again");
    expect(html).toContain("<button");
  });

  it("uses English for an obsolete Bangla preference", async () => {
    const text = textOf(await renderHtml(<LoadingNote onRetry={noop} initialElapsedMs={5_000} />, "bn"));
    expect(text).not.toContain("সার্ভার চালু হচ্ছে");
    expect(text).toContain("Waking");
  });
});
