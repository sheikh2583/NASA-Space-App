import { useMemo } from "react";
import { burnScale } from "../lib/colour";
import { useTranslation } from "react-i18next";
import type { SummaryPoint } from "../types";
import { date, isoYear, num, weekOfYear } from "../lib/format";

interface Props {
  series: SummaryPoint[];
  selected: string | null;
  onSelect: (weekStart: string) => void;
}

const CELL = 11;
const GAP = 1;
const LEFT = 34;
const TOP = 14;

/** Years as rows, ISO weeks as columns. Colour = detections (log scale; light = few, dark = many);
 *  hatching = modeled, dots = adjusted from NOAA-20, ring = unusual week, grey = no sensor. */
export default function Calendar({ series, selected, onSelect }: Props) {
  const { t } = useTranslation();
  const { years, cells, max } = useMemo(() => {
    const cells = series.map((p) => ({ p, y: isoYear(p.t), w: weekOfYear(p.t) }));
    const years = [...new Set(cells.map((c) => c.y))].sort((a, b) => a - b);
    const max = Math.max(2, ...series.map((p) => p.value ?? 0));
    return { years, cells, max };
  }, [series]);
  const color = burnScale(max);
  const width = LEFT + 52 * (CELL + GAP);
  const height = TOP + years.length * (CELL + GAP);
  const row = (y: number) => years.indexOf(y);

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
        {years.map((y, i) => (
          <text key={y} x={0} y={TOP + i * (CELL + GAP) + CELL - 2}>{num(y).replace(/[,.\s]/g, "")}</text>
        ))}
        {cells.map(({ p, y, w }) => {
          const x = LEFT + (w - 1) * (CELL + GAP);
          const yy = TOP + row(y) * (CELL + GAP);
          const v = p.value;
          const fill = v === null ? "var(--none-cell)" : v <= 0 ? "#f3efe8" : (color(Math.max(v, 1)) as string);
          const label = t("calendar.cell", { date: date(p.t), value: num(v, 1), lo: num(p.lo, 1), hi: num(p.hi, 1),
                                            source: t(`source.${p.source}`) });
          return (
            <g key={p.t}>
              <rect className={"cell" + (selected === p.t ? " sel" : "")} x={x} y={yy} width={CELL} height={CELL} rx={2} fill={fill}
                    tabIndex={0} role="gridcell" aria-label={label} onClick={() => onSelect(p.t)}
                    onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") onSelect(p.t); }}>
                <title>{label}</title>
              </rect>
              {v !== null && p.source === "modeled_from_modis" && <rect x={x} y={yy} width={CELL} height={CELL} rx={2} fill="url(#hatch)" pointerEvents="none" />}
              {v !== null && p.source === "adjusted_from_noaa20" && <rect x={x} y={yy} width={CELL} height={CELL} rx={2} fill="url(#dots)" pointerEvents="none" />}
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
      </div>
    </div>
  );
}
