import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { AOIError, api } from "./api";
import Calendar from "./components/Calendar";
import SeasonCard from "./components/SeasonCard";
import { DriversPanel, OutlookPanel, PeriodsPanel, StatusCard } from "./components/Panels";
import ErrorBoundary from "./components/ErrorBoundary";
import LoadingNote from "./components/LoadingNote";
import AnalysisControls from "./components/AnalysisControls";
import AreaFilters from "./components/AreaFilters";
import HelpButton from "./components/Help";
import { areaLabel, defaultArea, loadAreaCatalog, type AreaOption } from "./areas";
import { DATA_MODE, RECORD_END, RECORD_START } from "./config";
import { addDays, num } from "./lib/format";
import { format, parse } from "./lib/urlState";
import { metadataEnd, validRecordEnd } from "./lib/recordEnd";
import type {
  AOIRequest, CellsResponse, CompareResponse, CriticalPeriodsResponse, DriversResponse, OutlookResponse, Res,
  SeasonProfileResponse, SummaryResponse,
} from "./types";

type View = "explore" | "validation" | "method";
type Status = "idle" | "loading" | "ok" | "empty" | "oversized" | "error";

export function analysisArea(option: AreaOption): Pick<AOIRequest, "area_id" | "geometry" | "bbox"> {
  return option.cellCount !== undefined ? { area_id: option.id } : option.request;
}

const MapView = lazy(() => import("./components/MapView"));
const SeriesChart = lazy(() => import("./components/SeriesChart"));
const ValidationPage = lazy(() => import("./components/Pages").then((module) => ({ default: module.ValidationPage })));
const MethodPage = lazy(() => import("./components/Pages").then((module) => ({ default: module.MethodPage })));

