import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-draw";
import "leaflet-draw/dist/leaflet.draw.css";
import { RAMP_CSS, burnScale } from "../lib/colour";
import { useTranslation } from "react-i18next";
import type { AOIRequest, Cell } from "../types";
import { date } from "../lib/format";
import { STATIC_DEMO } from "../snapshot";

interface Props {
  aoi: AOIRequest | null;
  cells: Cell[] | null;
  period: { start: string; end: string } | null;
  onDraw: (geometry: GeoJSON.Polygon) => void;
}

// Leaflet-draw's default icons point at image files the bundler does not ship; the draw tools only need the toolbar sprites.
delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl;

export default function MapView({ aoi, cells, period, onDraw }: Props) {
  const { t } = useTranslation();
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<L.Map | null>(null);
  const aoiLayer = useRef<L.FeatureGroup | null>(null);
  const cellLayer = useRef<L.LayerGroup | null>(null);
  const drawRef = useRef(onDraw);
  drawRef.current = onDraw;

  useEffect(() => {
    if (!el.current || map.current) return;
    const m = L.map(el.current, { center: [26.5, 83], zoom: 5, worldCopyJump: true });
    L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a> | Fire data: NASA FIRMS',
      subdomains: "abcd", maxZoom: 12,
    }).addTo(m);
    const drawn = new L.FeatureGroup().addTo(m);
    cellLayer.current = L.layerGroup().addTo(m);
    aoiLayer.current = drawn;
    const ctl = new L.Control.Draw({
      position: "topright",
      draw: { polyline: false, circle: false, marker: false, circlemarker: false,
              rectangle: { shapeOptions: { color: "#1f1a17", weight: 2, fill: false } },
              polygon: { allowIntersection: false, shapeOptions: { color: "#1f1a17", weight: 2, fill: false } } },
      edit: { featureGroup: drawn, edit: false, remove: false },
    });
    if (!STATIC_DEMO) m.addControl(ctl);
    m.on(L.Draw.Event.CREATED, (e) => {
      const layer = (e as L.DrawEvents.Created).layer as L.Polygon;
      const gj = layer.toGeoJSON().geometry as GeoJSON.Polygon;
      drawRef.current(gj);
    });
    map.current = m;
  }, []);

  useEffect(() => {
    const g = aoiLayer.current;
    if (!g || !map.current) return;
    g.clearLayers();
    if (!aoi) return;
    const shape = aoi.geometry
      ? L.geoJSON(aoi.geometry, { style: { color: "#1f1a17", weight: 2, fill: false } })
      : L.rectangle([[aoi.bbox![1], aoi.bbox![0]], [aoi.bbox![3], aoi.bbox![2]]], { color: "#1f1a17", weight: 2, fill: false });
    shape.addTo(g);
    map.current.fitBounds(shape.getBounds(), { padding: [20, 20], maxZoom: 9 });
  }, [aoi]);

  useEffect(() => {
    const lg = cellLayer.current;
    if (!lg) return;
    lg.clearLayers();
    if (!cells || cells.length === 0) return;
    const max = Math.max(...cells.map((c) => c.value), 1.01);
    const color = burnScale(max);
    for (const c of cells) {
      const mostlyModeled = c.modeled_share > 0.5;
      L.rectangle([[c.lat_c - 0.05, c.lon_c - 0.05], [c.lat_c + 0.05, c.lon_c + 0.05]], {
        stroke: mostlyModeled, color: "#1f1a17", weight: 1, dashArray: "3 3", fillOpacity: 0.78,
        fillColor: color(Math.max(c.value, 1)) as string,
      }).bindTooltip(`${c.value.toFixed(1)}`).addTo(lg);
    }
  }, [cells]);

  return (
    <>
      <div ref={el} className="map" role="application" aria-label={t("map.draw_hint")} />
      {cells && period && (
        <div className="legend" aria-live="polite">
          <strong>{t("map.where_title")}</strong>
          <div className="meta">{t("map.where_period", { start: date(period.start), end: date(period.end) })}</div>
          <div className="ramp" style={{ background: RAMP_CSS }} />
          <div className="ends"><span>{t("map.legend_low")}</span><span>{t("map.legend_high")}</span></div>
          <div className="meta">{t("map.modeled_outline")}</div>
        </div>
      )}
    </>
  );
}
