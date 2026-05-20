"""
rtorrent_client.py - rTorrent XMLRPC client for RTorrent MCP Server
Austrian anime categorization and torrent management
"""

import asyncio
import logging
import xmlrpc.client
from typing import Any

from . import DEFAULT_RTORRENT_HOST, DEFAULT_RTORRENT_PORT

logger = logging.getLogger(__name__)


class RTorrentClient:
    """Async rTorrent XMLRPC client"""

    def __init__(self, host: str = DEFAULT_RTORRENT_HOST, port: int = DEFAULT_RTORRENT_PORT):
        self.host = host
        self.port = port
        self.server = None
        self.connected = False

    async def connect(self) -> bool:
        """Connect to rTorrent XMLRPC server"""
        try:
            if not self.server:
                self.server = xmlrpc.client.ServerProxy(f"http://{self.host}:{self.port}/RPC2")
            # Test connection
            await asyncio.get_running_loop().run_in_executor(None, self.server.system.listMethods)
            self.connected = True
            logger.info("Connected to rTorrent successfully")
            return True
        except Exception as e:
            url = f"http://{self.host}:{self.port}/RPC2"
            logger.error("rTorrent connection error: %s (tried %s)", e, url)
            self.connected = False
            return False

    async def get_torrents(self) -> list[dict[str, Any]]:
        """Get list of all torrents"""
        if not self.connected:
            await self.connect()

        try:
            loop = asyncio.get_running_loop()
            torrent_hashes = await loop.run_in_executor(None, self.server.download_list)

            torrents = []
            for hash_str in torrent_hashes:
                try:
                    info = await loop.run_in_executor(None, self.server.d.get_name, hash_str)
                    state = await loop.run_in_executor(None, self.server.d.get_state, hash_str)
                    size = await loop.run_in_executor(None, self.server.d.get_size_bytes, hash_str)
                    completed = await loop.run_in_executor(None, self.server.d.get_completed_bytes, hash_str)

                    torrents.append(
                        {
                            "hash": hash_str,
                            "name": info,
                            "state": state,
                            "size_bytes": size,
                            "completed_bytes": completed,
                            "progress": (completed / size) * 100 if size > 0 else 0,
                        }
                    )
                except Exception as e:
                    logger.warning(f"Error getting info for torrent {hash_str}: {e}")

            return torrents
        except Exception as e:
            logger.error(f"Error getting torrents: {e}")
            return []

    async def add_torrent(self, magnet_link: str, category: str = "anime") -> dict[str, Any]:
        """Add torrent from magnet link with Austrian anime categorization"""
        if not self.connected:
            await self.connect()

        try:
            loop = asyncio.get_running_loop()
            # rTorrent XMLRPC method is load.start (not load_start)
            await loop.run_in_executor(None, self.server.load.start, "", magnet_link)

            # Get hash from most recently added torrent
            await asyncio.sleep(1)  # Give it time to load
            torrents = await loop.run_in_executor(None, self.server.download_list)

            if torrents:
                # Get the last torrent (most recently added)
                hash_str = torrents[-1]
                # Set custom1 for category (rTorrent custom field)
                # rTorrent uses d.custom1.set method
                try:
                    await loop.run_in_executor(None, self.server.d.custom1.set, hash_str, category)
                except Exception as e:
                    logger.warning(f"Could not set category: {e}")
                    # Continue anyway - torrent was added successfully

                return {
                    "status": "success",
                    "hash": hash_str,
                    "message": "Torrent added successfully",
                    "category": category,
                    "magnet": magnet_link[:50] + "...",
                }
            else:
                return {"status": "error", "message": "Torrent added but could not retrieve hash"}
        except Exception as e:
            logger.error(f"Error adding torrent: {e}")
            return {"status": "error", "message": f"Error adding torrent: {str(e)}"}

    async def pause_torrent(self, torrent_hash: str) -> dict[str, Any]:
        """Pause a torrent"""
        if not self.connected:
            await self.connect()

        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self.server.d.pause, torrent_hash)
            return {"status": "success", "hash": torrent_hash, "action": "paused"}
        except Exception as e:
            return {"status": "error", "hash": torrent_hash, "message": str(e)}

    async def resume_torrent(self, torrent_hash: str) -> dict[str, Any]:
        """Resume a torrent"""
        if not self.connected:
            await self.connect()

        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self.server.d.resume, torrent_hash)
            return {"status": "success", "hash": torrent_hash, "action": "resumed"}
        except Exception as e:
            return {"status": "error", "hash": torrent_hash, "message": str(e)}

    async def delete_torrent(self, torrent_hash: str, delete_files: bool = False) -> dict[str, Any]:
        """Delete a torrent"""
        if not self.connected:
            await self.connect()

        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self.server.d.close, torrent_hash)
            if delete_files:
                await loop.run_in_executor(None, self.server.d.erase, torrent_hash)

            return {
                "status": "success",
                "hash": torrent_hash,
                "action": "deleted",
                "files_deleted": delete_files,
            }
        except Exception as e:
            return {"status": "error", "hash": torrent_hash, "message": str(e)}

    async def get_torrent_base_path(self, torrent_hash: str) -> str:
        """Get base path for torrent (directory or file path)"""
        if not self.connected:
            await self.connect()

        try:
            loop = asyncio.get_running_loop()
            base_path = await loop.run_in_executor(None, self.server.d.get_base_path, torrent_hash)
            return base_path or ""
        except Exception as e:
            logger.error(f"Error getting base path for {torrent_hash}: {e}")
            return ""

    async def get_torrent_directory(self, torrent_hash: str) -> str:
        """Get directory path for torrent"""
        if not self.connected:
            await self.connect()

        try:
            loop = asyncio.get_running_loop()
            directory = await loop.run_in_executor(None, self.server.d.get_directory, torrent_hash)
            return directory or ""
        except Exception as e:
            logger.error(f"Error getting directory for {torrent_hash}: {e}")
            return ""

    async def is_torrent_complete(self, torrent_hash: str) -> bool:
        """Check if torrent is 100% complete"""
        if not self.connected:
            await self.connect()

        try:
            loop = asyncio.get_running_loop()
            size_bytes = await loop.run_in_executor(None, self.server.d.get_size_bytes, torrent_hash)
            completed_bytes = await loop.run_in_executor(None, self.server.d.get_completed_bytes, torrent_hash)

            if size_bytes == 0:
                return False

            # Consider complete if >= 99.9% (handles rounding)
            return (completed_bytes / size_bytes) >= 0.999
        except Exception as e:
            logger.error(f"Error checking completion for {torrent_hash}: {e}")
            return False


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
        output_schema={
            "type": "object",
            "properties": {
                "torrents": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "hash": {"type": "string"},
                            "name": {"type": "string"},
                            "state": {"type": "string"},
                            "size_bytes": {"type": "number"},
                            "completed_bytes": {"type": "number"},
                            "progress": {"type": "number"},
                        },
                    },
                }
            },
        },
    )
    async def list_rt_torrents() -> dict:
        client = await get_rtorrent_client()
        torrents = await client.get_torrents()
        return {"torrents": torrents}

    @mcp.tool(
        name="pause_rt_torrent",
        description="""
        Pause a specific torrent in rTorrent.

        Args:
            torrent_hash (str): The hash of the torrent to pause

        Returns:
            dict: Result with status and torrent hash
        """,
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
        output_schema={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "host": {"type": "string"},
                "port": {"type": "number"},
                "connected": {"type": "boolean"},
                "message": {"type": "string"},
            },
        },
    )
    def get_rt_status() -> dict:
        global _rt_client
        if _rt_client is None:
            return {
                "status": "disconnected",
                "host": DEFAULT_RTORRENT_HOST,
                "port": DEFAULT_RTORRENT_PORT,
                "connected": False,
                "message": "Not connected to rTorrent yet",
            }
        else:
            return {
                "status": "connected" if _rt_client.connected else "disconnected",
                "host": DEFAULT_RTORRENT_HOST,
                "port": DEFAULT_RTORRENT_PORT,
                "connected": _rt_client.connected,
                "message": "Connected" if _rt_client.connected else "Disconnected",
            }

    @mcp.resource("rtorrent://config")
    def rtorrent_config() -> str:
        """rTorrent configuration information"""
        import json

        return json.dumps(
            {
                "default_host": DEFAULT_RTORRENT_HOST,
                "default_port": DEFAULT_RTORRENT_PORT,
                "default_category": "anime",
                "scgi_url": f"http://{DEFAULT_RTORRENT_HOST}:{DEFAULT_RTORRENT_PORT}/RPC2",
                "setup_instructions": [
                    "1. Install rTorrent with SCGI support",
                    "2. Configure SCGI port in .rtorrent.rc",
                    "3. Start rTorrent daemon",
                    "4. Ensure SCGI server is running on port 12224",
                ],
            }
        )
