import { scaleSequentialLog } from "d3-scale";
import { interpolateInferno } from "d3-scale-chromatic";

/** Detections -> colour. Light = few, dark = many (reversed inferno: perceptually even and colour-blind safe). */
export function burnScale(max: number) {
  return scaleSequentialLog((t: number) => interpolateInferno(0.97 - 0.82 * t)).domain([1, Math.max(max, 1.01)]);
}
export const RAMP_CSS = `linear-gradient(90deg, ${[0, 0.25, 0.5, 0.75, 1].map((t) => interpolateInferno(0.97 - 0.82 * t)).join(", ")})`;
