# Configuration

All settings are environment variables, set either in a `.env` file at the repo
root or in the `env` block of your `claude_desktop_config.json` MCP entry.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RTORRENT_HOST` | `localhost` | rTorrent SCGI host |
| `RTORRENT_PORT` | `12224` | rTorrent XML-RPC port |
| `RTORRENT_PATH` | `/var/lib/rtorrent/session` | rTorrent session path |
| `NYAA_BASE_URL` | `https://nyaa.si` | Nyaa.si base URL |
| `NYAA_ASW_USERNAME` | `AkihitoSubsWeeklies` | ASW user page on nyaa.si for direct lookup |
| `PIRATEBAY_BASE_URL` | `https://thepiratebay10.xyz` | The Pirate Bay domain (changes frequently) |
| `ANNAS_ARCHIVE_BASE` | `https://annas-archive.is` | Anna's Archive search mirror (`.org` no longer resolves; `.li`/`.gl` are anti-bot gated) |
| `ANNAS_ARCHIVE_MIRRORS` | `is,gl,li,org` | Comma-separated failover order for Anna's search |
| `ANNAS_SESSION_COOKIE` | _(empty)_ | Anna's session cookie to enable download links — see [ONBOARDING.md](ONBOARDING.md) |
| `OMDB_API_KEY` | _(empty)_ | OMDb API key for IMDb metadata (free at omdbapi.com) |
| `TVDB_API_KEY` | _(empty)_ | TVDB API key for TV metadata (requires subscription) |
| `PLEX_URL` | _(empty)_ | Plex server URL (enables library refresh after post-process) |
| `PLEX_TOKEN` | _(empty)_ | Plex authentication token |
| `JELLYFIN_URL` | _(empty)_ | Jellyfin server URL (enables library scan after post-process) |
| `JELLYFIN_API_KEY` | _(empty)_ | Jellyfin API key |
| `LINK_MODE` | `hardlink` | `hardlink`, `symlink`, `copy`, or `move` — how post-processing places finished files (hardlink preserves rTorrent seeding) |
| `ALLOWED_CATEGORIES` | `["Anime"]` | Allowed content categories |
| `ALLOWED_RESOLUTIONS` | `["720p", "1080p"]` | Allowed video resolutions |
| `MAX_TORRENT_SIZE_GB` | `10` | Maximum allowed torrent size in GB |
| `POST_PROCESSING_ENABLED` | `false` | Enable automatic post-processing |
| `POST_PROCESSING_POLL_INTERVAL` | `60` | Seconds between polling for completed downloads |
| `DELETE_TORRENT_AFTER_COMPLETE` | `true` | Remove torrent after completion |
| `NORMALIZE_FILENAMES` | `true` | Normalize filenames before moving |
| `INGESTION_ANIME_PATH` | _(empty)_ | Temporary ingestion folder for anime |
| `INGESTION_TV_PATH` | _(empty)_ | Temporary ingestion folder for TV shows |
| `INGESTION_MOVIES_PATH` | _(empty)_ | Temporary ingestion folder for movies |
| `API_KEY` | _(empty)_ | Bearer/X-API-Key auth for the REST API (`/api/*`) — optional, set to enable |
| `RTORRENT_SAMPLING_BASE_URL` | `http://127.0.0.1:11434/v1` | OpenAI-compatible LLM endpoint for `agentic_rtorrent_workflow` (Ollama default) |
| `RTORRENT_SAMPLING_MODEL` | `llama3.2` | LLM model for the agentic workflow |
| `RTORRENT_SAMPLING_USE_CLIENT_LLM` | _(empty)_ | Set to `1` to prefer the MCP host's LLM over the server-side sampling endpoint |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |
| `DEBUG` | `false` | Enable debug mode |

## Setting Variables

**In a `.env` file** at the repo root — copy `.env.example` and edit:

```env
RTORRENT_HOST=localhost
RTORRENT_PORT=12224
NYAA_BASE_URL=https://nyaa.si
ALLOWED_CATEGORIES=Anime
ALLOWED_RESOLUTIONS=720p,1080p
LOG_LEVEL=INFO
```

**In `claude_desktop_config.json`** (overrides `.env` for that client):

```json
{
  "mcpServers": {
    "rtorrent-mcp": {
      "command": "uv",
      "args": ["--directory", "C:\\path\\to\\rtorrent-mcp", "run", "rtorrent-mcp"],
      "env": {
        "RTORRENT_HOST": "localhost",
        "RTORRENT_PORT": "12224"
      }
    }
  }
}
```

## Plex / Jellyfin scanning

Only services with both URL and key/token set are contacted — the others are
skipped silently, so it's safe to configure just one.

```env
PLEX_URL=http://localhost:32400
PLEX_TOKEN=your_plex_token

JELLYFIN_URL=http://localhost:8096
JELLYFIN_API_KEY=your_jellyfin_key
```

Trigger a scan manually for an already-processed torrent without re-running
the file move:

```python
await torrent_management(action="notify_media", torrent_hash="...", category="tv")
```

See also: [Architecture](ARCHITECTURE.md) for how post-processing and media
notification fit together, and [ONBOARDING.md](ONBOARDING.md) for first-time
rTorrent and Anna's Archive setup.
