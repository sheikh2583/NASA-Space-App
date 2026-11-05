import { useEffect, useState, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api";
import type { ValidationPiece, ValidationResponse } from "../types";
import { date, num } from "../lib/format";

type Row = Record<string, unknown>;
type ValidationReport = ValidationResponse & { corrupt?: string[] };

export function ValidationNotices({ report }: { report: ValidationReport }) {
  const { t } = useTranslation();
  return <>
    {report.missing.length > 0 && <p className="note">{t("validation.missing", { list: report.missing.join(", ") })}</p>}
    {Boolean(report.corrupt?.length) && <p className="warn" role="alert">{t("validation.corrupt", { list: report.corrupt!.join(", ") })}</p>}
  </>;
}

function Table({ rows, cols, rowClassName }: { rows: Row[]; cols: string[]; rowClassName?: (row: Row) => string | undefined }) {
  return (
    <table className="t">
      <thead><tr>{cols.map((c) => <th key={c}>{c}</th>)}</tr></thead>
      <tbody>
        {rows.map((r, i) => (
          <tr key={i} className={rowClassName?.(r)}>{cols.map((c) => <td key={c} className={typeof r[c] === "number" ? "n" : ""}>{typeof r[c] === "number" ? (c === "year" ? num(r[c] as number, 0).replace(/[,.\s\u00a0]/g, "") : num(r[c] as number, 3)) : String(r[c] ?? "")}</td>)}</tr>
        ))}
      </tbody>
    </table>
  );
}

function PieceCard({ title, p, children }: { title: string; p?: ValidationPiece; children?: ReactNode }) {
  const { t } = useTranslation();
  if (!p) return null;
  return (
    <section className="card">
      <h2>{title}</h2>
      <p className="meta">{t("validation.generated", { date: date(p.generated_at.slice(0, 10)) })}</p>
      {children}
      <h3 style={{ fontSize: 13 }}>{t("validation.limitations")}</h3>
      <ul className="note">{p.limitations.map((l) => <li key={l}>{l}</li>)}</ul>
    </section>
  );
}

export function ValidationPage() {
  const { t } = useTranslation();
  const [v, setV] = useState<ValidationReport | null>(null);
  const [err, setErr] = useState(false);
  useEffect(() => { api.get<ValidationReport>("/meta/validation").then(setV).catch(() => setErr(true)); }, []);
  if (err) return <div className="panels"><p className="warn">{t("state.error")}</p></div>;
  if (!v) return <div className="panels"><p className="note">{t("state.loading")}</p></div>;
  const P = v.pieces;
  const h = P.harmonization?.metrics as { region_week?: Row[]; method_chosen?: Row } | undefined;
  const iv = P.intervals?.metrics as { coverage?: Row[] } | undefined;
  const ivs = P.intervals_by_stratum?.metrics as { rows?: Row[] } | undefined;
  const dr = P.drift?.metrics as { flagged_region_years?: Row[] } | undefined;
  const os = P.outlook_skill?.metrics as { by_region?: Row[] } | undefined;
  const qa = P.qa?.metrics as { checks?: Row[]; summary?: string[] } | undefined;
  return (
    <div className="panels" style={{ maxWidth: 1000, margin: "0 auto" }}>
      <h2>{t("validation.title")}</h2>
      <ValidationNotices report={v} />
      {qa?.summary && <section className="card">{qa.summary.map((s) => <p key={s}>{s}</p>)}</section>}
      <PieceCard title={t("validation.harmonization")} p={P.harmonization}>
        {h?.method_chosen && (
          <p className="meta">
            {t("validation.method_chosen", { method: h.method_chosen.method === "b1" ? "B1" : h.method_chosen.method === "xgb" ? "XGBoost CUDA" : "LightGBM" })}{" "}
            {Object.entries((h.method_chosen.selection_mean_ccc ?? h.method_chosen.mean_ccc) as Record<string, number>).map(([k, v]) => `${k} ${num(v, 3)}`).join(" · ")}
          </p>
        )}
        {h?.region_week && <Table rows={h.region_week} cols={["holdout", "method", "rel_bias", "rmse_log1p", "spearman", "lins_ccc", "n"]} />}
      </PieceCard>
      <PieceCard title={t("validation.intervals")} p={P.intervals}>
        <p className="warn">{t("validation.conditional_limit")}</p>
        {iv?.coverage && <Table rows={iv.coverage.filter((r) => r.res === "week")} cols={["landcover", "season", "n", "coverage", "mean_width"]} />}
      </PieceCard>
      <PieceCard title={t("validation.by_stratum")} p={P.intervals_by_stratum}>
        {ivs?.rows?.some((row) => typeof row.n === "number" && row.n >= 500 &&
          typeof row.coverage === "number" && row.coverage < 0.8) &&
          <p className="warn" role="status">{t("validation.stop_condition")}</p>}
        <p className="note">{t("validation.by_stratum_note")}</p>
        {ivs?.rows && <Table rows={ivs.rows} cols={["stratum", "n", "coverage", "interval_score"]}
          rowClassName={(row) => typeof row.coverage === "number" && row.coverage < 0.85 ? "warn" : undefined} />}
      </PieceCard>
      <PieceCard title={t("validation.drift")} p={P.drift}>
        {dr?.flagged_region_years && <Table rows={dr.flagged_region_years.slice(0, 20)} cols={["region_id", "year", "reason"]} />}
      </PieceCard>
      <PieceCard title={t("validation.outlook")} p={P.outlook_skill}>
        {os?.by_region && <Table rows={os.by_region} cols={["region_id", "vs_climatology", "vs_persistence", "status", "n_seasons"]} />}
      </PieceCard>
      <PieceCard title={t("validation.qa")} p={P.qa}>
        {qa?.checks && <Table rows={qa.checks} cols={["check", "result", "detail"]} />}
      </PieceCard>
    </div>
  );
}

/** Tiny Markdown renderer for the method text (headings, paragraphs, lists, bold). */
function renderMd(md: string): ReactNode[] {
  const out: ReactNode[] = [];
  const bold = (s: string) => s.split(/\*\*(.+?)\*\*/g).map((x, i) => (i % 2 ? <strong key={i}>{x}</strong> : x));
  let list: string[] = [];
  const flush = () => { if (list.length) { out.push(<ul key={out.length}>{list.map((l, i) => <li key={i}>{bold(l)}</li>)}</ul>); list = []; } };
  for (const line of md.split("\n")) {
    if (/^\s*[-*] /.test(line)) { list.push(line.replace(/^\s*[-*] /, "")); continue; }
    flush();
    if (line.startsWith("# ")) out.push(<h2 key={out.length}>{line.slice(2)}</h2>);
    else if (line.startsWith("## ")) out.push(<h3 key={out.length}>{line.slice(3)}</h3>);
    else if (line.trim()) out.push(<p key={out.length}>{bold(line)}</p>);
  }
  flush();
  return out;
}

export function MethodPage() {
  const { t } = useTranslation();
  const [md, setMd] = useState<string>("");
  useEffect(() => {
    fetch("./method_en.md").then((r) => { if (!r.ok) throw new Error("method_unavailable"); return r.text(); }).then(setMd).catch(() => setMd(""));
  }, []);
  return (
    <div className="panels">
      <section className="card method">
        {md ? renderMd(md) : <p className="note">{t("state.loading")}</p>}
      </section>
    </div>
  );
}
