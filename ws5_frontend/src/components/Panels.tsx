import { useTranslation } from "react-i18next";
import type { CriticalPeriod, DriversResponse, OutlookResponse } from "../types";
import { date, num } from "../lib/format";

export function StatusCard({ o }: { o: OutlookResponse }) {
  const { t } = useTranslation();
  const cs = o.current_status;
  return (
    <section className="card" aria-labelledby="status-h">
      <h2 id="status-h">{t("status.title")}</h2>
      <div className="status">
        <div className={`level ${cs.level}`}>{t(`status.level_${cs.level}`)}</div>
        <div>{t("status.percentile", { p: num(cs.week_percentile) })}</div>
        <div className="meta">{t("status.data_through", { date: date(cs.data_through) })}</div>
        <div className="meta">{cs.data_source ? t("status.source", { source: cs.data_source }) : null}</div>
      </div>
    </section>
  );
}

export function PeriodsPanel({ periods, selected, onSelect }: { periods: CriticalPeriod[]; selected: string | null; onSelect: (p: CriticalPeriod) => void }) {
  const { t } = useTranslation();
  const top = Math.max(1, ...periods.map((p) => p.severity));
  return (
    <section className="card" aria-labelledby="periods-h">
      <h2 id="periods-h">{t("periods.title")}</h2>
      {periods.length === 0 && <p className="note">{t("periods.none")}</p>}
      <ol className="periods">
        {periods.slice(0, 12).map((p) => (
          <li key={p.start}>
            <button className={selected === p.start ? "sel" : ""} onClick={() => onSelect(p)} aria-pressed={selected === p.start}>
              <strong>{t("periods.row", { rank: num(p.rank), start: date(p.start), end: date(p.end) })}</strong>
              <span className="meta">{t("periods.weeks", { count: p.n_weeks, n: num(p.n_weeks) })} · {t("periods.severity", { s: num(p.severity, 1) })}</span>
              <span className="bar"><span style={{ width: `${(100 * p.severity) / top}%` }} /></span>
              <span>
                {p.agri_tag
                  ? <span className="tag agri">{p.agri_share !== null ? t("periods.agri", { share: num(100 * p.agri_share) }) : t("periods.agri_rule")}</span>
                  : <span className="tag">{t("periods.wild")}</span>}
                {p.depends_on_modeled_history && <span className="tag mod">{t("periods.modeled_note")}</span>}
              </span>
            </button>
          </li>
        ))}
      </ol>
    </section>
  );
}

export function DriversPanel({ d }: { d: DriversResponse }) {
  const { t } = useTranslation();
  return (
    <section className="card" aria-labelledby="drivers-h">
      <h2 id="drivers-h">{t("drivers.title")}</h2>
      <p className="meta">{t("drivers.region", { region: d.region.region_name })}</p>
      {d.status === "insufficient_data" && <p className="note">{t("state.insufficient")}</p>}
      {d.status === "ok" && d.items.length === 0 && <p className="note">{t("drivers.none")}</p>}
      <ul>
        {d.items.map((it) => (
          <li key={it.driver}>
            {t("drivers.sentence", {
              direction: t("drivers.higher"), driver: it.driver,
              when: it.lag_weeks === 0 ? t("drivers.same_week") : t("drivers.lag", { n: num(it.lag_weeks) }),
              more: it.direction === "positive" ? t("drivers.more") : t("drivers.less"),
            })}{" "}
            <span className="meta">{t("drivers.stats", { r: num(it.strength, 2), lo: num(it.ci[0], 2), hi: num(it.ci[1], 2) })} · {t(`drivers.evidence_${it.evidence}`)}</span>
          </li>
        ))}
      </ul>
      <ul className="note">{d.caveats.map((c) => <li key={c}>{c}</li>)}</ul>
    </section>
  );
}

export function OutlookPanel({ o }: { o: OutlookResponse }) {
  const { t } = useTranslation();
  const r = o.expected_range;
  const ci = o.skill.ci;
  return (
    <section className="card" aria-labelledby="outlook-h">
      <h2 id="outlook-h">{t("outlook.title")}</h2>
      <p>{t("outlook.std", { p: num(o.season_to_date_percentile) })}</p>
      <p className="meta">{t("outlook.range", { q10: num(r.q10), q50: num(r.q50), q90: num(r.q90) })}</p>
      <p>{o.status === "skill" && ci
        ? t("outlook.skill", { s: num(100 * (o.skill.vs_climatology ?? 0)), lo: num(100 * ci[0]), hi: num(100 * ci[1]) })
        : t("outlook.no_skill")}</p>
      {o.status === "skill" && <p className="meta">{t("outlook.alert", { level: t(`status.level_${o.alert.level}`) })}</p>}
      <p className="meta">{t("status.region", { region: o.region.region_name })}</p>
    </section>
  );
}
