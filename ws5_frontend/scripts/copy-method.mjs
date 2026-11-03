// Copies Samiul's method text into public/ before dev and build (never edit it here; docs/method_*.md is his).
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
mkdirSync("public", { recursive: true });
for (const lang of ["en", "bn"]) {
  const src = `../docs/method_${lang}.md`;
  if (existsSync(src)) copyFileSync(src, `public/method_${lang}.md`);
}
