/** Grouped English digits for the English interface. */
export function num(x: number | null | undefined, digits = 0): string {
  if (x === null || x === undefined || Number.isNaN(x)) return "–";
  const locale = "en-GB";
  return new Intl.NumberFormat(locale, { maximumFractionDigits: digits, minimumFractionDigits: 0 }).format(x);
}

export function date(iso: string, opts: Intl.DateTimeFormatOptions = { day: "numeric", month: "short", year: "numeric" }): string {
  const locale = "en-GB";
  return new Intl.DateTimeFormat(locale, { ...opts, timeZone: "UTC" }).format(new Date(iso + "T00:00:00Z"));
}

export function monthDay(md: string): string {
  return date(`2023-${md}`, { day: "numeric", month: "short" });
}

/** Actual ISO week number 1-53 for display of separate observations. */
export function isoWeekOfYear(iso: string): number {
  const d = new Date(iso + "T00:00:00Z");
  const day = (d.getUTCDay() + 6) % 7;
  d.setUTCDate(d.getUTCDate() - day + 3);
  const firstThu = new Date(Date.UTC(d.getUTCFullYear(), 0, 4));
  const w = 1 + Math.round(((d.getTime() - firstThu.getTime()) / 86400000 - 3 + ((firstThu.getUTCDay() + 6) % 7)) / 7);
  return w;
}

/** Folded same-week climatology convention; not observation coordinates. */
export function weekOfYear(iso: string): number {
  return Math.min(isoWeekOfYear(iso), 52);
}

export function weekColumn(md: string): number {
  const week = weekOfYear(`2023-${md}`);
  return md.startsWith("01-") && week > 50 ? 1 : week;
}

export function isoYear(iso: string): number {
  const d = new Date(iso + "T00:00:00Z");
  d.setUTCDate(d.getUTCDate() + 3 - ((d.getUTCDay() + 6) % 7));
  return d.getUTCFullYear();
}

export function addDays(iso: string, n: number): string {
  const d = new Date(iso + "T00:00:00Z");
  d.setUTCDate(d.getUTCDate() + n);
  return d.toISOString().slice(0, 10);
}
