import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { RAMP_CSS, burnScale } from "../lib/colour";
import { useTranslation } from "react-i18next";
import type { AOIRequest, Cell } from "../types";
import { date } from "../lib/format";
import type { AreaOption } from "../areas";

interface Props {
  aoi: AOIRequest | null;
  cells: Cell[] | null;
  period: { start: string; end: string } | null;
  areas: AreaOption[];
  selectedId: string | null;
  onSelect: (area: AreaOption) => void;
}

export default function MapView({ aoi, cells, period, areas, selectedId, onSelect }: Props) {
  const { t } = useTranslation();
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<L.Map | null>(null);
  const aoiLayer = useRef<L.FeatureGroup | null>(null);
  const cellLayer = useRef<L.LayerGroup | null>(null);
  const regionLayer = useRef<L.LayerGroup | null>(null);
  const [tileError, setTileError] = useState(false);
  const selectRef = useRef(onSelect);
  selectRef.current = onSelect;

  useEffect(() => {
    if (!el.current || map.current) return;
    const m = L.map(el.current, { center: [26.5, 83], zoom: 5, worldCopyJump: true });
    // OSM's standard raster endpoint supports normal interactive browser maps
    // without a provider key. FIRMS credentials belong only on the data backend.
    const tiles = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | Boundaries: <a href="https://www.geoboundaries.org/">geoBoundaries</a>, <a href="https://github.com/datameet/maps">DataMeet India</a> (<a href="https://creativecommons.org/licenses/by/2.5/in/">CC BY 2.5 IN</a>) | Fire data: NASA FIRMS',
      maxZoom: 12,
    });
    tiles.on("tileerror", () => setTileError(true));
    tiles.on("tileload", () => setTileError(false));
    tiles.addTo(m);
    const drawn = new L.FeatureGroup().addTo(m);
    cellLayer.current = L.layerGroup().addTo(m);
    regionLayer.current = L.layerGroup().addTo(m);
    aoiLayer.current = drawn;
    map.current = m;
    return () => {
      tiles.off();
      m.remove();
      map.current = null;
      aoiLayer.current = null;
      cellLayer.current = null;
      regionLayer.current = null;
    };
  }, []);

  useEffect(() => {
    const group = regionLayer.current;
    if (!group) return;
    group.clearLayers();
    for (const area of areas.filter((a) => a.cellCount !== undefined && a.request.geometry)) {
      const selected = area.id === selectedId;
      const layer = L.geoJSON(area.request.geometry!, { style: {
        color: selected ? "#b4380f" : "#3d6b4f", weight: selected ? 2 : 1,
        fillColor: selected ? "#b4380f" : "#3d6b4f", fillOpacity: selected ? 0.15 : 0.04,
      }});
      // Tooltip text is a DOM text node, never interpreted as HTML.
      const label = document.createElement("span"); label.textContent = area.name;
      layer.bindTooltip(label).on("click", () => selectRef.current(area)).addTo(group);
    }
  }, [areas, selectedId]);

  useEffect(() => {
    const g = aoiLayer.current;
    if (!g || !map.current) return;
    g.clearLayers();
    if (!aoi) return;
    const shape = aoi.geometry
      ? L.geoJSON(aoi.geometry, { interactive: false, style: { color: "#b4380f", weight: 2, fill: false } })
      : L.rectangle([[aoi.bbox![1], aoi.bbox![0]], [aoi.bbox![3], aoi.bbox![2]]], { interactive: false, color: "#b4380f", weight: 2, fill: false });
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
        interactive: false, stroke: mostlyModeled, color: "#1f1a17", weight: 1, dashArray: "3 3", fillOpacity: 0.78,
        fillColor: color(Math.max(c.value, 1)) as string,
      }).bindTooltip(`${c.value.toFixed(1)}`).addTo(lg);
    }
  }, [cells]);

  return (
    <>
      <div ref={el} className="map" role="application" aria-label={t("map.draw_hint")} />
      {tileError && <p className="warn" role="status">{t("map.tiles_unavailable")}</p>}
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
