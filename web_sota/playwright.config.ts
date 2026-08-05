import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60000,
  retries: 1,
  use: {
    baseURL: "http://127.0.0.1:10911",
    headless: true,
    screenshot: "only-on-failure",
  },
  webServer: [
    {
      command:
        "uv run uvicorn rtorrent_mcp.server:app --host 127.0.0.1 --port 10910 --log-level warning",
      port: 10910,
      cwd: "../",
      timeout: 30000,
      reuseExistingServer: false,
    },
    {
      command: "npm run dev -- --port 10911 --host",
      port: 10911,
      cwd: ".",
      timeout: 30000,
      reuseExistingServer: false,
    },
  ],
});
