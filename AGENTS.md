# AGENTS.md — rtorrent-mcp (qbt-mcp)

> Per-repo overrides for the fleet-wide [AGENTS.md](../../mcp-central-docs/standards/AGENTS.md).
> Repo dir: `rtorrent-mcp`; Python package `rtorrent_mcp`; PyPI name `rtorrent-mcp` (historic qBittorrent prototype name `qbtmcp` is retired).

## Ports

| Service | Port | Notes |
|---------|------|-------|
| rTorrent XML-RPC (nginx) | `12224` | In Docker: crazymax/rtorrent-rutorrent |
| ruTorrent WebUI | `12222` | In Docker container |
| rtorrent-mcp backend (uvicorn) | `10910` | MCP HTTP `/mcp` + REST `/api/*` |
| rtorrent-mcp frontend (Vite) | `10911` | Proxies `/api` + `/mcp` → 10910 |

## Tests

```powershell
# Run all tests (coverage requires 80%)
uv run pytest

# Run specific files
uv run pytest tests/test_media_integrator.py -v -o "addopts="

# Playwright e2e (in web_sota/)
cd web_sota
npx playwright test
```

## Architecture

```
6 portmanteau tools + 1 agentic workflow:

torrent_management (13 actions)  — add, list, pause, resume, delete, status, info,
                                   notify_media, check_completed, process,
                                   start_processing, stop_processing, normalize
search_management  (14 actions)  — anime, manga, japanese_tv, movies, tv_shows,
                                   tv_smart, ebooks_annas, ebooks_gutenberg,
                                   ebooks_pb, comics, annas_detail, imdb, imdb_search, tvdb
nlp_management      (3 actions)  — command, parse, help
legal_management    (4 actions)  — risk, check, advice, status
system_management   (5 actions)  — help, status, health, info, analyze
workflow_management (8 actions)  — franchise, batch_series, status, cancel,
                                   list, estimate, queue, schedule
agentic_rtorrent_workflow        — LLM-orchestrated multi-step (requires Ollama)
```

## Cross-Connect

- **Plex/Jellyfin**: `MediaIntegrator` fires library scans after direct downloads (anime via nyaa).
  Configure via `PLEX_URL`/`PLEX_TOKEN`/`JELLYFIN_URL`/`JELLYFIN_API_KEY` in `.env`.
- ***arr apps** (Radarr/Sonarr): Do NOT go through rtorrent-mcp. Configure rTorrent as a
  download client directly in each *arr (Settings > Download Clients > rTorrent,
  host: localhost, port: 12224, path: /RPC2).
  See `docs/ARR_RTORRENT_SETUP.md`.
- **Obscura MCP (`obscura-mcp`)**: Uses the Obscura Rust headless engine to solve Cloudflare/Turnstile/CAPTCHA challenges and JS countdown queues on protected indexers or Anna's Archive slow mirror links.

## Key Files

| File | Purpose |
|------|---------|
| `src/rtorrent_mcp/config/settings.py` | All env var config |
| `src/rtorrent_mcp/services/filename_normalizer.py` | Media normalizer & Plex path builder |
| `src/rtorrent_mcp/services/gutenberg_search.py` | Project Gutenberg e-book search via Gutendex API |
| `src/rtorrent_mcp/services/media_integrator.py` | Plex/Jellyfin notification |
| `src/rtorrent_mcp/services/post_processor.py` | File move/link + media trigger |
| `src/rtorrent_mcp/services/rtorrent_client.py` | rTorrent XML-RPC client |
| `src/rtorrent_mcp/server.py` | FastMCP server entrypoint |
| `src/rtorrent_mcp/tools/portmanteau/` | Portmanteau tool implementations |
| `web_sota/src/pages/nyaa.tsx` | Nyaa Anime Search page |
| `web_sota/src/pages/piratebay.tsx` | The Pirate Bay TV & Movies page |
| `web_sota/src/pages/gutenberg.tsx` | Project Gutenberg E-Book Search page |
| `web_sota/e2e/app.spec.ts` | Playwright e2e tests (11 tests) |

## Config (.env)

```env
RTORRENT_HOST=localhost
RTORRENT_PORT=12224

PLEX_URL=http://localhost:32400
PLEX_TOKEN=
JELLYFIN_URL=http://localhost:8096
JELLYFIN_API_KEY=

LINK_MODE=hardlink             # hardlink, symlink, copy, move (preserves rTorrent seeding)

OMDB_API_KEY=               # required for IMDb metadata
API_KEY=                    # optional REST API auth

RTORRENT_SAMPLING_BASE_URL=http://127.0.0.1:11434/v1
RTORRENT_SAMPLING_MODEL=llama3.2
```

## Notes

- **History**: Started as a qBittorrent prototype (`qbtmcp`); pivoted to rTorrent (see CHANGELOG).
  For new clones: `git clone https://github.com/sandraschi/rtorrent-mcp.git`.
- **Sampling**: Defaults to Ollama on localhost (`llama3.2`). Set
  `RTORRENT_SAMPLING_USE_CLIENT_LLM=1` to prefer the MCP host's LLM.
- **Ollama endpoint**: Must include `/v1` suffix (default is correct).
- **REST bridge**: `/api/*` on 10910 — health, capabilities, skills, llm/discover, ai/chat, rtorrent/*, search/nyaa, search/piratebay, normalize/filename, plex/status, plex/scan, plex/ingest, fleet/apps, v1/diagnostics (CUA).
- **Coverage**: `--cov-fail-under=55` (2026-08-25: 238 tests green at 59.44%).
