import { useTranslation } from "react-i18next";
import { monthDay, num } from "../lib/format";
import type { SeasonInfo, SeasonProfileResponse, SeasonTrend } from "../types";

function TimingTrend({ trend }: { trend: SeasonTrend | null }) {
  const { t } = useTranslation();
  if (!trend?.ci || (trend.verdict !== "later" && trend.verdict !== "earlier") || trend.days_per_decade == null) return null;
  return <p>{t(`season.timing_${trend.verdict}`, {
    n: num(Math.abs(trend.days_per_decade), 1), lo: num(trend.ci[0], 1), hi: num(trend.ci[1], 1),
  })}</p>;
}

function AmountTrend({ trend }: { trend: SeasonTrend | null }) {
  const { t } = useTranslation();
  if (!trend?.ci || (trend.verdict !== "more" && trend.verdict !== "fewer") || trend.pct_per_decade == null) return null;
  const bounds = trend.ci.map((value) => Math.abs(value)).sort((a, b) => a - b);
  return <>
    <p>{t(`season.amount_${trend.verdict}`, {
      n: num(Math.abs(trend.pct_per_decade)), lo: num(bounds[0]), hi: num(bounds[1]),
    })}</p>
    <p className="meta">{t("season.amount_caveat")}</p>
  </>;
}

function CurrentSeason({ season }: { season: SeasonInfo }) {
  const { t } = useTranslation();
  if (!season.current) return null;
  if (season.current.status === "ended") return <p>{t("season.ended")}</p>;
  if (season.current.status === "not_started") return <p>{t("season.not_started")}</p>;
  return <p>{t("season.now", {
    total: num(season.current.to_date_total), typical: num(season.current.typical_to_date_total),
    p: num(season.current.percentile_at_cutoff),
  })}</p>;
}

export default function SeasonCard({ profile }: { profile: SeasonProfileResponse }) {
  const { t } = useTranslation();
  return <section className="card">
    <h2>{t("season.title")}</h2>
    {profile.seasons.length === 0 && <p className="note">{t("season.none")}</p>}
    {profile.seasons.map((season) => {
      const typical = season.typical;
      if (!typical?.p10?.median_md || !typical.p50?.median_md || !typical.p90?.median_md) return null;
      return <div key={season.name}>
        <h3>{t(`season.name_${season.name}`)}</h3>
        <p>{t("season.window", {
          from: monthDay(typical.p10.median_md), to: monthDay(typical.p90.median_md), mid: monthDay(typical.p50.median_md),
        })}</p>
        <CurrentSeason season={season} />
        <TimingTrend trend={season.timing_trend} />
        <AmountTrend trend={season.magnitude_trend} />
      </div>;
    })}
    <p className="meta">{t("season.definition")}</p>
  </section>;
}
