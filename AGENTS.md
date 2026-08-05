# AGENTS.md — rtorrent-mcp (qbt-mcp)

> Per-repo overrides for the fleet-wide [AGENTS.md](../../mcp-central-docs/standards/AGENTS.md).
> Repo dir name is legacy `qbt-mcp`; Python package is `rtorrent_mcp`, PyPI name is `rtorrent-mcp`.

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
search_management  (13 actions)  — anime, manga, japanese_tv, movies, tv_shows,
                                   tv_smart, ebooks_annas, ebooks_pb, comics,
                                   annas_detail, imdb, imdb_search, tvdb
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

## Key Files

| File | Purpose |
|------|---------|
| `src/rtorrent_mcp/config/settings.py` | All env var config |
| `src/rtorrent_mcp/services/media_integrator.py` | Plex/Jellyfin notification |
| `src/rtorrent_mcp/services/post_processor.py` | File move + media trigger |
| `src/rtorrent_mcp/services/rtorrent_client.py` | rTorrent XML-RPC client |
| `src/rtorrent_mcp/server.py` | FastMCP server entrypoint |
| `src/rtorrent_mcp/tools/portmanteau/` | Portmanteau tool implementations |
| `web_sota/e2e/app.spec.ts` | Playwright e2e tests (11 tests) |

## Config (.env)

```env
RTORRENT_HOST=localhost
RTORRENT_PORT=12224

PLEX_URL=http://localhost:32400
PLEX_TOKEN=
JELLYFIN_URL=http://localhost:8096
JELLYFIN_API_KEY=

OMDB_API_KEY=               # required for IMDb metadata
API_KEY=                    # optional REST API auth

RTORRENT_SAMPLING_BASE_URL=http://127.0.0.1:11434/v1
RTORRENT_SAMPLING_MODEL=llama3.2
```

## Notes

- **Dir name**: This repo is cloned as `qbt-mcp` (historic qBittorrent prototype).
  For new clones: `git clone https://github.com/sandraschi/rtorrent-mcp.git`.
- **Sampling**: Defaults to Ollama on localhost (`llama3.2`). Set
  `RTORRENT_SAMPLING_USE_CLIENT_LLM=1` to prefer the MCP host's LLM.
- **Ollama endpoint**: Must include `/v1` suffix (default is correct).
- **REST bridge**: `/api/*` on 10910 — health, capabilities, skills, llm/discover, ai/chat, rtorrent/*, fleet/apps, v1/diagnostics (CUA).
- **Coverage**: `--cov-fail-under=40` (2026-08-05 assfix; was 80% unreachable — 8% before dead-code removal, 46% after; raise the bar in follow-ups).
