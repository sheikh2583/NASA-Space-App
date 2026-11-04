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

const AREA_NAMES: Record<string, { en: string; bn: string; aliases?: string[] }> = {
  barisal: { en: "Barishal", bn: "বরিশাল", aliases: ["Barisal"] },
  chittagong: { en: "Chattogram", bn: "চট্টগ্রাম", aliases: ["Chittagong"] },
  dhaka: { en: "Dhaka", bn: "ঢাকা" },
  khulna: { en: "Khulna", bn: "খুলনা" },
  mymensingh: { en: "Mymensingh", bn: "ময়মনসিংহ" },
  rajshani: { en: "Rajshahi", bn: "রাজশাহী", aliases: ["Rajshani"] },
  rangpur: { en: "Rangpur", bn: "রংপুর" },
  sylhet: { en: "Sylhet", bn: "সিলেট" },
  delhi: { en: "Delhi", bn: "দিল্লি", aliases: ["New Delhi"] },
  haryana: { en: "Haryana", bn: "হরিয়ানা" },
  punjab: { en: "Punjab", bn: "পাঞ্জাব" },
};

export function areaLabel(area: AreaOption, language: string): string {
  const names = AREA_NAMES[normalize(area.name)];
  return names ? (language.startsWith("bn") ? names.bn : names.en) : area.name;
}

export function selectableAreas(areas: AreaOption[]): AreaOption[] {
  return areas.filter((area) => Boolean(area.request.geometry) && (area.cellCount ?? 0) > 0)
    .sort((a, b) => areaLabel(a, "en").localeCompare(areaLabel(b, "en")));
}

export function defaultArea(areas: AreaOption[]): AreaOption | undefined {
  return areas.find((area) => area.country === "BD" && normalize(area.name) === "dhaka") ?? areas[0];
}

export function filterAreas(areas: AreaOption[], country: string, query: string): AreaOption[] {
  const terms = normalize(query).split(/\s+/).filter(Boolean);
  return areas.filter((area) => {
    if (country && area.country !== country) return false;
    const names = AREA_NAMES[normalize(area.name)];
    const haystack = normalize([area.name, names?.en, names?.bn, ...(names?.aliases ?? []),
      area.country === "BD" ? "Bangladesh বাংলাদেশ" : "India ভারত"].filter(Boolean).join(" "));
    return terms.every((term) => haystack.includes(term));
  });
}

export async function loadAreaCatalog(): Promise<AreaOption[]> {
  const response = await fetch(`${import.meta.env.BASE_URL}demo/areas.json`);
  if (!response.ok) throw new Error("Area catalog unavailable");
  const data = await response.json() as { areas: AreaOption[] };
  const areas = selectableAreas(data.areas);
  if (!areas.length) throw new Error("No covered administrative boundaries available");
  return areas;
}
