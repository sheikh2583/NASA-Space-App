import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { RAMP_CSS, burnScale } from "../lib/colour";
import { useTranslation } from "react-i18next";
import type { AOIRequest, Cell } from "../types";
import { date } from "../lib/format";
import { areaLabel, type AreaOption } from "../areas";

interface Props {
  aoi: AOIRequest | null;
  cells: Cell[] | null;
  period: { start: string; end: string } | null;
  areas: AreaOption[];
  selectedId: string | null;
  onSelect: (area: AreaOption) => void;
}

function regionStyle(selected: boolean): L.PathOptions {
  return {
    color: selected ? "#b4380f" : "#3d6b4f", weight: selected ? 2 : 1,
    fillColor: selected ? "#b4380f" : "#3d6b4f", fillOpacity: selected ? 0.15 : 0.04,
  };
}

export function updateRegionSelection(layers: Map<string, L.GeoJSON>, previous: string | null, selected: string | null) {
  for (const id of new Set([previous, selected])) {
    if (!id) continue;
    const layer = layers.get(id);
    if (!layer) continue;
    const active = id === selected;
    layer.setStyle(regionStyle(active));
    layer.eachLayer((child) => (child as L.Path).getElement?.()?.setAttribute("aria-pressed", String(active)));
  }
}

export default function MapView({ aoi, cells, period, areas, selectedId, onSelect }: Props) {
  const { t, i18n } = useTranslation();
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<L.Map | null>(null);
  const aoiLayer = useRef<L.FeatureGroup | null>(null);
  const cellLayer = useRef<L.LayerGroup | null>(null);
  const regionLayer = useRef<L.LayerGroup | null>(null);
  const regions = useRef(new Map<string, L.GeoJSON>());
  const previousSelected = useRef<string | null>(null);
  const selectedRef = useRef(selectedId);
  selectedRef.current = selectedId;
  const labels = useRef({ t, language: i18n.language });
  labels.current = { t, language: i18n.language };
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
    const selection = new L.FeatureGroup().addTo(m);
    cellLayer.current = L.layerGroup().addTo(m);
    regionLayer.current = L.layerGroup().addTo(m);
    aoiLayer.current = selection;
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
    regions.current.clear();
    for (const area of areas.filter((a) => a.cellCount !== undefined && a.request.geometry)) {
      const layer = L.geoJSON(area.request.geometry!, { style: regionStyle(area.id === selectedRef.current), onEachFeature: (_feature, featureLayer) => {
        featureLayer.on("add", () => {
          const path = (featureLayer as L.Path).getElement();
          if (!path) return;
          path.setAttribute("role", "button"); path.setAttribute("tabindex", "0");
          path.setAttribute("aria-label", labels.current.t("area.map_select", { name: areaLabel(area, labels.current.language) }));
          path.setAttribute("aria-pressed", String(area.id === selectedRef.current));
          path.addEventListener("keydown", (event) => {
            const key = (event as KeyboardEvent).key;
            if (key === "Enter" || key === " ") { event.preventDefault(); selectRef.current(area); }
          });
        });
      }});
      // Tooltip text is a DOM text node, never interpreted as HTML.
      const label = document.createElement("span"); label.textContent = areaLabel(area, labels.current.language);
      layer.bindTooltip(label).on("click", () => selectRef.current(area)).addTo(group);
      regions.current.set(area.id, layer);
    }
    return () => { group.clearLayers(); regions.current.clear(); previousSelected.current = null; };
  }, [areas]);

  useEffect(() => {
    updateRegionSelection(regions.current, previousSelected.current, selectedId);
    previousSelected.current = selectedId;
  }, [areas, selectedId]);

  useEffect(() => {
    for (const area of areas) {
      const layer = regions.current.get(area.id);
      if (!layer) continue;
      const label = document.createElement("span"); label.textContent = areaLabel(area, i18n.language);
      layer.setTooltipContent(label);
      layer.eachLayer((child) => (child as L.Path).getElement?.()?.setAttribute("aria-label", t("area.map_select", { name: areaLabel(area, i18n.language) })));
    }
  }, [areas, t, i18n.language]);

  const geometry = aoi?.geometry;
  const bbox = aoi?.bbox;
  useEffect(() => {
    const g = aoiLayer.current;
    if (!g || !map.current) return;
    g.clearLayers();
    if (!geometry && !bbox) return;
    const shape = geometry
      ? L.geoJSON(geometry, { interactive: false, style: { color: "#b4380f", weight: 2, fill: false } })
      : L.rectangle([[bbox![1], bbox![0]], [bbox![3], bbox![2]]], { interactive: false, color: "#b4380f", weight: 2, fill: false });
    shape.addTo(g);
    map.current.fitBounds(shape.getBounds(), { padding: [20, 20], maxZoom: 9 });
  }, [geometry, bbox]);

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
      <div ref={el} className="map" role="application" aria-label={t("map.select_hint")} />
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
