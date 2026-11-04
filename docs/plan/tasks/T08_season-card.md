---
id: T08
title: Season card and typical-window strip on the calendar (en/bn)
kind: agent
owner: Shammo
authors: [Shammo]
phase: P1
size: M
needs: [T07]
requires: []
branch: ws1/T08-season-card
touches: [ws5_frontend/src/App.tsx, ws5_frontend/src/types.ts, ws5_frontend/src/components/Calendar.tsx,
          ws5_frontend/src/lib/format.ts, ws5_frontend/src/lib/format.test.ts, ws5_frontend/src/styles.css,
          ws5_frontend/src/i18n/en.json, ws5_frontend/src/i18n/bn.json]
creates: [ws5_frontend/src/components/SeasonCard.tsx, ws5_frontend/src/components/SeasonCard.test.tsx]
checks: [CHECK-PLAN, CHECK-WEB, CHECK-SNAP]
---
## Goal
Answer the challenge's plainest question on screen: *when does burning usually happen here, and how is this season
going?* Show it in one card and as a strip above the calendar, in both languages, on a phone, and in snapshot mode.

## Context
- The data comes from `/aoi/season` (T07); in snapshot mode it comes from `areas.<key>.season`.
- An example response, with only the profile part, is `contracts/fixtures/punjab_season_profile.json`.
- Dates come as `median_md` / `q25_md` / `q75_md` strings like `"11-02"`, in a non-leap reference year.
- `lib/format.ts` `date(iso, opts)` already formats in the active language.
- `Calendar.tsx` draws years as rows and ISO weeks 1-52 as columns, with `LEFT = 34`, `TOP = 14` and
  `CELL + GAP = 12`. `weekOfYear()` folds week 53 into 52.
- Component tests run in node: use `renderHtml` and `textOf` from `src/test/render.tsx`. Don't add jsdom or a
  testing library.

## Steps
1. **`types.ts`.** Add interfaces mirroring `contracts/json_schemas/season_profile.schema.json`:
   - `SeasonTiming { median_md: string | null; q25_md: string | null; q75_md: string | null; median_offset_days: number }`
   - `SeasonTrend { metric: string; basis: string; n: number; ci: [number, number] | null; verdict: "later" | "earlier" | "more" | "fewer" | "no_clear_shift" | "insufficient_seasons"; days_per_decade?: number | null; pct_per_decade?: number | null; caveat?: string }`
   - `SeasonCurrent { season_year: number; status: "in_progress" | "ended" | "not_started"; to_date_total?: number; percentile_at_cutoff?: number | null; typical_to_date_total?: number | null; typical_share_by_cutoff?: number | null; data_through?: string }`
   - `SeasonInfo { name: string; window: { start_md: string; end_md: string }; typical: { n_seasons: number; p10: SeasonTiming | null; p50: SeasonTiming | null; p90: SeasonTiming | null; peak: SeasonTiming | null } | null; timing_trend: SeasonTrend | null; magnitude_trend: SeasonTrend | null; current: SeasonCurrent | null }`
   - `SeasonProfileResponse extends Envelope { area: string | null; as_of: string; data_through: string | null; definition: string; seasons: SeasonInfo[] }`
2. **`lib/format.ts`.** Add two functions, with tests in `format.test.ts`:
   - `monthDay(md: string): string` returns `date("2023-" + md, { day: "numeric", month: "short" })`.
   - `weekColumn(md: string): number` returns `weekOfYear("2023-" + md)`, except that it returns 1 when `md` starts
     with `"01-"` and the result is over 50.
   - Tests: `weekColumn("01-01") === 1` (1 Jan 2023 is in ISO week 52 of 2022), `weekColumn("11-02") === 44`,
     `weekColumn("12-31") === 52`.
