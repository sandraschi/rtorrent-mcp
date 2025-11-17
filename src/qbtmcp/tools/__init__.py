"""
Tools package for RTorrent MCP Server

This package contains all MCP tool definitions, organized by functionality.
Each tool file contains self-documenting MCP tools with proper schemas.
"""

# Import TV-specific tools
from ..services.piratebay_search import register_tv_search_tools
from ..services.tv_integration_tools import register_tv_integration_tools
from ..services.tv_nlp_tools import register_tv_nlp_tools
from .legal_tools import register_legal_tools
from .nlp_tools import register_nlp_tools
from .search_tools import register_search_tools
from .system_tools import register_system_tools
from .torrent_tools import register_torrent_tools

__all__ = [
    "register_torrent_tools",
    "register_search_tools",
    "register_legal_tools",
    "register_nlp_tools",
    "register_system_tools",
    "register_tv_search_tools",
    "register_tv_nlp_tools",
    "register_tv_integration_tools"
]

def register_all_tools(mcp_server, settings):
    """
    Register all MCP tools with the server.

    Args:
        mcp_server: FastMCP server instance
        settings: Application settings
    """
    register_torrent_tools(mcp_server, settings)
    register_search_tools(mcp_server, settings)
    register_legal_tools(mcp_server, settings)
    register_nlp_tools(mcp_server, settings)
    register_system_tools(mcp_server, settings)

    # Register TV-specific tools
    register_tv_search_tools(mcp_server)
    register_tv_nlp_tools(mcp_server)
    register_tv_integration_tools(mcp_server)