function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false);
  useEffect(() => {
    if (typeof window === "undefined" || typeof window.matchMedia !== "function") return;
    const media = window.matchMedia(query);
    const update = () => setMatches(media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, [query]);
  return matches;
}

function CompareCard({ compact, areas, selectedId, value, onChange, onCompare }: {
  compact: boolean;
  areas: AreaOption[];
  selectedId: string | null;
  value: string;
  onChange: (value: string) => void;
  onCompare: () => void;
}) {
  const { t, i18n } = useTranslation();
  const body = <div className="controls">
    <label>{t("compare.with")}
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">–</option>
        {areas.filter((candidate) => candidate.id !== selectedId).map((candidate) =>
          <option key={candidate.id} value={candidate.id}>{areaLabel(candidate, i18n.language)}</option>)}
      </select>
    </label>
    <button className="chip" onClick={onCompare} disabled={!value || value === selectedId}>{t("compare.run")}</button>
  </div>;
  return compact
    ? <details className="card collapsible"><summary>{t("compare.title")}</summary>{body}</details>
    : <section className="card"><h2>{t("compare.title")}</h2>{body}</section>;
}

export default function App() {
  const { t, i18n } = useTranslation();
  const initialUrlState = useRef(parse(typeof window === "undefined" ? "" : window.location.hash)).current;
  const initialPeriod = useRef(initialUrlState.p);
  const [view, setView] = useState<View>(initialUrlState.v ?? "explore");
  const [area, setArea] = useState<Pick<AOIRequest, "geometry" | "bbox"> | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [areas, setAreas] = useState<AreaOption[]>([]);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [catalogVersion, setCatalogVersion] = useState(0);
  const [catalogUnavailable, setCatalogUnavailable] = useState(false);
  const generation = useRef(0);
  const batch = useRef<AbortController | null>(null);
  const pendingLoad = useRef<number | null>(null);
  const comparison = useRef<AbortController | null>(null);
  const previousSelection = useRef<{ area: typeof area; res: Res } | null>(null);
  const pickArea = useCallback((option: AreaOption) => {
    setSelectedId(option.id); setArea(option.request); setCompareWith("");
  }, []);
  useEffect(() => { let active = true;
    setCatalogLoading(true); setCatalogUnavailable(false);
    loadAreaCatalog().then((options) => {
      if (!active) return;
      setAreas(options);
      const initial = options.find((option) => option.id === initialUrlState.a) ?? defaultArea(options);
      if (initial) pickArea(initial);
    }).catch(() => { if (active) setCatalogUnavailable(true); })
      .finally(() => { if (active) setCatalogLoading(false); });
    return () => { active = false; };
  }, [catalogVersion, initialUrlState.a, pickArea]);
  const [start, setStart] = useState(RECORD_START);
  const [end, setEnd] = useState(RECORD_END);
  const [recordEnd, setRecordEnd] = useState(RECORD_END);
  const [metadataReady, setMetadataReady] = useState(false);
  const [metadataFallback, setMetadataFallback] = useState(false);
  const endEdited = useRef(false);
  useEffect(() => {
    let active = true;
    api.recordEnd().then((value) => {
      if (!validRecordEnd(value)) throw new Error("Invalid record metadata");
      if (!active) return;
      setRecordEnd(value);
      setEnd((current) => metadataEnd(current, value, endEdited.current));
      setStart((current) => current > value ? value : current);
    }).catch(() => { if (active) setMetadataFallback(true); })
      .finally(() => { if (active) setMetadataReady(true); });
    return () => { active = false; };
  }, []);
  const [res, setRes] = useState<Res>("week");
  const [status, setStatus] = useState<Status>("idle");
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [periods, setPeriods] = useState<CriticalPeriodsResponse | null>(null);
  const [drivers, setDrivers] = useState<DriversResponse | null>(null);
  const [outlook, setOutlook] = useState<OutlookResponse | null>(null);
  const [season, setSeason] = useState<SeasonProfileResponse | null>(null);
  const [cells, setCells] = useState<CellsResponse | null>(null);
  const [period, setPeriod] = useState<{ start: string; end: string; key: string } | null>(null);
  const [compareWith, setCompareWith] = useState<string>("");
  const [compare, setCompare] = useState<CompareResponse | null>(null);
  const [copied, setCopied] = useState(false);
  const [copyFallback, setCopyFallback] = useState(false);
  const copyTimer = useRef<number | null>(null);
  const fallbackInput = useRef<HTMLInputElement | null>(null);
  const phone = useMediaQuery("(max-width: 640px)");

  useEffect(() => { void i18n.changeLanguage("en"); }, [i18n]);

  const requestArea = useMemo(() => {
    const option = areas.find((candidate) => candidate.id === selectedId);
    return option ? analysisArea(option) : area;
  }, [areas, selectedId, area]);
  const req: AOIRequest | null = useMemo(() => requestArea ? { ...requestArea, start, end, res } : null, [requestArea, start, end, res]);

  const load = useCallback(async (r: AOIRequest) => {
    if (pendingLoad.current !== null) window.clearTimeout(pendingLoad.current);
    pendingLoad.current = null;
    batch.current?.abort(); comparison.current?.abort();
    const ctl = new AbortController();
    batch.current = ctl;
    const current = ++generation.current;
    setStatus("loading");
    setSummary(null); setPeriods(null); setDrivers(null); setOutlook(null); setSeason(null); setCells(null); setPeriod(null);
    setCompare(null);
    try {
      const s = await api.post<SummaryResponse>("/aoi/summary", r, ctl.signal);
      if (ctl.signal.aborted || current !== generation.current) return;
      setSummary(s);
      if (!s.series.length) { setStatus("empty"); return; }
      setStatus("ok");
      const [p, d, o, seasonProfile] = await Promise.allSettled([
        api.post<CriticalPeriodsResponse>("/aoi/critical-periods", r, ctl.signal),
        api.post<DriversResponse>("/aoi/drivers", r, ctl.signal),
        api.post<OutlookResponse>("/aoi/outlook", r, ctl.signal),
        api.post<SeasonProfileResponse>("/aoi/season", r, ctl.signal),
      ]);
      if (ctl.signal.aborted || current !== generation.current) return;
      setPeriods(p.status === "fulfilled" ? p.value : null);
      setDrivers(d.status === "fulfilled" ? d.value : null);
      setOutlook(o.status === "fulfilled" ? o.value : null);
      setSeason(seasonProfile.status === "fulfilled" ? seasonProfile.value : null);
      const linkedWeek = initialPeriod.current;
      initialPeriod.current = undefined;
      const lastWeek = s.series[s.series.length - 1]?.t;
      if (linkedWeek) setPeriod({ start: linkedWeek, end: addDays(linkedWeek, 6), key: linkedWeek });
      else if (lastWeek) setPeriod({ start: addDays(lastWeek, -7 * 7), end: addDays(lastWeek, 6), key: "recent" });
    } catch (e) {
      if (ctl.signal.aborted || current !== generation.current) return;
      initialPeriod.current = undefined;
      setSummary(null);
      setStatus(e instanceof AOIError ? "oversized" : "error");
    }
  }, []);

  useEffect(() => {
    if (!req || !metadataReady) return;
    const dateOnly = previousSelection.current?.area === area && previousSelection.current.res === res;
    previousSelection.current = { area, res };
    generation.current++;
    batch.current?.abort(); comparison.current?.abort();
    setStatus("loading");
    const timer = window.setTimeout(() => { pendingLoad.current = null; void load(req); }, dateOnly ? 300 : 0);
    pendingLoad.current = timer;
    return () => {
      window.clearTimeout(timer);
      if (pendingLoad.current === timer) pendingLoad.current = null;
      generation.current++;
      batch.current?.abort(); comparison.current?.abort();
    };
  }, [req, metadataReady, area, res, load]);

  useEffect(() => {
    if (catalogLoading) return;
    const catalogId = selectedId && areas.some((option) => option.id === selectedId) ? selectedId : undefined;
    history.replaceState(null, "", format({
      v: view,
      a: catalogId,
      p: period?.start ?? initialPeriod.current,
    }));
  }, [areas, catalogLoading, period, selectedId, view]);

  useEffect(() => {
    if (!requestArea || !period) return;
    let active = true;
    const ctl = new AbortController();
    api.post<CellsResponse>("/aoi/cells", { ...requestArea, start: period.start, end: period.end, res: "week" }, ctl.signal)
      .then((value) => { if (active) setCells(value); }).catch(() => { if (active) setCells(null); });
    return () => { active = false; ctl.abort(); };
  }, [requestArea, period]);

  const runCompare = async () => {
    if (!req || !compareWith) return;
    const other = areas.find((candidate) => candidate.id === compareWith && candidate.id !== selectedId);
    if (!other) return;
    comparison.current?.abort();
    const ctl = new AbortController();
    comparison.current = ctl;
    const current = generation.current;
    const result = await api.post<CompareResponse>("/aoi/compare", { a: req, b: { ...analysisArea(other), start, end, res } }, ctl.signal).catch(() => null);
    if (!ctl.signal.aborted && current === generation.current) setCompare(result);
  };
  const copyLink = async () => {
    setCopyFallback(false);
    try {
      if (!navigator.clipboard?.writeText) throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      if (copyTimer.current !== null) window.clearTimeout(copyTimer.current);
      copyTimer.current = window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
      setCopyFallback(true);
    }
  };
  useEffect(() => {
    if (copyFallback) fallbackInput.current?.select();
  }, [copyFallback]);
  useEffect(() => () => {
    if (copyTimer.current !== null) window.clearTimeout(copyTimer.current);
  }, []);
  const reset = () => {
    batch.current?.abort(); comparison.current?.abort();
    generation.current++; setArea(null); setSelectedId(null); setStatus("idle"); setSummary(null); setPeriods(null);
    setDrivers(null); setOutlook(null); setSeason(null); setCells(null); setPeriod(null); setCompare(null);
  };

  return (
    <Suspense fallback={<p className="note page-loading">{t("state.loading")}</p>}>
      <header className="topbar">
        <div>
          <h1>{t("app.title")}</h1>
          <div className="sub">{t("app.subtitle")}</div>
        </div>
        <nav aria-label="views">
          {(["explore", "validation", "method"] as View[]).map((v) => (
            <button key={v} aria-current={view === v ? "page" : undefined} onClick={() => setView(v)}>{t(`nav.${v}`)}</button>
          ))}
        </nav>
      </header>
      <div className={`banner ${DATA_MODE}`}>
        <span className="data-badge">{t(`app.data_${DATA_MODE}`)}</span> {t("app.scope")}
      </div>
      {view === "validation" && <ErrorBoundary><ValidationPage /></ErrorBoundary>}
      {view === "method" && <ErrorBoundary><MethodPage /></ErrorBoundary>}
      {view === "explore" && (
        <main className="explorer">
          <AreaFilters areas={areas} selectedId={selectedId} loading={catalogLoading} unavailable={catalogUnavailable}
            onRetry={() => setCatalogVersion((version) => version + 1)} onApply={pickArea} />
          <div className="layout">
          <div className="mapcol">
            <MapView aoi={area ? { ...area, start, end, res } : null} cells={cells?.cells ?? null} period={period} areas={areas} selectedId={selectedId} onSelect={pickArea} />
          </div>
          <div className="panels">
            {metadataFallback && <p className="warn">{t("hosting.date_fallback", { date: recordEnd })}</p>}
            <AnalysisControls start={start} end={end} recordEnd={recordEnd} res={res} canRun={Boolean(req) && metadataReady}
              onStart={setStart} onEnd={(value) => { endEdited.current = true; setEnd(value); }} onRes={setRes}
              onRefresh={() => req && void load(req)} onReset={reset}
              summary={summary && status === "ok" ? t("aoi.summary", { cells: num(summary.aoi.n_cells), area: num(summary.aoi.area_km2) }) : undefined} />
            {status === "idle" && !catalogLoading && !catalogUnavailable && <p className="note">{t("map.select_hint")}</p>}
            {status === "loading" && <LoadingNote onRetry={() => req && void load(req)} />}
            {status === "empty" && <p className="warn">{t("state.empty")}</p>}
            {status === "oversized" && <p className="warn">{t("state.oversized")}</p>}
            {status === "error" && <p className="warn">{t("state.error")}</p>}
            {status === "ok" && summary && (
              <>
                {outlook && <ErrorBoundary><StatusCard o={outlook} /></ErrorBoundary>}
                {season && <ErrorBoundary><SeasonCard profile={season} /></ErrorBoundary>}
                <ErrorBoundary>
                  <section className="card">
                    <div className="card-title"><h2>{t("calendar.title")}</h2><HelpButton topic="calendar" /></div>
                    <p className="meta">{t("calendar.hint")}</p>
                    {res === "week" && <Calendar series={summary.series} selected={period?.key ?? null}
                      bands={(season?.seasons ?? []).flatMap((item) => {
                        const typical = item.typical;
                        return typical?.p10?.median_md && typical.p90?.median_md && typical.peak?.median_md
                          ? [{ label: t(`season.name_${item.name}`), from: typical.p10.median_md,
                              to: typical.p90.median_md, peak: typical.peak.median_md }]
                          : [];
                      })}
                      onSelect={(w) => setPeriod({ start: w, end: addDays(w, 6), key: w })} />}
                  </section>
                </ErrorBoundary>
                <ErrorBoundary>
                  <section className="card">
                    <div className="card-title"><h2>{t("chart.title")}</h2><HelpButton topic="bands" /></div>
                    <SeriesChart series={summary.series} seams={summary.seams ?? []} highlight={period}
                                 second={compare?.b.series} />
                  </section>
                </ErrorBoundary>
                {periods && <ErrorBoundary><PeriodsPanel periods={periods.periods} selected={period?.key ?? null}
                  onSelect={(p) => setPeriod({ start: p.start, end: p.end, key: p.start })} /></ErrorBoundary>}
                {outlook && <ErrorBoundary><OutlookPanel o={outlook} /></ErrorBoundary>}
                {drivers && <ErrorBoundary><DriversPanel d={drivers} collapsible={phone} /></ErrorBoundary>}
                <CompareCard compact={phone} areas={areas} selectedId={selectedId} value={compareWith}
                  onChange={setCompareWith} onCompare={() => void runCompare()} />
                <section className="card">
                  <h2>{t("export.title")}</h2>
                  <div className="exportrow">
                    <button onClick={() => req && api.exportCsv(req, "summary")}>{t("export.summary")}</button>
                    <button onClick={() => req && period && api.exportCsv({ ...req, start: period.start, end: period.end }, "cells")}>{t("export.cells")}</button>
                    <button onClick={() => req && api.exportCsv(req, "critical_periods")}>{t("export.periods")}</button>
                    <button onClick={() => window.print()}>{t("export.print")}</button>
                    <button onClick={() => void copyLink()}>{t("export.copy_link")}</button>
                  </div>
                  {copied && <p className="meta" role="status">{t("export.copied")}</p>}
                  {copyFallback && <input ref={fallbackInput} readOnly value={window.location.href}
                    aria-label={t("export.copy_link")} onFocus={(event) => event.currentTarget.select()} />}
                </section>
              </>
            )}
          </div>
          </div>
        </main>
      )}
    </Suspense>
  );
}
