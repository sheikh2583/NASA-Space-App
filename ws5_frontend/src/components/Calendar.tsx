import { useMemo } from "react";
import { burnScale } from "../lib/colour";
import { useTranslation } from "react-i18next";
import type { SummaryPoint } from "../types";
import { date, isoYear, monthDay, num, weekColumn, weekOfYear } from "../lib/format";

export interface SeasonBand {
  label: string;
  from: string;
  to: string;
  peak: string;
}

interface Props {
  series: SummaryPoint[];
  selected: string | null;
  onSelect: (weekStart: string) => void;
  bands?: SeasonBand[];
}

const CELL = 11;
const GAP = 1;
const LEFT = 34;
const TOP = 14;

/** Years as rows, ISO weeks as columns. Colour = detections (log scale; light = few, dark = many);
 *  hatching = modeled, dots = adjusted from NOAA-20, ring = unusual week, grey = no sensor. */
export default function Calendar({ series, selected, onSelect, bands = [] }: Props) {
  const { t } = useTranslation();
  const { years, cells, max } = useMemo(() => {
    const cells = series.map((p) => ({ p, y: isoYear(p.t), w: weekOfYear(p.t) }));
    const years = [...new Set(cells.map((c) => c.y))].sort((a, b) => a - b);
    const max = Math.max(2, ...series.map((p) => p.value ?? 0));
    return { years, cells, max };
  }, [series]);
  const color = burnScale(max);
  const width = LEFT + 52 * (CELL + GAP);
  const cellsTop = TOP + bands.length * 10;
  const height = cellsTop + years.length * (CELL + GAP);
  const row = (y: number) => years.indexOf(y);
  const bandX = (week: number) => LEFT + (week - 1) * (CELL + GAP);
  const bandWidth = (from: number, to: number) => (to - from + 1) * (CELL + GAP) - GAP;

  return (
    <div className="calendar">
      <svg width={width} height={height} role="grid" aria-label={t("calendar.title")}>
        <defs>
          <pattern id="hatch" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="4" stroke="#fff" strokeWidth="1.2" strokeOpacity="0.75" />
          </pattern>
          <pattern id="dots" width="4" height="4" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="2" r="0.8" fill="#fff" fillOpacity="0.85" />
          </pattern>
        </defs>
        {[1, 14, 27, 40].map((w) => (
          <text key={w} x={LEFT + (w - 1) * (CELL + GAP)} y={10}>{num(w)}</text>
        ))}
        {bands.map((band, i) => {
          const from = weekColumn(band.from);
          const to = weekColumn(band.to);
          const peak = weekColumn(band.peak);
          const y = TOP + i * 10;
          const label = t("season.band_label", {
            name: band.label, from: monthDay(band.from), to: monthDay(band.to),
          });
          const spans = from <= to ? [[from, to]] : [[from, 52], [1, to]];
          return <g key={`${band.label}-${band.from}-${band.to}`} role="img" aria-label={label}>
            <title>{label}</title>
            {spans.map(([start, end]) => <rect key={start} x={bandX(start)} y={y} width={bandWidth(start, end)} height={6}
              rx={2} fill="var(--band)" />)}
            <rect x={bandX(peak) + CELL / 2 - 1} y={y - 1} width={2} height={8} fill="var(--ink)" />
          </g>;
        })}
        {years.map((y, i) => (
          <text key={y} x={0} y={cellsTop + i * (CELL + GAP) + CELL - 2}>{num(y).replace(/[,.\s]/g, "")}</text>
        ))}
        {cells.map(({ p, y, w }) => {
          const x = LEFT + (w - 1) * (CELL + GAP);
          const yy = cellsTop + row(y) * (CELL + GAP);
          const v = p.value;
          const fill = v === null ? "var(--none-cell)" : v <= 0 ? "#f3efe8" : (color(Math.max(v, 1)) as string);
          const partial = p.complete === false;
          const label = t("calendar.cell", { date: date(p.t), value: num(v, 1), lo: num(p.lo, 1), hi: num(p.hi, 1),
                                            source: t(`source.${p.source}`) })
                        + (partial ? " · " + t("series.partial", { n: num(p.n_days ?? 0) }) : "");
          return (
            <g key={p.t}>
              <rect className={"cell" + (selected === p.t ? " sel" : "")} x={x} y={yy} width={CELL} height={CELL} rx={2} fill={fill}
                    tabIndex={0} role="gridcell" aria-label={label} onClick={() => onSelect(p.t)}
                    onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") onSelect(p.t); }}>
                <title>{label}</title>
              </rect>
              {v !== null && p.source === "modeled_from_modis" && <rect x={x} y={yy} width={CELL} height={CELL} rx={2} fill="url(#hatch)" pointerEvents="none" />}
              {v !== null && p.source === "adjusted_from_noaa20" && <rect x={x} y={yy} width={CELL} height={CELL} rx={2} fill="url(#dots)" pointerEvents="none" />}
              {partial && <rect x={x + 0.5} y={yy + 0.5} width={CELL - 1} height={CELL - 1} rx={2} fill="none" stroke="var(--ink)" strokeDasharray="2 2" pointerEvents="none" />}
              {p.anomaly?.flag && <circle cx={x + CELL / 2} cy={yy + CELL / 2} r={CELL / 2 + 1} fill="none" stroke="#1d5fa8" strokeWidth={1.6} pointerEvents="none" />}
            </g>
          );
        })}
      </svg>
      <div className="keys">
        <span>{t("calendar.legend_modeled")}</span>
        <span>{t("calendar.legend_adjusted")}</span>
        <span>{t("calendar.legend_flag")}</span>
        <span>{t("calendar.legend_none")}</span>
        <span>{t("calendar.legend_partial")}</span>
      </div>
    </div>
  );
}
