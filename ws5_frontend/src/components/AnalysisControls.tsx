import { useTranslation } from "react-i18next";
import type { Res } from "../types";

interface Props {
  start: string;
  end: string;
  res: Res;
  summary?: string;
  canRun: boolean;
  fixed?: boolean;
  onStart: (value: string) => void;
  onEnd: (value: string) => void;
  onRes: (value: Res) => void;
  onRefresh: () => void;
  onReset: () => void;
}

export default function AnalysisControls(props: Props) {
  const { t } = useTranslation();
  return (
    <section className="card controls" aria-label={t("controls.res")}>
      <label>{t("controls.start")}
        <input disabled={props.fixed} type="date" value={props.start} min="2000-11-01" max={props.end}
          onChange={(event) => props.onStart(event.target.value)} />
      </label>
      <label>{t("controls.end")}
        <input disabled={props.fixed} type="date" value={props.end} min={props.start}
          onChange={(event) => props.onEnd(event.target.value)} />
      </label>
      <label>{t("controls.res")}
        <select disabled={props.fixed} value={props.res} onChange={(event) => props.onRes(event.target.value as Res)}>
          <option value="week">{t("controls.res_week")}</option>
          <option value="month">{t("controls.res_month")}</option>
          <option value="day">{t("controls.res_day")}</option>
        </select>
      </label>
      <div className="control-actions">
        <button className="chip" disabled={!props.canRun} onClick={props.onRefresh}>{t("controls.refresh")}</button>
        <button className="chip" disabled={!props.canRun} onClick={props.onReset}>{t("controls.reset")}</button>
      </div>
      {props.summary && <span className="meta">{props.summary}</span>}
    </section>
  );
}
