# rTorrent MCP Server 

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>


> 📖 **[Installation Guide](INSTALL.md)** — quick start, manual setup, and troubleshooting

**rTorrent MCP**  FastMCP 3.1.0 server for **anime BitTorrent automation** with Austrian legal context, talking to **rTorrent** over XML-RPC/SCGI (not a generic site scraper).

**What this is:** A **BitTorrent** control plane: add/list/pause torrents, search indexers (Nyaa, etc.), workflows, and post-processing against your **rTorrent** instance. It is **not** a generic systems MCP, and it is **not** a qBittorrent Web API client.

**Web UI (`web_sota/`):** A **small** Vite + React dashboard + **REST bridge** (`/api/*`) on the same uvicorn process as MCP (status, torrent list, magnet add). It is a **deliberately minimal** alternative to the ruTorrent WebUI bundled with Dockersee **[Quick Start](#quick-start)** (subsection *ruTorrent vs this projects webapp*) and [`web_sota/README.md`](web_sota/README.md). **Agents** still use **MCP tools** for full workflows.

> ** Naming:** GitHub repo **`rtorrent-mcp`**; Python package **`rtorrent_mcp`**. The old **qBittorrent**
> prototype used the historic name **`qbtmcp`**  that client is **not** supported; control is **rTorrent**
> via XML-RPC. See **[docs/RTORRENT_REFERENCE.md](docs/RTORRENT_REFERENCE.md)** and
> **[docs/RTORRENT_SETUP.md](docs/RTORRENT_SETUP.md)**.

**Logs & tool text:** Prefer ASCII markers (`[OK]`, `[FAIL]`, `[WARN]`) instead of Unicode emoji so MCP clients, Windows consoles, and JSON stay predictable.

## Features 

- **rTorrent docs:** **[docs/RTORRENT_REFERENCE.md](docs/RTORRENT_REFERENCE.md)** (architecture + env) and **[docs/RTORRENT_SETUP.md](docs/RTORRENT_SETUP.md)** (Docker, plugins, long setup)
- **FastMCP 3.1.0**: Portmanteau tools, MCPB packaging, prompts, skills provider, sampling, agentic workflow tool, CI/CD
- **6 Consolidated Tools**: torrent, search, nlp, legal, system, workflow management
- **rTorrent integration**: Torrent operations via XML-RPC to your instance (add/list/pause/resume/delete, etc.)
- **Multi-Source Search**: nyaa.si (anime), Pirate Bay (TV), YTS (movies), Anna's Archive (ebooks)
- **Post-Processing**: Automatic completion detection, filename normalization, Plex integration
- **Metadata Services**: IMDb and TVDB metadata retrieval for movies and TV shows
- **Austrian Legal Compliance**: Built-in legal risk assessment for Austrian users
- **Natural language**: Parse anime-related commands in English/German
- **Quality scoring**: Simple heuristics for release ordering (e.g. group/metadata cues)
- **Tool schemas**: Docstrings and structured parameters for MCP clients
- **System tools**: Health/status helpers and optional workspace/repo inspection where implemented
- **Configuration**: Environment variables and `.env` support
- **Tests**: Unit and integration tests under `tests/`

## Quick Start

```powershell
git clone https://github.com/sandraschi/qbt-mcp
cd qbt-mcp
just
```

This opens an interactive dashboard showing all available commands. Run `just bootstrap` to install dependencies, then `just serve` or `just dev` to start.

### Manual Setup

If you don't have `just` installed:
### Prerequisites
- Python 3.10 or higher
- Docker Desktop (for rTorrent) - **Recommended**
- Claude Desktop (for MCP integration)
### rTorrent stack (Docker, recommended)
#### What [crazy-max/docker-rtorrent-rutorrent](https://github.com/crazy-max/docker-rtorrent-rutorrent) is
**CrazyMax** maintains a well-used Docker setup that packages **rTorrent** (the actual client), **ruTorrent** (a PHP web UI on top of rTorrent), and **nginx** as a front door. Nginx exposes **XML-RPC** on a TCP port so clients (this MCP server, scripts, other tools) can call rTorrents RPC at `/RPC2` without you wiring SCGI sockets by hand. The image is aimed at install Docker, get a working rTorrent + classic WebUI, not at building rTorrent from source.
This repos root [`docker-compose.yml`](docker-compose.yml) pins **`crazymax/rtorrent-rutorrent:latest`**, maps **XML-RPC** to **12224** and **ruTorrent** to **12222**, and uses volumes under `./config`, your downloads folder, `./watch`, and `./logs` (see the compose file for exact bind paths on Windows).
#### Install (minimal)
1. Install **Docker Desktop** and ensure it is running.
2. Clone this repository (or copy `docker-compose.yml` and related layout).
3. From the **repository root**:
docker compose up -d
(Use `docker-compose up -d` if your Docker install only provides the hyphenated CLI.)
4. Check the container:
docker logs rtorrent-mcp
5. **Endpoints (defaults in this repo):**
- **XML-RPC (for MCP):** `http://localhost:12224/RPC2`
- **ruTorrent WebUI:** `http://localhost:12222`
Point the MCP server at the RPC endpoint with **`RTORRENT_HOST`** / **`RTORRENT_PORT`** (see [docs/RTORRENT_REFERENCE.md](docs/RTORRENT_REFERENCE.md)).
#### ruTorrent vs this projects webapp (`web_sota/`)
**ruTorrent** (bundled in CrazyMaxs image) is the full UI: plugins, RSS, autotools, labels, and a lot of surface area. Many people find it **overcomplicated** and the UI **dated**; it is still the right place when you need **plugin workflows** (RSS rules, auto-move, unpack, etc.) that we do not replicate.
**Our webapp** under [`web_sota/`](web_sota/) is intentionally **rudimentary**: a small **Vite + React** dashboard on a **REST bridge** (`/api/*`) served by the same Python process as MCPsee [`web_sota/README.md`](web_sota/README.md). Today it is a **light substitute** for day-to-day glances: health, rTorrent probe, torrent list, **magnet add**. It is **not** a feature-complete ruTorrent replacement. Use it when you want something simple; keep ruTorrent (or MCP tools) when you need depth.
Run the stack (backend + Vite) with:
.\web_sota\start.ps1
Default dev URLs are documented in `web_sota/README.md` (Vite + uvicorn ports).
#### Optional: ruTorrent plugins (CrazyMax image)
The upstream image ships ruTorrent with many plugins; common automation-related ones include RSS/feeds, autotools, scheduler, unpack, ratio/seedingtime. See [docs/RTORRENT_SETUP.md](docs/RTORRENT_SETUP.md) for a longer list and configuration notes.

## Installation

**rTorrent in Docker (CrazyMax image), ports, and webapp vs ruTorrent** are covered under **[Quick Start  rTorrent stack (Docker, recommended)](#rtorrent-stack-docker-recommended)** above. This section is for the **Python MCP package** and optional **desktop** wiring.

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (RECOMMENDED)
- Python 3.12+

### Quick Start
Run immediately via `uvx`:
```bash
uvx rtorrent-mcp
```

### Claude Desktop Integration
Add to your `claude_desktop_config.json`:
```json
"mcpServers": {
  "rtorrent-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/rtorrent-mcp", "run", "rtorrent-mcp"]
  }
}
```

### Platform setup

#### Quick Setup (Windows - Docker Recommended)

**Prerequisites:** Docker Desktop must be installed and running.

```batch
# Download the project files
# Place docker-compose.yml and install.bat in your desired directory

# Run the installation script
install.bat

# The script will:
# - Create necessary directories
# - Configure rTorrent with SCGI support
# - Start the Docker containers
# - Test the connection
```

**Management Commands:**
```batch
start.bat      # Start rTorrent containers
stop.bat       # Stop rTorrent containers  
status.bat     # Check container status and health
uninstall.bat  # Remove everything
```

#### Alternative: WSL2 Setup

```powershell
# Enable WSL2 (run as Administrator)
wsl --install -d Ubuntu

# Inside WSL2 Ubuntu
sudo apt update
sudo apt install rtorrent
```

#### Linux/macOS Setup

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install rtorrent

# CentOS/RHEL/Fedora
sudo yum install rtorrent
# or
sudo dnf install rtorrent

# macOS
brew install rtorrent

# Verify SCGI support
rtorrent -h | grep -i scgi
```

#### Basic Configuration

**For Docker (Windows):**

1. **Create rTorrent configuration**
   ```powershell
   # Create config directory
   mkdir C:\rtorrent-mcp\config
   
   # Create rtorrent.rc configuration
   @"
   # SCGI configuration for MCP server
   scgi_port = 0.0.0.0:5000
   
   # Basic settings
   session.path.set = /config/session
   directory.default.set = /downloads
   log.execute = /config/rtorrent.log
   
   # Performance settings
   max_uploads.set = 50
   max_connections.set = 200
   max_peers.set = 100
   
   # Austrian Legal Compliance
   system.method.set_key = event.download.inserted_new, anime_category, "d.custom1.set=anime"
   "@ | Out-File -FilePath "C:\rtorrent-mcp\config\rtorrent.rc" -Encoding UTF8
   ```

2. **Restart container to apply configuration**
   ```powershell
   docker-compose restart
   ```

3. **Verify connection**
   ```powershell
   # Test SCGI connection from Windows
   Invoke-RestMethod -Uri "http://localhost:5000/RPC2" -Method POST -ContentType "text/xml" -Body '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>'
   ```

**For WSL2/Linux/macOS:**

1. **Create rTorrent configuration**
   ```bash
   mkdir -p ~/.rtorrent
   cat > ~/.rtorrent.rc << 'EOF'
   # SCGI configuration for MCP server
   scgi_port = localhost:5000
   
   # Basic settings
   session.path.set = ~/.rtorrent/session
   directory.default.set = ~/Downloads
   log.execute = ~/.rtorrent/rtorrent.log
   
   # Performance settings
   max_uploads.set = 50
   max_connections.set = 200
   max_peers.set = 100
   EOF
   ```

2. **Start rTorrent daemon**
   ```bash
   # Start in background
   rtorrent -d
   
   # Or with systemd (create service)
   sudo systemctl start rtorrent
   sudo systemctl enable rtorrent
   ```

3. **Verify connection**
   ```bash
   # Test SCGI connection
   curl -X POST -H "Content-Type: text/xml" \
     -d '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>' \
     http://localhost:5000/RPC2
   ```

For Windows, macOS, Docker, and advanced configuration options, see [docs/RTORRENT_SETUP.md](docs/RTORRENT_SETUP.md).

### Configuration

1. **Create a `.env` file** (or set environment variables)

   ```env
   # rTorrent settings
   RTORRENT_HOST=localhost
   RTORRENT_PORT=12224
   RTORRENT_PATH=/var/lib/rtorrent/session

   # Nyaa.si settings
   NYAA_BASE_URL=https://nyaa.si

   # Application settings
   DEBUG=false
   LOG_LEVEL=INFO
   ```

### Running the Server

```bash
# Run with stdio transport (for Claude Desktop)
python -m rtorrent_mcp.server --transport stdio

# Or with HTTP transport
python -m rtorrent_mcp.server --transport http

# Custom config file
python -m rtorrent_mcp.server --config /path/to/config.env

# Direct module execution
python src/rtorrent_mcp/server.py
```

## Development

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=rtorrent_mcp --cov-report=html
```

### Code Style

```bash
# Format code with ruff
uv run ruff format .

# Lint code with ruff
uv run ruff check . --fix

# Type checking with pyright
uv run pyright

# Security scanning
uv run bandit -r src/
uv run safety scan
```

## Features in Detail

### Smart Anime Search

```python
# Basic search
await search_anime("Detective Conan", resolution="720p", group="ASW")

# Advanced search with filters
await search_anime(
    query="One Piece",
    resolution="1080p",
    group="Erai-raws"
)
```

### rTorrent Integration

```python
# Add torrent from magnet link
magnet = "magnet:?xt=urn:btih:..."
await add_torrent(magnet, category="anime")

# Monitor and manage downloads
await list_torrents()
await pause_torrent("torrent_hash")
await resume_torrent("torrent_hash")
await delete_torrent("torrent_hash", delete_files=True)

# Check connection status
await get_status()
```

### (AT) Austrian Legal Compliance

```python
# Check if content is safe for Austria
is_safe = await check_austrian_legal_status(torrent_info)
if is_safe:
    await add_torrent_qbt(torrent_info["magnet"])
else:
    logger.warning("Content may not be legal in Austria")
```

### Extended Search Capabilities

```python
# Search manga
await search_manga("One Piece", subcategory="translated")

# Search Japanese TV shows
await search_japanese_tv("Terrace House", subcategory="translated")

# Search movies on YTS
await search_movies("The Matrix", quality="1080p", sort_by="seeds")

# Search ebooks on Anna's Archive (60M+ books!)
await search_ebooks_annas("Python Programming", content_type="books")

# Search comics on Pirate Bay
await search_comics("Watchmen", max_results=20)
```

### Metadata Services

```python
# Get IMDb metadata for a movie
await get_imdb_metadata("The Matrix", year=1999)

# Search IMDb for multiple matches
await search_imdb("Matrix", year=1999)

# Get TVDB metadata (requires API subscription)
await get_tvdb_metadata("Breaking Bad", year=2008)

# Get detailed Anna's Archive torrent info
await get_annas_detail("https://annas-archive.org/...")
```

### Post-Processing System

```python
# Check for completed downloads
completed = await check_completed_downloads()

# Process a completed download
await process_completed_download("torrent_hash")

# Start automatic post-processing (background polling)
await start_post_processing()

# Stop post-processing
await stop_post_processing()

# Normalize a filename
normalized = await normalize_filename("Show.Name.S01E01.RELEASE-GROUP.mkv", category="tv")
```

### Natural Language Processing

```python
# English commands
await sandra_anime_command("get me this weeks asw anime, 720p")

# German commands
await sandra_anime_command("lade detective conan asw 720p")

# Parse commands without executing
await parse_anime_command("asw attack on titan 1080p")

# Get command help
await get_command_help()
```

### System Tools

```python
# Server help / tool listing
await help()

# System status and health check
await get_system_status()

# Analyze the repository
await analyze_repo()
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RTORRENT_HOST` | `localhost` | rTorrent SCGI host |
| `RTORRENT_PORT` | `12224` | rTorrent XML-RPC port |
| `RTORRENT_PATH` | `/var/lib/rtorrent/session` | rTorrent session path |
| `NYAA_BASE_URL` | `https://nyaa.si` | Nyaa.si base URL |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `DEBUG` | `false` | Enable debug mode |
| `ALLOWED_CATEGORIES` | `["Anime"]` | Allowed content categories |
| `ALLOWED_RESOLUTIONS` | `["720p", "1080p"]` | Allowed video resolutions |
| `MAX_TORRENT_SIZE_GB` | `10` | Maximum allowed torrent size in GB |
| `POST_PROCESSING_ENABLED` | `false` | Enable automatic post-processing |
| `POST_PROCESSING_POLL_INTERVAL` | `60` | Seconds between polling for completed downloads |
| `DELETE_TORRENT_AFTER_COMPLETE` | `true` | Remove torrent after completion |
| `NORMALIZE_FILENAMES` | `true` | Normalize filenames before moving |
| `INGESTION_ANIME_PATH` | - | Path to temporary ingestion folder for anime |
| `INGESTION_TV_PATH` | - | Path to temporary ingestion folder for TV shows |
| `INGESTION_MOVIES_PATH` | - | Path to temporary ingestion folder for movies |
| `OMDB_API_KEY` | - | OMDb API key for IMDb metadata (free at omdbapi.com) |
| `TVDB_API_KEY` | - | TVDB API key for TV metadata (requires subscription) |
| `API_KEY` | - | Bearer/X-API-Key auth for REST API (optional, set to enable) |
| `NYAA_ASW_USERNAME` | `AkihitoSubsWeeklies` | ASW user page on nyaa.si for direct lookup |
| `PIRATEBAY_BASE_URL` | `https://thepiratebay10.xyz` | The Pirate Bay domain (changes frequently) |
| `RTORRENT_SAMPLING_BASE_URL` | `http://127.0.0.1:11434/v1` | OpenAI-compatible LLM endpoint (Ollama default) |
| `RTORRENT_SAMPLING_MODEL` | `llama3.2` | LLM model for agentic workflow |
| `RTORRENT_SAMPLING_USE_CLIENT_LLM` | - | Set to `1` to prefer host LLM over server-side |
| `PLEX_URL` | - | Plex server URL (enables library refresh after post-process) |
| `PLEX_TOKEN` | - | Plex authentication token |
| `JELLYFIN_URL` | - | Jellyfin server URL (enables library scan after post-process) |
| `JELLYFIN_API_KEY` | - | Jellyfin API key |

## Media Service Integration

### Architecture

**Two paths**, depending on whether *arr is in the loop:

#### Direct (anime via nyaa — no *arr)
```
rTorrent (rtorrent-mcp initiated)
  → PostProcessor (normalize + move to ingestion)
    → MediaIntegrator (scan Plex/Jellyfin)
```
For content downloaded directly through rtorrent-mcp (anime, manga from nyaa),
the MediaIntegrator fires Plex/Jellyfin scans so files appear in your media
libraries without waiting for a scheduled scan.

#### *arr-managed (movies/TV)
```
*arr (searches, decides what to grab)
  → *arr sends magnet/torrent to rTorrent (via Download Client config)
    → rTorrent downloads
      → *arr polls rTorrent' or watches folder
        → *arr imports + renames
          → *arr notifies Plex/Jellyfin
```
For *arr-managed content, **configure rTorrent as a download client directly
in Radarr/Sonarr** (Settings > Download Clients > rTorrent). The *arr handles
everything: dispatch, completion detection, import, and media server notification.
No rtorrent-mcp integration needed.

### Enable Plex/Jellyfin scanning

Set the URL + API key in `.env`:

```env
# Plex
PLEX_URL=http://localhost:32400
PLEX_TOKEN=your_plex_token

# Jellyfin
JELLYFIN_URL=http://localhost:8096
JELLYFIN_API_KEY=your_jellyfin_key
```

Only services with both URL and key set are contacted — others are skipped silently.

### Manual trigger

```python
await torrent_management(action="notify_media", torrent_hash="...", category="tv")
```

This fires the scan pipeline for an already-processed torrent without re-running
the file move.

## Documentation

### API Reference

For detailed API documentation, run the server and visit:

```
http://localhost:10910/api/health
```

### Product Requirements Document

See [PRD.md](docs/PRD.md) for product background, requirements, and technical notes.

### Extended Search Guide

See [EXTENDED_SEARCH_GUIDE.md](docs/EXTENDED_SEARCH_GUIDE.md) for complete guide to using all search capabilities including manga, movies, ebooks, comics, and metadata services.

### Post-Processing Setup

See [POST_PROCESSING_SETUP.md](docs/POST_PROCESSING_SETUP.md) for complete post-processing configuration guide, including ingestion folder setup and Plex integration.

### Status Report

See [STATUS_REPORT.md](docs/STATUS_REPORT.md) for current project status, metrics, and development roadmap.

### Development

1. Clone this repository and `cd` into it (or open an existing clone), then install development dependencies:

   ```bash
   git clone https://github.com/sandraschi/rtorrent-mcp.git
   cd rtorrent-mcp
   uv sync --dev
   ```

2. Run tests:

   ```bash
   uv run pytest
   ```

3. Build documentation:

   ```bash
   uv run mkdocs serve
   ```

   Then visit <http://localhost:8001>

## Claude Desktop integration

The recommended `mcpServers` snippet is under [Installation](#installation)  **Claude Desktop Integration**.

### Manual MCP configuration

For advanced users or custom setups, manually configure Claude Desktop:

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
**Location**: `%APPDATA%/Claude/claude_desktop_config.json` (Windows)
**Location**: `~/.config/Claude/claude_desktop_config.json` (Linux)

Add this configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rtorrent-mcp": {
      "command": "python",
      "args": ["-m", "rtorrent_mcp.server", "--transport", "stdio"],
      "cwd": "/path/to/your/rtorrent_mcp",
      "env": {
        "PYTHONPATH": "/path/to/your/rtorrent_mcp/src",
        "RTORRENT_HOST": "localhost",
        "RTORRENT_PORT": "12224",
        "NYAA_BASE_URL": "https://nyaa.si"
      }
    }
  }
}
```

**Configuration Notes**:
- Replace `/path/to/your/rtorrent_mcp` with your actual repository path
- Adjust environment variables as needed for your setup
- The server will start automatically when Claude Desktop launches

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/-feature`)
3. Commit your changes (`git commit -m 'Add some  feature'`)
4. Push to the branch (`git push origin feature/-feature`)
5. Open a Pull Request


