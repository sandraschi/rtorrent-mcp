# RTorrent MCP Server - Status Report

**Date:** 2026-05-10  
**Project:** rtorrent_mcp (RTorrent MCP Server)  
**Version:** 3.0.1  
**Status:** Active development (bugbash complete, production-capable)

---

## Executive Summary

FastMCP 3.1 MCP server for rTorrent automation and multi-source search, with AT-oriented legal
risk hints in tool outputs. Two bugbash passes completed 2026-05-10.

**Current state:**
- [OK] Core torrent + search paths stable with race-condition fixes
- [OK] REST API secured (API_KEY auth, CORS, input validation, sanitized errors)
- [OK] Fleet port compliance (10910 backend, 10911 frontend, registered)
- [OK] Webapp torrent tables: state column (stopped/downloading/seeding/hashing) with color badges
- [OK] ASW username configurable (NYAA_ASW_USERNAME), PirateBay constants deduplicated
- [OK] Anna's Archive scraping: expanded CSS selectors, dedup key includes size
- [OK] Media service cross-connect: `MediaIntegrator` notifies Plex/Jellyfin after post-processing (no *arr — they manage rTorrent directly)
- [WARN] Test coverage below 80% target
- [WARN] Workflow management `franchise`/`batch_series` are stubs (queued, not executing)
- [WARN] Settings page is cosmetic placeholder (not wired to backend)

---

## Project Metrics

### Code statistics
- **MCP surface:** Portmanteau + agentic tools (exact count depends on server version/mode)
- **Tests:** See `tests/`; run `uv run pytest` for current counts
- **Coverage:** Run `uv run pytest --cov=src/rtorrent_mcp` for current %
- **Checklist:** `docs/MCP_PRODUCTION_CHECKLIST.md` is a self-audit aid, not external certification

### Recent activity
- Refresh this section from `git log` / your tracker when updating the report

---

## Completed Features

### 1. Core Infrastructure
- [OK] **FastMCP 3.1**: Portmanteau tools, sampling, skills provider, agentic workflow
- [OK] **rTorrent Integration**: HTTP XMLRPC via nginx (port 12224→container 8000)
- [OK] **Windows Compatibility**: No Unix socket dependencies; `disk_usage` platform-aware
- [OK] **Docker Support**: docker-compose.yml with rTorrent + ruTorrent
- [OK] **Configuration Management**: Environment variables, `.env` support, `--config` flag works
- [OK] **REST API**: Auth (API_KEY), CORS, input validation, error codes

### 2. Search Capabilities
- [OK] **nyaa.si Anime Search**: ASW release group prioritization
- [OK] **The Pirate Bay TV Search**: MeGusta release group prioritization
- [OK] **Anna's Archive search**: Ebook and paper search (via public index; size varies)
- [OK] **YTS Movie Search**: Movie torrent search
- [OK] **Extended Search Tools**: Advanced filtering and quality scoring

### 3. Torrent Management
- [OK] **Add Torrents**: Magnet link support with categorization
- [OK] **List Torrents**: Status monitoring and filtering
- [OK] **Pause/Resume**: Torrent control operations
- [OK] **Delete Torrents**: With optional file deletion
- [OK] **Status Monitoring**: Connection health checks

### 4. Natural language processing
- [OK] **Anime NLP**: English/German command parsing where implemented
- [OK] **TV show commands**: Episode parsing (e.g. S28E03)
- [OK] **Command parsing**: Heuristic query extraction
- [OK] **Austrian context**: Legal risk messaging (not legal advice)

### 5. Legal Compliance
- [OK] **Austrian Legal Framework**: Risk assessment for Austria
- [OK] **Country-Specific Warnings**: Legal status by jurisdiction
- [OK] **Release Group Prioritization**: ASW (anime), MeGusta (TV)
- [OK] **Content Categorization**: Automatic anime categorization

### 6. System Tools
- [OK] **Multilevel Help System**: Basic/intermediate/advanced/expert
- [OK] **System status**: Health/status endpoints and tool actions
- [OK] **Repo/workspace helpers**: Optional analysis actions where implemented
- [OK] **Validation Tools**: rTorrent setup validation

---

## New Features (In Development)

### 1. Post-Processing System
**Status:** [OK] Implemented

**Capabilities:**
- Automatic completion detection (polling)
- Torrent removal after completion
- Filename normalization (removes release group tags)
- Ingestion folder management (anime/TV/movies)
- Media service notification: **Radarr**, **Sonarr**, **Plex**, **Jellyfin** (via `MediaIntegrator`)

**Files:**
- `src/rtorrent_mcp/services/post_processor.py`
- `src/rtorrent_mcp/services/media_integrator.py`
- `src/rtorrent_mcp/tools/post_processing_tools.py`
- `docs/POST_PROCESSING_SETUP.md`

