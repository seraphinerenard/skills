import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// The dev server proxies the API to the FastAPI process, so the browser only
// talks to :5173 and there is no CORS handling in dev. Override the backend
// address with NORTHLINE_API when :8000 is taken.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/api": process.env.NORTHLINE_API || "http://127.0.0.1:8000",
    },
  },
});