3. **`SeasonCard.tsx`.** Props: `{ profile: SeasonProfileResponse }`. Renders `<section className="card">` with:
   - `h2`: `t("season.title")`, "When burning usually happens".
   - For each season with `typical?.p10 && typical.p90 && typical.p50`:
     - `h3`: `t("season.name_" + name)`;
     - `<p>`: `t("season.window", { from: monthDay(p10), to: monthDay(p90), mid: monthDay(p50) })`, "Usually from
       {{from}} to {{to}}, most around {{mid}}."
   - **Current season:**
     - `in_progress`: `t("season.now", { total: num(to_date_total), typical: num(typical_to_date_total), p: num(percentile_at_cutoff) })`,
       "This season so far: {{total}} detections; {{typical}} would be typical by this date (percentile {{p}})."
     - `ended` → `t("season.ended")`; `not_started` → `t("season.not_started")`.
   - **Trend:** only when the verdict is `later` or `earlier`: `t("season.timing_" + verdict, { n: num(Math.abs(days_per_decade), 1), lo: num(ci[0], 1), hi: num(ci[1], 1) })`.
     Only when the verdict is `more` or `fewer`: `t("season.amount_" + verdict, { n: num(Math.abs(pct_per_decade)), lo: …, hi: … })`,
     followed by `t("season.amount_caveat")`.
   - `<p className="meta">`: `t("season.definition")`, a translated short form of `profile.definition`.
   - `profile.seasons.length === 0` → `<p className="note">{t("season.none")}</p>`.
4. **Calendar strip.**
   - `Calendar` gets an optional prop `bands?: { label: string; from: string; to: string; peak: string }[]`.
   - For each band, draw one row **above** the year rows: increase `TOP` by 10 px per band. Draw a rect from
     `weekColumn(from)` to `weekColumn(to)`, 6 px high, with `fill="var(--band)"`, and a 2 px tick at
     `weekColumn(peak)`.
   - When `from > to` (a window that crosses the new year, like Bangladesh), draw two rects: from → 52 and 1 → to.
   - Add `<title>` and `aria-label`: `t("season.band_label", { name, from, to })`.
   - Define `--band: #d98c3f` in `:root` (`styles.css`).
5. **`App.tsx`.**
   - Add `season` state, typed `SeasonProfileResponse | null`.
   - In `load()`, add `api.post<SeasonProfileResponse>("/aoi/season", r)` to the `Promise.allSettled` list.
   - Clear it in `reset()`.
   - Render `<ErrorBoundary><SeasonCard profile={season} /></ErrorBoundary>` right after `StatusCard`.
   - Pass `bands` (from `season.seasons[].typical`) to `Calendar`.
   - A failed request leaves `season` null and renders nothing.
6. **i18n.** Add every `season.*` key to `en.json` and `bn.json` (Bangla drafted with AI help; T34 checks they are complete). Keys:
   - `title`, `window`, `now`, `ended`, `not_started`, `none`, `definition`, `band_label`, `amount_caveat`;
   - `name_paddy_residue` (bn "ধান কাটার পর খড় পোড়ানো"), `name_wheat_residue` (bn "গম কাটার পর খড় পোড়ানো"),
     `name_dry_season` (bn "শুষ্ক মৌসুম");
   - `timing_later`, `timing_earlier`, `amount_more`, `amount_fewer`.
7. **`SeasonCard.test.tsx`.** Use the real exported profile:
   `import raw from "../../public/demo/snapshot.json"`, then
   `const profile = (raw as unknown as { areas: Record<string, { season: SeasonProfileResponse }> }).areas.pb.season`.
   This is the same import style as `src/snapshot.test.ts`. Then check:
   - English: two `<h3>` headings; the paddy sentence contains "Oct" and "Nov".
   - Bangla: neither "Usually" nor "paddy" appears.
   - `{ ...profile, seasons: [] }` renders `t("season.none")`'s English text.
   - A copy of the profile with the paddy `timing_trend` set to `{ verdict: "later", days_per_decade: 4.3, ci: [1, 6.6], n: 14, metric: "p50 day", basis: "observed_era" }`
     contains "later".

8. Run the checks. Then serve the snapshot build (`npm run preview`) and look at both demo areas at 390 px width.
   Take screenshots for the PR.
9. Mark the card done, `split`, push and open the PR.

## Acceptance
- [ ] `format.test.ts` and `SeasonCard.test.tsx` pass.
- [ ] The snapshot build shows the season card and the calendar strip for both areas, in en and bn. Screenshots are
  in the PR.
- [ ] `npm run check:strings` passes: no hard-coded text.

## Stop and ask if
- `snapshot.json` has no `areas.pb.season` (T07 not merged on this branch's base), or any date renders as "Invalid Date".
