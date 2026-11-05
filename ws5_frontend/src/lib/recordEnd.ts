export function validRecordEnd(value: unknown): value is string {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const parsed = new Date(value + "T00:00:00Z");
  return !Number.isNaN(parsed.valueOf()) && parsed.toISOString().slice(0, 10) === value && value >= "2000-11-01";
}

export function metadataEnd(current: string, available: string, explicitlyEdited: boolean): string {
  return explicitlyEdited ? (current > available ? available : current) : available;
}
