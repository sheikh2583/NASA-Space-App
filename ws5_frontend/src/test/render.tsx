/**
 * Test helper: render a component to static HTML in Vitest's node environment (no jsdom, no testing library).
 * Use it for component tests:  const html = await renderHtml(<StatusCard o={...} />);
 * Event handlers don't run here; put interaction logic in plain functions under src/lib/ and test those directly.
 */
import type { ReactElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { I18nextProvider } from "react-i18next";
import i18n from "../i18n";

export async function renderHtml(element: ReactElement, lang: "en" | "bn" = "en"): Promise<string> {
  // src/i18n sets document.documentElement.lang on language change; give the node test environment a stand-in.
  const g = globalThis as { document?: { documentElement: { lang?: string } } };
  g.document ??= { documentElement: {} };
  await i18n.changeLanguage(lang);
  return renderToStaticMarkup(<I18nextProvider i18n={i18n}>{element}</I18nextProvider>);
}

/** Visible text only (tags removed, whitespace collapsed), for readable assertions. */
export function textOf(html: string): string {
  return html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
}
