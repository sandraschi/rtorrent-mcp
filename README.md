# qBTMCP - qBittorrent MCP Server 🇦🇹🎌

FastMCP 2.1 compliant server for anime torrenting automation with Austrian legal compliance.

## Features 🎯

- **nyaa.si Anime Search**: Automated search with ASW release group prioritization
- **qBittorrent Integration**: Full Web UI API control (add/pause/resume/delete)
- **Austrian Legal Compliance**: Built-in legal risk assessment by country
- **Natural Language Commands**: Process Sandra's anime requests in English/German
- **Quality Scoring**: Intelligent ranking of releases by group reputation

## Quick Start 🚀

```bash
# Install dependencies
pip install -r requirements.txt

# Configure qBittorrent Web UI
# Tools → Options → Web UI → Enable Remote Control
# Default: localhost:8080, admin/adminadmin

# Start MCP server
python server.py
```

## Usage Examples 📺

### Anime Search
```python
# Search ASW Detective Conan 720p
await search_anime("Detective Conan", "720p", "ASW")

# Natural language commands
await sandra_anime_command("get me this weeks asw anime, 720p")
await sandra_anime_command("lade detective conan asw 720p")  # German
```

### qBittorrent Control
```python
# Add torrent
await add_torrent_qbt(magnet_link, category="anime")

# List torrents
await list_qbt_torrents()

# Pause/Resume
await pause_torrent(torrent_hash)
await resume_torrent(torrent_hash)
```

### Legal Compliance
```python
# Check legal status
await check_legal_status("austria")  # ✅ Safe for Sandra in Vienna
await check_legal_status("germany")  # 🚨 High risk, VPN mandatory
```

## Release Group Priorities 🏆

1. **ASW** (100pts) - Austrian preference
2. **SubsPlease** (90pts)
3. **Erai-raws** (85pts)
4. **EMBER** (80pts)
5. **Judas** (75pts)

## Austrian Context 🇦🇹

- **Legal Status**: Personal downloading generally tolerated
- **Sandra's Location**: Vienna, 9th district
- **Risk Assessment**: Safe for individual anime consumption
- **Language Support**: English + German commands

## Configuration ⚙️

Copy `.env.example` to `.env` and configure:

```env
QBITTORRENT_HOST=localhost
QBITTORRENT_PORT=8080
QBITTORRENT_USERNAME=admin
QBITTORRENT_PASSWORD=adminadmin
DEFAULT_RESOLUTION=720p
PREFERRED_RELEASE_GROUP=ASW
```

## Legal Disclaimer ⚖️

This tool is designed for Austrian legal context where personal downloading is generally tolerated. Users in other jurisdictions should research local copyright laws. High-risk countries (Germany, Japan) require additional precautions.

## Dependencies 📦

- FastMCP 2.1+ (MCP server framework)
- aiohttp (HTTP client)
- BeautifulSoup4 (HTML parsing)
- pydantic (Data validation)

## Author 👩‍💻

Sandra's Austrian Anime Automation 🇦🇹🎌

*"Sin temor y sin esperanza" - Practical automation without hype.*
