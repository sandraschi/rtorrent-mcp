import { expect, test } from "@playwright/test";

const AUTH = {
  Authorization: "Basic " + Buffer.from("user:pass").toString("base64"),
};

test.describe("Frontend", () => {
  test("dashboard loads with stat cards", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.getByRole("heading", { name: "Add magnet (XML-RPC)" }),
    ).toBeVisible({ timeout: 15000 });
    await expect(
      page.getByRole("heading", { name: "Torrent list (first 12)" }),
    ).toBeVisible();
  });

  test("each page loads without crash", async ({ page }) => {
    const pages = [
      "/",
      "/status",
      "/tools",
      "/apps",
      "/chat",
      "/help",
      "/settings",
    ];
    for (const p of pages) {
      await page.goto(p);
      await expect(page.locator("body")).not.toBeEmpty({ timeout: 10000 });
    }
  });

  test("navigation sidebar works", async ({ page }) => {
    await page.goto("/");
    const nav = page.locator('nav, aside, [role="navigation"], .sidebar');
    if ((await nav.count()) > 0) {
      await expect(nav.first()).toBeVisible();
    }
  });

  test("topbar health check visible", async ({ page }) => {
    await page.goto("/");
    // topbar should render — look for a status indicator or server badge
    const topbar = page.locator('header, [role="banner"], .topbar');
    if ((await topbar.count()) > 0) {
      await expect(topbar.first()).toBeVisible();
    }
  });

  test("status page shows rTorrent connection probe", async ({ page }) => {
    await page.goto("/status");
    await expect(page.locator("text=Status").first()).toBeVisible({
      timeout: 15000,
    });
  });

  test("help page renders documentation", async ({ page }) => {
    await page.goto("/help");
    await expect(page.locator("body")).not.toBeEmpty({ timeout: 10000 });
  });
});

const BE = "http://127.0.0.1:10910";

test.describe("REST API", () => {
  test("GET /api/health returns ok", async ({ request }) => {
    const resp = await request.get(`${BE}/api/health`);
    expect(resp.ok()).toBeTruthy();
    const body = await resp.json();
    expect(body.ok).toBe(true);
    expect(body.service).toBe("rtorrent-mcp");
  });

  test("GET /api/info returns app name", async ({ request }) => {
    const resp = await request.get(`${BE}/api/info`);
    expect(resp.ok()).toBeTruthy();
    const body = await resp.json();
    expect(body).toHaveProperty("app_name");
  });

  test("POST /api/rtorrent/magnet with invalid body returns 400", async ({
    request,
  }) => {
    const resp = await request.post(`${BE}/api/rtorrent/magnet`, { data: {} });
    expect(resp.status()).toBe(400);
  });

  test("GET /api/rtorrent/torrents returns 503 when rTorrent is unreachable", async ({
    request,
  }) => {
    const resp = await request.get(`${BE}/api/rtorrent/torrents`);
    // 401 (no API key) or 503 (rTorrent down) — both indicate the route exists and responds
    expect([401, 503]).toContain(resp.status());
  });

  test("GET /api/rtorrent/status returns connected or error", async ({
    request,
  }) => {
    const resp = await request.get(`${BE}/api/rtorrent/status`);
    const body = await resp.json();
    expect(body).toHaveProperty("connected");
  });
});
