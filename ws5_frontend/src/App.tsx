import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { AOIError, api } from "./api";
import Calendar from "./components/Calendar";
import { DriversPanel, OutlookPanel, PeriodsPanel, StatusCard } from "./components/Panels";
import ErrorBoundary from "./components/ErrorBoundary";
import AnalysisControls from "./components/AnalysisControls";
import AreaFilters from "./components/AreaFilters";
import { areaLabel, defaultArea, loadAreaCatalog, type AreaOption } from "./areas";
import { DATA_MODE, RECORD_END, RECORD_START } from "./config";
import { STATIC_DEMO } from "./snapshot";
import { addDays, num } from "./lib/format";
import type {
  AOIRequest, CellsResponse, CompareResponse, CriticalPeriodsResponse, DriversResponse, OutlookResponse, Res, SummaryResponse,
} from "./types";

type View = "explore" | "validation" | "method";
type Status = "idle" | "loading" | "ok" | "empty" | "oversized" | "error";

const MapView = lazy(() => import("./components/MapView"));
const SeriesChart = lazy(() => import("./components/SeriesChart"));
const ValidationPage = lazy(() => import("./components/Pages").then((module) => ({ default: module.ValidationPage })));
const MethodPage = lazy(() => import("./components/Pages").then((module) => ({ default: module.MethodPage })));

