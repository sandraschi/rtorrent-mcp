# qBTMCP - qBittorrent MCP Server 🇦🇹🎌

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.10-brightgreen)](https://fastmcp.anthropic.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

FastMCP 2.10 compliant server for anime torrenting automation with Austrian legal compliance.

## Features 🎯

- **FastMCP 2.10 Compatible**: Latest standards and performance improvements
- **nyaa.si Anime Search**: Automated search with ASW release group prioritization
- **qBittorrent Integration**: Full Web UI API control (add/pause/resume/delete)
- **Austrian Legal Compliance**: Built-in legal risk assessment for Austrian users
- **Natural Language Commands**: Process Sandra's anime requests in English/German
- **Quality Scoring**: Intelligent ranking of releases by group reputation
- **Configuration Management**: Environment variables and .env file support
- **Comprehensive Testing**: Unit and integration tests for all components

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- qBittorrent with Web UI enabled
- (Optional) Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sandraschi/qbtmcp.git
   cd qbtmcp
   ```

2. **Set up a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   For development:
   ```bash
   pip install -r requirements.txt[dev]
   ```

### Configuration

1. **Configure qBittorrent Web UI**
   - Open qBittorrent
   - Go to Tools → Options → Web UI
   - Enable Web UI and set username/password
   - Default: http://localhost:8080, admin/adminadmin

2. **Create a `.env` file** (or set environment variables)
   ```env
   # qBittorrent settings
   QBITTORRENT_URL=http://localhost:8080
   QBITTORRENT_USERNAME=admin
   QBITTORRENT_PASSWORD=adminadmin
   
   # Nyaa.si settings
   NYAA_BASE_URL=https://nyaa.si
   
   # Application settings
   DEBUG=false
   LOG_LEVEL=INFO
   ```

### Running the Server

```bash
# Run with stdio transport (for Claude Desktop)
python server.py

# Or with HTTP transport
python server.py --transport http

# Custom config file
python server.py --config /path/to/config.env
```

## 📦 Development

### Testing
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=qbtmcp --cov-report=html
```

### Code Style
```bash
# Format code with black
black .

# Sort imports
isort .

# Type checking
mypy .
```

## 🎯 Features in Detail

### 🔍 Smart Anime Search
```python
# Basic search
await search_anime("Detective Conan", resolution="720p", group="ASW")

# Advanced search with filters
await search_anime(
    query="One Piece",
    resolution="1080p",
    group="Erai-raws",
    category="Anime",
    min_seeders=5
)
```

### 🎛️ qBittorrent Integration
```python
# Add torrent from magnet link
magnet = "magnet:?xt=urn:btih:..."
await add_torrent_qbt(magnet, category="anime", tags=["anime", "asw"])

# Monitor and manage downloads
await list_qbt_torrents(status="downloading")
await pause_torrent("torrent_hash")
await resume_torrent("torrent_hash")
await delete_torrent("torrent_hash", delete_files=True)

# Automatic management
await set_auto_management("torrent_hash", enable=True)
await set_sequential_download("torrent_hash", enable=True)
```

### 🇦🇹 Austrian Legal Compliance
```python
# Check if content is safe for Austria
is_safe = await check_austrian_legal_status(torrent_info)
if is_safe:
    await add_torrent_qbt(torrent_info["magnet"])
else:
    logger.warning("Content may not be legal in Austria")
```

### 🤖 Natural Language Processing
```python
# English commands
await process_command("Download the latest Detective Conan episode in 720p from ASW")

# German commands
await process_command("Lade die neueste Folge Detective Conan in 720p von ASW")

# Complex queries
await process_command("Find me the best quality of Attack on Titan, but nothing below 720p")
```

## 🔧 Configuration Options

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `QBITTORRENT_URL` | `http://localhost:8080` | qBittorrent Web UI URL |
| `QBITTORRENT_USERNAME` | `admin` | qBittorrent username |
| `QBITTORRENT_PASSWORD` | `adminadmin` | qBittorrent password |
| `NYAA_BASE_URL` | `https://nyaa.si` | Nyaa.si base URL |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `DEBUG` | `false` | Enable debug mode |
| `ALLOWED_CATEGORIES` | `["Anime"]` | Allowed content categories |
| `ALLOWED_RESOLUTIONS` | `["720p", "1080p"]` | Allowed video resolutions |
| `MAX_TORRENT_SIZE_GB` | `10` | Maximum allowed torrent size in GB |

## 📚 Documentation

### API Reference
For detailed API documentation, run the server and visit:
```
http://localhost:8000/docs
```

### Development
1. Install development dependencies:
   ```bash
   pip install -r requirements.txt[dev]
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Build documentation:
   ```bash
   mkdocs serve
   ```
   Then visit http://localhost:8001

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [qBittorrent](https://www.qbittorrent.org/) - The awesome torrent client
- [Nyaa.si](https://nyaa.si/) - For the anime torrents
- [FastMCP](https://fastmcp.anthropic.com) - The MCP framework

---

Made with ❤️ in Vienna, Austria

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
