# Architecture

## Ports

| Service | Port | Notes |
|---------|------|-------|
| rTorrent XML-RPC (nginx) | `12224` | In Docker: `crazymax/rtorrent-rutorrent` |
| ruTorrent WebUI | `12222` | Bundled in the same Docker container |
| rtorrent-mcp backend (uvicorn) | `10910` | MCP HTTP `/mcp` + REST `/api/*` |
| rtorrent-mcp frontend (Vite) | `10911` | Dev server; proxies `/api` + `/mcp` → `10910` |

## Tool surface

Six portmanteau tools plus one agentic workflow (see [TOOLS.md](TOOLS.md) for
the full action reference):

```
torrent_management   (13 actions) — add, list, pause, resume, delete, status, info,
                                     notify_media, check_completed, process,
                                     start_processing, stop_processing, normalize
search_management    (14 actions) — anime, manga, japanese_tv, movies, tv_shows,
                                     tv_smart, ebooks_annas, ebooks_gutenberg,
                                     ebooks_pb, comics, annas_detail, imdb, imdb_search, tvdb
nlp_management        (3 actions) — command, parse, help
legal_management      (4 actions) — risk, check, advice, status
system_management     (5 actions) — help, status, health, info, analyze
workflow_management   (8 actions) — franchise, batch_series, status, cancel,
                                     list, estimate, queue, schedule
agentic_rtorrent_workflow         — LLM-orchestrated multi-step workflow (requires Ollama or a client LLM)
```

## Media pipeline

There are two independent paths for getting a finished download into Plex or
Jellyfin, depending on whether a *arr app is in the loop.

### Direct (anime via nyaa — no *arr)

```
rTorrent (rtorrent-mcp initiated)
  -> PostProcessor (normalize + move to ingestion folder)
    -> MediaIntegrator (scan Plex/Jellyfin)
```

For content downloaded directly through rtorrent-mcp (anime, manga from
nyaa), `MediaIntegrator` fires Plex/Jellyfin scans so files appear in your
media libraries without waiting for a scheduled scan.

### *arr-managed (movies/TV)

```
*arr (searches, decides what to grab)
  -> *arr sends magnet/torrent to rTorrent (via Download Client config)
    -> rTorrent downloads
      -> *arr polls rTorrent / watches folder
        -> *arr imports + renames
          -> *arr notifies Plex/Jellyfin
```

For *arr-managed content, configure rTorrent as a download client directly in
Radarr/Sonarr (Settings > Download Clients > rTorrent) — the *arr handles
dispatch, completion detection, import, and media server notification.
rtorrent-mcp is not involved. See
[docs/ARR_RTORRENT_SETUP.md](ARR_RTORRENT_SETUP.md).

## Key files

| File | Purpose |
|------|---------|
| `src/rtorrent_mcp/server.py` | FastMCP server entrypoint |
| `src/rtorrent_mcp/config/settings.py` | All env var config |
| `src/rtorrent_mcp/services/rtorrent_client.py` | rTorrent XML-RPC client |
| `src/rtorrent_mcp/services/filename_normalizer.py` | Media normalizer & Plex path builder |
| `src/rtorrent_mcp/services/post_processor.py` | File move/link + media trigger |
| `src/rtorrent_mcp/services/media_integrator.py` | Plex/Jellyfin notification |
| `src/rtorrent_mcp/services/gutenberg_search.py` | Project Gutenberg e-book search via Gutendex API |
| `src/rtorrent_mcp/tools/portmanteau/` | Portmanteau tool implementations |
| `web_sota/src/pages/nyaa.tsx` | Nyaa Anime Search page |
| `web_sota/src/pages/piratebay.tsx` | The Pirate Bay TV & Movies page |
| `web_sota/src/pages/gutenberg.tsx` | Project Gutenberg E-Book Search page |

## REST bridge

The same uvicorn process that serves MCP also exposes a small REST API on
port `10910` for the `web_sota/` dashboard:

- `GET /api/health` — liveness + version
- `GET /api/capabilities` — tools/resources/skills surface (dynamic discovery)
- `GET /api/skills` / `GET /api/skills/{name}` — bundled SKILL.md listing/content
- `GET /api/llm/discover` — probe Ollama `:11434` / LM Studio `:1234` / vLLM `:8000`
- `POST /api/ai/chat` — chat completion via the configured sampling endpoint
- `GET /api/rtorrent/status` / `GET /api/rtorrent/torrents` / `POST /api/rtorrent/magnet`
- `GET /api/fleet/apps` — probe the fleet webapp reservoir for live peers
- `GET /api/v1/diagnostics` / `GET /api/v1/system/info` — CUA smoke diagnostics

Set `API_KEY` (see [CONFIGURATION.md](CONFIGURATION.md)) to require
`Authorization: Bearer <key>` on `/api/*`.

## Cross-fleet integration

- **Obscura MCP** (`obscura-mcp`) — uses a Rust headless engine to solve
  Cloudflare/Turnstile/CAPTCHA challenges on protected indexers or Anna's
  Archive slow-mirror links.
