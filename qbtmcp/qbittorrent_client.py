"""
qbittorrent_client.py - qBittorrent Web UI API client for qBTMCP
Austrian anime categorization and torrent management
"""

import logging
from typing import List, Dict, Any, Optional
import aiohttp
import json

from . import (
    DEFAULT_QBITTORRENT_HOST, 
    DEFAULT_QBITTORRENT_PORT, 
    DEFAULT_QBITTORRENT_USERNAME, 
    DEFAULT_QBITTORRENT_PASSWORD
)

logger = logging.getLogger(__name__)

class QBittorrentClient:
    """Async qBittorrent Web UI API client"""
    
    def __init__(self, host: str = DEFAULT_QBITTORRENT_HOST, port: int = DEFAULT_QBITTORRENT_PORT,
                 username: str = DEFAULT_QBITTORRENT_USERNAME, password: str = DEFAULT_QBITTORRENT_PASSWORD):
        self.base_url = f"http://{host}:{port}"
        self.username = username
        self.password = password
        self.session = None
        self.authenticated = False
    
    async def connect(self) -> bool:
        """Connect and authenticate with qBittorrent"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            login_url = f"{self.base_url}/api/v2/auth/login"
            login_data = {
                "username": self.username,
                "password": self.password
            }
            
            async with self.session.post(login_url, data=login_data) as response:
                if response.status == 200:
                    result = await response.text()
                    if result == "Ok.":
                        self.authenticated = True
                        logger.info("Connected to qBittorrent successfully")
                        return True
                    else:
                        logger.error(f"qBittorrent login failed: {result}")
                        return False
                else:
                    logger.error(f"qBittorrent connection failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"qBittorrent connection error: {e}")
            return False
    
    async def get_torrents(self) -> List[Dict[str, Any]]:
        """Get list of all torrents"""
        if not self.authenticated:
            await self.connect()
        
        try:
            url = f"{self.base_url}/api/v2/torrents/info"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get torrents: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting torrents: {e}")
            return []
    
    async def add_torrent(self, magnet_link: str, category: str = "anime") -> Dict[str, Any]:
        """Add torrent from magnet link with Austrian anime categorization"""
        if not self.authenticated:
            await self.connect()
        
        try:
            url = f"{self.base_url}/api/v2/torrents/add"
            data = {
                "urls": magnet_link,
                "category": category,
                "autoTMM": "false"  # Disable automatic torrent management
            }
            
            async with self.session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.text()
                    return {
                        "status": "success",
                        "message": result if result else "Torrent added successfully",
                        "category": category,
                        "magnet": magnet_link[:50] + "..."
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Failed to add torrent: {response.status}"
                    }
        except Exception as e:
            logger.error(f"Error adding torrent: {e}")
            return {
                "status": "error",
                "message": f"Error adding torrent: {str(e)}"
            }
    
    async def pause_torrent(self, torrent_hash: str) -> Dict[str, Any]:
        """Pause a torrent"""
        if not self.authenticated:
            await self.connect()
        
        try:
            url = f"{self.base_url}/api/v2/torrents/pause"
            data = {"hashes": torrent_hash}
            
            async with self.session.post(url, data=data) as response:
                if response.status == 200:
                    return {"status": "success", "hash": torrent_hash, "action": "paused"}
                else:
                    return {"status": "error", "hash": torrent_hash, "message": f"Failed: {response.status}"}
        except Exception as e:
            return {"status": "error", "hash": torrent_hash, "message": str(e)}
    
    async def resume_torrent(self, torrent_hash: str) -> Dict[str, Any]:
        """Resume a torrent"""
        if not self.authenticated:
            await self.connect()
        
        try:
            url = f"{self.base_url}/api/v2/torrents/resume"
            data = {"hashes": torrent_hash}
            
            async with self.session.post(url, data=data) as response:
                if response.status == 200:
                    return {"status": "success", "hash": torrent_hash, "action": "resumed"}
                else:
                    return {"status": "error", "hash": torrent_hash, "message": f"Failed: {response.status}"}
        except Exception as e:
            return {"status": "error", "hash": torrent_hash, "message": str(e)}
    
    async def delete_torrent(self, torrent_hash: str, delete_files: bool = False) -> Dict[str, Any]:
        """Delete a torrent"""
        if not self.authenticated:
            await self.connect()
        
        try:
            url = f"{self.base_url}/api/v2/torrents/delete"
            data = {
                "hashes": torrent_hash,
                "deleteFiles": "true" if delete_files else "false"
            }
            
            async with self.session.post(url, data=data) as response:
                if response.status == 200:
                    return {
                        "status": "success", 
                        "hash": torrent_hash, 
                        "action": "deleted",
                        "files_deleted": delete_files
                    }
                else:
                    return {"status": "error", "hash": torrent_hash, "message": f"Failed: {response.status}"}
        except Exception as e:
            return {"status": "error", "hash": torrent_hash, "message": str(e)}
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()

# Global client instance
_qbt_client = None

async def get_qbittorrent_client() -> QBittorrentClient:
    """Get or create qBittorrent client instance"""
    global _qbt_client
    if _qbt_client is None:
        _qbt_client = QBittorrentClient()
    return _qbt_client

def register_qbittorrent_tools(mcp):
    """Register qBittorrent tools with FastMCP server"""
    
    @mcp.tool()
    async def add_torrent_qbt(magnet_link: str, category: str = "anime") -> dict:
        """Add torrent to qBittorrent with Austrian anime categorization
        
        Args:
            magnet_link: Magnet URI to add
            category: Torrent category (anime, movies, etc)
        """
        client = await get_qbittorrent_client()
        return await client.add_torrent(magnet_link, category)
    
    @mcp.tool()
    async def list_qbt_torrents() -> List[dict]:
        """List torrents in qBittorrent"""
        client = await get_qbittorrent_client()
        return await client.get_torrents()
    
    @mcp.tool()
    async def pause_torrent(torrent_hash: str) -> dict:
        """Pause a torrent in qBittorrent"""
        client = await get_qbittorrent_client()
        return await client.pause_torrent(torrent_hash)
    
    @mcp.tool()
    async def resume_torrent(torrent_hash: str) -> dict:
        """Resume a torrent in qBittorrent"""
        client = await get_qbittorrent_client()
        return await client.resume_torrent(torrent_hash)
    
    @mcp.tool()
    async def delete_torrent(torrent_hash: str, delete_files: bool = False) -> dict:
        """Delete a torrent from qBittorrent
        
        Args:
            torrent_hash: Hash of the torrent to delete
            delete_files: Whether to delete downloaded files as well
        """
        client = await get_qbittorrent_client()
        return await client.delete_torrent(torrent_hash, delete_files)
    
    @mcp.tool()
    def get_qbt_status() -> dict:
        """Get qBittorrent connection status"""
        global _qbt_client
        if _qbt_client is None:
            return {
                "status": "disconnected",
                "host": DEFAULT_QBITTORRENT_HOST,
                "port": DEFAULT_QBITTORRENT_PORT,
                "message": "Not connected to qBittorrent yet"
            }
        else:
            return {
                "status": "connected" if _qbt_client.authenticated else "disconnected",
                "host": DEFAULT_QBITTORRENT_HOST,
                "port": DEFAULT_QBITTORRENT_PORT,
                "authenticated": _qbt_client.authenticated
            }
    
    @mcp.resource("qbittorrent://config")
    def qbittorrent_config() -> str:
        """qBittorrent configuration information"""
        return json.dumps({
            "default_host": DEFAULT_QBITTORRENT_HOST,
            "default_port": DEFAULT_QBITTORRENT_PORT,
            "default_category": "anime",
            "web_ui_url": f"http://{DEFAULT_QBITTORRENT_HOST}:{DEFAULT_QBITTORRENT_PORT}",
            "setup_instructions": [
                "1. Open qBittorrent",
                "2. Go to Tools → Options → Web UI",
                "3. Enable 'Remote Control'",
                "4. Set port to 8080 (default)",
                "5. Set username/password (default: admin/adminadmin)"
            ]
        })
