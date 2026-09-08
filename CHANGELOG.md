
## [Unreleased]

### Fixed
- **Anna's Archive search was fabricating fake results (BUG-032)**: the site's own "No records found..." empty-state box matched a broad CSS fallback selector and had no real title link inside it, so the scraper fell back to `container.get_text(strip=True)[:200]` and scraped the empty-state copy as if it were a book title -- `success: true, count: 1` on a genuinely empty search. A second, always-true fake-success path ("query appears on page") also fabricated a placeholder result on every empty search, since Anna's Archive echoes the query in its results heading regardless of hit count. Both replaced with an honest `([], None)`; a container with no real title link is now skipped instead of scraped. Full writeup: [mcp-central-docs BUGS_DEPOT.md, BUG-032](../mcp-central-docs/troubleshooting/details/BUG-032_Annas_Archive_Selector_Rot_Fake_Success.md).

### Added
- **Obscura headless-browser fallback for bot-gated Anna's Archive mirrors**: split `_search_annas_on` into fetch (aiohttp, falling back to the Obscura Rust engine when a mirror looks bot-gated -- 403/503 or a known challenge-page marker) and parse (pure, no I/O, so the BUG-032 fix applies to both paths identically). Obscura helpers moved from `api/web_routes.py` into a new `services/obscura_bridge.py` so services code can use them without a backwards api-to-service import; `web_routes.py` re-exports under the original names, zero behavior change to the existing download flow.
- **`.gl`/`.li` mirror scoping documented**: `docs/ANNAS_MIRROR_OBSCURA_FALLBACK_PLAN.md` records that `.gl` still fails Obscura's one-shot stealth render against DDoS-Guard's JS challenge (confirmed live, not assumed -- the raw output is the actual challenge page, not a false-positive marker match). Filed upstream: [h4ckf0r0day/obscura#925](https://github.com/h4ckf0r0day/obscura/issues/925).

## [3.1.0] - 2026-08-25 (tagged 2026-09-08)

### Fixed (2026-09-08 - first tagged native release)
- **Backend never actually ran in any prior NSIS install**: `pyinstaller` was
  never a project dependency, only a standalone `uv tool install` running in
  its own isolated environment. `uv run pyinstaller` silently resolved there
  instead of the project venv, so the frozen backend exe had no visibility
  into fastmcp/uvicorn/starlette and crashed instantly with
  `ModuleNotFoundError: No module named 'uvicorn'`. Fixed by adding
  `pyinstaller` as a dev dependency; also fixed a `PermissionError` this
  exposed in `rtorrent-mcp-backend.spec`'s metadata-copying step.
- **Packaged app's dashboard always showed "Backend down"**: Chromium's
  Private Network Access policy silently blocks `fetch()` from the app's
  `https://tauri.localhost` origin to `http://127.0.0.1:10910` unless the
  CORS preflight explicitly allows it. Fixed with
  `allow_private_network=True` on the existing CORS middleware.
- **Dashboard status was all-or-nothing**: `useRtorrentBridge` batched
  health/rTorrent-status/torrents into one `Promise.all`, so rTorrent being
  offline (its own Docker container not running) falsely reported the MCP
  backend itself as down too. Switched to `Promise.allSettled`.
- Added the fleet-mandatory `useZoom()` hook (Ctrl+Scroll/Ctrl+0), missing
  from this repo's native shell entirely.

First real end-to-end verification: `native/build.ps1` full pipeline +
`python scripts/cua-smoke.py` (install -> launch -> health -> diagnostics ->
nav walk -> uninstall), 11/11 phases passing.

### Added
- **Dedicated Indexer Search Pages**:
  - **Nyaa Anime Search** (`/nyaa`): Nyaa.si anime indexer with group selection (ASW, SubsPlease, Erai-raws), resolution filters, quality score badges, and direct rTorrent dispatch.
  - **The Pirate Bay Search** (`/bay`): TV & Movies indexer with parsed episode badges (`S01E05`), group selection (MeGusta, RARBG, EZTV), and quick dispatch.
- **Filename Normalizer & Path Builder**:
  - `src/rtorrent_mcp/services/filename_normalizer.py`: Scene tag & CRC hash cleaner, SXXEXX season/episode parser, and Plex-compliant path builder (`Movies/Movie (Year)/...` & `TV Shows/Show/Season XX/...`).
  - Interactive Filename Normalizer tester card in web application Tools page.
- **Seeding Preservation & Link Modes**:
  - Added `link_mode` (`hardlink`, `symlink`, `copy`, `move`) in `post_processor.py` so active BitTorrent seeding is preserved when organizing completed files into Plex libraries.
- **REST Bridge Endpoints**:
  - Added `/api/search/nyaa`, `/api/search/piratebay`, `/api/normalize/filename`, `/api/plex/status`, `/api/plex/scan`, and `/api/plex/ingest`.
- **Plex Ingestion Controls**:
  - Added Plex status indicator and manual scan/ingest trigger controls in web application Settings page.

### Fixed
- **Cross-drive Path Error**: Wrapped `os.path.commonpath` calculation in `media_integrator.py` to safely handle Windows cross-drive file paths.
- **Test Suite Expansion**: Added unit tests in `tests/test_filename_normalizer.py` and endpoint tests in `tests/test_web_routes.py` (238 tests passing at 59.44% coverage).

## [Unreleased] - 2026-08-05

### Fixed (assfix 2026-08-05)
- **CORS never applied** - middleware was attached to `self._app`, which only exists after `http_app()` builds it; moved to `http_app(middleware=...)` (fleet standard).
- **HTTP transport** - replaced `run_http_async()` with `uvicorn.Server` on `mcp.http_app()` per fleet standard.
- **165/165 tests green** - 23 stale tests updated to the refactored API (post-processing signature, FastMCP 3.4 `list_tools`/`list_resources`, OMDb API-key contract, TV NLP behavior); `test_tools.py` rewritten against the portmanteau surface.
- **pyright 175 -> 0 errors** - deleted dead legacy individual tool modules, typed the XML-RPC proxy as `Any`, fixed BS4/str typing, `TransportArgs` subclasses `argparse.Namespace`.
- **Coverage gate** - `--cov-fail-under` 80 -> 40 in the main pass; raised to 55 in the follow-up (226 tests, 58.75% measured).
- **Chat page** called a non-existent `/api/ai/chat`; endpoint implemented against the configured sampling endpoint.
- **Vite port 10912 -> 10911** (fleet registry).
- **CUA config paths** - added `/api/v1/diagnostics` + `/api/v1/system/info` (config referenced missing endpoints).
- **post_processor** - graceful client-unavailable handling; `MediaIntegrator` import no longer swallows ImportError.
- **tv_nlp** - `_clean_show_name` handles hyphens/underscores; fallback parsing for "episodes of/from X" and "download X from Y".
- **natural_language** - `extract_resolution(None)` returns `""` instead of crashing.

### Added
- REST endpoints: `/api/capabilities`, `/api/skills`, `/api/skills/{name}`, `/api/llm/discover`, `/api/ai/chat`, `/api/fleet/apps`, `/api/v1/diagnostics`, `/api/v1/system/info`.
- Webapp Skills page + route + sidebar entry; settings LLM auto-discovery; App Hub fleet discovery; dashboard `data-testid` KPIs.
- `@tauri-apps/api` + `zustand` deps; Tauri `backend-status` event listener with exponential-backoff HTTP poll.
- Session-context injection (`.claude-plugin`, `.cursorrules`, `.windsurfrules`, `.github/copilot-instructions.md`, `.opencode/skills/session-context`).
- MCPB 3-4-100 prompts (`system.md` 3000+ words, `user.md` 4000+ words, `examples.json` 108 entries) + 256x256 icon + v0.2 `manifest.json`.
- `.pre-commit-config.yaml` + `scripts/pre-commit-biome.ps1`, `.gitattributes` LF normalization.
- CI: push/PR triggers, `PYTHON_VERSION` env, frontend job (Node 22, tsc, biome, build).
- `start.ps1`: port zombie clearing, backend readiness poll, auto browser-open.
- Ruff `T20` print ban with per-file-ignore for the CLI entry point.

### Changed
- Coverage threshold 80% -> 40% (documented in AGENTS.md).
- `glama.json` - FastMCP 3.4.4, stable, 7 tools, dual transport, version field.
- Tauri version 0.1.0 -> 3.0.0 (matches pyproject).
- `.env.example` - `PORT=8000` -> `10910`, added REST/LLM sections.
- **Tests 165 -> 226** - added REST bridge suite (`tests/test_web_routes.py`, 25 tests over the Starlette app incl. auth + error paths), sampling handler suite (`tests/test_sampling.py`), transport config suite (`tests/test_transport.py`), prompt registration suite (`tests/test_prompts.py`), and portmanteau action tests (`tests/test_portmanteau_extra.py`).
- Removed tracked junk (`.windsurf/`, `_llm_test_scripts/`, `dev_test.py`, `remove_description_params.py` - now gitignored).
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
- **`web_sota`**: Replaced misleading "fleet auto-discovery", fake throughput, qBittorrent Web API help text, and static "System Online" with honest copy; added **`web_sota/README.md`**, **MCP HTTP** reachability (proxied `GET /mcp`), and port **10909** in Vite to match `start.ps1`.

### Added
- **Post-Processing System**: Automatic completion detection, filename normalization, and Plex integration
- **Extended Search Capabilities**: Manga, Japanese TV, Movies (YTS), Anna's Archive, Comics, extended Pirate Bay
- **Metadata Services**: IMDb and TVDB metadata retrieval
- Initial release of RTorrent MCP Server (rTorrent XMLRPC, NYAA.si search, legal compliance, NLP, MCPB, CI/CD)

### Changed
- Implemented rTorrent SCGI backend (after qBittorrent proved unusable)
- Updated to FastMCP 2.12 for better Claude integration

### Fixed
- rTorrent connection via XMLRPC through nginx (port 8000→12224 mapping)
- Connection now works using standard XMLRPC protocol through nginx proxy

---

## [3.0.1] - 2026-05-10

### Fixed — Comprehensive bugbash (25+ fixes across 16 files)

#### Critical
- **nlp_management**: `process_sandra_command` called with wrong parameter count (TypeError crash)
- **metadata_service**: OMDb API endpoint upgraded HTTP→HTTPS (cleartext API key exposure)
- **metadata_service**: OMDb API key now required with clear error (dead code path since 2017)
- **api/web_routes**: REST API now requires `API_KEY` auth; magnet links validated with regex
- **server/config**: `--config` CLI flag now works (was dead — Settings loaded at import time)

#### High (crashes / memory leaks / race conditions)
- **core_tools**: `help()` renamed to `_help_tool()` (shadowed Python builtin)
- **system_management**: `psutil.disk_usage("/")` → platform-aware `C:\` on Windows
- **tv_integration_tools**: Episode tracker now persists state (was fully stateless, data lost)
- **piratebay_search/extended**: Hardcoded TPB domain → `settings.PIRATEBAY_BASE_URL`
- **settings**: Default port 8000 (forbidden) → **10910** (fleet-compliant); bind 0.0.0.0 → 127.0.0.1
- **torrent_management**: Poll task reference stored to prevent double-start leaks
- **post_processor**: `processed_hashes` set capped at 10k entries (was unbounded memory leak)
- **search_management**: `tv_shows` action defaults to `MeGusta` instead of `ASW`
- **agentic_workflow**: Infinite loop guard default fixed (`True` → `False`)
- **rtorrent_client + post_processor**: 14 instances `asyncio.get_event_loop()` → `asyncio.get_running_loop()`

#### Medium (logic / design)
- **post_processor**: Added `_processed_lock` for check/mark race condition
- **natural_language**: Empty query for "this week" → `"new"`; release group casing via lookup dict
- **api/web_routes**: Error codes use proper status (401/503) + `error_code` fields + CORS middleware
- **tv_nlp_tools**: Stop-word removal removed (was corrupting show titles like "Law and Order")
- **web_routes**: REST API uses singleton `get_rtorrent_client()` instead of creating per-request
- **workflow_management**: Workflow IDs include `secrets.token_hex(4)` suffix to prevent collisions
- **rtorrent_client**: `d.remove` (non-standard) → `d.close` only; lambda → direct arg pass
- **post_processor**: Dead XMLRPC call removed; duplicate `.mkv` fixed; unused param dropped
- **torrent_management**: TOCTOU race in `_get_post_processor` → `asyncio.Lock`
- **server/transport**: Event loop fallback for `asyncio.run()` inside existing loops; `MCP_PORT` validation

#### Docs / metadata
- Version unified to **3.0.0** across `__init__.py`, `settings.py`, `core_tools.py`, `system_management.py`
- FastMCP references updated 2.12 → 3.1 throughout
- `transport.py` docstring updated 2.14.4 → 3.1
- `_UvicornASGIApp` now handles startup errors with proper ASGI 500 response
- MCP path normalized to include leading `/`
- Stub `franchise`/`batch_series` workflows return `"queued_not_executing"` + clear warning
- `legal_management` "check" action now uses `country` parameter instead of hardcoded "austria"

#### Webapp
- **Torrent tables**: Both dashboard + status pages now render `state` column (stopped/downloading/seeding/hashing) with color-coded badges
- **Port conflict**: Frontend moved from 10909 (taken by speech-mcp) → 10911; backend 10910 registered in fleet port registry
- **Cleanup**: Removed dead `App.css` (Vite boilerplate, unused), removed dead `@tanstack/react-query` dep (never imported), removed `start.ps1.bak` clutter

#### Configuration & scraping
- **nyaa_search.py**: Hardcoded ASW username `"AkihitoSubsWeeklies"` → `settings.NYAA_ASW_USERNAME` (configurable via `.env`)
- **nyaa_search.py**: Dedup key `title` → `(title, size)` so different-resolution releases are not lost
- **piratebay_search.py**: Duplicated TV constants → imported from `services/__init__.py` with fallback
- **tv_integration_tools.py**: `"MeGusta" in group` → `== "MeGusta"` (exact match)
- **core_tools.py**: Fake `recent_activity` stubs → honest placeholder
- **annas_archive_search.py**: Added more CSS selectors for Anna's Archive search + detail page; title fallback to `<title>`
- **settings**: Added `NYAA_ASW_USERNAME`, `API_KEY`, `PIRATEBAY_BASE_URL` settings

#### Cross-connect: media service integration
- **New service** `media_integrator.py`: Plex/Jellyfin scan notification for direct rTorrent downloads
  - `scan_plex()` — refreshes Plex library sections (auto-discovers all or target specific)
  - `scan_jellyfin()` — triggers Jellyfin library scan (path-aware incremental or full refresh)
  - `notify_all()` — fires Plex + Jellyfin scans after post-processing
- **PostProcessor**: After successful file move, automatically calls `notify_all()` — results in response
- **`torrent_management(action="notify_media")`**: Manual trigger for Plex/Jellyfin scan
- **Design note**: *arr apps (Radarr/Sonarr) are NOT notified by rtorrent-mcp — *arr should be configured
  with rTorrent as a download client directly. *arr handles its own completion detection, import, and
  media server notification.
- **Settings**: `PLEX_URL`, `PLEX_TOKEN`, `JELLYFIN_URL`, `JELLYFIN_API_KEY` — all optional
- **Port registry**: Added missing `arr-mcp` entries (10938/10939) to WEBAPP_PORTS.md
- **Tests**: Added `test_media_integrator.py` (6 tests); Playwright e2e suite (11 tests) in `web_sota/e2e/app.spec.ts`
- **Docs**: Added `docs/ARR_RTORRENT_SETUP.md` — guide for configuring rTorrent as a download client in *arr apps (Radarr, Sonarr, Prowlarr)

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
