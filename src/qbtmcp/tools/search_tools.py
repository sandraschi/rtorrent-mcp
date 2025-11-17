"""
Search tools for RTorrent MCP Server

MCP tools for anime search and discovery via NYAA.si
"""

import logging

from fastmcp import FastMCP

from ..services.nyaa_search import search_nyaa_anime

logger = logging.getLogger(__name__)


def register_search_tools(mcp: FastMCP, settings) -> None:
    """
    Register anime search tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
        settings: Application settings
    """

    @mcp.tool(
        name="search_anime",
        description="Search nyaa.si for anime releases with Austrian preferences. "
                   "This tool searches for anime torrents on nyaa.si with intelligent scoring "
                   "based on Austrian legal requirements and preferred release groups. "
                   "Args: query (str): Anime name to search for, "
                   "resolution (str): Preferred resolution (default: '720p'), "
                   "group (str): Release group preference (default: 'ASW'). "
                   "Returns: array of anime releases with quality scoring and torrent details."
    )
    async def search_anime(query: str, resolution: str = "720p", group: str = "ASW") -> list[dict]:
        """Search nyaa.si for anime releases with Austrian preferences"""
        try:
            return await search_nyaa_anime(query, resolution, group)
        except Exception as e:
            logger.error(f"Error searching anime '{query}': {e}")
            return [{"error": f"Search failed: {str(e)}"}]
