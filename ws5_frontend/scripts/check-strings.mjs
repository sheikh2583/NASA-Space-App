// Fails if a component has visible English text outside t(...): a heuristic for "no hard-coded UI strings".
import { readdirSync, readFileSync } from "node:fs";
const dir = "src/components";
// Proper names in data attributions are not UI text and are never translated.
const ALLOWED = new Set(["OpenStreetMap", "CARTO"]);
let bad = 0;
for (const f of readdirSync(dir)) {
  const src = readFileSync(`${dir}/${f}`, "utf8");
  const hits = [...src.matchAll(/>\s*([A-Za-z][A-Za-z ,.'-]{2,})\s*</g)].map((m) => m[1].trim()).filter((h) => !ALLOWED.has(h) && !/^[A-Za-z_]\w*\.\w+$/.test(h)); // skip code like `p.t` between > and <
  for (const h of hits) { console.log(`${f}: "${h}"`); bad++; }
}
if (bad) { console.error(`${bad} hard-coded strings`); process.exit(1); }
console.log("no hard-coded UI strings found");