### 2. Extended Search Services
**Status:** [OK] Implemented, [WARN] Needs testing

**New Search Engines:**
- **Anna's Archive**: Ebook and academic paper search
- **Extended Nyaa Search**: Advanced anime filtering
- **Extended Pirate Bay Search**: Enhanced TV show search
- **YTS Search**: Movie torrent search

**Files:**
- `src/rtorrent_mcp/services/annas_archive_search.py`
- `src/rtorrent_mcp/services/nyaa_extended_search.py`
- `src/rtorrent_mcp/services/piratebay_extended_search.py`
- `src/rtorrent_mcp/services/yts_search.py`

### 3. Metadata Service
**Status:** [OK] Implemented, [WARN] Needs testing

**Capabilities:**
- IMDb metadata retrieval
- TVDB metadata support
- Metadata enrichment for downloads

**Files:**
- `src/rtorrent_mcp/services/metadata_service.py`

---

## [WARN] Areas Requiring Attention

### 1. Test Coverage
**Current:** Below 80% target
**Target:** 80% line coverage

**Action Items:**
- [ ] Add unit tests for post-processing service
- [ ] Add unit tests for extended search services
- [ ] Add unit tests for metadata service
- [ ] Increase integration test coverage
- [ ] Add tests for error handling paths

### 2. Workflow Stubs
**Status:** `franchise` and `batch_series` actions queue workflows but do not execute downloads.
The `_execute_franchise_workflow` function is not yet implemented.

### 3. GitHub Actions
**Status:** [WARN] Verify all GitHub Actions workflows pass after bugbash changes.

---

## Performance Metrics

### Search Performance
- **ASW Search**: Finds ASW releases consistently (1080p fallback working)
- **MeGusta Search**: Query matching filter working correctly
- **Search Depth**: Top 50 results processed
- **Filtering**: Strict group filtering when requested

### Reliability
- [OK] No AF_UNIX errors (Windows compatible)
- [OK] Robust HTML parsing with fallbacks
- [OK] Error handling for network issues
- [OK] User-Agent headers prevent blocking

### Code Quality
- [OK] Type hints throughout codebase
- [OK] Comprehensive error handling with error_code fields
- [OK] Structured logging (%s format, not f-strings)
- [OK] FastMCP 3.1 compliant (portmanteau tools, sampling, skills, agentic workflow)
- [OK] PowerShell-first (Windows compatibility)
- [OK] No deprecated `asyncio.get_event_loop()` — migrated to `asyncio.get_running_loop()`
- [OK] REST API: auth, CORS, input validation, sanitized error messages

---

## Next Steps

### Immediate (High Priority)
1. **Increase Test Coverage**
   - Target: 80% line coverage
   - Focus on new services (post-processing, extended search, metadata)
   - Add integration tests for complete workflows

2. **Commit Pending Changes**
   - Review all modified and untracked files
   - Create feature branch for new functionality
   - Commit with descriptive messages

3. **Verify CI/CD**
   - Check GitHub Actions status
   - Fix any failing tests
   - Ensure automated quality checks pass

### Short Term (Medium Priority)
1. **Documentation Updates**
   - Update README with new features
   - Add usage examples for post-processing
   - Document extended search capabilities

2. **Integration Testing**
   - Test post-processing with real downloads
   - Verify metadata service integration
   - Test extended search tools end-to-end

3. **Performance Optimization**
   - Profile search operations
   - Optimize HTML parsing
   - Cache frequently accessed data

### Long Term (Low Priority)
1. **Episode Tracking Database**
   - Track downloaded episodes
   - Auto-download new episodes
   - Episode notification system

2. **Media Dashboard**
   - See `docs/MEDIA_DASHBOARD_PLAN.md` for details
   - Web interface for monitoring
   - Download statistics and analytics

3. **Multi-Group Search**
   - Search multiple groups simultaneously
   - Quality comparison across groups
   - User-configurable preferences

---

## Architecture Overview

### Directory Structure
```
src/rtorrent_mcp/
├── api/                    # API layer (future)
├── config/                 # Configuration management
│   └── settings.py        # Pydantic settings
├── models/                 # Data models (future)
├── services/              # Business logic services
│   ├── rtorrent_client.py # rTorrent XMLRPC client
│   ├── nyaa_search.py     # Basic nyaa.si search
│   ├── nyaa_extended_search.py  # Extended search
│   ├── piratebay_search.py      # Basic Pirate Bay search
│   ├── piratebay_extended_search.py  # Extended search
│   ├── annas_archive_search.py # Anna's Archive search
│   ├── yts_search.py      # YTS movie search
│   ├── metadata_service.py      # IMDb/TVDB metadata
│   ├── post_processor.py  # Post-processing service
│   ├── media_integrator.py # Media service notification (*arr, Plex, Jellyfin)
│   ├── natural_language.py      # NLP for anime
│   ├── tv_nlp_tools.py    # NLP for TV shows
│   └── legal_compliance.py      # Legal framework
├── tools/                  # MCP tool definitions
│   ├── torrent_tools.py   # Torrent management
│   ├── search_tools.py     # Search operations
│   ├── post_processing_tools.py  # Post-processing
│   ├── nlp_tools.py       # Natural language
│   ├── legal_tools.py     # Legal compliance
│   └── system_tools.py    # System operations
├── utils/                  # Utility functions
└── server.py              # FastMCP server entry point
```

