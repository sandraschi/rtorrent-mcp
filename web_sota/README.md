# rtorrent-mcp web UI (`web_sota`)

**Vite + React** front-end for the same **Python** process that serves MCP over HTTP.

This is a **small** UI: list/status/magnet add via REST—not a full **ruTorrent** replacement. If you use [CrazyMax’s Docker stack](../README.md#rtorrent-stack-docker-recommended) from the repo root, ruTorrent’s classic WebUI is still there for RSS/plugins; use this app when you want something **light** instead of that surface area.

## What is wired

| Path | Purpose |
|------|---------|
| `/api/health` | JSON: server OK + version |
| `/api/info` | JSON: app name, `RTORRENT_HOST`, `RTORRENT_PORT`, Nyaa base URL |
| `/api/rtorrent/status` | JSON: XML-RPC connect probe to rTorrent |
| `/api/rtorrent/torrents` | JSON: torrent list (hash, name, progress, sizes) |
| `/api/rtorrent/magnet` | POST JSON `{ "magnet": "magnet:?...", "category": "anime" }` |
| `/mcp` | Streamable MCP (agents: Cursor, Claude, etc.) |

Vite dev server proxies **`/api`** and **`/mcp`** to the backend (`vite.config.ts`).

## Run

From repo root:

```powershell
.\web_sota\start.ps1
```

- **Vite:** `http://127.0.0.1:10911`
- **Backend (uvicorn):** `http://127.0.0.1:10910` — MCP + REST on one ASGI app

Configure rTorrent in `.env` (`RTORRENT_HOST`, `RTORRENT_PORT`, default `12224` if using nginx/RPC2).

## Notes

- **Agents** should still use **MCP tools** for full portmanteau coverage; the SPA uses the **REST bridge** for dashboard/status and quick magnet add.
- **Security:** bind backend to `127.0.0.1` only unless you add auth; the REST API can add torrents.
