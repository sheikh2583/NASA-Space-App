import type { AOIRequest } from "./types";

export const RECORD_START = "2000-11-01";
export const RECORD_END = "2026-11-02";

export const DEMOS: Record<"bd" | "pb", AOIRequest> = {
  bd: { bbox: [89.5, 23.0, 90.5, 24.0], start: RECORD_START, end: RECORD_END },
  pb: {
    geometry: {
      type: "Polygon",
      coordinates: [[[74.6, 29.8], [76.4, 29.8], [76.4, 31.2], [74.6, 31.2], [74.6, 29.8]]],
    },
    start: RECORD_START,
    end: RECORD_END,
  },
};

export const DATA_MODE = import.meta.env.VITE_DATA_MODE === "synthetic" ? "synthetic" : "real";
