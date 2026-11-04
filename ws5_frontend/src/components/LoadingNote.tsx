import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { wakePhase } from "../lib/waking";

interface Props {
  onRetry: () => void;
  /** Start time already elapsed, in ms; for tests and for keeping the clock across re-renders. */
  initialElapsedMs?: number;
}

/** "Loading…" that turns into "Waking the server…" after 3 s and offers a retry after 90 s (cold Render starts). */
export default function LoadingNote({ onRetry, initialElapsedMs = 0 }: Props) {
  const { t } = useTranslation();
  const [elapsed, setElapsed] = useState(initialElapsedMs);
  useEffect(() => {
    const started = Date.now() - initialElapsedMs;
    const id = window.setInterval(() => setElapsed(Date.now() - started), 1_000);
    return () => window.clearInterval(id);
  }, [initialElapsedMs]);
  const phase = wakePhase(elapsed);
  if (phase === "loading") return <p className="note" aria-live="polite">{t("state.loading")}</p>;
  return (
    <div className="note waking" role="status" aria-live="polite">
      {phase === "waking" && <span className="spinner" aria-hidden="true" />}
      <span>{t(phase === "waking" ? "state.waking" : "state.still_waking")}</span>
      {phase === "retry" && <button type="button" onClick={onRetry}>{t("state.retry")}</button>}
    </div>
  );
}
