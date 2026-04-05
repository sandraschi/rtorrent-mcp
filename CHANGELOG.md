# Changelog

All notable changes to **rTorrent MCP Server** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> ** Naming:** Repository **`rtorrent-mcp`**, Python import **`rtorrent_mcp`**. The historic name
> **`qbtmcp`** was the qBittorrent prototype — retired; use **`rtorrent-mcp`** for new work.

## [3.0.0] - 2025-12-01

### FastMCP 3.1

- **FastMCP 3.1.x**: Portmanteau tools, strict validation, `on_duplicate=replace`, server `version` field
- **Sampling**: `RTorrentSamplingHandler` — OpenAI-compatible HTTP (default Ollama); `RTORRENT_SAMPLING_USE_CLIENT_LLM=1` defers to host LLM
- **Agentic workflow**: `agentic_rtorrent_workflow` — `context.sample_step` with portmanteau tools (SEP-1577-style)
- **Skills**: `SkillsDirectoryProvider` on `src/rtorrent_mcp/skills/` (e.g. `skill://rtorrent-mcp/SKILL.md`)
- **MCPB**: `mcpb.json` updated; `justfile` for `uv`/pytest/ruff/mcpb tasks
- **Prompts**: Existing 7 prompt templates unchanged (discoverable via MCP)

### Earlier: MCPB + portmanteau baseline

- **MCPB**: Packaged server definition for MCPB-compatible clients
- **CI/CD**: GitHub Actions (lint, test, security, publish)

### Six portmanteau tools + one agentic tool

| # | Tool | Actions | Description |
|---|------|---------|-------------|
| 1 | `torrent_management` | 12 | Torrent ops + post-processing |
| 2 | `search_management` | 13 | All search operations |
| 3 | `nlp_management` | 3 | Natural language processing |
| 4 | `legal_management` | 4 | Legal compliance |
| 5 | `system_management` | 5 | System operations |
| 6 | `workflow_management` | 8 | Complex multi-step workflows |
| 7 | `agentic_rtorrent_workflow` | — | LLM-orchestrated flows (requires sampling) |

### 🆕 **Workflow Management (NEW)**

The `workflow_management` portmanteau handles "tricky" operations like downloading entire anime franchises:

```python
# Download ALL One Piece (series + movies + OVAs + specials)
workflow_management(action="franchise", anime_family="one piece")

# Estimate download size first
workflow_management(action="estimate", anime_family="detective conan")

# Batch download episodes 1-100
workflow_management(action="batch_series", anime_family="naruto", episode_start=1, episode_end=100)

# Schedule for overnight
workflow_management(action="schedule", anime_family="dragon ball", schedule_time="02:00")
```

**Supported Franchises:**
- One Piece (1000+ episodes, 15+ movies, OVAs, specials)
- Detective Conan (1100+ episodes, 25+ movies)
- Naruto / Shippuden / Boruto
- Dragon Ball / Z / Super / GT
- Bleach / Thousand-Year Blood War
- Attack on Titan
- Jujutsu Kaisen
- Demon Slayer
- Spy x Family

### **Prompt Templates**

