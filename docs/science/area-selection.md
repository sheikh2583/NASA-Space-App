# Named-area explorer

The main area workflow is country → local name search → division/state → **Apply filters**, with **Reset** returning to Dhaka. The first view loads Dhaka's real administrative outline. Named boundaries are also selectable on the OpenStreetMap map by click or Enter/Space on the focused map button. Manual drawing and sample rectangles are absent from the primary UI; the underlying API still supports geometry/bbox requests.

The interaction takes inspiration from Dhoa's inspector (`X:\AIUB Hackathon\app\streamlit_app.py`, `render_filter_panel`): dependent administrative selectors, local filtering, and a deliberate Apply action above the map. FireSense uses its own React implementation and existing scientific data; no Dhoa GPU workloads or datasets were used.

## Data and selection

- `scripts/export_area_catalog.py` reads the processed cell table and original local ADM1 boundaries. It exports only loaded regions into `ws5_frontend/public/demo/areas.json`.
- Eight Bangladesh divisions and Punjab/Haryana/Delhi are available in the primary picker and region comparison. The two old sample AOIs remain only in the saved JSON/compatibility fixtures, not the selector or startup view. Source identifiers and raw spellings are retained; display labels use Rajshahi, Haryana, Barishal, and Chattogram, with source spellings accepted as search aliases.
- Selection sends the original Polygon/MultiPolygon to the API. Verified cell counts use boundary intersections with grid centres, matching `Store.select`. Assigned edge cells outside the original outline are not silently added.
- The exporter saves real API responses for all 13 named choices. Snapshot lookup matches the exact request geometry/bbox; unsupported geometries/dates are rejected rather than returning a different region's totals.
- Country/name filtering happens locally with no geocoder requests, extra API credentials, or public Nominatim dependency. OSM is the basemap, not the administrative boundary source.
- Search accepts English/Bangla names, aliases, case/diacritic variations, and country words. A unique result becomes the draft selection automatically; it is applied only on submit. “Viewing” continues to name the applied area until then. Reset applies the default boundary immediately. Language changes preserve selection IDs.
- If the catalog fails, the form offers Retry instead of substituting a sample rectangle. Loading/empty/error states disable inappropriate actions. Dates and calendar selection no longer refit the map when the geographic extent has not changed.
- Applying an area clears old results; request-generation checks prevent a slower previous response from replacing the latest area. Keyboard-accessible selectors provide an alternative to map clicks. Mock API responses remain synthetic fixtures, not scientific outputs for newly chosen areas.

## Boundary attribution

The exported IDs match these geoBoundaries source releases:

| Coverage | Source release | Original source / license |
|---|---|---|
| Bangladesh ADM1 | BGD-ADM1-32408957, represented year 2015 | geoBoundaries / Wikimedia Commons; CC0 1.0, per [release metadata](https://www.geoboundaries.org/api/current/gbOpen/BGD/ADM1/) |
| India ADM1 (three retained regions) | IND-ADM1-1811400, represented year 2011 | DataMeet India community / Election Commission of India; CC BY 2.5 IN, per [release metadata](https://www.geoboundaries.org/api/current/gbOpen/IND/ADM1/) and [DataMeet maps](https://github.com/datameet/maps) |

Geometry is retained from downloaded files; only supported features are extracted. Historical boundary vintages must not be mistaken for current official administrative boundaries. Map attribution credits OSM, geoBoundaries, DataMeet, and the India license. Respect the [OSM tile policy](https://operations.osmfoundation.org/policies/tiles/).

Regenerate and review `areas.json` (`scripts/export_area_catalog.py`) after changing scientific coverage. The source package includes it as a deliberate public artifact and excludes raw downloads. Test with `npm test`, `npm run check:strings`, and a production build with the Render settings (`VITE_API_BASE_URL=/`, `VITE_DATA_MODE=real`). Browser verification should cover country changes, a search yielding no results, a Bengali place-name search, selecting/applying a region, direct map selection, and a narrow viewport.