## 🛡️ Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [rTorrent](https://rakshasa.github.io/rtorrent/) - The lightweight torrent client
- [Nyaa.si](https://nyaa.si/) - For the anime torrents
- [FastMCP](https://FastMCP 3.1.0anthropic.com) - The MCP framework
- [Claude Desktop](https://claude.ai/desktop) - For MCP integration

---

### Legal compliance (examples)

```python
await check_legal_status("austria")
await check_legal_status("germany")
```

Interpretation of results is on you; this is not legal advice.

## Release group priorities (defaults)

Heuristic ordering used by search helpers (tune in config as needed):

1. **ASW**
2. **SubsPlease**
3. **Erai-raws**
4. **EMBER**
5. **Judas**

## Austrian context (AT)

- Tooling includes AT-oriented legal **risk hints** in outputs; verify locally.
- Command parsing supports English and German where implemented.

## Configuration

Copy `.env.example` to `.env` and configure:

```env
RTORRENT_HOST=localhost
RTORRENT_PORT=12224
NYAA_BASE_URL=https://nyaa.si
ALLOWED_CATEGORIES=Anime
ALLOWED_RESOLUTIONS=720p,1080p
DEFAULT_RESOLUTION=720p
PREFERRED_RELEASE_GROUP=ASW
LOG_LEVEL=INFO
```

## Testing 

### Run Tests

```bash
# Run all tests with coverage
pytest

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only

# Run with verbose output
pytest -v

# Generate coverage report
pytest --cov=rtorrent_mcp --cov-report=html
```

### Test Structure

```
tests/
 conftest.py              # Test configuration and fixtures
 unit/                    # Unit tests (isolated components)
    test_rtorrent_client.py
 integration/             # Integration tests (full workflows)
     test_mcp_integration.py
```

### PowerShell Test Runner

Windows users can use the PowerShell test runner:

```powershell
# Run all tests
.\scripts\run-tests.ps1

# Run with coverage
.\scripts\run-tests.ps1 -Coverage

# Run unit tests only
.\scripts\run-tests.ps1 -Unit
```

### Modern Development Commands

With UV installed, from a **clone** of this repo at the repository root, you can use these modern commands:

```bash
# Install all dependencies (including dev tools)
uv sync --dev

# Run linting and formatting
uv run ruff check . --fix
uv run ruff format .

# Run type checking
uv run pyright

# Run security scans
uv run bandit -r src/
uv run safety scan

# Run tests with coverage
uv run pytest --cov=src/rtorrent_mcp --cov-report=html

# Build package
uv build

# Validate package
uv run twine check dist/*
```

## CI, tests, and checklist

- **CI**: GitHub Actions runs lint, type check, and tests (see `.github/workflows/`)
- **Tests**: `uv run pytest` (coverage optional via `pytest --cov`)
- **Self-review**: [`docs/MCP_PRODUCTION_CHECKLIST.md`](docs/MCP_PRODUCTION_CHECKLIST.md) is a checklist for hardening; it is not a third-party certification.

Treat this project like any other self-hosted tool: verify behaviour in your environment and keep dependencies updated.

## Legal Disclaimer 

This tool is designed for Austrian legal context where personal downloading is generally tolerated. Users in other jurisdictions should research local copyright laws. High-risk countries (Germany, Japan) require additional precautions.

## Dependencies 

- **FastMCP 3.1.0+**: MCP server framework with stdio transport
- **UV**: Modern Python package manager for fast, reliable builds
- **aiohttp**: Async HTTP client for indexer APIs
- **beautifulsoup4**: HTML parsing for search results
- **xmlrpc.client**: rTorrent SCGI communication (Python stdlib)
- **psutil**: System monitoring and health checks
- **pydantic**: Data validation and settings management
- **python-dotenv**: Environment configuration

### Development Dependencies

- **ruff**: Fast Python linter and formatter
- **pyright**: Type checking and static analysis
- **bandit**: Security vulnerability scanner
- **safety**: Dependency vulnerability scanner
- **pytest**: Testing framework with coverage
- **build & twine**: Package building and publishing

## Author

Maintainer: sandraschi / rtorrent-mcp contributors.
