"""
rtorrent_client.py - rTorrent SCGI client for RTorrent MCP Server
Austrian anime categorization and torrent management
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
import xmlrpc.client
import socket

from . import (
    DEFAULT_RTORRENT_HOST,
    DEFAULT_RTORRENT_PORT
)

logger = logging.getLogger(__name__)

class RTorrentClient:
    """Async rTorrent SCGI client"""

    def __init__(self, host: str = DEFAULT_RTORRENT_HOST, port: int = DEFAULT_RTORRENT_PORT):
        self.host = host
        self.port = port
        self.server = None
        self.connected = False

    async def connect(self) -> bool:
        """Connect to rTorrent SCGI server"""
        try:
            if not self.server:
                self.server = xmlrpc.client.ServerProxy(f'http://{self.host}:{self.port}/RPC2')
            # Test connection
            await asyncio.get_event_loop().run_in_executor(None, self.server.system.listMethods)
            self.connected = True
            logger.info("Connected to rTorrent successfully")
            return True
        except Exception as e:
            logger.error(f"rTorrent connection error: {e}")
            self.connected = False
            return False

    async def get_torrents(self) -> List[Dict[str, Any]]:
        """Get list of all torrents"""
        if not self.connected:
            await self.connect()

        try:
            loop = asyncio.get_event_loop()
            torrent_hashes = await loop.run_in_executor(None, self.server.download_list)

            torrents = []
            for hash_str in torrent_hashes:
                try:
                    info = await loop.run_in_executor(None, self.server.d.get_name, hash_str)
                    state = await loop.run_in_executor(None, self.server.d.get_state, hash_str)
                    size = await loop.run_in_executor(None, self.server.d.get_size_bytes, hash_str)
                    completed = await loop.run_in_executor(None, self.server.d.get_completed_bytes, hash_str)

                    torrents.append({
                        "hash": hash_str,
                        "name": info,
                        "state": state,
                        "size_bytes": size,
                        "completed_bytes": completed,
                        "progress": (completed / size) * 100 if size > 0 else 0
                    })
                except Exception as e:
                    logger.warning(f"Error getting info for torrent {hash_str}: {e}")

            return torrents
        except Exception as e:
            logger.error(f"Error getting torrents: {e}")
            return []

    async def add_torrent(self, magnet_link: str, category: str = "anime") -> Dict[str, Any]:
        """Add torrent from magnet link with Austrian anime categorization"""
        if not self.connected:
            await self.connect()

        try:
            loop = asyncio.get_event_loop()
            hash_str = await loop.run_in_executor(None, self.server.load_start, magnet_link)

            # Set custom1 for category (rTorrent custom field)
            await loop.run_in_executor(None, self.server.d.set_custom1, hash_str, category)

            return {
                "status": "success",
                "hash": hash_str,
                "message": "Torrent added successfully",
                "category": category,
                "magnet": magnet_link[:50] + "..."
            }
        except Exception as e:
            logger.error(f"Error adding torrent: {e}")
            return {
                "status": "error",
                "message": f"Error adding torrent: {str(e)}"
            }

    async def pause_torrent(self, torrent_hash: str) -> Dict[str, Any]:
        """Pause a torrent"""
        if not self.connected:
            await self.connect()

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.server.d.pause, torrent_hash)
            return {"status": "success", "hash": torrent_hash, "action": "paused"}
        except Exception as e:
            return {"status": "error", "hash": torrent_hash, "message": str(e)}

    async def resume_torrent(self, torrent_hash: str) -> Dict[str, Any]:
        """Resume a torrent"""
        if not self.connected:
            await self.connect()

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.server.d.resume, torrent_hash)
            return {"status": "success", "hash": torrent_hash, "action": "resumed"}
        except Exception as e:
            return {"status": "error", "hash": torrent_hash, "message": str(e)}

    async def delete_torrent(self, torrent_hash: str, delete_files: bool = False) -> Dict[str, Any]:
        """Delete a torrent"""
        if not self.connected:
            await self.connect()

        try:
            loop = asyncio.get_event_loop()
            if delete_files:
                await loop.run_in_executor(None, self.server.d.erase, torrent_hash)
            else:
                await loop.run_in_executor(None, self.server.d.close, torrent_hash)
                await loop.run_in_executor(None, self.server.d.remove, torrent_hash)

            return {
                "status": "success",
                "hash": torrent_hash,
                "action": "deleted",
                "files_deleted": delete_files
            }
        except Exception as e:
            return {"status": "error", "hash": torrent_hash, "message": str(e)}

# Global client instance
_rt_client = None

async def get_rtorrent_client() -> RTorrentClient:
    """Get or create rTorrent client instance"""
    global _rt_client
    if _rt_client is None:
        _rt_client = RTorrentClient()
    return _rt_client

def register_rtorrent_tools(mcp):
    """Register rTorrent tools with FastMCP server"""

    @mcp.tool(
        name="add_torrent_rt",
        description="""
        Add a torrent to rTorrent with Austrian anime categorization.

        This tool allows you to add torrents via magnet links and automatically
        categorizes them for Austrian legal compliance.

        Args:
            magnet_link (str): The magnet URI of the torrent to add
            category (str): The category to assign (default: "anime")

        Returns:
            dict: Result of the operation with status and details
        """,
        inputSchema={
            "type": "object",
            "properties": {
                "magnet_link": {"type": "string", "description": "Magnet URI"},
                "category": {"type": "string", "description": "Torrent category", "default": "anime"}
            },
            "required": ["magnet_link"]
        }
    )
    async def add_torrent_rt(magnet_link: str, category: str = "anime") -> dict:
        client = await get_rtorrent_client()
        return await client.add_torrent(magnet_link, category)

    @mcp.tool(
        name="list_rt_torrents",
        description="""
        List all torrents currently in rTorrent with their status.

        Provides detailed information about each torrent including:
        - Hash identifier
        - Name
        - State (active, paused, stopped)
        - Size and completion progress

        Returns:
            list: List of torrent dictionaries
        """,
        outputSchema={
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "hash": {"type": "string"},
                    "name": {"type": "string"},
                    "state": {"type": "string"},
                    "size_bytes": {"type": "number"},
                    "completed_bytes": {"type": "number"},
                    "progress": {"type": "number"}
                }
            }
        }
    )
    async def list_rt_torrents() -> List[dict]:
        client = await get_rtorrent_client()
        return await client.get_torrents()

    @mcp.tool(
        name="pause_rt_torrent",
        description="""
        Pause a specific torrent in rTorrent.

        Args:
            torrent_hash (str): The hash of the torrent to pause

        Returns:
            dict: Result with status and torrent hash
        """,
        inputSchema={
            "type": "object",
            "properties": {
                "torrent_hash": {"type": "string", "description": "Torrent hash"}
            },
            "required": ["torrent_hash"]
        }
    )
    async def pause_torrent(torrent_hash: str) -> dict:
        client = await get_rtorrent_client()
        return await client.pause_torrent(torrent_hash)

    @mcp.tool(
        name="resume_rt_torrent",
        description="""
        Resume a specific torrent in rTorrent.

        Args:
            torrent_hash (str): The hash of the torrent to resume

        Returns:
            dict: Result with status and torrent hash
        """,
        inputSchema={
            "type": "object",
            "properties": {
                "torrent_hash": {"type": "string", "description": "Torrent hash"}
            },
            "required": ["torrent_hash"]
        }
    )
    async def resume_torrent(torrent_hash: str) -> dict:
        client = await get_rtorrent_client()
        return await client.resume_torrent(torrent_hash)

    @mcp.tool(
        name="delete_rt_torrent",
        description="""
        Delete a torrent from rTorrent with optional file deletion.

        Args:
            torrent_hash (str): The hash of the torrent to delete
            delete_files (bool): Whether to delete the downloaded files

        Returns:
            dict: Result with status, hash, and deletion details
        """,
        inputSchema={
            "type": "object",
            "properties": {
                "torrent_hash": {"type": "string", "description": "Torrent hash"},
                "delete_files": {"type": "boolean", "description": "Delete files", "default": False}
            },
            "required": ["torrent_hash"]
        }
    )
    async def delete_torrent(torrent_hash: str, delete_files: bool = False) -> dict:
        client = await get_rtorrent_client()
        return await client.delete_torrent(torrent_hash, delete_files)

    @mcp.tool(
        name="get_rt_status",
        description="""
        Get the current connection status of rTorrent.

        Returns:
            dict: Connection status and configuration details
        """,
        outputSchema={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "host": {"type": "string"},
                "port": {"type": "number"},
                "connected": {"type": "boolean"},
                "message": {"type": "string"}
            }
        }
    )
    def get_rt_status() -> dict:
        global _rt_client
        if _rt_client is None:
            return {
                "status": "disconnected",
                "host": DEFAULT_RTORRENT_HOST,
                "port": DEFAULT_RTORRENT_PORT,
                "connected": False,
                "message": "Not connected to rTorrent yet"
            }
        else:
            return {
                "status": "connected" if _rt_client.connected else "disconnected",
                "host": DEFAULT_RTORRENT_HOST,
                "port": DEFAULT_RTORRENT_PORT,
                "connected": _rt_client.connected,
                "message": "Connected" if _rt_client.connected else "Disconnected"
            }

    @mcp.resource("rtorrent://config")
    def rtorrent_config() -> str:
        """rTorrent configuration information"""
        import json
        return json.dumps({
            "default_host": DEFAULT_RTORRENT_HOST,
            "default_port": DEFAULT_RTORRENT_PORT,
            "default_category": "anime",
            "scgi_url": f"http://{DEFAULT_RTORRENT_HOST}:{DEFAULT_RTORRENT_PORT}/RPC2",
            "setup_instructions": [
                "1. Install rTorrent with SCGI support",
                "2. Configure SCGI port in .rtorrent.rc",
                "3. Start rTorrent daemon",
                "4. Ensure SCGI server is running on port 5000"
            ]
        })
