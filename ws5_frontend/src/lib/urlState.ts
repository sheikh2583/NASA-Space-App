export interface UrlState {
  v?: "explore" | "validation" | "method";
  a?: string;
  p?: string;
  s?: string;
}

const views = new Set<NonNullable<UrlState["v"]>>(["explore", "validation", "method"]);

function validDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const [year, month, day] = value.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  return date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day;
}

export function parse(hash: string): UrlState {
  const params = new URLSearchParams(hash.replace(/^#/, ""));
  const state: UrlState = {};
  const view = params.get("v");
  const area = params.get("a");
  const period = params.get("p");
  const story = params.get("s");
  if (view && views.has(view as NonNullable<UrlState["v"]>)) state.v = view as NonNullable<UrlState["v"]>;
  if (area) state.a = area;
  if (period && validDate(period)) state.p = period;
  if (story) state.s = story;
  return state;
}

export function format(state: UrlState): string {
  const params = new URLSearchParams();
  if (state.v) params.set("v", state.v);
  if (state.a) params.set("a", state.a);
  if (state.p) params.set("p", state.p);
  if (state.s) params.set("s", state.s);
  const value = params.toString();
  return value ? `#${value}` : "";
}
