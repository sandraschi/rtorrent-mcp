# rtorrent-mcp

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.4-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>

Talk to Claude to add torrents, search anime/manga/movies/ebooks across half
a dozen sites, and get finished downloads renamed and sorted into Plex or
Jellyfin automatically.

## What this wraps

rtorrent-mcp drives **rTorrent**, a lightweight BitTorrent client, over its
XML-RPC/SCGI interface — it does not scrape a generic download site and it is
not a qBittorrent client. rTorrent itself is not bundled; the easiest way to
get one running is the included Docker Compose stack (see
[Quick Install](#quick-install) below). Full setup, plugins, and
troubleshooting: [docs/RTORRENT_SETUP.md](docs/RTORRENT_SETUP.md).

## What You Can Do

**How it runs**: talks to your rTorrent instance (Docker recommended) over
XML-RPC; ships a small companion web dashboard (`web_sota/`) as a lightweight
alternative to the full ruTorrent WebUI bundled in the same Docker image.

| Direction | Artifacts | Notes |
|-----------|-----------|-------|
| **Hands-in** | Magnet links, search queries, natural-language commands | Via MCP tools or the webapp |
| **Hands-out** | Added/managed torrents, search results, renamed & sorted media files | Plex/Jellyfin libraries notified automatically |

- Search anime (nyaa.si), manga, Japanese TV, movies (YTS), TV shows, ebooks
  (Anna's Archive, Project Gutenberg), and comics from one place
- Add, pause, resume, and delete torrents; check status and health
- Automatic post-processing: rename, move, and notify Plex/Jellyfin when a
  download completes
- Natural-language commands in English or German
  ("get me this week's asw anime, 720p")
- Franchise and batch-series download workflows
- Austrian legal-context hints on search results (not legal advice)

## Quick Install

1. Get rTorrent running: `docker compose up -d` (see [Onboarding](docs/ONBOARDING.md))
2. Download the latest `.mcpb` from [Releases](https://github.com/sandraschi/rtorrent-mcp/releases/latest) and drag it onto Claude Desktop

That's it — no Python, git, or terminal required. Other install methods
(mcpb CLI, manual config, dev mode with `just`): [INSTALL.md](INSTALL.md).

## Example Prompts

- "Get me this week's ASW anime in 720p"
- "Search for The Matrix on YTS in 1080p"
- "Check for completed downloads and notify Plex"

## Documentation

| Doc | Contents |
|-----|----------|
| [Installation](INSTALL.md) | All install methods, prerequisites, troubleshooting |
| [Onboarding](docs/ONBOARDING.md) | First-time rTorrent + Anna's Archive setup |
| [Architecture](docs/ARCHITECTURE.md) | Ports, tool surface, media pipeline, key files |
| [Configuration](docs/CONFIGURATION.md) | All environment variables and config options |
| [Tool Reference](docs/TOOLS.md) | Every MCP tool and action, with examples |
| [Development](docs/DEVELOPMENT.md) | Dev setup, tests, code style, contributing |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and fixes |
| [Extended Search Guide](docs/EXTENDED_SEARCH_GUIDE.md) | Full guide to manga, movies, ebooks, comics, metadata search |
| [*arr Integration](docs/ARR_RTORRENT_SETUP.md) | Wiring rTorrent as a Radarr/Sonarr download client |
| [Product Requirements](docs/PRD.md) | Background and product rationale |

### Austrian context

This tool is built around the Austrian legal context, where personal
downloading is generally tolerated, and includes AT-oriented risk hints on
search results. Users in other jurisdictions should research local copyright
law — high-risk countries (e.g. Germany, Japan) warrant extra caution. This
is not legal advice.

## Requirements

- Python 3.13+ and [uv](https://docs.astral.sh/uv/)
- Docker Desktop (recommended, for running rTorrent)
- Claude Desktop, or any MCP-compatible client

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgments

- [rTorrent](https://rakshasa.github.io/rtorrent/) — the lightweight torrent client
- [Nyaa.si](https://nyaa.si/) — anime torrent indexer
- [FastMCP](https://gofastmcp.com/) — the MCP server framework
