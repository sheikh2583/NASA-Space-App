# NOTES (ws5_frontend)

## Decisions and assumptions
- React 19 + Vite 8 + TypeScript (6/7) + Leaflet/leaflet-draw + Recharts + custom SVG calendar. Plain CSS instead of
  Tailwind (one less build step). i18n with i18next; bn.json is an AI draft that needs a fluent review.
- Static fallback: when the API fails, the app finds the region containing the AOI centre in VITE_FALLBACK_BASE_URL/index.json.
- Method panel reads docs/science/method_*.md, copied into public/ by scripts/copy-method.mjs before dev and build.
- `npm run check:strings` fails on visible English outside t().

## Known issues
- Not yet checked on a real phone, with a colour-blindness simulator, or by a Bangla reader (manual tasks).

## AI assistance log (where AI tools helped)
- 2026-11-03: everything in this folder was written with Claude (AI assistant) at Sheikh's direction before the event, on synthetic data, and assigned to this workstream's owner. Review it before relying on it; rerun on real data.