### Tool Distribution (Portmanteau)
- **6 Portmanteau Tools + 1 Agentic Workflow** (45 total actions)
- **Torrent Management** (13 actions): add, list, pause, resume, delete, status, info, notify_media, check_completed, process, start_processing, stop_processing, normalize
- **Search Management** (13 actions): anime, manga, japanese_tv, movies, tv_shows, tv_smart, ebooks_annas, ebooks_pb, comics, annas_detail, imdb, imdb_search, tvdb
- **NLP Management** (3 actions): command, parse, help
- **Legal Management** (4 actions): risk, check, advice, status
- **System Management** (5 actions): help, status, health, info, analyze
- **Workflow Management** (8 actions): franchise, batch_series, status, cancel, list, estimate, queue, schedule

---

## Security Status

### Security Measures
- [OK] No hardcoded credentials
- [OK] Environment variable configuration
- [OK] Input validation on all tool parameters + API endpoints
- [OK] REST API: Bearer/X-API-Key auth when API_KEY is set
- [OK] Magnet link format validation via regex
- [OK] Error messages sanitized (no internal path/stack leakage)
- [OK] OMDb API over HTTPS (was HTTP)
- [OK] User-Agent headers prevent blocking
- [OK] Dependency scanning configured (bandit, safety)

### Security Tools
- **Bandit:** Security vulnerability scanner
- **Safety:** Dependency vulnerability scanner
- **DefusedXML:** Safe XML parsing

---

## Documentation Status

### Existing Documentation
- [OK] **README.md**: Setup and usage
- [OK] **CHANGELOG.md**: Version history
- [OK] **CONTRIBUTING.md**: Contribution guidelines
- [OK] **SECURITY.md**: Security policy
- [OK] **PRD.md**: Product requirements document
- [OK] **STATUS_REPORT.md**: This document
- [OK] **POST_PROCESSING_SETUP.md**: Post-processing guide
- [OK] **RTORRENT_SETUP.md**: rTorrent installation guide
- [OK] **TROUBLESHOOTING.md**: Common issues and solutions

### Documentation Gaps
- [WARN] Extended search tools usage examples
- [WARN] Metadata service integration guide
- [WARN] Media dashboard documentation (planned)
- [WARN] API reference documentation

---

## Success Metrics

### Achievements
- [OK] **FastMCP 3.x** baseline with portmanteau + sampling/agentic paths (see CHANGELOG)
- [OK] **Windows-first** docs and scripts where applicable
- [OK] **Multi-source search**: Nyaa, TPB, YTS, Anna’s Archive, etc. (see code and README)
- [OK] **Legal hints**: Jurisdiction-oriented messaging in tools

### Quality indicators
- [OK] Type hints and Ruff in CI
- [OK] Structured logging
- [OK] Docs: README, setup guides, PRD

---

## Notes

### Austrian Legal Compliance
- All releases categorized as "anime" for Austrian legal compliance
- Focus on specific release groups (ASW, MeGusta) preferred in Austria
- No illegal content promotion - tools are for personal use only
- Legal warnings provided for high-risk countries

### Release Groups
- **ASW (AkihitoSubsWeeklies)**: Preferred for anime, often 1080p HEVC x265
- **MeGusta**: Often used for TV-oriented search defaults in this project

### Episode Format Standards
- **S28E03** = Season 28, Episode 03 (standard format)
- Supported in both anime and TV searches
- Used for episode tracking and filtering

---

## Conclusion

Production-capable rTorrent MCP server with 6 portmanteau tools, agentic workflow (FastMCP 3.1),
multi-source search, post-processing, and AT-oriented legal hints. Two bugbash passes completed
2026-05-10 addressing critical (crashes, security), high (memory leaks, race conditions),
medium (logic, design), and minor (config, scraping) issues.

Known gaps: test coverage below target, workflow stubs (franchise/batch_series not executing),
settings page is cosmetic, settings page unwired.

**Status:** Active development — version 3.0.1

---

*Updated: 2026-05-10*  
*Project: rtorrent_mcp (RTorrent MCP Server)*  
*Version: 3.0.1*
