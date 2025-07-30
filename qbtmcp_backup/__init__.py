"""
qBTMCP - qBittorrent MCP Server Package
FastMCP 2.1 compliant anime torrenting automation with Austrian legal compliance
"""

__version__ = "1.0.0"
__author__ = "Sandra's Austrian Anime Automation 🇦🇹🎌"
__description__ = "qBittorrent automation with nyaa.si anime search and Austrian legal compliance"

# Austrian legal compliance mapping
LEGAL_RISK = {
    "austria": "safe",
    "germany": "high", 
    "japan": "criminal",
    "us": "medium",
    "uk": "medium"
}

# Default anime preferences (Austrian context)
DEFAULT_RESOLUTION = "720p"
DEFAULT_RELEASE_GROUP = "ASW"
PREFERRED_RELEASE_GROUPS = {
    "ASW": 100,
    "SubsPlease": 90,
    "Erai-raws": 85,
    "EMBER": 80,
    "Judas": 75
}

# qBittorrent default connection settings
DEFAULT_QBITTORRENT_HOST = "localhost"
DEFAULT_QBITTORRENT_PORT = 8080
DEFAULT_QBITTORRENT_USERNAME = "admin"
DEFAULT_QBITTORRENT_PASSWORD = "adminadmin"
