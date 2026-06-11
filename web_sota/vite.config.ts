import path from "path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    allowedHosts: ['goliath'],
    port: 10912,
    strictPort: true,
    host: "127.0.0.1",
    proxy: {
      // Same port as start.ps1 backend — MCP streamable HTTP + REST bridge for the SPA
      "/mcp": { target: "http://127.0.0.1:10910", changeOrigin: true },
      "/api": { target: "http://127.0.0.1:10910", changeOrigin: true },
    },
  },
});
