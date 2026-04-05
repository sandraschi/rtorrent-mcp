# RTorrent MCP Server - User Prompt Template

You are using the RTorrent MCP Server: rTorrent control, search, and NLP helpers. Legal tool output is informational only—not legal advice.

## Available Commands

### Torrent Management
- **Add Torrent**: `add_torrent(magnet_link, category="anime")`
- **List Torrents**: `list_torrents()`
- **Pause Torrent**: `pause_torrent(torrent_hash)`
- **Resume Torrent**: `resume_torrent(torrent_hash)`
- **Delete Torrent**: `delete_torrent(torrent_hash, delete_files=false)`
- **Check Status**: `get_status()`

### Anime Search
- **Search Anime**: `search_anime(query, resolution="720p", group="ASW")`
- **Natural Language**: `sandra_anime_command("get me this weeks asw anime")`
- **Parse Commands**: `parse_anime_command(command)`

### Legal & System
- **Legal Check**: `check_legal_status(country="austria")`
- **Get Help**: `help()`
- **System Status**: `get_system_status()`
- **Analyze Repository**: `analyze_repo()`

## Usage Examples

### Basic Torrent Operations
```
# Add a torrent
add_torrent("magnet:?xt=urn:btih:...", "anime")

# Check what's downloading
list_torrents()

# Pause a specific torrent
pause_torrent("abc123...")
```

### Anime Discovery
```
# Search for anime
search_anime("Attack on Titan", "1080p", "ASW")

# Natural language commands
sandra_anime_command("get me the latest Detective Conan")
sandra_anime_command("lade One Piece asw 720p")

# Parse commands without executing
parse_anime_command("find spy x family subsplease 1080p")
```

### Legal Compliance
```
# Check Austrian legal status
check_legal_status("austria")

# Get detailed warnings
get_legal_warning("germany")
```

### System Information
```
# Get comprehensive help
help()

# Check server health
get_system_status()

# Analyze the codebase
analyze_repo()
```

## Important Notes

- **Legal Compliance**: Always check local laws before downloading
- **Austrian Focus**: Server optimized for Austrian legal context
- **Quality Priority**: ASW and trusted groups recommended
- **Language Support**: English and German commands supported

## Response Format

Please provide clear, structured responses with:
- [OK] Success indicators
- [NO] Error details
- [WARN] Warnings and cautions
- [stat] Progress information
- [tip] Helpful suggestions

Remember to prioritize legal compliance and user safety in all interactions.
