"""
Unit tests for RTorrent client
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from src.qbtmcp.services.rtorrent_client import RTorrentClient, get_rtorrent_client


@pytest.fixture
def mock_server():
    """Mock rTorrent server"""
    mock_server = MagicMock()
    mock_server.system.listMethods.return_value = ["d.get_name", "d.get_state"]
    mock_server.download_list.return_value = ["hash1", "hash2"]
    mock_server.d.get_name.side_effect = ["Torrent 1", "Torrent 2"]
    mock_server.d.get_state.side_effect = ["active", "paused"]
    mock_server.d.get_size_bytes.side_effect = [1000000, 2000000]
    mock_server.d.get_completed_bytes.side_effect = [500000, 1500000]
    return mock_server


@pytest.fixture
def client(mock_server):
    """RTorrent client with mocked server"""
    client = RTorrentClient()
    client.server = mock_server
    client.connected = True
    return client


class TestRTorrentClient:
    """Unit tests for RTorrentClient"""

    def test_connect_success(self, mock_server):
        """Test successful connection"""
        client = RTorrentClient()
        client.server = mock_server

        async def test_connect():
            result = await client.connect()
            assert result is True
            assert client.connected is True

        asyncio.run(test_connect())

    def test_get_torrents(self, client, mock_server):
        """Test getting torrents list"""
        async def test_get_torrents():
            torrents = await client.get_torrents()
            assert len(torrents) == 2
            assert torrents[0]["name"] == "Torrent 1"
            assert torrents[0]["state"] == "active"
            assert torrents[0]["progress"] == 50.0

        asyncio.run(test_get_torrents())

    def test_add_torrent(self, client, mock_server):
        """Test adding torrent"""
        mock_server.load_start.return_value = "new_hash"

        async def test_add_torrent():
            result = await client.add_torrent("magnet://test")
            assert result["status"] == "success"
            assert result["hash"] == "new_hash"
            assert result["category"] == "anime"

        asyncio.run(test_add_torrent())

    def test_pause_torrent(self, client, mock_server):
        """Test pausing torrent"""
        async def test_pause_torrent():
            result = await client.pause_torrent("hash1")
            assert result["status"] == "success"
            assert result["hash"] == "hash1"
            assert result["action"] == "paused"

        asyncio.run(test_pause_torrent())

    def test_resume_torrent(self, client, mock_server):
        """Test resuming torrent"""
        async def test_resume_torrent():
            result = await client.resume_torrent("hash1")
            assert result["status"] == "success"
            assert result["hash"] == "hash1"
            assert result["action"] == "resumed"

        asyncio.run(test_resume_torrent())

    def test_delete_torrent(self, client, mock_server):
        """Test deleting torrent"""
        async def test_delete_torrent():
            result = await client.delete_torrent("hash1", delete_files=False)
            assert result["status"] == "success"
            assert result["hash"] == "hash1"
            assert result["action"] == "deleted"
            assert result["files_deleted"] is False

        asyncio.run(test_delete_torrent())


class TestRTorrentClientSingleton:
    """Test singleton pattern"""

    def test_get_client_singleton(self):
        """Test that get_rtorrent_client returns singleton"""
        async def test_singleton():
            client1 = await get_rtorrent_client()
            client2 = await get_rtorrent_client()
            assert client1 is client2

        asyncio.run(test_singleton())
