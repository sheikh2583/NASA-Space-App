import { DEMOS } from "./config";
import type { AOIRequest } from "./types";

export interface AreaOption {
  id: string;
  name: string;
  country: "BD" | "IN";
  cellCount?: number;
  labelKey?: string;
  request: Pick<AOIRequest, "geometry" | "bbox">;
}

export const EXAMPLE_AREAS: AreaOption[] = [
  { id: "bd", name: "Central Bangladesh", country: "BD", labelKey: "area.example_bd", request: { bbox: DEMOS.bd.bbox } },
  { id: "pb", name: "Central Punjab", country: "IN", labelKey: "area.example_pb", request: { geometry: DEMOS.pb.geometry } },
];

function normalize(value: string): string {
  return value.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLocaleLowerCase().trim();
}

export function filterAreas(areas: AreaOption[], country: string, query: string): AreaOption[] {
  return areas.filter((area) => (!country || area.country === country) && normalize(area.name).includes(normalize(query)));
}

export async function loadAreaCatalog(): Promise<AreaOption[]> {
  const response = await fetch(`${import.meta.env.BASE_URL}demo/areas.json`);
  if (!response.ok) throw new Error("Area catalog unavailable");
  const data = await response.json() as { areas: AreaOption[] };
  return [...data.areas.sort((a, b) => a.name.localeCompare(b.name)), ...EXAMPLE_AREAS];
}
