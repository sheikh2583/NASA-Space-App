import { weekOfYear } from "./format";

export interface MonthColumn {
  month: number;
  col: number;
}

export function monthColumns(): MonthColumn[] {
  return Array.from({ length: 12 }, (_, index) => {
    const month = index + 1;
    return { month, col: weekOfYear(`2023-${String(month).padStart(2, "0")}-04`) };
  });
}
