"""
Services module for RTorrent MCP Server
"""

# Default rTorrent settings
DEFAULT_RTORRENT_HOST = "localhost"
DEFAULT_RTORRENT_PORT = 5000

# NYAA search defaults
PREFERRED_RELEASE_GROUPS = {
    "ASW": 50,
    "SubsPlease": 40,
    "Erai-raws": 30,
    "HorribleSubs": 20
}
DEFAULT_RESOLUTION = "720p"
DEFAULT_RELEASE_GROUP = "ASW"

# Legal risk levels by country
LEGAL_RISK = {
    "austria": "safe",
    "germany": "high",
    "japan": "criminal",
    "usa": "medium",
    "uk": "medium",
    "france": "high",
    "canada": "medium",
    "australia": "medium"
}
