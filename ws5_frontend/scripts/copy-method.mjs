// Copies Samiul's method text into public/ before dev and build (never edit it here; docs/science/method_*.md is his).
import { copyFileSync, existsSync, mkdirSync, rmSync } from "node:fs";
mkdirSync("public", { recursive: true });
// Remove only the obsolete generated delivery copy, preserving docs/science/method_bn.md.
rmSync("public/method_bn.md", { force: true });
for (const lang of ["en"]) {
  const src = `../docs/science/method_${lang}.md`;
  if (existsSync(src)) copyFileSync(src, `public/method_${lang}.md`);
}