| Prompt | Description |
|--------|-------------|
| `anime_search_prompt` | Search anime with Austrian preferences |
| `franchise_download_prompt` | Guide for downloading entire franchise |
| `legal_check_prompt` | Legal status check workflow |
| `tv_show_search_prompt` | Western TV show search |
| `ebook_search_prompt` | Ebook search (Anna's Archive) |
| `torrent_workflow_prompt` | Standard torrent workflow |
| `system_status_prompt` | System status check |

### **CI/CD Pipeline**

New `.github/workflows/ci.yml` with:
-  Lint & Type Check (Ruff, Pyright, MyPy)
-  Security Scan (Bandit, Safety)
-  Tests (Python 3.10-3.13)
-  Build & Validate
-  FastMCP / package validation
-  PyPI Publish (on release)

---

## [2.1.0] - 2025-12-01

### Consolidated tools

All individual tools have been merged into portmanteau tools. No stragglers (except help/status in system_management).

#### **Torrent Management** (12 actions)
`add`, `list`, `pause`, `resume`, `delete`, `status`, `info`,
`check_completed`, `process`, `start_processing`, `stop_processing`, `normalize`

#### **Search Management** (13 actions)  
`anime`, `manga`, `japanese_tv`, `movies`, `tv_shows`, `tv_smart`,
`ebooks_annas`, `ebooks_pb`, `comics`, `annas_detail`, `imdb`, `imdb_search`, `tvdb`

#### **NLP Management** (3 actions)
`command`, `parse`, `help`

#### **Legal Management** (4 actions)
`risk`, `check`, `advice`, `status`

#### **System Management** (5 actions)
`help`, `status`, `health`, `info`, `analyze`

### **Removed Individual Tools**
- ~~post_processing_tools~~ → merged into `torrent_management`
- ~~tv_integration_tools~~ → merged into `search_management`
- ~~tv_nlp_tools~~ → merged into `search_management`
- ~~piratebay_search~~ → merged into `search_management`

---

## [2.0.0] - 2025-12-01

### Major architecture change

#### Portmanteau tools
Individual tools were consolidated into five portmanteau tools (operation/action parameters). Aligns with FastMCP multi-action tool style.

**Before:** 30+ individual tools  
**After:** 5 consolidated portmanteau tools

#### **New Portmanteau Tools**

| Tool | Actions | Description |
|------|---------|-------------|
| `torrent_management` | add, list, pause, resume, delete, status, info | All rTorrent operations |
| `search_management` | anime, manga, movies, ebooks_annas, ebooks_pb, comics, annas_detail, imdb, imdb_search, tvdb | All search operations |
| `nlp_management` | command, parse, help | Natural language commands (EN/DE) |
| `legal_management` | risk, check, advice, status | Austrian legal compliance |
| `system_management` | help, status, health, info, analyze | System operations |

### Benefits
- Fewer top-level tools for MCP clients
- Related operations grouped by domain
- Docstrings with Args/Returns/Examples
- **Legacy:** `--legacy` for individual tools where supported

### Usage
```bash
# Default: portmanteau tools
python -m rtorrent_mcp.server

# Legacy mode: individual tools
python -m rtorrent_mcp.server --legacy
```

### **New Files**
- `src/rtorrent_mcp/tools/portmanteau/__init__.py`
- `src/rtorrent_mcp/tools/portmanteau/torrent_management.py`
- `src/rtorrent_mcp/tools/portmanteau/search_management.py`
- `src/rtorrent_mcp/tools/portmanteau/nlp_management.py`
- `src/rtorrent_mcp/tools/portmanteau/legal_management.py`
- `src/rtorrent_mcp/tools/portmanteau/system_management.py`

---

## [Unreleased]

### Changed

- **Emoji:** Removed decorative Unicode emoji from MCP logs, tool payloads, and key docs; use ASCII markers (`[OK]`, `[FAIL]`, `[WARN]`, `(AT)` for Austria) for client/terminal safety.
- **Rename:** GitHub / distribution **`rtorrent-mcp`**, Python package **`rtorrent_mcp`**. Historic **`qbtmcp`** (qBittorrent prototype) is retired — update imports and clone URL.
- **Docs:** New **[docs/RTORRENT_REFERENCE.md](docs/RTORRENT_REFERENCE.md)**; Help page in **`web_sota`** expanded with rTorrent / XML-RPC / env details.
- **README**: Opening section now states **BitTorrent** + **rTorrent (SCGI)** explicitly and clarifies that **`web_sota` is a shell/demo**, not the control plane.
- **`web_sota`**: Replaced misleading “fleet auto-discovery”, fake throughput, qBittorrent Web API help text, and static “System Online” with honest copy; added **`web_sota/README.md`**, **MCP HTTP** reachability (proxied `GET /mcp`), and port **10909** in Vite to match `start.ps1`.

### Added
- **Post-Processing System**: Automatic completion detection, filename normalization, and Plex integration
  - `check_completed_downloads`: Check for 100% complete downloads
  - `process_completed_download`: Process and move completed downloads
  - `start_post_processing`: Start automatic background polling
  - `stop_post_processing`: Stop automatic post-processing
  - `normalize_filename`: Clean filenames by removing release group tags
  - Configuration via environment variables (POST_PROCESSING_ENABLED, INGESTION_*_PATH)
  - See [POST_PROCESSING_SETUP.md](docs/POST_PROCESSING_SETUP.md) for details

- **Extended Search Capabilities**:
  - **Manga Search**: Search nyaa.si for manga (raw/translated/english)
  - **Japanese TV Search**: Search nyaa.si for Japanese TV shows
  - **Movie Search**: YTS (yify) integration - gold standard for movies
  - **Anna's Archive Search**: Ebook and academic paper search (60M+ books!)
  - **Comic Search**: Search The Pirate Bay for western comics
  - **Extended Pirate Bay Search**: Enhanced TV show and category search
  - See [EXTENDED_SEARCH_GUIDE.md](docs/EXTENDED_SEARCH_GUIDE.md) for usage

- **Metadata Services**:
  - **IMDb Metadata**: Get movie/TV show metadata via OMDb API
  - **IMDb Search**: Search IMDb for multiple title matches
  - **TVDB Metadata**: Get TV show metadata (requires subscription)
  - **Anna's Archive Detail**: Get detailed torrent info with magnet links

- Initial release of RTorrent MCP Server
- rTorrent XMLRPC API integration (through nginx)
- NYAA.si anime search with quality scoring
- Austrian legal compliance checking
- Natural language command processing (English/German)
- MCPB packaging support
- Comprehensive CI/CD pipeline
- Security scanning and vulnerability assessment
- Code quality tools (Black, isort, mypy, flake8)
- Unit and integration test suites
- Self-documenting tools with JSON schemas
- Claude Desktop integration guides
- Comprehensive status reporting and documentation

### Changed
- Implemented rTorrent SCGI backend (after qBittorrent proved unusable)
- Updated to FastMCP 2.12 for better Claude integration
- Improved error handling and logging
- Enhanced security and privacy features

### Fixed
-  **rTorrent connection issue resolved**: Fixed SCGI connection problem by using XMLRPC through nginx (port 8000) instead of direct SCGI configuration
  - Updated docker-compose.yml to map port 12224 to container port 8000 (XMLRPC)
  - Removed unnecessary custom startup scripts and socat bridge
  - Connection now works using standard XMLRPC protocol through nginx proxy
  - Verified with rTorrent version 0.15.5

### Technical Details
- **Framework**: FastMCP 2.12
- **Backend**: rTorrent XMLRPC API (through nginx)
- **Search Engines**: NYAA.si, The Pirate Bay, YTS, Anna's Archive
- **Legal Compliance**: Austria-focused
- **Languages**: English/German NLP support
- **Packaging**: MCPB bundles
- **CI/CD**: GitHub Actions with security scanning
- **Total MCP Tools**: 52 tools registered
- **Test Coverage**: 34.43% (target: 80%)

---

## [1.0.0] - 2025-09-23

### Added
- Complete RTorrent MCP Server implementation
- Austrian legal compliance framework
- Multi-language natural language processing
- MCPB packaging for Claude Desktop
- Comprehensive documentation and guides
- Security and code quality tooling
- GitHub Actions CI/CD pipeline

### Changed
- Full rTorrent SCGI implementation
- Updated to modern MCP standards (2.12)
- Improved user experience and error handling

### Technical Improvements
- Async/await implementation for better performance
- Structured logging throughout the application
- Type hints and comprehensive error handling
- Self-documenting API with JSON schemas
- Extensive test coverage (unit and integration)

---

## [0.1.0] - 2025-09-01

### Added
- Initial MCP Server prototype (started with qBittorrent, pivoted to rTorrent)
- Basic torrent management functionality
- NYAA.si search integration
- Austrian legal compliance checks
- Natural language command processing

### Known Issues
- Initially limited to qBittorrent WebUI API (proved unusable, led to rTorrent pivot)
- Basic error handling
- Minimal test coverage

---

<!-- Release Notes Template

## [x.y.z] - YYYY-MM-DD

### Added
- New features and functionalities

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security-related changes

### Performance
- Performance improvements

### Documentation
- Documentation updates

### Dependencies
- Dependency updates

-->

---

## Release Notes

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Process

1. **Development**: Features developed on `develop` branch
2. **Staging**: Merged to `main` for testing
3. **Release**: Tagged versions create GitHub releases
4. **Distribution**: MCPB packages published to registry

### Support

- **Latest**: Most recent stable release
- **LTS**: Long-term support versions (if applicable)
- **Nightly**: Development builds (not recommended for production)

### Migration Guide

#### The Great Pivot: qBittorrent → rTorrent (v1.0.0)
> qBittorrent had no API or CLI suitable for MCP control. rTorrent provides
> powerful SCGI-based programmatic control, making it ideal for automation.
- Update configuration to use rTorrent SCGI settings
- Install rTorrent with SCGI support
- Update MCP server configuration
- Test torrent operations with new backend

---

**Legend:**
-  New features
-  Improvements
-  Bug fixes
-  Documentation
-  Security
-  Performance

---

*This changelog is automatically updated via CI/CD pipeline.*
