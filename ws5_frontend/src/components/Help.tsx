import { useEffect, useReducer, useRef } from "react";
import { useTranslation } from "react-i18next";

export type HelpAction = "open" | "close" | "toggle" | "escape";

export function helpReducer(state: boolean, action: HelpAction): boolean {
  if (action === "open") return true;
  if (action === "toggle") return !state;
  return false;
}

export default function HelpButton({ topic }: { topic: string }) {
  const { t } = useTranslation();
  const [open, dispatch] = useReducer(helpReducer, false);
  const root = useRef<HTMLSpanElement>(null);
  const id = `help-${topic}`;

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => { if (event.key === "Escape") dispatch("escape"); };
    const onPointerDown = (event: PointerEvent) => {
      if (open && root.current && !root.current.contains(event.target as Node)) dispatch("close");
    };
    document.addEventListener("keydown", onKeyDown);
    document.addEventListener("pointerdown", onPointerDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("pointerdown", onPointerDown);
    };
  }, [open]);

  const topicName = t(`help.topic_${topic}`);
  return <span className="help" ref={root}>
    <button type="button" className="help-button" aria-label={t("help.open", { topic: topicName })}
      aria-expanded={open} aria-controls={id} onClick={(event) => {
        event.preventDefault(); event.stopPropagation(); dispatch("toggle");
      }}>?</button>
    <span className="help-dialog" role="dialog" aria-label={topicName} id={id} hidden={!open}>
      <span>{t(`help.${topic}`)}</span>
      <button type="button" className="help-close" onClick={() => dispatch("close")}>{t("help.close")}</button>
    </span>
  </span>;
}
