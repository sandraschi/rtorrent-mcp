# rtorrent-mcp

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.4-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>

> # ⛔ Not for piracy.
> **This software does not help with copyright infringement — no infringing
> sources, no sourcing help, no configuration for infringing purposes.**
> BitTorrent is neutral infrastructure with real lawful uses; this repo is
> for those. Read first: [Legal notice](docs/LEGAL_NOTICE.md) ·
> [Lawful sourcing](docs/LEGAL_SOURCING.md) · [Safety](docs/SAFETY_TORRENTING.md) ·
> [Country specifics](docs/LEGAL_COUNTRIES.md).
> Sourcing questions in issues are respectfully declined and closed.

Talk to Claude to add torrents, search anime/manga/movies/ebooks across half
a dozen sites, and get finished downloads renamed and sorted into Plex or
Jellyfin automatically.

## What this wraps

rtorrent-mcp drives a torrent client over its automation interface — it
does not scrape a generic download site. Two backends, one tool surface
(`TORRENT_BACKEND`, default `rtorrent`):

- **rTorrent** over XML-RPC/SCGI (not bundled; easiest via the included
  Docker Compose stack — see [Quick Install](#quick-install) below).
- **qBittorrent** over its WebUI API v2 (native exe, no Docker needed).
  Set `TORRENT_BACKEND=qbittorrent` plus `QBITTORRENT_URL` (and
  `QBITTORRENT_API_KEY` on ≥ v5.2.0, else username/password).

Full rTorrent setup, plugins, and troubleshooting:
[docs/RTORRENT_SETUP.md](docs/RTORRENT_SETUP.md). Backend design, client
coverage, and no-seed proof gates: [docs/DUAL_BACKEND_SPEC.md](docs/DUAL_BACKEND_SPEC.md).

## What You Can Do

**How it runs**: talks to your torrent backend (rTorrent over XML-RPC,
Docker recommended; or native qBittorrent over its WebUI API) plus a small
companion web dashboard (`web_sota/`) as a lightweight
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
| [Legal notice](docs/LEGAL_NOTICE.md) | **Not-for-piracy stance, what this software is, issue policy** |
| [Lawful sourcing](docs/LEGAL_SOURCING.md) | What you may lawfully put through a client |
| [Torrenting safety](docs/SAFETY_TORRENTING.md) | Swarm visibility, VPN limits, malware, seeding liability |
| [Country specifics](docs/LEGAL_COUNTRIES.md) | Austria, Germany, USA, UK, Japan enforcement (+ EMEA: FR/IT/NL/CH/ES) |
| [VPN privacy](docs/VPN_PRIVACY.md) | Justified uses, dual use, criteria, named providers, what fails |

### Austrian context

This tool is built around the Austrian legal context, where personal
downloading is generally tolerated, and includes AT-oriented risk hints on
search results. Full picture (beyond Austria): [Country specifics](docs/LEGAL_COUNTRIES.md).
Users in other jurisdictions should research local copyright
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
