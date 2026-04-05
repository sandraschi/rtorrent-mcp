# rTorrent reference (for **rtorrent-mcp**)

This document summarizes how **rTorrent** fits into this MCP server. For Docker, plugins, and long-form setup, see **[RTORRENT_SETUP.md](RTORRENT_SETUP.md)**.

## What is rTorrent?

**rTorrent** is a **BitTorrent** client controlled via **XML-RPC** (and historically SCGI). This project does **not** talk to qBittorrent’s Web API — that was an early prototype (**historic** name `qbtmcp`). The repo is **`rtorrent-mcp`**; the Python import package is **`rtorrent_mcp`**.

## How this MCP connects

```
Agent (Cursor / Claude)  →  MCP (stdio or HTTP /mcp)
                                 ↓
                    rtorrent_mcp.services.rtorrent_client
                                 ↓
              HTTP XML-RPC  →  http://RTORRENT_HOST:RTORRENT_PORT/RPC2
                                 ↓
              (typical Docker) nginx → Unix socket → rTorrent
```

The client uses Python’s `xmlrpc.client.ServerProxy` against **`/RPC2`** — the same endpoint **ruTorrent** / **crazymax** images expose via nginx.

## Essential environment variables

| Variable | Default (typical) | Role |
|----------|-------------------|------|
| `RTORRENT_HOST` | `localhost` | Hostname of the XML-RPC endpoint |
| `RTORRENT_PORT` | `12224` | Port where **`/RPC2`** is reachable (nginx in Docker) |
| `RTORRENT_PATH` | `/var/lib/rtorrent/session` | Session path context (see your compose) |

Optional: `NYAA_BASE_URL`, `POST_PROCESSING_*`, `INGESTION_*`, metadata keys — see `src/rtorrent_mcp/config/settings.py` and `.env.example` if present.

## Quick sanity check (XML-RPC)

With rTorrent listening on `localhost:12224`:

```bash
curl -X POST http://localhost:12224/RPC2 -H "Content-Type: text/xml" \
  -d "<?xml version='1.0'?><methodCall><methodName>system.client_version</methodName></methodCall>"
```

You should get an XML response with a `fault` **or** a `string` with the client version — either way, the endpoint is alive.

## BitTorrent vs this MCP

- **BitTorrent** is the protocol (swarms, pieces, magnet links, `.torrent` files).
- **rTorrent** is one client implementation.
- **This MCP** automates rTorrent + your search/post-processing stack; it does not replace ruTorrent’s UI or qBittorrent.

## Further reading

- **[RTORRENT_SETUP.md](RTORRENT_SETUP.md)** — Docker, plugins, RSS, autotools, scheduling.
- **[README.md](../README.md)** — repo layout, MCP install, `web_sota` disclaimer.
