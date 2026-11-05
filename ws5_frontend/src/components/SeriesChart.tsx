import { Area, CartesianGrid, ComposedChart, Line, ReferenceArea, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useTranslation } from "react-i18next";
import { useMemo } from "react";
import type { SummaryPoint } from "../types";
import { date, num } from "../lib/format";

interface Props {
  series: SummaryPoint[];
  seams: string[];
  highlight: { start: string; end: string } | null;
  second?: SummaryPoint[];
}

/** Value line with its 90% band; modeled years shaded; seams marked. */
export default function SeriesChart({ series, seams, highlight, second }: Props) {
  const { t } = useTranslation();
  // A partial period (data ends inside it) is drawn as a dot, not as a drop in the line or band.
  const data = useMemo(() => series.map((p, i) => {
    const partial = p.complete === false;
    return {
      t: p.t, value: partial ? null : p.value,
      band: !partial && p.lo !== null && p.hi !== null ? [p.lo, p.hi] : null,
      b: second?.[i]?.value ?? undefined, drift: p.drift_flag ? p.value : undefined,
      partial: partial ? p.value : undefined,
    };
  }), [series, second]);
  const first = series[0]?.t;
  const last = series[series.length - 1]?.t;
  const inRange = (d: string) => first && last && d >= first && d <= last;
  // The x axis is categorical (period starts), so a seam is drawn at the first period on or after it.
  const snap = (d: string) => series.find((p) => p.t >= d)?.t ?? null;
  const seamAt = seams.filter(inRange).map((s) => ({ s, x: snap(s) })).filter((z): z is { s: string; x: string } => z.x !== null);
  return (
    <div style={{ width: "100%", height: 260 }}>
      <ResponsiveContainer>
        <ComposedChart data={data} margin={{ top: 14, right: 8, bottom: 0, left: 0 }}>
          <CartesianGrid stroke="#eee6dc" vertical={false} />
          <XAxis dataKey="t" tickFormatter={(d: string) => date(d, { year: "numeric" })} minTickGap={40} fontSize={11} />
          <YAxis fontSize={11} width={44} tickFormatter={(v: number) => num(v)} />
          <Tooltip labelFormatter={(d) => date(String(d))}
                   formatter={(v, name) => [Array.isArray(v) ? `${num(v[0] as number, 1)} – ${num(v[1] as number, 1)}` : num(v as number, 1), String(name)]} />
          {seams.length > 0 && first && first < seams[0] && (
            <ReferenceArea x1={first} x2={snap(seams[0]) ?? last} fill="#efe6da" fillOpacity={0.6} />
          )}
          {seamAt.map(({ s, x }) => (
            <ReferenceLine key={s} x={x} stroke="#6b625b" strokeDasharray="4 3"
                           label={{ value: t(s < "2020" ? "chart.seam_2012" : "chart.seam_2026"), fontSize: 10, position: s < "2020" ? "insideTopLeft" : "insideTopRight", fill: "#4a423c" }} />
          ))}
          {highlight && snap(highlight.start) && (
            <ReferenceArea x1={snap(highlight.start)!} x2={[...series].reverse().find((p) => p.t <= highlight.end)?.t ?? snap(highlight.start)!}
                           fill="#1d5fa8" fillOpacity={0.18} />
          )}
          <Area type="stepAfter" dataKey="band" name={t("chart.band")} stroke="none" fill="#e9a17f" fillOpacity={0.45} isAnimationActive={false} />
          <Line type="stepAfter" dataKey="value" name={t("chart.value")} stroke="#8c2a0c" dot={false} strokeWidth={1.4} isAnimationActive={false} />
          {second && <Line type="stepAfter" dataKey="b" name="B" stroke="#1d5fa8" dot={false} strokeWidth={1.2} isAnimationActive={false} />}
          <Line dataKey="drift" name={t("chart.drift")} stroke="none" dot={{ r: 2, fill: "#c27c0e" }} isAnimationActive={false} />
          <Line dataKey="partial" name={t("chart.partial")} stroke="none" dot={{ r: 3, fill: "#fff", stroke: "#8c2a0c", strokeWidth: 1.4 }} isAnimationActive={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
