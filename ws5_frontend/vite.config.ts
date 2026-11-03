import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base "./" so the build works from any static-host sub-path (GitHub Pages, Netlify, Cloudflare Pages).
export default defineConfig({
  plugins: [react()],
  base: "./",
  server: { port: 5173 },
  test: { environment: "node" },
});
