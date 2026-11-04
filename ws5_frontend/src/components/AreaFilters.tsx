import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { areaLabel, defaultArea, filterAreas, type AreaOption } from "../areas";

interface Props {
  areas: AreaOption[];
  selectedId: string | null;
  loading: boolean;
  unavailable: boolean;
  onRetry: () => void;
  onApply: (area: AreaOption) => void;
}

export default function AreaFilters({ areas, selectedId, loading, unavailable, onRetry, onApply }: Props) {
  const { t, i18n } = useTranslation();
  const [country, setCountry] = useState("BD");
  const [query, setQuery] = useState("");
  const [draft, setDraft] = useState(selectedId ?? "");
  const applied = areas.find((a) => a.id === selectedId);
  useEffect(() => {
    const selected = areas.find((a) => a.id === selectedId);
    if (selected) setCountry(selected.country);
    setDraft(selectedId ?? ""); setQuery("");
  }, [selectedId, areas]);
  const filtered = filterAreas(areas, country, query);
  const selected = filtered.find((a) => a.id === draft);
  const label = (area: AreaOption) => areaLabel(area, i18n.language);
  const disabled = loading || unavailable;
  const reset = () => {
    const initial = defaultArea(areas);
    setQuery("");
    if (initial) { setCountry(initial.country); setDraft(initial.id); onApply(initial); }
  };
  return <section className="area-filters" aria-labelledby="area-filter-title">
    <div className="area-filter-heading">
      <div><h2 id="area-filter-title">{t("area.title")}</h2><p>{t("area.hint")}</p></div>
      <span className="tag">{loading ? t("state.loading") : t("area.coverage", { count: areas.length })}</span>
    </div>
    <form className="area-filter-form" onSubmit={(event) => { event.preventDefault(); if (selected) onApply(selected); }}>
      <label>{t("area.country")}<select disabled={disabled} value={country} onChange={(event) => { setCountry(event.target.value); setDraft(""); setQuery(""); }}>
        <option value="BD">{t("area.country_bd")}</option><option value="IN">{t("area.country_in")}</option>
      </select></label>
      <label>{t("area.search")}<input disabled={disabled} type="search" value={query} placeholder={t("area.placeholder")}
        onChange={(event) => {
          const value = event.target.value;
          setQuery(value);
          const matches = filterAreas(areas, country, value);
          setDraft(matches.length === 1 ? matches[0].id : "");
        }} /></label>
      <label>{t("area.region")}<select disabled={disabled} value={selected ? draft : ""} onChange={(event) => setDraft(event.target.value)}>
        <option value="">{t("area.choose")}</option>
        {filtered.map((a) => <option key={a.id} value={a.id}>{label(a)}</option>)}
      </select></label>
      <div className="area-filter-actions">
        <button className="apply-area" type="submit" disabled={disabled || !selected}>{t("area.apply")}</button>
        <button className="reset-area" type="button" disabled={disabled || !areas.length} onClick={reset}>{t("area.reset")}</button>
      </div>
    </form>
    <div className="area-filter-foot" aria-live="polite">
      {applied && <strong>{t("area.viewing", { name: label(applied) })}</strong>}
      {!disabled && <span>{selected && selected.id !== selectedId ? t("area.pending", { name: label(selected) }) : t(filtered.length ? "area.map_hint" : "area.no_match")}</span>}
      {unavailable && <span className="warn" role="alert">{t("area.unavailable")} <button type="button" onClick={onRetry}>{t("area.retry")}</button></span>}
    </div>
  </section>;
}
