"""
Services module for rTorrent MCP Server

rTorrent Connection Architecture:
    We use crazymax/rtorrent-rutorrent Docker image which provides:
    - rTorrent (the actual torrent client)
    - ruTorrent (web UI)
    - nginx (XMLRPC proxy)

    Connection flow:
        MCP Server → HTTP/XMLRPC (port 12224) → nginx → Unix Socket → rTorrent

    The MCP server connects to http://localhost:12224/RPC2 using standard XMLRPC.
    nginx inside the container translates HTTP to the internal Unix socket.
"""

# Default rTorrent settings - connects to crazymax/rtorrent-rutorrent Docker container
DEFAULT_RTORRENT_HOST = "localhost"
DEFAULT_RTORRENT_PORT = 12224  # Maps to container port 8000 (nginx XMLRPC proxy)

# NYAA search defaults
PREFERRED_RELEASE_GROUPS = {"ASW": 50, "SubsPlease": 40, "Erai-raws": 30, "HorribleSubs": 20}
DEFAULT_RESOLUTION = "720p"
DEFAULT_RELEASE_GROUP = "ASW"

# The Pirate Bay TV search defaults
PREFERRED_TV_RELEASE_GROUPS = {"MeGusta": 50, "RARBG": 40, "EZTV": 35, "YIFY": 30, "YTS": 25}
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
    "australia": "medium",
}
