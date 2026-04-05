"""
Portmanteau tools for rTorrent MCP Server (FastMCP 3.x).

This package contains 6 consolidated action-based tools following FastMCP 2.13 best practices.
Each portmanteau tool replaces multiple individual tools with a single interface using action parameters.

PORTMANTEAU TOOLS (max 15, currently 6):
1. torrent_management - Torrent ops + post-processing (12 actions)
2. search_management - All search operations (13 actions)
3. nlp_management - Natural language processing (3 actions)
4. legal_management - Legal compliance (4 actions)
5. system_management - System operations (5 actions)
6. workflow_management - Complex multi-step workflows (8 actions)

PORTMANTEAU PATTERN RATIONALE:
- Prevents tool explosion (40+ tools → 6 tools)
- Improves discoverability by grouping related operations
- Reduces cognitive load when working with torrent/search tasks
- Enables consistent interface across all operations
- Follows FastMCP 2.13 best practices for feature-rich MCP servers
"""

from .legal_management import register_legal_management_tool
from .nlp_management import register_nlp_management_tool
from .search_management import register_search_management_tool
from .system_management import register_system_management_tool
from .torrent_management import register_torrent_management_tool
from .workflow_management import register_workflow_management_tool

__all__ = [
    "register_torrent_management_tool",
    "register_search_management_tool",
    "register_nlp_management_tool",
    "register_legal_management_tool",
    "register_system_management_tool",
    "register_workflow_management_tool",
    "register_all_portmanteau_tools",
]


def register_all_portmanteau_tools(mcp, settings) -> None:
    """
    Register all 6 portmanteau tools with the server.

    Args:
        mcp: FastMCP server instance
        settings: Application settings
    """
    register_torrent_management_tool(mcp, settings)
    register_search_management_tool(mcp, settings)
    register_nlp_management_tool(mcp, settings)
    register_legal_management_tool(mcp, settings)
    register_system_management_tool(mcp, settings)
    register_workflow_management_tool(mcp, settings)
