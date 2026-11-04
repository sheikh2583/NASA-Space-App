import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { filterAreas, type AreaOption } from "../areas";

interface Props {
  areas: AreaOption[];
  selectedId: string | null;
  unavailable: boolean;
  onApply: (area: AreaOption) => void;
}

export default function AreaFilters({ areas, selectedId, unavailable, onApply }: Props) {
  const { t } = useTranslation();
  const [country, setCountry] = useState("BD");
  const [query, setQuery] = useState("");
  const [draft, setDraft] = useState(selectedId ?? "");
  useEffect(() => {
    const selected = areas.find((a) => a.id === selectedId);
    if (selected) setCountry(selected.country);
    setDraft(selectedId ?? "");
    setQuery("");
  }, [selectedId, areas]);
  const filtered = filterAreas(areas, country, query);
  const selected = filtered.find((a) => a.id === draft);
  return <section className="area-filters" aria-labelledby="area-filter-title">
    <div className="area-filter-heading">
      <div><h2 id="area-filter-title">{t("area.title")}</h2><p>{t("area.hint")}</p></div>
      <span className="tag">{t("area.coverage", { count: areas.length })}</span>
    </div>
    <form className="area-filter-form" onSubmit={(event) => { event.preventDefault(); if (selected) onApply(selected); }}>
      <label>{t("area.country")}<select value={country} onChange={(event) => { setCountry(event.target.value); setDraft(""); setQuery(""); }}>
        <option value="BD">{t("area.country_bd")}</option><option value="IN">{t("area.country_in")}</option>
      </select></label>
      <label>{t("area.search")}<input type="search" value={query} placeholder={t("area.placeholder")}
        onChange={(event) => { setQuery(event.target.value); setDraft(""); }} /></label>
      <label>{t("area.region")}<select value={selected ? draft : ""} onChange={(event) => setDraft(event.target.value)}>
        <option value="">{t("area.choose")}</option>
        {filtered.map((a) => <option key={a.id} value={a.id}>{a.labelKey ? t(a.labelKey) : a.name}</option>)}
      </select></label>
      <button className="apply-area" type="submit" disabled={!selected}>{t("area.apply")}</button>
    </form>
    <div className="area-filter-foot" aria-live="polite">
      <span>{selected ? t("area.selected", { name: selected.labelKey ? t(selected.labelKey) : selected.name }) : t(filtered.length ? "area.map_hint" : "area.no_match")}</span>
      {unavailable && <span className="warn">{t("area.unavailable")}</span>}
    </div>
  </section>;
}
