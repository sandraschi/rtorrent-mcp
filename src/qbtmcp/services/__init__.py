"""
Services module for RTorrent MCP Server
"""

# Default rTorrent settings
DEFAULT_RTORRENT_HOST = "localhost"
DEFAULT_RTORRENT_PORT = 12224  # Avoid ports ending in 00/000

# NYAA search defaults
PREFERRED_RELEASE_GROUPS = {
    "ASW": 50,
    "SubsPlease": 40,
    "Erai-raws": 30,
    "HorribleSubs": 20
}
DEFAULT_RESOLUTION = "720p"
DEFAULT_RELEASE_GROUP = "ASW"

# The Pirate Bay TV search defaults
PREFERRED_TV_RELEASE_GROUPS = {
    "MeGusta": 50,
    "RARBG": 40,
    "EZTV": 35,
    "YIFY": 30,
    "YTS": 25
}
DEFAULT_TV_RESOLUTION = "1080p"
DEFAULT_TV_RELEASE_GROUP = "MeGusta"

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
