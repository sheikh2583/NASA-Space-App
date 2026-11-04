/** Render's free service sleeps after 15 idle minutes and takes about a minute to wake (docs/guides/deployment.md).
 *  While the first request waits, say so instead of showing a bare "Loading…"; after 90 s, offer a retry. */
export const WAKING_AFTER_MS = 3_000;
export const RETRY_AFTER_MS = 90_000;

export type WakePhase = "loading" | "waking" | "retry";

export function wakePhase(elapsedMs: number): WakePhase {
  if (elapsedMs >= RETRY_AFTER_MS) return "retry";
  if (elapsedMs >= WAKING_AFTER_MS) return "waking";
  return "loading";
}