export default function App() {
  const { t, i18n } = useTranslation();
  const [view, setView] = useState<View>("explore");
  const [area, setArea] = useState<Pick<AOIRequest, "geometry" | "bbox"> | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [areas, setAreas] = useState<AreaOption[]>([]);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [catalogVersion, setCatalogVersion] = useState(0);
  const [catalogUnavailable, setCatalogUnavailable] = useState(false);
  const generation = useRef(0);
  useEffect(() => { let active = true;
    setCatalogLoading(true); setCatalogUnavailable(false);
    loadAreaCatalog().then((options) => {
      if (!active) return;
      setAreas(options);
      const initial = defaultArea(options);
      if (initial) { setSelectedId(initial.id); setArea(initial.request); }
    }).catch(() => { if (active) setCatalogUnavailable(true); })
      .finally(() => { if (active) setCatalogLoading(false); });
    return () => { active = false; };
  }, [catalogVersion]);
  const [start, setStart] = useState(RECORD_START);
  const [end, setEnd] = useState(RECORD_END);
  const [res, setRes] = useState<Res>("week");
  const [status, setStatus] = useState<Status>("idle");
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [periods, setPeriods] = useState<CriticalPeriodsResponse | null>(null);
  const [drivers, setDrivers] = useState<DriversResponse | null>(null);
  const [outlook, setOutlook] = useState<OutlookResponse | null>(null);
  const [cells, setCells] = useState<CellsResponse | null>(null);
  const [period, setPeriod] = useState<{ start: string; end: string; key: string } | null>(null);
  const [compareWith, setCompareWith] = useState<string>("");
  const [compare, setCompare] = useState<CompareResponse | null>(null);
  const [fallbackNote, setFallbackNote] = useState<string | null>(null);

  const req: AOIRequest | null = useMemo(() => area ? { ...area, start, end, res } : null, [area, start, end, res]);

  const load = useCallback(async (r: AOIRequest) => {
    const current = ++generation.current;
    setStatus("loading");
    setSummary(null); setPeriods(null); setDrivers(null); setOutlook(null); setCells(null); setPeriod(null); setFallbackNote(null);
    setCompare(null);
    try {
      const s = await api.post<SummaryResponse>("/aoi/summary", r);
      if (current !== generation.current) return;
      setSummary(s);
      setFallbackNote(s.fromFallback ? (s.notes?.[0] ?? "").replace("fallback:", "") : null);
      if (!s.series.length) { setStatus("empty"); return; }
      setStatus("ok");
      const [p, d, o] = await Promise.allSettled([
        api.post<CriticalPeriodsResponse>("/aoi/critical-periods", r),
        api.post<DriversResponse>("/aoi/drivers", r),
        api.post<OutlookResponse>("/aoi/outlook", r),
      ]);
      if (current !== generation.current) return;
      setPeriods(p.status === "fulfilled" ? p.value : null);
      setDrivers(d.status === "fulfilled" ? d.value : null);
      setOutlook(o.status === "fulfilled" ? o.value : null);
      const lastWeek = s.series[s.series.length - 1]?.t;
      if (lastWeek) setPeriod({ start: addDays(lastWeek, -7 * 7), end: addDays(lastWeek, 6), key: "recent" });
    } catch (e) {
      if (current !== generation.current) return;
      setSummary(null);
      setStatus(e instanceof AOIError ? "oversized" : "error");
    }
  }, []);

  useEffect(() => { if (req) void load(req); }, [area, start, end, res]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (STATIC_DEMO || !area || !period) return;
    let active = true;
    api.post<CellsResponse>("/aoi/cells", { ...area, start: period.start, end: period.end, res: "week" })
      .then((value) => { if (active) setCells(value); }).catch(() => { if (active) setCells(null); });
    return () => { active = false; };
  }, [area, period]);

  const pickArea = (option: AreaOption) => { setSelectedId(option.id); setArea(option.request); setCompareWith(""); };
  const runCompare = async () => {
    if (!req || !compareWith) return;
    const other = areas.find((candidate) => candidate.id === compareWith && candidate.id !== selectedId);
    if (!other) return;
    const current = generation.current;
    const result = await api.post<CompareResponse>("/aoi/compare", { a: req, b: { ...other.request, start, end, res } }).catch(() => null);
    if (current === generation.current) setCompare(result);
  };
  const toggleLang = () => void i18n.changeLanguage(i18n.language === "bn" ? "en" : "bn");
  const reset = () => {
    generation.current++; setArea(null); setSelectedId(null); setStatus("idle"); setSummary(null); setPeriods(null);
    setDrivers(null); setOutlook(null); setCells(null); setPeriod(null); setCompare(null);
    setFallbackNote(null);
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
        <button className="lang" onClick={toggleLang} lang={i18n.language === "bn" ? "en" : "bn"}>{t("lang.toggle")}</button>
      </header>
      <div className={`banner ${DATA_MODE}`}>
        <span className="data-badge">{t(`app.data_${DATA_MODE}`)}</span> {t("app.scope")}
      </div>
      {STATIC_DEMO && <div className="banner">{t("hosting.snapshot")}</div>}
      {view === "validation" && <ErrorBoundary><ValidationPage /></ErrorBoundary>}
      {view === "method" && <ErrorBoundary><MethodPage /></ErrorBoundary>}
      {view === "explore" && (
        <main className="explorer">
          <AreaFilters areas={areas} selectedId={selectedId} loading={catalogLoading} unavailable={catalogUnavailable}
            onRetry={() => setCatalogVersion((version) => version + 1)} onApply={pickArea} />
          <div className="layout">
          <div className="mapcol">
            <MapView aoi={req} cells={cells?.cells ?? null} period={period} areas={areas} selectedId={selectedId} onSelect={pickArea} />
          </div>
          <div className="panels">
            <AnalysisControls fixed={STATIC_DEMO} start={start} end={end} res={res} canRun={Boolean(req)}
              onStart={setStart} onEnd={setEnd} onRes={setRes}
              onRefresh={() => req && void load(req)} onReset={reset}
              summary={summary && status === "ok" ? t("aoi.summary", { cells: num(summary.aoi.n_cells), area: num(summary.aoi.area_km2) }) : undefined} />
            {status === "idle" && !catalogLoading && !catalogUnavailable && <p className="note">{t(STATIC_DEMO ? "hosting.pick_area" : "map.select_hint")}</p>}
            {status === "loading" && <p className="note" aria-live="polite">{t("state.loading")}</p>}
            {status === "empty" && <p className="warn">{t("state.empty")}</p>}
            {status === "oversized" && <p className="warn">{t("state.oversized")}</p>}
            {status === "error" && <p className="warn">{t("state.error")}</p>}
            {fallbackNote && <p className="warn">{t("state.fallback", { region: fallbackNote })}</p>}
            {status === "ok" && summary && (
              <>
                {outlook && <ErrorBoundary><StatusCard o={outlook} /></ErrorBoundary>}
                <ErrorBoundary>
                  <section className="card">
                    <h2>{t("calendar.title")}</h2>
                    <p className="meta">{t("calendar.hint")}</p>
                    {res === "week" && <Calendar series={summary.series} selected={period?.key ?? null}
                      onSelect={(w) => setPeriod({ start: w, end: addDays(w, 6), key: w })} />}
                  </section>
                </ErrorBoundary>
                <ErrorBoundary>
                  <section className="card">
                    <h2>{t("chart.title")}</h2>
                    <SeriesChart series={summary.series} seams={summary.seams ?? []} highlight={period}
                                 second={compare?.b.series} />
                  </section>
                </ErrorBoundary>
                {periods && <ErrorBoundary><PeriodsPanel periods={periods.periods} selected={period?.key ?? null}
                  onSelect={(p) => setPeriod({ start: p.start, end: p.end, key: p.start })} /></ErrorBoundary>}
                {outlook && <ErrorBoundary><OutlookPanel o={outlook} /></ErrorBoundary>}
                {drivers && <ErrorBoundary><DriversPanel d={drivers} /></ErrorBoundary>}
                <section className="card">
                  <h2>{t("compare.title")}</h2>
                  <div className="controls">
                    <label>{t("compare.with")}
                      <select value={compareWith} onChange={(e) => setCompareWith(e.target.value)}>
                        <option value="">–</option>
                        {areas.filter((candidate) => candidate.id !== selectedId).map((candidate) =>
                          <option key={candidate.id} value={candidate.id}>{areaLabel(candidate, i18n.language)}</option>)}
                      </select>
                    </label>
                    <button className="chip" onClick={runCompare} disabled={!compareWith || compareWith === selectedId}>{t("compare.run")}</button>
                  </div>
                </section>
                <section className="card">
                  <h2>{t("export.title")}</h2>
                  <div className="exportrow">
                    <button disabled={STATIC_DEMO} onClick={() => req && api.exportCsv(req, "summary")}>{t("export.summary")}</button>
                    <button disabled={STATIC_DEMO} onClick={() => req && period && api.exportCsv({ ...req, start: period.start, end: period.end }, "cells")}>{t("export.cells")}</button>
                    <button disabled={STATIC_DEMO} onClick={() => req && api.exportCsv(req, "critical_periods")}>{t("export.periods")}</button>
                    <button onClick={() => window.print()}>{t("export.print")}</button>
                  </div>
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
