"""
Tools package for rTorrent MCP Server - FastMCP 3.1

ARCHITECTURE:
- portmanteau/ : 6 consolidated tools
- agentic_workflow.py : agentic_rtorrent_workflow (sampling + tools)

PORTMANTEAU TOOLS (max 15, currently 6) plus agentic workflow:
1. torrent_management (12 actions): add, list, pause, resume, delete, status, info,
                       check_completed, process, start_processing, stop_processing, normalize
2. search_management (13 actions): anime, manga, japanese_tv, movies, tv_shows, tv_smart,
                      ebooks_annas, ebooks_pb, comics, annas_detail, imdb, imdb_search, tvdb
3. nlp_management (3 actions): command, parse, help
4. legal_management (4 actions): risk, check, advice, status
5. system_management (5 actions): help, status, health, info, analyze
6. workflow_management (8 actions): franchise, batch_series, status, cancel, list, estimate, queue, schedule

TOTAL: 45 actions consolidated into 6 portmanteau tools
"""

from .agentic_workflow import register_agentic_rtorrent_workflow
from .portmanteau import register_all_portmanteau_tools

__all__ = [
    "register_agentic_rtorrent_workflow",
    "register_all_portmanteau_tools",
    "register_all_tools",
]


def register_all_tools(mcp_server, settings, use_portmanteau: bool = True):
    """
    Register all MCP tools with the server.

    Args:
        mcp_server: FastMCP server instance
        settings: Application settings
        use_portmanteau: Ignored (always True). Portmanteau pattern is mandatory.
    """
    register_all_portmanteau_tools(mcp_server, settings)
    register_agentic_rtorrent_workflow(mcp_server)
