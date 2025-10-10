"""
Torrent tools for RTorrent MCP Server

MCP tools for rTorrent operations with Austrian anime categorization.
"""

import logging
from typing import List, Dict, Any
from fastmcp import FastMCP

from ..services.rtorrent_client_scgi import get_rtorrent_scgi_client

logger = logging.getLogger(__name__)


def register_torrent_tools(mcp: FastMCP, settings) -> None:
    """
    Register rTorrent management tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
        settings: Application settings
    """

    @mcp.tool(
        name="add_torrent",
        description="Add a torrent to rTorrent with Austrian anime categorization. "
                   "This tool allows you to add torrents via magnet links and automatically "
                   "categorizes them for Austrian legal compliance. "
                   "Args: magnet_link (str): The magnet URI of the torrent to add, "
                   "category (str): The category to assign (default: 'anime'). "
                   "Returns: dict with operation result and status details.",
    )
    async def add_torrent(magnet_link: str, category: str = "anime") -> dict:
        """Add torrent to rTorrent with Austrian anime categorization"""
        logger.info(f"Adding torrent with category '{category}': {magnet_link[:50]}...")
        try:
            client = await get_rtorrent_scgi_client()
            result = await client.add_torrent(magnet_link, category)
            if result.get("status") == "success":
                logger.info(f"Successfully added torrent: {result.get('hash', 'unknown')}")
            else:
                logger.warning(f"Failed to add torrent: {result.get('message', 'unknown error')}")
            return result
        except ConnectionError as e:
            logger.error(f"rTorrent connection error while adding torrent: {e}", exc_info=True)
            return {
                "status": "error",
                "message": "Failed to connect to rTorrent server. Please check if rTorrent is running.",
                "error_type": "connection_error",
                "details": str(e)
            }
        except TimeoutError as e:
            logger.error(f"Timeout error while adding torrent: {e}", exc_info=True)
            return {
                "status": "error",
                "message": "Operation timed out. rTorrent may be unresponsive.",
                "error_type": "timeout_error",
                "details": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error adding torrent: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to add torrent: {str(e)}",
                "error_type": "unexpected_error",
                "details": str(e)
            }

    @mcp.tool(
        name="list_torrents",
        description="List all torrents currently in rTorrent with their status. "
                   "Provides detailed information about each torrent including hash identifier, "
                   "name, state (active, paused, stopped), size and completion progress. "
                   "Returns: array of torrent objects with status details."
    )
    async def list_torrents() -> List[dict]:
        """List torrents in rTorrent"""
        try:
            client = await get_rtorrent_scgi_client()
            return await client.get_torrents()
        except Exception as e:
            logger.error(f"Error listing torrents: {e}")
            return [{"error": f"Failed to list torrents: {str(e)}"}]

    @mcp.tool(
        name="pause_torrent",
        description="Pause a specific torrent in rTorrent. "
                   "Args: torrent_hash (str): The hash identifier of the torrent to pause. "
                   "Returns: dict with operation status and torrent hash.",
    )
    async def pause_torrent(torrent_hash: str) -> dict:
        """Pause a torrent in rTorrent"""
        try:
            client = await get_rtorrent_scgi_client()
            return await client.pause_torrent(torrent_hash)
        except Exception as e:
            logger.error(f"Error pausing torrent {torrent_hash}: {e}")
            return {"status": "error", "hash": torrent_hash, "message": str(e)}

    @mcp.tool(
        name="resume_torrent",
        description="Resume a specific torrent in rTorrent. "
                   "Args: torrent_hash (str): The hash identifier of the torrent to resume. "
                   "Returns: dict with operation status and torrent hash."
    )
    async def resume_torrent(torrent_hash: str) -> dict:
        """Resume a torrent in rTorrent"""
        try:
            client = await get_rtorrent_scgi_client()
            return await client.resume_torrent(torrent_hash)
        except Exception as e:
            logger.error(f"Error resuming torrent {torrent_hash}: {e}")
            return {"status": "error", "hash": torrent_hash, "message": str(e)}

    @mcp.tool(
        name="delete_torrent",
        description="Delete a torrent from rTorrent with optional file deletion. "
                   "Args: torrent_hash (str): The hash identifier of the torrent to delete, "
                   "delete_files (bool): Whether to delete the downloaded files (default: false). "
                   "Returns: dict with operation status and deletion details."
    )
    async def delete_torrent(torrent_hash: str, delete_files: bool = False) -> dict:
        """Delete a torrent from rTorrent"""
        try:
            client = await get_rtorrent_scgi_client()
            return await client.delete_torrent(torrent_hash, delete_files)
        except Exception as e:
            logger.error(f"Error deleting torrent {torrent_hash}: {e}")
            return {"status": "error", "hash": torrent_hash, "message": str(e)}

    @mcp.tool(
        name="get_status",
        description="Get the current connection status of rTorrent. "
                   "Returns: dict with connection status, host, port, and status message."
    )
    async def get_status() -> dict:
        """Get rTorrent connection status"""
        try:
            client = await get_rtorrent_scgi_client()
            return await client.get_connection_info()
        except Exception as e:
            logger.error(f"Error getting rTorrent status: {e}")
            return {
                "status": "error",
                "message": f"Failed to get status: {str(e)}"
            }
